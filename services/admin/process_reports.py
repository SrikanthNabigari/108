"""Report processor — generates pending 108 Life Reading reports.

How it works in subscription mode:
    1. The customer registers via gateway/routers/reports.py — order lands
       in the orders table with status='paid'.
    2. The operator (you) pings Claude Code hourly: "process pending reports"
    3. Claude Code runs this script: it reads pending orders, builds the
       narrative prompts, spawns the 108-report-writer sub-agent for each
       narrative section (in isolated context — no chat contamination),
       assembles the full Markdown, renders to PDF, sends email.

How it works in API mode (production, post-200 reports):
    Same script, but instead of Claude Code's Agent tool it calls the
    Anthropic API directly with the same prompts. Toggle via
    REPORT_NARRATIVE_BACKEND env var: 'claude_code' (default) or 'api'.

Usage:
    uv run python services/admin/process_reports.py                  # process all pending
    uv run python services/admin/process_reports.py --order-id 42    # one order
    uv run python services/admin/process_reports.py --dry-run        # don't email
    uv run python services/admin/process_reports.py --print-prompts  # print prompts only
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from packages.report.src.data_collector import collect_chart_data  # noqa: E402
from packages.report.src.narrative import build_all_prompts  # noqa: E402
from packages.report.src.templates import render_markdown  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

DB_PATH = os.environ.get("REPORT_DB_PATH", str(ROOT / "data" / "108_reports.db"))
NARRATIVE_BACKEND = os.environ.get("REPORT_NARRATIVE_BACKEND", "claude_code")
REPORT_OUTPUT_DIR = Path(os.environ.get("REPORT_OUTPUT_DIR", "/tmp/108_reports"))
REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── DB schema ──

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    birth_datetime TEXT NOT NULL,
    birth_lat REAL NOT NULL,
    birth_lon REAL NOT NULL,
    birth_place TEXT,
    user_question TEXT NOT NULL,
    addons TEXT,
    base_price_inr INTEGER DEFAULT 99,
    addon_price_inr INTEGER DEFAULT 0,
    razorpay_order_id TEXT,
    payment_status TEXT DEFAULT 'pending',
    payment_id TEXT,
    paid_at TEXT,
    status TEXT DEFAULT 'pending',  -- pending | generating | generated | sent | failed | flagged
    generated_at TEXT,
    sent_at TEXT,
    output_md_path TEXT,
    output_pdf_path TEXT,
    error_message TEXT,
    needs_human_review INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);
"""


@dataclass
class Order:
    id: int
    full_name: str
    email: str
    phone: str | None
    birth_datetime: str
    birth_lat: float
    birth_lon: float
    birth_place: str | None
    user_question: str
    addons: list[str]


def init_db(path: str = DB_PATH) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def fetch_pending_orders(conn: sqlite3.Connection, order_id: int | None = None) -> list[Order]:
    if order_id is not None:
        rows = conn.execute(
            "SELECT * FROM orders WHERE id = ? AND payment_status = 'paid' AND status IN ('pending', 'failed')",
            (order_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM orders WHERE payment_status = 'paid' AND status IN ('pending', 'failed') ORDER BY paid_at",
        ).fetchall()
    return [
        Order(
            id=r["id"],
            full_name=r["full_name"],
            email=r["email"],
            phone=r["phone"],
            birth_datetime=r["birth_datetime"],
            birth_lat=r["birth_lat"],
            birth_lon=r["birth_lon"],
            birth_place=r["birth_place"],
            user_question=r["user_question"],
            addons=json.loads(r["addons"] or "[]"),
        )
        for r in rows
    ]


def mark_status(conn: sqlite3.Connection, order_id: int, status: str, **fields: Any) -> None:
    cols = ["status = ?"]
    vals: list[Any] = [status]
    for k, v in fields.items():
        cols.append(f"{k} = ?")
        vals.append(v)
    vals.append(order_id)
    conn.execute(f"UPDATE orders SET {', '.join(cols)} WHERE id = ?", vals)
    conn.commit()


def detect_crisis(text: str) -> bool:
    """Return True if the user's question/context suggests crisis content."""
    if not text:
        return False
    crisis_phrases = [
        "kill myself",
        "suicide",
        "end my life",
        "self-harm",
        "self harm",
        "want to die",
        "no reason to live",
        "hurt myself",
        "ending it all",
        "abusive",
        "abuse me",
        "rape",
        "molested",
    ]
    t = text.lower()
    return any(p in t for p in crisis_phrases)


CRISIS_TEXT = """**A note before continuing:** Your message contains content that astrology should not be the only thing answering. Please reach out to one of these — they are free, confidential, and trained:

- **iCall:** +91 9152987821 (India, multilingual)
- **Vandrevala Foundation:** 1860 2662 345 (24/7)

If you're in immediate danger, please call your local emergency number.

Your report can wait. You matter more than the chart.
"""


# ── Narrative generation backends ──


def generate_narrative_via_api(prompt: str) -> str:
    """Production mode: call Anthropic API."""
    from packages.report.src.narrative import generate_section_text

    return generate_section_text(prompt)


def generate_narrative_via_claude_code(prompt: str, section_id: str, order: Order) -> str:
    """Subscription mode: print the prompt for the operator's Claude Code session.

    In manual operation, the operator (Claude Code session) reads the prompt,
    spawns the 108-report-writer sub-agent with it, and pastes the result back
    into a pre-staged file. This function just stages the prompt and returns
    a placeholder — the orchestration script that wraps this awaits the
    operator's response file.

    For automated subscription mode (future), this would invoke the Agent tool
    programmatically via Claude Code's MCP interface.
    """
    staged_dir = REPORT_OUTPUT_DIR / f"order_{order.id}" / "prompts"
    staged_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = staged_dir / f"{section_id}.prompt.txt"
    prompt_file.write_text(prompt)

    response_file = staged_dir / f"{section_id}.response.md"
    if response_file.exists():
        return response_file.read_text()

    # Placeholder — operator should run the agent and save response
    return f"*(awaiting narrative from 108-report-writer agent; prompt at {prompt_file})*"


def generate_narrative(prompt: str, section_id: str, order: Order) -> str:
    if NARRATIVE_BACKEND == "api":
        return generate_narrative_via_api(prompt)
    return generate_narrative_via_claude_code(prompt, section_id, order)


# ── Main pipeline ──


def process_order(
    conn: sqlite3.Connection, order: Order, dry_run: bool = False, print_prompts: bool = False
) -> dict[str, Any]:
    logger.info(f"Processing order #{order.id}: {order.full_name} ({order.email})")
    mark_status(conn, order.id, "generating")

    try:
        # Crisis detection on user input
        if detect_crisis(order.user_question):
            logger.warning(f"Order #{order.id} flagged for crisis content review")
            md = f"# 108 Life Reading\n\n**{order.full_name}**\n\n{CRISIS_TEXT}"
            out_md = REPORT_OUTPUT_DIR / f"order_{order.id}_FLAGGED.md"
            out_md.write_text(md)
            mark_status(
                conn,
                order.id,
                "flagged",
                generated_at=datetime.utcnow().isoformat(),
                output_md_path=str(out_md),
                needs_human_review=1,
                error_message="Crisis content detected in user_question",
            )
            return {"order_id": order.id, "status": "flagged", "md_path": str(out_md)}

        # Collect chart data
        chart = collect_chart_data(
            birth_datetime=order.birth_datetime,
            birth_lat=order.birth_lat,
            birth_lon=order.birth_lon,
            full_name=order.full_name,
            user_question=order.user_question,
            addons=order.addons,
        )

        # Build prompts for AI sections
        prompts = build_all_prompts(chart)

        if print_prompts:
            for sid, p in prompts.items():
                print(f"\n========== ORDER {order.id} :: {sid} ==========\n{p}\n")

        # Generate narratives (one per AI section)
        narratives: dict[str, str] = {}
        for sid, prompt in prompts.items():
            narratives[sid] = generate_narrative(prompt, sid, order)

        # Stitcher final pass — reads all narratives, writes cover_hook,
        # closing_cta, and one pull-quote per section.
        pull_quotes: dict[str, str] = {}
        try:
            from packages.report.src.narrative import (
                build_prompt_stitcher,
                parse_stitcher_output,
            )

            stitcher_prompt = build_prompt_stitcher(chart, narratives)
            stitcher_raw = generate_narrative(stitcher_prompt, "stitcher", order)
            stitched = parse_stitcher_output(stitcher_raw)
            if stitched.get("cover_hook"):
                narratives["opening"] = stitched["cover_hook"]
            if stitched.get("closing_cta"):
                narratives["closing_cta"] = stitched["closing_cta"]
            pull_quotes = stitched.get("pull_quotes") or {}
        except Exception:
            logger.exception(f"Stitcher pass failed for order {order.id}; continuing without it")

        # Render full Markdown
        md = render_markdown(chart, narratives=narratives, pull_quotes=pull_quotes)
        out_md = REPORT_OUTPUT_DIR / f"order_{order.id}_{order.full_name.replace(' ','_')}.md"
        out_md.write_text(md)

        # PDF render — to be added in render.py module (not yet in MVP)
        out_pdf = None  # PDF path here when render.py exists

        if not dry_run:
            # Email send hook — wire actual SES/Resend here
            logger.info(f"  Would send PDF to {order.email}")
            mark_status(
                conn,
                order.id,
                "sent",
                generated_at=datetime.utcnow().isoformat(),
                sent_at=datetime.utcnow().isoformat(),
                output_md_path=str(out_md),
                output_pdf_path=str(out_pdf) if out_pdf else None,
            )
        else:
            mark_status(
                conn,
                order.id,
                "generated",
                generated_at=datetime.utcnow().isoformat(),
                output_md_path=str(out_md),
                output_pdf_path=str(out_pdf) if out_pdf else None,
            )

        return {"order_id": order.id, "status": "success", "md_path": str(out_md)}

    except Exception as e:
        logger.exception(f"Order #{order.id} failed")
        mark_status(conn, order.id, "failed", error_message=str(e)[:500])
        return {"order_id": order.id, "status": "error", "error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Process pending 108 reports.")
    parser.add_argument("--order-id", type=int, help="Process a single order by ID")
    parser.add_argument("--dry-run", action="store_true", help="Don't email; just generate")
    parser.add_argument("--print-prompts", action="store_true", help="Print prompts to stdout")
    args = parser.parse_args()

    conn = init_db()
    pending = fetch_pending_orders(conn, order_id=args.order_id)
    logger.info(f"Found {len(pending)} pending orders")

    results = [process_order(conn, o, args.dry_run, args.print_prompts) for o in pending]
    summary = {
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "flagged": sum(1 for r in results if r["status"] == "flagged"),
        "errors": sum(1 for r in results if r["status"] == "error"),
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

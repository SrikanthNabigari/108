#!/usr/bin/env python3
"""v20 fulfillment — generate the report for a paid storefront (Supabase) order.

Pipeline: read order from the STOREFRONT Supabase (los_orders) → collect chart
data → generate narratives (Anthropic API, gated by REPORT_API_ENABLED) →
stitch → render PDF → upload to the `los-reports` bucket → 30-day signed URL →
insert `los_reports` → mark order `ready` → email the customer (SMTP).

Env (auto-loaded from repo-root .env.local + .env, env wins):
  STOREFRONT Supabase : SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY   (.env.local)
  Generation          : ANTHROPIC_API_KEY, REPORT_API_ENABLED=true (.env)
  Email               : SMTP_HOST/PORT/USER/PASS (+ optional FROM_*)

When REPORT_API_ENABLED is not "true", the script refuses the API path (so the
Anthropic key is never billed unless explicitly switched on) and exits — that
order is left for the scheduled Claude Code subscription path instead.

Usage:
  uv run python services/admin/generate_v20_order.py <order_id>
  uv run python services/admin/generate_v20_order.py --next     # oldest paid order
"""
from __future__ import annotations

import json
import smtplib
import ssl
import sys
import urllib.request
from datetime import UTC, datetime
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


# ── env loading ──────────────────────────────────────────────────────────
def load_env() -> dict[str, str]:
    import os

    env: dict[str, str] = {}
    for fname in (".env", ".env.local"):  # .env.local wins for Supabase storefront
        fp = ROOT / fname
        if not fp.exists():
            continue
        for line in fp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if v})
    # Export to os.environ so downstream code (generate_section_text reads
    # os.environ["ANTHROPIC_API_KEY"]) sees the file-loaded values too.
    for k, v in env.items():
        os.environ.setdefault(k, v)
    return env


ENV = load_env()
SB_URL = ENV["SUPABASE_URL"]
SB_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
HDR = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}
# "api" (Anthropic SDK) or "claude_code" (assemble from staged agent responses)
BACKEND = ENV.get("REPORT_BACKEND", "api").lower()


# ── Supabase REST helpers ────────────────────────────────────────────────
def sb_req(method: str, path: str, body: dict | list | None = None, extra: dict | None = None):
    url = f"{SB_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {**HDR, "Content-Type": "application/json"}
    if extra:
        headers.update(extra)
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw.strip() else None


def get_order(order_id: str) -> dict:
    rows = sb_req("GET", f"/rest/v1/los_orders?id=eq.{order_id}&select=*")
    if not rows:
        raise SystemExit(f"order {order_id} not found")
    return rows[0]


def next_paid_order() -> dict | None:
    rows = sb_req(
        "GET",
        "/rest/v1/los_orders?status=eq.paid&select=*&order=paid_at.asc&limit=1",
    )
    return rows[0] if rows else None


def set_status(order_id: str, status: str, **fields):
    sb_req(
        "PATCH",
        f"/rest/v1/los_orders?id=eq.{order_id}",
        {"status": status, **fields},
        {"Prefer": "return=minimal"},
    )


# ── storage ──────────────────────────────────────────────────────────────
def upload_pdf(order_id: str, pdf: bytes) -> str:
    """Upload to los-reports bucket (upsert) and return a 30-day signed URL."""
    obj_path = f"{order_id}/108-life-reading.pdf"
    up = urllib.request.Request(
        f"{SB_URL}/storage/v1/object/los-reports/{obj_path}",
        data=pdf,
        method="POST",
        headers={**HDR, "Content-Type": "application/pdf", "x-upsert": "true"},
    )
    with urllib.request.urlopen(up, timeout=120) as r:
        r.read()
    signed = sb_req(
        "POST",
        f"/storage/v1/object/sign/los-reports/{obj_path}",
        {"expiresIn": 60 * 60 * 24 * 30},
    )
    return f"{SB_URL}/storage/v1{signed['signedURL']}", obj_path


# ── email ────────────────────────────────────────────────────────────────
def send_ready_email(to: str, name: str, url: str):
    host = ENV.get("SMTP_HOST")
    user = ENV.get("SMTP_USER") or ENV.get("GMAIL_SENDER_ADDRESS")
    pw = ENV.get("SMTP_PASS") or (ENV.get("GMAIL_APP_PASSWORD") or "").replace(" ", "")
    if not (host and user and pw):
        print("  [email] SMTP not configured — skipping email", file=sys.stderr)
        return False
    port = int(ENV.get("SMTP_PORT", 587))
    from_name = ENV.get("SMTP_FROM_NAME", "108 — Life's Operating System")
    html = f"""<div style="font-family:Georgia,serif;max-width:520px;margin:auto;color:#1a1a1a">
      <h2 style="color:#b8860b">Namaste {name},</h2>
      <p>Your 108 Life Reading has been decoded and is ready to download.</p>
      <p style="margin:28px 0"><a href="{url}"
        style="background:#b8860b;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none">
        Download your reading (PDF)</a></p>
      <p style="color:#666;font-size:13px">This private link expires in 30 days — save the PDF.</p>
      <p style="color:#999;font-size:12px;margin-top:32px">108 — Life's Operating System</p>
    </div>"""
    msg = MIMEText(html, "html")
    msg["Subject"] = "Your 108 Life Reading is ready"
    msg["From"] = f"{from_name} <{user}>"
    msg["To"] = to
    s = smtplib.SMTP(host, port, timeout=30)
    s.starttls(context=ssl.create_default_context())
    s.login(user, pw)
    s.sendmail(user, [to], msg.as_string())
    s.quit()
    return True


# ── narrative generation ─────────────────────────────────────────────────
def generate_narratives(chart: dict) -> tuple[dict[str, str], dict[str, str], str]:
    from packages.report.src.narrative import (
        build_all_prompts,
        build_prompt_stitcher,
        generate_section_text,
        parse_stitcher_output,
    )

    model = ENV.get("REPORT_MODEL", "claude-sonnet-4-6")
    prompts = build_all_prompts(chart)
    narratives: dict[str, str] = {}
    for sid, prompt in prompts.items():
        print(f"  · section {sid} …", file=sys.stderr)
        try:
            narratives[sid] = generate_section_text(prompt, model=model)
        except Exception as e:
            narratives[sid] = f"*(section unavailable: {e})*"
    pull_quotes: dict[str, str] = {}
    try:
        raw = generate_section_text(build_prompt_stitcher(chart, narratives), model=model)
        stitched = parse_stitcher_output(raw)
        if stitched.get("cover_hook"):
            narratives["opening"] = stitched["cover_hook"]
        if stitched.get("closing_cta"):
            narratives["closing_cta"] = stitched["closing_cta"]
        pull_quotes = stitched.get("pull_quotes") or {}
    except Exception as e:
        print(f"  [stitcher] failed: {e}", file=sys.stderr)
    return narratives, pull_quotes, model


def generate_narratives_cc(chart: dict, stage: Path) -> tuple[dict[str, str], dict[str, str], str]:
    """Claude Code path: assemble narratives from staged agent .response.md files.

    Builds the stitcher prompt from the section narratives; if its response
    isn't staged yet, writes the prompt and exits so the operator can run the
    108-stitcher agent, then re-run this script.
    """
    from packages.report.src.narrative import (
        build_all_prompts,
        build_prompt_stitcher,
        parse_stitcher_output,
    )

    prompts = build_all_prompts(chart)
    narratives: dict[str, str] = {}
    missing = []
    for sid in prompts:
        rf = stage / f"{sid}.response.md"
        if rf.exists() and rf.read_text(encoding="utf-8").strip():
            narratives[sid] = rf.read_text(encoding="utf-8").strip()
        else:
            missing.append(sid)
    if missing:
        raise SystemExit(f"missing staged responses for: {', '.join(missing)}")

    pull_quotes: dict[str, str] = {}
    stitch_resp = stage / "stitcher.response.md"
    if stitch_resp.exists() and stitch_resp.read_text(encoding="utf-8").strip():
        stitched = parse_stitcher_output(stitch_resp.read_text(encoding="utf-8"))
        if stitched.get("cover_hook"):
            narratives["opening"] = stitched["cover_hook"]
        if stitched.get("closing_cta"):
            narratives["closing_cta"] = stitched["closing_cta"]
        pull_quotes = stitched.get("pull_quotes") or {}
    else:
        (stage / "stitcher.prompt.txt").write_text(
            build_prompt_stitcher(chart, narratives), encoding="utf-8"
        )
        raise SystemExit(
            "STITCHER PENDING — staged stitcher.prompt.txt. Run the 108-stitcher "
            f"agent on it, save to {stitch_resp}, then re-run this script."
        )
    return narratives, pull_quotes, "claude_code"


# ── main ─────────────────────────────────────────────────────────────────
def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else "--next"
    order = next_paid_order() if arg == "--next" else get_order(arg)
    if not order:
        print("No paid order to process.")
        return

    oid = order["id"]
    print(
        f"Order {oid}: {order['full_name']} <{order['email']}> · {order['pack_id']} · {order['status']}"
    )

    if order["status"] not in ("paid", "generating"):
        raise SystemExit(f"order status is '{order['status']}', expected paid")

    if BACKEND == "api":
        if ENV.get("REPORT_API_ENABLED", "false").lower() != "true":
            raise SystemExit(
                "REPORT_API_ENABLED is not 'true' — Anthropic API path disabled. "
                "Set REPORT_API_ENABLED=true to bill the API, or REPORT_BACKEND="
                "claude_code to assemble from staged agent responses."
            )
        if not ENV.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY not set")

    set_status(oid, "generating")

    # birth datetime → ISO with tz (storefront stores naive IST)
    bdt = str(order["birth_datetime"])
    if "+" not in bdt and "Z" not in bdt:
        bdt = bdt.replace(" ", "T")
        bdt = (
            f"{bdt}+05:30"
            if order.get("timezone", "Asia/Kolkata") == "Asia/Kolkata"
            else f"{bdt}+00:00"
        )

    from packages.report.src.data_collector import collect_chart_data
    from packages.report.src.render import markdown_to_pdf
    from packages.report.src.templates import render_markdown

    print("  collecting chart data …", file=sys.stderr)
    chart = collect_chart_data(
        birth_datetime=bdt,
        birth_lat=float(order["birth_latitude"]),
        birth_lon=float(order["birth_longitude"]),
        full_name=order["full_name"],
        user_question=order.get("user_question") or "",
        addons=order.get("addons") or [],
    )

    print(f"  generating narratives (backend={BACKEND}) …", file=sys.stderr)
    if BACKEND == "claude_code":
        stage = ROOT / "docs" / "reports" / "v20_orders" / f"order_{oid}" / "prompts"
        narratives, pull_quotes, model = generate_narratives_cc(chart, stage)
    else:
        narratives, pull_quotes, model = generate_narratives(chart)

    print("  rendering PDF …", file=sys.stderr)
    md = render_markdown(chart, narratives=narratives, pull_quotes=pull_quotes)
    out_dir = ROOT / "docs" / "reports" / "v20_orders"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"order_{oid}.pdf"
    pdf = markdown_to_pdf(md, output_path=pdf_path, chart_data=chart)
    (out_dir / f"order_{oid}.md").write_text(md, encoding="utf-8")

    page_count = None
    try:
        from pypdf import PdfReader

        page_count = len(PdfReader(str(pdf_path)).pages)
    except Exception:
        pass

    print("  uploading to los-reports bucket …", file=sys.stderr)
    public_url, obj_path = upload_pdf(oid, pdf)

    now = datetime.now(UTC).isoformat()
    sb_req(
        "POST",
        "/rest/v1/los_reports",
        {
            "order_id": oid,
            "pdf_path": obj_path,
            "public_url": public_url,
            "page_count": page_count,
            "file_size_bytes": len(pdf),
            "backend": BACKEND,
            "model_used": model,
            "generated_at": now,
        },
        {"Prefer": "return=minimal"},
    )
    set_status(oid, "ready", generated_at=now)

    print("  emailing customer …", file=sys.stderr)
    emailed = send_ready_email(order["email"], order["full_name"], public_url)
    if emailed:
        set_status(oid, "delivered", delivered_at=now)

    print(f"\nDONE · {page_count or '?'} pages · {len(pdf)//1024} KB")
    print(f"  PDF   : {pdf_path}")
    print(f"  URL   : {public_url}")
    print(f"  status: {'delivered' if emailed else 'ready'}")


if __name__ == "__main__":
    main()

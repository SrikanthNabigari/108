#!/usr/bin/env python3
"""Stage section prompts for a paid v20 order (Claude Code subscription path).

Collects chart data, builds every section prompt, and writes them to
docs/reports/v20_orders/order_<id>/prompts/<section>.prompt.txt plus a
manifest.json mapping each section -> agent + prompt/response paths.

The operator (Claude Code session) then runs each section's agent on its
prompt file and saves the narrative to <section>.response.md. Finally
generate_v20_order.py with REPORT_BACKEND=claude_code assembles them.

Usage: uv run python services/admin/stage_v20_prompts.py <order_id>
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def load_env() -> dict[str, str]:
    import os

    env: dict[str, str] = {}
    for fname in (".env", ".env.local"):
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
    return env


ENV = load_env()
SB_URL = ENV["SUPABASE_URL"]
SB_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]


def get_order(order_id: str) -> dict:
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/los_orders?id=eq.{order_id}&select=*",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    )
    rows = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    if not rows:
        raise SystemExit(f"order {order_id} not found")
    return rows[0]


def main() -> None:
    oid = sys.argv[1]
    order = get_order(oid)

    bdt = str(order["birth_datetime"])
    if "+" not in bdt and "Z" not in bdt:
        bdt = bdt.replace(" ", "T") + "+05:30"

    from packages.report.src.data_collector import collect_chart_data
    from packages.report.src.narrative import SECTION_AGENT, build_all_prompts

    chart = collect_chart_data(
        birth_datetime=bdt,
        birth_lat=float(order["birth_latitude"]),
        birth_lon=float(order["birth_longitude"]),
        full_name=order["full_name"],
        user_question=order.get("user_question") or "",
        addons=order.get("addons") or [],
    )
    prompts = build_all_prompts(chart)

    stage = ROOT / "docs" / "reports" / "v20_orders" / f"order_{oid}" / "prompts"
    stage.mkdir(parents=True, exist_ok=True)

    manifest = {}
    for sid, prompt in prompts.items():
        ppath = stage / f"{sid}.prompt.txt"
        ppath.write_text(prompt, encoding="utf-8")
        manifest[sid] = {
            "agent": SECTION_AGENT.get(sid, "108-report-writer"),
            "prompt": str(ppath),
            "response": str(stage / f"{sid}.response.md"),
        }
    (stage / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"order {oid}: {order['full_name']} · {order['pack_id']} · {len(prompts)} sections")
    print(f"staged -> {stage}")
    for sid, m in manifest.items():
        print(f"  {sid:26s} -> {m['agent']}")


if __name__ == "__main__":
    main()

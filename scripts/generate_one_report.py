#!/usr/bin/env python3
"""Single-order report generator. Invoked by 108-website's order_worker.

Reads a JSON spec from stdin:
  {
    "order_id": "...",
    "full_name": "...",
    "birth_datetime": "1992-12-03T03:00:00+05:30",
    "birth_lat": 16.7,
    "birth_lon": 81.3,
    "user_question": "...",
    "addons": ["past_5_years", ...],
    "partner_birth": null | {...},
    "output_pdf": "/abs/path/to/order.pdf"
  }

For now this writes a STUB PDF — real agent orchestration requires the
Anthropic API path (services/admin/process_reports.py with NARRATIVE_BACKEND='api')
or the operator running agents manually. When ANTHROPIC_API_KEY is set,
we use the API path. Otherwise we render a placeholder explaining the situation.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Make 108-core importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.report.src.data_collector import collect_chart_data
from packages.report.src.narrative import build_all_prompts, parse_stitcher_output
from packages.report.src.render import markdown_to_pdf
from packages.report.src.templates import render_markdown


def main() -> None:
    spec = json.loads(sys.stdin.read())

    chart = collect_chart_data(
        birth_datetime=spec["birth_datetime"],
        birth_lat=float(spec["birth_lat"]),
        birth_lon=float(spec["birth_lon"]),
        full_name=spec["full_name"],
        user_question=spec.get("user_question") or "",
        addons=spec.get("addons") or [],
    )

    narratives: dict[str, str] = {}
    pull_quotes: dict[str, str] = {}

    # If Anthropic API is configured, generate via API
    if os.environ.get("ANTHROPIC_API_KEY"):
        from packages.report.src.narrative import build_prompt_stitcher, generate_section_text

        prompts = build_all_prompts(chart)
        for sid, prompt in prompts.items():
            try:
                narratives[sid] = generate_section_text(prompt)
            except Exception as e:
                narratives[sid] = f"*(section failed to generate: {e})*"
        # Stitcher
        try:
            stitcher_prompt = build_prompt_stitcher(chart, narratives)
            raw = generate_section_text(stitcher_prompt)
            stitched = parse_stitcher_output(raw)
            if stitched.get("cover_hook"):
                narratives["opening"] = stitched["cover_hook"]
            if stitched.get("closing_cta"):
                narratives["closing_cta"] = stitched["closing_cta"]
            pull_quotes = stitched.get("pull_quotes") or {}
        except Exception as e:
            print(f"[generate_one] stitcher failed: {e}", file=sys.stderr)
    else:
        # Stub mode — clearly inform the customer's PDF that this is a placeholder
        narratives["opening"] = (
            "This report was queued before the agent pipeline was fully wired. "
            "Your operator has been notified — the real reading will follow within 24 hours."
        )

    md = render_markdown(chart, narratives=narratives, pull_quotes=pull_quotes)
    out_path = Path(spec["output_pdf"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_to_pdf(md, output_path=out_path, chart_data=chart)
    print(f"[generate_one] wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

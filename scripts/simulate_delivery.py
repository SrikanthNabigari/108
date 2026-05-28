#!/usr/bin/env python3
"""Simulate Phase 1 delivery flow end-to-end.

What this does:

    1. Loads (or builds) a customer chart
    2. Runs the Chart-Specific Question Generator (CSQG)
    3. Prints the WhatsApp message + click-to-chat link the operator would use
    4. Prints the operator audit block
    5. Emails the existing v11 PDF (the previously-generated report) to the
       test recipient with the proper subject + body

Run:
    uv run python scripts/simulate_delivery.py
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

# Make 108-core importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.report.src.delivery import (
    _env,
    build_intake_questions_message,
    build_report_delivery_email,
    build_whatsapp_link,
    send_pdf_email,
)
from packages.report.src.question_generator import (
    generate_questions,
    to_audit_block,
)


def main() -> None:
    print("=" * 72)
    print("108 — Phase 1 delivery simulation")
    print("=" * 72)
    print()

    # ── 1. Load Srikanth's chart from the existing v10 build ───────────
    chart_pkl = Path("/tmp/srikanth_super_v10/chart.pkl")
    if not chart_pkl.exists():
        print(f"FAIL: chart pickle not found at {chart_pkl}")
        sys.exit(1)
    with Path(chart_pkl).open("rb") as f:
        chart = pickle.load(f)
    full_name = chart["birth"]["full_name"]
    print(f"[1] Chart loaded for: {full_name}")
    print(f"    Lagna: {chart['lagna']['rashi']} {chart['lagna']['degree']:.2f}°")
    print(f"    Moon:  {chart['moon']['rashi']} {chart['moon']['nakshatra']}")
    print()

    # ── 2. Run the CSQG ────────────────────────────────────────────────
    questions = generate_questions(chart)
    print(f"[2] CSQG fired {len(questions)} chart-specific questions")
    print()
    print(to_audit_block(questions))
    print()

    # ── 3. Build the WhatsApp message + wa.me link ─────────────────────
    msg = build_intake_questions_message(full_name, questions, order_id="DEMO-001")
    customer_whatsapp = _env("OPERATOR_WHATSAPP_NUMBER")  # using operator's
    # own number for this simulation so the link opens on their phone
    wa_link = build_whatsapp_link(customer_whatsapp, msg)
    print("[3] WhatsApp click-to-chat link (operator clicks to send):")
    print()
    print(f"    {wa_link}")
    print()
    print(f"    (URL length: {len(wa_link)} chars)")
    print()
    print("--- WhatsApp message body (pre-filled in WhatsApp on click) ---")
    print(msg)
    print("--- end message ---")
    print()

    # ── 4. Email the v11 PDF to test recipient ─────────────────────────
    pdf_path = Path(
        "/home/ubuntu/projects/swarodaya/SWARODAYA/108-core/docs/reports/"
        "v4_test_pool/srikanth_SUPER_v11.pdf"
    )
    if not pdf_path.exists():
        print(f"FAIL: PDF not found at {pdf_path}")
        sys.exit(1)
    to_addr = _env("TEST_DELIVERY_EMAIL")
    subject, body_text, body_html = build_report_delivery_email(full_name, used_intake=True)
    print("[4] Sending PDF email...")
    print(f"    From:    {_env('GMAIL_SENDER_ADDRESS')}")
    print(f"    To:      {to_addr}")
    print(f"    Subject: {subject}")
    print(f"    PDF:     {pdf_path.name} ({pdf_path.stat().st_size / 1024:.0f} KB)")
    print()
    try:
        result = send_pdf_email(
            to_address=to_addr,
            subject=subject,
            body_text=body_text,
            pdf_path=pdf_path,
            body_html=body_html,
        )
        print(f"    ✓ Sent. {result['size_bytes'] / 1024:.0f} KB attachment delivered.")
    except RuntimeError as e:
        print(f"    ✗ {e}")
        sys.exit(2)
    print()

    print("=" * 72)
    print("Simulation complete.")
    print("=" * 72)
    print()
    print("What the operator would do in real life:")
    print("  - Click the wa.me link above on a phone (or desktop WhatsApp)")
    print("  - WhatsApp opens with the question message pre-filled")
    print("  - Tap send (the customer receives it)")
    print("  - Wait for customer's reply on WhatsApp")
    print("  - Paste reply into intake_events.json, run generate_report")
    print("  - Email PDF (this script just did that)")
    print()
    print("If customer doesn't reply within 24 hours: generate report without")
    print("intake_events — 'What Already Happened' section is conditional and")
    print("won't render, but the rest of the report is still strong.")


if __name__ == "__main__":
    main()

"""Delivery layer — WhatsApp click-to-chat links + Gmail SMTP email with PDF.

Phase 1 architecture (manual operator workflow):

    1. Customer pays + submits birth details (website form)
    2. Backend computes chart + runs CSQG → 5-7 chart-specific questions
    3. Backend builds a wa.me link with questions embedded
    4. Operator clicks link → WhatsApp opens with message pre-filled to customer
    5. Operator hits send (or the customer's WhatsApp shows incoming)
    6. Customer replies on WhatsApp (24h window)
    7. Operator pastes replies into the system, triggers report generation
    8. Backend sends PDF as email attachment (Gmail SMTP)

Phase 2 (when economics permit): replace wa.me + manual operator with WhatsApp
Business API (Gupshup / WATI), keep the email-PDF leg.

Credentials live in .env (gitignored):
    GMAIL_SENDER_ADDRESS, GMAIL_APP_PASSWORD, SMTP_HOST, SMTP_PORT
    OPERATOR_WHATSAPP_NUMBER (not used here — operator's own number;
        we use the customer's number to build the wa.me link)
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote


def _env(key: str, default: str | None = None) -> str:
    """Read env var, optionally falling back to .env file in project root."""
    val = os.getenv(key)
    if val:
        return val
    # Tiny .env loader so this module works without external deps
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key:
                return v.strip()
    if default is not None:
        return default
    raise RuntimeError(f"Missing required env var: {key}")


# ── WhatsApp click-to-chat link ──────────────────────────────────────


def build_whatsapp_link(phone_number: str, message: str) -> str:
    """Build a wa.me URL that opens WhatsApp with a pre-filled message.

    Args:
        phone_number: Customer's number with country code, NO + or spaces.
            E.g. "919441997979" for India +91 94419 97979.
        message: The message text. Will be URL-encoded.

    Returns:
        A wa.me URL string. Operator clicks → WhatsApp opens → operator
        confirms send. Phase 2 will replace this with Business API.

    Notes:
        - wa.me URLs are length-limited (~4096 chars after encoding).
        - If your message exceeds that, split into 2 messages.
    """
    digits_only = "".join(c for c in phone_number if c.isdigit())
    encoded = quote(message, safe="")
    return f"https://wa.me/{digits_only}?text={encoded}"


# ── Gmail SMTP email + PDF attachment ────────────────────────────────


def send_pdf_email(
    to_address: str,
    subject: str,
    body_text: str,
    pdf_path: str | Path,
    from_address: str | None = None,
    body_html: str | None = None,
) -> dict:
    """Send an email with PDF attachment via Gmail SMTP.

    Args:
        to_address: Recipient email.
        subject: Email subject line.
        body_text: Plain-text body.
        pdf_path: Path to PDF file to attach.
        from_address: Sender address (defaults to GMAIL_SENDER_ADDRESS).
        body_html: Optional HTML body (multipart alternative).

    Returns:
        dict with {ok, message_id, to, subject, attached_pdf, size_bytes}.

    Raises:
        RuntimeError on SMTP / auth / attachment failure.
    """
    sender = from_address or _env("GMAIL_SENDER_ADDRESS")
    password = _env("GMAIL_APP_PASSWORD")
    smtp_host = _env("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(_env("SMTP_PORT", "587"))
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise RuntimeError(f"PDF not found: {pdf_path}")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_address
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")

    pdf_bytes = pdf_path.read_bytes()
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=pdf_path.name,
    )

    # Gmail SMTP: STARTTLS on 587, then auth, then send
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            # App-password may contain spaces; Gmail accepts either form
            smtp.login(sender, password.replace(" ", ""))
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        raise RuntimeError(
            f"SMTP authentication failed for {sender}. "
            f"Verify GMAIL_APP_PASSWORD is current (regenerate at "
            f"myaccount.google.com → Security → App passwords). Error: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Email send failed: {e}") from e

    return {
        "ok": True,
        "to": to_address,
        "subject": subject,
        "attached_pdf": str(pdf_path),
        "size_bytes": len(pdf_bytes),
    }


# ── Compose helpers (templates that the orchestrator uses) ────────────


def build_intake_questions_message(
    full_name: str,
    questions: list,  # list[Question] from question_generator
    order_id: str | None = None,
) -> str:
    """Compose the WhatsApp intake-questions message body."""
    first_name = full_name.split()[0] if full_name else "there"
    lines = [
        f"Namaste {first_name},",
        "",
        "Thank you for your 108 Life Reading order"
        + (f" ({order_id})" if order_id else "")
        + ". Before generating your report, we looked at your chart and found a few "
        + "specific signatures we'd like to confirm with you. Even one-line answers are enough.",
        "",
        "(If a question doesn't apply, just reply 'skip'. Your answers stay private.)",
        "",
    ]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q.text}")
        lines.append("")
    lines.append("Reply within 24 hours and we'll deliver your report shortly after.")
    lines.append(
        "If we don't hear back, we'll generate the chart-based reading and send it anyway."
    )
    return "\n".join(lines)


def build_report_delivery_email(
    full_name: str,
    used_intake: bool,
) -> tuple[str, str, str]:
    """Compose subject + plain body + html body for the PDF delivery email."""
    first_name = full_name.split()[0] if full_name else "there"
    subject = f"Your 108 Life Reading — {full_name}"
    intake_note = (
        "\n\nThis report is grounded in the answers you shared on WhatsApp — "
        "the 'What Already Happened' section reads the years you described back "
        "to you through the lens of the chart."
        if used_intake
        else "\n\nThis report is generated from your birth chart alone. If you'd "
        "like a more personalised version that maps your specific past events to "
        "the chart, reply here with the events you remember."
    )
    body = (
        f"Namaste {first_name},\n\n"
        f"Your 108 Life Reading is attached. It is a 60+ page reading covering "
        f"your chart's architecture, your current life-chapter, the next year, "
        f"and the long arcs."
        f"{intake_note}\n\n"
        f"Open it on Chrome or any modern PDF reader. The reading is best taken "
        f"slowly — give it a quiet evening, read it twice.\n\n"
        f"If anything in the reading does not feel right, reply to this email "
        f"and we will look at it.\n\n"
        f"With care,\n"
        f"108"
    )
    html = (
        "<html><body style='font-family:Georgia,serif;font-size:14px;"
        "line-height:1.6;color:#222;'>"
        f"<p>Namaste {first_name},</p>"
        f"<p>Your 108 Life Reading is attached. It is a 60+ page reading "
        f"covering your chart's architecture, your current life-chapter, the "
        f"next year, and the long arcs.</p>"
        f"<p>{intake_note.strip()}</p>"
        f"<p>Open it on Chrome or any modern PDF reader. The reading is best "
        f"taken slowly — give it a quiet evening, read it twice.</p>"
        f"<p>If anything in the reading does not feel right, reply to this "
        f"email and we will look at it.</p>"
        f"<p style='margin-top:2em;color:#888;'>With care,<br/>108</p>"
        "</body></html>"
    )
    return subject, body, html

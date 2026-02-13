"""AI-powered report generation using Anthropic Claude."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# Report type configurations
REPORT_CONFIGS: dict[str, dict[str, Any]] = {
    "annual_report": {
        "title": "Annual Forecast Report",
        "system_prompt": (
            "You are a Vedic Astrology (Jyotish) expert generating a comprehensive "
            "annual forecast report. Analyze the birth chart, current dasha periods, "
            "and major transits to provide a 12-month outlook. Cover: career, "
            "relationships, health, finance, and spiritual growth. Be specific with "
            "timing based on planetary periods and transits."
        ),
        "sections": [
            "Overview",
            "Career & Finance",
            "Relationships & Family",
            "Health & Wellness",
            "Spiritual Growth",
            "Month-by-Month Highlights",
            "Key Dates & Transits",
            "Remedies & Recommendations",
        ],
    },
    "career_report": {
        "title": "Career Blueprint Report",
        "system_prompt": (
            "You are a Vedic Astrology expert generating a detailed career analysis. "
            "Focus on the 10th house (karma), 6th house (service), 2nd house (wealth), "
            "and 11th house (gains). Analyze the current Mahadasha and Antardasha "
            "for career timing. Include professional strengths, ideal career paths, "
            "and upcoming opportunities or challenges."
        ),
        "sections": [
            "Career Overview",
            "Professional Strengths",
            "Ideal Career Paths",
            "Current Period Analysis",
            "Upcoming Opportunities",
            "Challenges & Remedies",
            "Financial Outlook",
        ],
    },
    "health_report": {
        "title": "Health & Wellness Report",
        "system_prompt": (
            "You are a Vedic Astrology expert generating a health analysis. "
            "Focus on the 6th house (disease), 8th house (chronic conditions), "
            "and 1st house (vitality). Analyze planetary afflictions, dosha "
            "influences, and transit impacts on health. Provide Ayurvedic "
            "constitution insights and wellness recommendations."
        ),
        "sections": [
            "Health Overview",
            "Constitution Analysis",
            "Vulnerable Areas",
            "Current Health Transits",
            "Preventive Measures",
            "Ayurvedic Recommendations",
            "Favorable Periods for Wellness",
        ],
    },
    "relationship_report": {
        "title": "Relationship Insights Report",
        "system_prompt": (
            "You are a Vedic Astrology expert generating a relationship analysis. "
            "Focus on the 7th house (partnerships), 5th house (romance), Venus "
            "placement and strength, and the Navamsa (D9) chart for marriage. "
            "Analyze dasha periods for relationship timing and compatibility factors."
        ),
        "sections": [
            "Relationship Overview",
            "Love & Romance",
            "Marriage Indicators",
            "Partnership Dynamics",
            "Current Period for Relationships",
            "Compatibility Factors",
            "Remedies for Relationship Growth",
        ],
    },
}


class ReportGenerator:
    """Generates AI-powered astrological reports using Claude."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate(self, report_type: str, birth_context: dict[str, Any]) -> dict[str, Any]:
        """Generate a report using Claude API.

        Args:
            report_type: Type of report (annual_report, career_report, etc.)
            birth_context: Dict with natal_planets, current_dasha, active_transits, etc.

        Returns:
            Report content dict with title, sections, summary, generated_at.
        """
        try:
            import anthropic
        except ImportError:
            logger.warning("anthropic package not installed, returning stub report")
            return self._stub_report(report_type)

        if not self.api_key:
            logger.warning("No Anthropic API key, returning stub report")
            return self._stub_report(report_type)

        config = REPORT_CONFIGS.get(report_type)
        if not config:
            logger.error(f"Unknown report type: {report_type}")
            return self._stub_report(report_type)

        # Build the user message with birth chart context
        user_message = self._build_user_message(report_type, config, birth_context)

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=config["system_prompt"],
                messages=[{"role": "user", "content": user_message}],
            )

            # Parse the response into sections
            content_text = response.content[0].text
            sections = self._parse_sections(content_text, config["sections"])

            return {
                "title": config["title"],
                "sections": sections,
                "summary": self._extract_summary(content_text),
                "generated_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return self._stub_report(report_type)

    def _build_user_message(self, report_type: str, config: dict, birth_context: dict) -> str:
        """Build the user message with birth chart data."""
        parts = [
            f"Generate a {config['title']} for the following person:",
            "",
        ]

        if natal := birth_context.get("natal_planets"):
            parts.append("## Birth Chart Planets")
            for planet, data in natal.items():
                if isinstance(data, dict):
                    sign = data.get("sign", "unknown")
                    house = data.get("house", "?")
                    retro = " (R)" if data.get("is_retrograde") else ""
                    parts.append(f"- {planet.title()}: {sign} in House {house}{retro}")
            parts.append("")

        if dasha := birth_context.get("current_dasha"):
            parts.append("## Current Dasha Period")
            parts.append(f"- Mahadasha: {dasha.get('mahadasha', 'unknown')}")
            parts.append(f"- Antardasha: {dasha.get('antardasha', 'unknown')}")
            if pd := dasha.get("pratyantardasha"):
                parts.append(f"- Pratyantardasha: {pd}")
            parts.append("")

        if transits := birth_context.get("active_transits"):
            parts.append("## Active Transits")
            for t in transits[:10]:
                if isinstance(t, dict):
                    parts.append(f"- {t.get('planet', '?')} in {t.get('sign', '?')}")
            parts.append("")

        section_list = ", ".join(config["sections"])
        parts.append(
            f"Please structure the report with these sections: {section_list}. "
            f"Use ## headings for each section. Include 2-3 key highlights per section. "
            f"Be specific about timing and use Vedic astrology terminology."
        )

        return "\n".join(parts)

    def _parse_sections(self, text: str, expected_sections: list[str]) -> list[dict[str, Any]]:
        """Parse Claude's response into structured sections."""
        sections: list[dict[str, Any]] = []
        current_heading = ""
        current_content: list[str] = []
        current_highlights: list[str] = []

        for line in text.split("\n"):
            if line.startswith("## "):
                # Save previous section
                if current_heading:
                    sections.append(
                        {
                            "heading": current_heading,
                            "content": "\n".join(current_content).strip(),
                            "highlights": current_highlights,
                        }
                    )
                current_heading = line[3:].strip()
                current_content = []
                current_highlights = []
            elif line.strip().startswith("- **") or line.strip().startswith("* **"):
                current_highlights.append(line.strip().lstrip("-* ").strip())
                current_content.append(line)
            else:
                current_content.append(line)

        # Save last section
        if current_heading:
            sections.append(
                {
                    "heading": current_heading,
                    "content": "\n".join(current_content).strip(),
                    "highlights": current_highlights,
                }
            )

        return (
            sections
            if sections
            else [
                {
                    "heading": "Report",
                    "content": text,
                    "highlights": [],
                }
            ]
        )

    def _extract_summary(self, text: str) -> str:
        """Extract first paragraph as summary."""
        paragraphs = text.split("\n\n")
        for p in paragraphs:
            clean = p.strip()
            if clean and not clean.startswith("#"):
                return clean[:500]
        return "Report generated successfully."

    def _stub_report(self, report_type: str) -> dict[str, Any]:
        """Return a stub report when AI generation is unavailable."""
        config = REPORT_CONFIGS.get(report_type, {"title": "Report", "sections": []})
        return {
            "title": config["title"],
            "sections": [
                {
                    "heading": section,
                    "content": (
                        f"This section will contain detailed {section.lower()} analysis "
                        f"based on your birth chart. AI generation requires an Anthropic API key."
                    ),
                    "highlights": [
                        "Full analysis available with API key configured",
                        "Based on your unique birth chart data",
                    ],
                }
                for section in config.get("sections", ["Overview"])
            ],
            "summary": (
                "Report stub generated. Configure ANTHROPIC_API_KEY " "for full AI-powered reports."
            ),
            "generated_at": datetime.now(UTC).isoformat(),
        }

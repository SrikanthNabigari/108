"""Report engine source modules.

Public surface:
    collect_chart_data(birth_data) -> dict
        Pulls every chart slice the report needs into one nested dict.
    REPORT_SECTIONS
        Ordered list of section ids the assembler walks.
"""

from packages.report.src.data_collector import collect_chart_data
from packages.report.src.templates import REPORT_SECTIONS

__all__ = ["REPORT_SECTIONS", "collect_chart_data"]

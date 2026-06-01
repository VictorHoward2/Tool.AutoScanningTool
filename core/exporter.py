"""Facade re-export: import từ đây thay vì `core.export` trực tiếp.

Các hàm thật nằm trong package `core.export`:
- Excel: `core.export.excel`
- HTML refer (Google/YouTube, một section): `core.export.refer_list_html`
- HTML báo cáo RSS đầy đủ: `core.export.full_report`
"""

from core.export import (
    export_full_security_report_html,
    export_full_security_report_html_from_json,
    export_rss_report_to_json,
    export_to_excel,
    export_to_html_bilingual,
    export_to_html_en,
    export_to_html_template,
    export_to_html_vi,
)

__all__ = [
    "export_to_excel",
    "export_to_html_template",
    "export_to_html_vi",
    "export_to_html_en",
    "export_to_html_bilingual",
    "export_full_security_report_html",
    "export_rss_report_to_json",
    "export_full_security_report_html_from_json",
]

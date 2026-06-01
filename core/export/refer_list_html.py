"""HTML danh sách bài theo template refer (một section Global Information).

Dùng cho Google / YouTube: load `global_information.html`, chèn card bài viết + (với RSS)
tóm tắt overview bằng AI. **Không** dùng cho báo cáo RSS nhiều section — xem
`full_report.export_full_security_report_html`.
"""

import html

from config.settings import GAUSS_FOR_RSS, IS_TEST_AI_PROCESS, RSS, TOPIC_KEYWORD
from core.ai_processor import AIProcessor
from core.export.refer_ui import (
    build_output_path,
    load_refer_template,
    replace_section_after_marker,
    safe_replace,
)
from core.logger import logger
from utils.time_utils import format_published

SECTION_KEY = "GLOBAL_INFORMATION"
SECTION_TITLE_VI = "Thong Tin Toan Cau"


def _category_chips_html(item: dict) -> str:
    raw = item.get("tags") or []
    chips: list[str] = []
    if isinstance(raw, list):
        for t in raw[:2]:
            s = str(t).strip() if t is not None else ""
            if s:
                chips.append(
                    '<span class="bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full '
                    'text-xs font-bold uppercase tracking-wider">'
                    f"{html.escape(s)}</span>"
                )
    if chips:
        return "".join(chips)
    return (
        '<span class="bg-surface-container-highest text-on-surface-variant px-3 py-1 rounded-full '
        'text-xs font-bold uppercase tracking-wider">Security</span>'
    )


def _render_articles(data, lang: str, overview: str = "") -> str:
    cards = ""
    if overview:
        cards += f"""
<article class="bg-surface-container-low rounded-lg p-6 group transition-all hover:bg-surface-container">
<div class="flex flex-col gap-4">
<h2 class="text-2xl font-bold text-primary group-hover:text-primary-container transition-colors">{"Tong quan" if lang == "vi" else "Overview"}</h2>
<p class="text-on-surface-variant leading-relaxed body-lg">{html.escape(overview)}</p>
</div>
</article>
"""

    for item in data:
        title = html.escape(item.get("title", "No Title"))
        link = item.get("link", "")
        title_html = f'<a href="{html.escape(link)}">{title}</a>' if link else title
        published = html.escape(format_published(item.get("published", "")))
        snippet = html.escape(item.get("snippet", ""))
        summary = html.escape(item.get("summary_vi", "") if lang == "vi" else item.get("summary_en", ""))
        category_tags = _category_chips_html(item)

        cards += f"""
<article class="bg-surface-container-low rounded-lg p-6 group transition-all hover:bg-surface-container">
<div class="flex flex-col gap-4">
<div class="flex justify-between items-start">
<h2 class="text-2xl font-bold text-primary group-hover:text-primary-container transition-colors">{title_html}</h2>
<div class="flex gap-2">{category_tags}</div>
</div>
<div class="flex items-center gap-4 text-on-surface-variant text-sm font-semibold">
<span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">calendar_today</span>{published}</span>
</div>
<p class="text-on-surface-variant leading-relaxed body-lg">{snippet}</p>
<div class="mt-4 p-5 bg-secondary-fixed/20 border-l-4 border-secondary rounded-r-lg">
<div class="flex items-center gap-2 mb-2 text-secondary font-bold text-xs uppercase tracking-widest">
<span class="material-symbols-outlined text-lg" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
{"AI Curator Summary" if lang == "en" else "Tom tat AI"}
</div>
<p class="text-on-secondary-fixed-variant text-sm font-medium italic">{summary}</p>
</div>
</div>
</article>
"""

    return f'<section class="space-y-8">{cards}</section>'


def _overview(data, lang: str):
    if not data:
        return ""
    if IS_TEST_AI_PROCESS:
        return (
            AIProcessor().summarize_overview_sample_vi(data)
            if lang == "vi"
            else AIProcessor().summarize_overview_sample_en(data)
        )
    if GAUSS_FOR_RSS:
        return (
            AIProcessor().summarize_overview_gauss_vi(data)
            if lang == "vi"
            else AIProcessor().summarize_overview_gauss_en(data)
        )
    return (
        AIProcessor().summarize_overview_gemini_vi(data)
        if lang == "vi"
        else AIProcessor().summarize_overview_gemini_en(data)
    )


def export_to_html_template(data, service, lang="vi"):
    """Lõi render: template + marker `<!-- Articles List -->` → file HTML theo `build_output_path`.

    `lang`: "vi" | "en". Với `service == RSS`, thêm khối overview do AI sinh.
    """
    template = load_refer_template("global_information/global_information.html")
    overview = _overview(data, lang) if service == RSS else ""
    rendered = _render_articles(data, lang=lang, overview=overview)
    template = replace_section_after_marker(template, "<!-- Articles List -->", rendered)
    if lang == "vi":
        template = safe_replace(template, "Global Information", SECTION_TITLE_VI)
        template = safe_replace(
            template,
            "Daily curated security intelligence from the bedrock of the digital landscape.",
            f"Tin an ninh mang duoc tong hop theo chu de {TOPIC_KEYWORD}.",
        )
    filepath = build_output_path(service, SECTION_KEY, "VI" if lang == "vi" else "EN")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(template)
    logger.info(f"[EXPORT] Xuất dữ liệu {SECTION_KEY} bản {'VI' if lang == 'vi' else 'EN'} thành công ra {filepath}")
    return filepath


def export_to_html_vi(data, service, output_path="output"):
    """Wrapper tiếng Việt. `output_path` giữ để tương thích API, chưa truyền xuống template."""
    return export_to_html_template(data, service, lang="vi")


def export_to_html_en(data, service, output_path="output"):
    """Wrapper tiếng Anh. `output_path` giữ để tương thích API, chưa truyền xuống template."""
    return export_to_html_template(data, service, lang="en")


def export_to_html_bilingual(data, service, default_lang="vi", output_path="output"):
    """Gọi template với một `lang` chính (`default_lang`); chưa phải trang song ngữ song song."""
    return export_to_html_template(data, service, lang=default_lang)

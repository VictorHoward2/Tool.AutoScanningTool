import html

from core.export.sections.refer_ui import (
    build_output_path,
    load_refer_template,
    replace_section_after_marker,
    safe_replace,
)
from core.logger import logger
from utils.time_utils import format_published

SECTION_KEY = "NEW_FEATURES"
SECTION_TITLE_VI = "Tính Năng Mới"
SECTION_TITLE_EN = "New Features"


def _render_articles(data, lang: str) -> str:
    cards = ""
    for item in data:
        title = html.escape(item.get("title", "No Title"))
        link = item.get("link", "")
        title_html = f'<a href="{html.escape(link)}">{title}</a>' if link else title
        published = html.escape(format_published(item.get("published", "")))
        snippet = html.escape(item.get("snippet", ""))
        summary = html.escape(item.get("summary_vi", "") if lang == "vi" else item.get("summary_en", ""))
        label = "Curator AI Summary" if lang == "en" else "Tóm tắt AI"

        cards += f"""
<article class="flex flex-col md:flex-row gap-8 bg-surface-container-low p-6 rounded-lg transition-all hover:bg-surface-container">
<div class="w-full md:w-1/3 aspect-video overflow-hidden rounded-lg">
<div class="w-full h-full bg-surface-container-high"></div>
</div>
<div class="flex-1 flex flex-col justify-center">
<div class="flex items-center gap-3 mb-3">
<span class="text-[10px] font-black text-secondary tracking-widest uppercase">Feature</span>
<span class="text-[10px] font-medium text-on-surface-variant/60 uppercase">{published}</span>
</div>
<h4 class="text-2xl font-extrabold text-on-surface mb-3 tracking-tight">{title_html}</h4>
<p class="text-on-surface-variant text-base mb-6 leading-relaxed">{snippet}</p>
<div class="bg-secondary-fixed/20 p-4 rounded-lg border-l-4 border-secondary">
<div class="flex items-center gap-2 mb-1">
<span class="material-symbols-outlined text-secondary text-sm" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
<span class="text-[10px] font-black text-secondary uppercase tracking-tight">{label}</span>
</div>
<p class="text-xs text-on-secondary-fixed-variant leading-normal">{summary}</p>
</div>
</div>
</article>
"""
    return f"<section class=\"space-y-12\">{cards}</section>"


def _export(data, service, lang: str):
    template = load_refer_template("new_features/new_features.html")
    rendered = _render_articles(data, lang=lang)
    template = replace_section_after_marker(template, "<!-- News List Section (Editorial Strips) -->", rendered)
    if lang == "vi":
        template = safe_replace(template, "New Features", SECTION_TITLE_VI)
    filepath = build_output_path(service, SECTION_KEY, "VI" if lang == "vi" else "EN")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(template)
    logger.info(f"[EXPORT] Xuất dữ liệu {SECTION_KEY} bản {'VI' if lang == 'vi' else 'EN'} thành công ra {filepath}")
    return filepath


def export_new_features_html_vi(data, service, output_path="output"):
    return _export(data, service, lang="vi")


def export_new_features_html_en(data, service, output_path="output"):
    return _export(data, service, lang="en")


def export_new_features_html_bilingual(data, service, default_lang="vi", output_path="output"):
    return _export(data, service, lang=default_lang)

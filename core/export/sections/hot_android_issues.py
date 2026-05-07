import html

from core.export.sections.refer_ui import (
    build_output_path,
    load_refer_template,
    replace_section_after_marker,
    safe_replace,
)
from core.logger import logger
from utils.time_utils import format_published

SECTION_KEY = "HOT_ANDROID_ISSUES"
SECTION_TITLE_VI = "Vấn Đề Android Nổi Bật"
SECTION_TITLE_EN = "Hot Android Issues"


def _render_articles(data, lang: str) -> str:
    cards = ""
    for item in data:
        title = html.escape(item.get("title", "No Title"))
        link = item.get("link", "")
        title_html = f'<a href="{html.escape(link)}">{title}</a>' if link else title
        published = html.escape(format_published(item.get("published", "")))
        snippet = html.escape(item.get("snippet", ""))
        summary = html.escape(item.get("summary_vi", "") if lang == "vi" else item.get("summary_en", ""))
        summary_label = "AI Intelligence Summary" if lang == "en" else "Tóm tắt AI"

        cards += f"""
<article class="group bg-surface-container-low rounded-lg p-6 lg:p-8 flex flex-col lg:flex-row gap-8 transition-transform hover:scale-[1.01] duration-300">
<div class="lg:w-1/3 shrink-0">
<div class="w-full h-48 bg-surface-container-high rounded-lg"></div>
</div>
<div class="flex-1 flex flex-col">
<div class="flex items-center gap-3 mb-3">
<span class="bg-error-container text-on-error-container text-[10px] px-2 py-1 font-black uppercase tracking-tighter rounded-sm">Issue</span>
<span class="text-on-surface-variant text-xs font-medium uppercase tracking-widest">{published}</span>
</div>
<h2 class="font-headline font-bold text-2xl text-on-surface mb-4 group-hover:text-primary transition-colors">{title_html}</h2>
<p class="text-on-surface-variant leading-relaxed mb-6">{snippet}</p>
<div class="bg-secondary-fixed/20 p-4 rounded-lg border-l-4 border-secondary flex items-start gap-4">
<span class="material-symbols-outlined text-secondary text-xl">auto_awesome</span>
<div>
<p class="text-xs font-bold text-secondary uppercase tracking-widest mb-1">{summary_label}</p>
<p class="text-sm text-on-surface leading-tight font-medium">{summary}</p>
</div>
</div>
</div>
</article>
"""
    return f"<section class=\"space-y-6\">{cards}</section>"


def _export(data, service, lang: str, title_vi: str, title_en: str):
    template = load_refer_template("hot_issues/hot_issues.html")
    rendered = _render_articles(data, lang=lang)
    template = replace_section_after_marker(template, "<!-- News Editorial Strips -->", rendered)
    template = safe_replace(template, "Hot Android Issues", title_vi if lang == "vi" else title_en)
    filepath = build_output_path(service, SECTION_KEY, "VI" if lang == "vi" else "EN")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(template)
    logger.info(f"[EXPORT] Xuất dữ liệu {SECTION_KEY} bản {'VI' if lang == 'vi' else 'EN'} thành công ra {filepath}")
    return filepath


def export_hot_android_issues_html_vi(data, service, output_path="output"):
    return _export(data, service, lang="vi", title_vi=SECTION_TITLE_VI, title_en=SECTION_TITLE_EN)


def export_hot_android_issues_html_en(data, service, output_path="output"):
    return _export(data, service, lang="en", title_vi=SECTION_TITLE_VI, title_en=SECTION_TITLE_EN)


def export_hot_android_issues_html_bilingual(data, service, default_lang="vi", output_path="output"):
    return _export(data, service, lang=default_lang, title_vi=SECTION_TITLE_VI, title_en=SECTION_TITLE_EN)

import os
from typing import Dict, List

from config.settings import DURATION, NOW, OUTPUT_PATH, TODAY
from core.export.html_assets import CSS_TEMPLATE, LANG_SWITCHER_JS
from core.logger import logger
from utils.time_utils import format_published


def _build_title(item: Dict[str, str]) -> str:
    title = item.get("title", "No Title")
    link = item.get("link", "")
    return f'<a href="{link}">{title}</a>' if link else title


def _render_simple_articles(data: List[Dict[str, str]], lang: str) -> str:
    articles_html = ""
    for idx, item in enumerate(data, start=1):
        title_html = _build_title(item)
        published = format_published(item.get("published", ""))
        snippet = item.get("snippet", "")
        summary_vi = item.get("summary_vi", "")
        summary_en = item.get("summary_en", "")
        summary = summary_vi if lang == "vi" else summary_en
        summary_label = "Tóm tắt" if lang == "vi" else "Summary"

        article_html = f"""
        <article>
            <h2>{idx}. {title_html}</h2>
            <div class="meta">{published}</div>
            <p class="snippet">{snippet}</p>
            {f'<p class="translation-label">{summary_label}:</p><p class="translation">{summary}</p>' if summary else ""}
        </article>
        """
        articles_html += article_html
    return articles_html


def _render_simple_articles_bilingual(data: List[Dict[str, str]]) -> str:
    articles_html = ""
    for idx, item in enumerate(data, start=1):
        title_html = _build_title(item)
        published = format_published(item.get("published", ""))
        snippet = item.get("snippet", "")
        summary_vi = item.get("summary_vi", "")
        summary_en = item.get("summary_en", "")

        article_html = f"""
        <article>
            <div class="lang-vi">
                <h2>{idx}. {title_html}</h2>
                <div class="meta">{published}</div>
                <p class="snippet">{snippet}</p>
                {f'<p class="translation-label">Tóm tắt:</p><p class="translation">{summary_vi}</p>' if summary_vi else ""}
            </div>
            <div class="lang-en" style="display:none">
                <h2>{idx}. {title_html}</h2>
                <div class="meta">{published}</div>
                <p class="snippet">{snippet}</p>
                {f'<p class="translation-label">Summary:</p><p class="translation">{summary_en}</p>' if summary_en else ""}
            </div>
        </article>
        """
        articles_html += article_html
    return articles_html


def export_section_html(
    data: List[Dict[str, str]],
    service: str,
    section_key: str,
    section_title_vi: str,
    section_title_en: str,
    lang: str = "vi",
):
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    filepath = os.path.join(
        OUTPUT_PATH,
        f"results_{NOW}_{DURATION}days_{service}_{section_key}_{'VI' if lang == 'vi' else 'EN'}.html",
    )

    section_title = section_title_vi if lang == "vi" else section_title_en
    today_label = (
        f"Ngày {TODAY} - {DURATION} ngày gần nhất."
        if lang == "vi"
        else f"Update at {TODAY} - The last {DURATION} days."
    )
    credit = "Thực hiện bởi Scanning Tool" if lang == "vi" else "Performed by Scanning Tool"
    articles_html = _render_simple_articles(data, lang)

    html = f"""<!DOCTYPE html>
        <html lang="{'vi' if lang == 'vi' else 'en'}">
        <head>
            <meta charset="UTF-8">
            <title>{section_title}</title>
            <style>{CSS_TEMPLATE}</style>
        </head>
        <body>
            <header>
                <h1>{section_title}</h1>
                <p>{today_label}</p>
                <p>{credit}</p>
            </header>
            <main>
                {articles_html}
            </main>
        </body>
        </html>
    """

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(html)
    logger.info(f"[EXPORT] Xuất dữ liệu {section_key} bản {'VI' if lang == 'vi' else 'EN'} thành công ra {filepath}")
    return filepath


def export_section_html_bilingual(
    data: List[Dict[str, str]],
    service: str,
    section_key: str,
    section_title_vi: str,
    section_title_en: str,
    default_lang: str = "vi",
):
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    filepath = os.path.join(
        OUTPUT_PATH,
        f"results_{NOW}_{DURATION}days_{service}_{section_key}_BILINGUAL.html",
    )

    today_label_vi = f'<p class="lang-vi">Ngày {TODAY} - {DURATION} ngày gần nhất.</p>'
    today_label_en = f'<p class="lang-en" style="display:none">Update at {TODAY} - The last {DURATION} days.</p>'
    credit_vi = '<p class="lang-vi">Thực hiện bởi Scanning Tool</p>'
    credit_en = '<p class="lang-en" style="display:none">Performed by Scanning Tool</p>'
    header_vi = f'<h1 class="lang-vi">{section_title_vi}</h1>'
    header_en = f'<h1 class="lang-en" style="display:none">{section_title_en}</h1>'
    articles_html = _render_simple_articles_bilingual(data)
    switcher_html = """
    <div class="lang-switcher" style="text-align:center;margin-bottom:12px;">
        <button id="lang-vi-btn" class="filter-btn active" onclick="switchLanguage('vi')">VI</button>
        <button id="lang-en-btn" class="filter-btn" onclick="switchLanguage('en')">EN</button>
    </div>
    """

    html = f"""<!DOCTYPE html>
        <html lang="{'vi' if default_lang == 'vi' else 'en'}">
        <head>
            <meta charset="UTF-8">
            <title>{section_title_en}</title>
            <style>{CSS_TEMPLATE}</style>
        </head>
        <body>
            <header>
                {header_vi}
                {header_en}
                {today_label_vi}
                {today_label_en}
                {credit_vi}
                {credit_en}
            </header>
            <div>{switcher_html}</div>
            <main>
                {articles_html}
            </main>
            <script>{LANG_SWITCHER_JS}</script>
            <script>switchLanguage('{default_lang}')</script>
        </body>
        </html>
    """

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(html)
    logger.info(f"[EXPORT] Xuất dữ liệu {section_key} bản BILINGUAL thành công ra {filepath}")
    return filepath

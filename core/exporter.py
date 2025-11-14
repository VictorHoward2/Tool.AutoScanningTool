import os
import re
import json
import pandas as pd
from config.settings import *
from core.logger import logger
from core.ai_processor import AIProcessor
from utils.time_utils import *
from collections import defaultdict
from typing import List, Tuple, Dict, Any

# export_to_excel(results)


def export_to_excel(data, sheetname):
    for item in data:
        if "content" in item:
            del item["content"]
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    file_path = os.path.join(OUTPUT_PATH, f"results_{NOW}_{DURATION}days.xlsx")
    sheet_name = f"{sheetname}_{NOW}"

    data = [{k.upper(): v for k, v in item.items()} for item in data]

    df = pd.DataFrame(data)

    # Check file exist, delete old sheet before add new sheet
    if os.path.exists(file_path):
        with pd.ExcelWriter(
            file_path, engine="openpyxl", mode="a", if_sheet_exists="new"
        ) as writer:
            if sheet_name in writer.book.sheetnames:
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    logger.info(f"[EXPORT] Xuất dữ liệu {sheetname} thành công ra {file_path}")


def _extract_keywords(obj: Any) -> List[str]:
    """
    Trả về list các từ khóa từ một giá trị trong JSON.
    Hỗ trợ hai dạng:
      - ["kw1", "kw2", ...]
      - {"keywords": ["kw1","kw2", ...], ...}
    """
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        # ưu tiên trường 'keywords', fallback: tìm list đầu tiên trong dict
        if "keywords" in obj and isinstance(obj["keywords"], list):
            return obj["keywords"]
        # fallback: lấy mọi giá trị list trong dict
        for v in obj.values():
            if isinstance(v, list):
                return v
    return []


def classify_security_article(content: str,
                              json_path: str = ".\\config\\security_categories.json",
                              top_n: int = 5,
                              threshold: int = 1,
                              debug: bool = False) -> List[Tuple[str, int]]:
    """
    Phân loại bài báo bảo mật dựa trên danh sách từ khóa (hỗ trợ cả 2 định dạng JSON).

    Args:
        content: nội dung bài viết cần phân loại
        json_path: đường dẫn tới file JSON chứa categories
        top_n: trả về tối đa top_n category
        threshold: ngưỡng điểm tối thiểu để một category được tính là relevant
        debug: nếu True sẽ in debug info

    Trả về:
        List[(category_name, score)] sắp theo điểm giảm dần
    """
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        categories_raw: Dict[str, Any] = json.load(f)

    if debug:
        print(f"\n\n[DEBUG] Content: {content}.")

    # Chuẩn hóa text
    text = content.lower()

    # Chuẩn bị dict: category -> list keywords (chuẩn hóa lowercase)
    categories: Dict[str, List[str]] = {}
    for cat_name, value in categories_raw.items():
        kws = _extract_keywords(value)
        # bỏ None, strip, lowercase, và loại bỏ rỗng
        kws_clean = [kw.strip().lower() for kw in kws if isinstance(kw, str) and kw.strip()]
        categories[cat_name] = kws_clean
        if debug:
            print(f"[DEBUG] Category '{cat_name}' has {len(kws_clean)} keywords")

    scores = defaultdict(int)

    # Đếm số lần xuất hiện từ khóa - dùng regex với negative/positive lookaround để match whole word/phrase
    for cat_name, kws in categories.items():
        if not kws:
            continue
        if debug:
            print(f"[DEBUG] Processing category: {cat_name}")
        for kw in kws:
            # escape keyword to be regex-safe; use word-boundary-like lookarounds
            # (?<!\w) ensures left is not alnum/underscore; (?!\w) ensures right is not alnum/underscore
            pattern = r"(?<!\w)" + re.escape(kw.lower()) + r"(?!\w)"
            matches = re.findall(pattern, text)
            if matches:
                scores[cat_name] += len(matches)
                if debug:
                    print(f"[DEBUG] Found {len(matches)} x '{kw}' in '{cat_name}' (pattern: {pattern})")

    # Sắp xếp theo điểm giảm dần
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Lọc theo threshold
    result = [(cat, sc) for cat, sc in ranked if sc >= threshold]

    return result[:top_n]

CSS_TEMPLATE = """
    body {
        font-family: "Inter", "Segoe UI", sans-serif;
        background: #f5f6fa;
        margin: 0;
        padding: 20px;
        color: #333;
        background-image: url("https://raw.githubusercontent.com/VictorHoward2/Tool.AutoScanningTool/refs/heads/main/ui/assets/News.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    header {
        max-width: 800px;
        margin: auto;
        padding: 20px 0;
        text-align: center;
    }
    header h1 { margin: 0; font-size: 2rem; }
    header p { color: #666; }
    main {
        max-width: 800px;
        margin: auto;
        display: grid;
        gap: 20px;
    }
    article {
        background: #fff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    article:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    article h2 {
        margin-top: 0;
        font-size: 1.25rem;
    }
    article h2 a {
        color: #1a73e8;
        text-decoration: none;
    }
    article h2 a:hover {
        text-decoration: underline;
    }
    .meta {
        font-size: 0.875rem;
        color: #999;
        margin-bottom: 10px;
    }
    .snippet {
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .translation-label {
        font-size: 0.9rem;
        font-style: italic;
        color: #555;
        margin-top: 12px;
        margin-bottom: 4px;
    }
    .translation {
        background: #f9f9f9;
        padding: 12px;
        border-left: 4px solid #1a73e8;
        border-radius: 6px;
        line-height: 1.6;
        font-style: italic;
        color: #444;
        white-space: pre-wrap;
    }
    .category-tags {
        margin-bottom: 12px;
    }
    .tag {
        display: inline-block;
        background: #e8f0fe;
        color: #1967d2;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .filter-bar {
        text-align: center;
        max-width: 800px;
        margin: auto;
        padding: 25px;
    }
    .filter-btn {
        background: #e0e0e0;
        border: none;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .filter-btn.active, .filter-btn:hover {
        background: #1a73e8;
        color: #fff;
    }
    .lang-switcher {
        text-align: center;
        margin-bottom: 12px;
    }

    .lang-switcher .filter-btn {
        padding: 10px 10px;
        font-size: 12px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        border-radius: 8px;
        margin: 0 5px;
        background: #f0f0f0;
        color: #333;
        transition: all 0.25s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }

    .lang-switcher .filter-btn:hover {
        background: #e5e5e5;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }

    .lang-switcher .filter-btn.active {
        background: #0078ff;
        color: white;
        box-shadow: 0 3px 6px rgba(0,120,255,0.3);
    }

    .lang-switcher .filter-btn.active:hover {
        background: #0069e0;
    }

"""

JS_TEMPLATE = """
    function filterArticles(category) {
        const articles = document.querySelectorAll('article');
        const buttons = document.querySelectorAll('.filter-btn');

        // Reset trạng thái nút
        buttons.forEach(btn => btn.classList.remove('active'));
        document.getElementById(category).classList.add('active');

        // Lọc bài viết
        articles.forEach(article => {
            const categories = article.dataset.categories || ''; // tránh lỗi undefined
            if (category === 'all' || categories.includes(category)) {
                article.style.display = 'block';
            } else {
                article.style.display = 'none';
            }
        });
    }
"""


def _build_filter_buttons(all_categories: set):
    filter_buttons = '<button id="all" class="filter-btn active" onclick="filterArticles(\'all\')">All</button>'
    for c in sorted(all_categories):
        filter_buttons += f'<button id="{c}" class="filter-btn" onclick="filterArticles(\'{c}\')">{c}</button>'
    return filter_buttons

def _render_articles_html(data, lang="vi"):
    # Returns (articles_html, all_categories_set)
    all_categories = set()
    articles_html = ""

    for idx, item in enumerate(data, start=1):
        title = item.get("title", "No Title")
        link = item.get("link", "")
        published = format_published(item.get("published", ""))
        snippet = item.get("snippet", "")
        vietsub = item.get("vietsub", "") if "vietsub" in item else ""
        summary_vi = item.get("summary_vi", "") if "summary_vi" in item else ""
        summary_en = item.get("summary_en", "") if "summary_en" in item else ""
        related = item.get("related", "") if "related" in item else ""
        extract_info = item.get("extract", "") if "extract" in item else ""
        categories_raw = classify_security_article(f"{title} {snippet}")
        categories = [c[0] if isinstance(c, tuple) else c for c in categories_raw]
        for c in categories:
            all_categories.add(c)

        tags_html = "".join(f'<span class="tag">{c}</span>' for c in categories)
        title_html = f'<a href="{link}">{title}</a>' if link else title

        # labels: support both lang
        if lang == "vi":
            viet_label = "Dịch tiếng Việt:"
            sum_label = "Tóm tắt:"
            rel_label = f"Có liên quan đến chủ đề {TOPIC_KEYWORD}:"
            ext_label = "Các thông tin hữu ích:"
            summary = summary_vi
        else:
            viet_label = ""
            sum_label = "Summary:"
            rel_label = f"Related to topic {TOPIC_KEYWORD}:"
            ext_label = "Useful info:"
            summary = summary_en
        vietnamese_line = f'<p class="translation-label">{viet_label}</p><p class="translation">{vietsub}</p>' if vietsub and lang =="vi" else ""
        summary_line = f'<p class="translation-label">{sum_label}</p><p class="translation">{summary}</p>'
        # related/extract
        related_line = f'<p class="translation-label">{rel_label}</p><p class="translation">{related}</p>' if related else ""
        extract_line = f'<p class="translation-label">{ext_label}</p><p class="translation">{extract_info}</p>' if extract_info else ""

        article_html = f"""
        <article data-categories="{' '.join(categories)}">
        <div class="category-tags">{tags_html}</div>
        <h2>{idx}. {title_html}</h2>
        <div class="meta">{published}</div>
        <p class="snippet">{snippet}</p>
        {vietnamese_line}
        {summary_line}
        {related_line}
        {extract_line}
        </article>
        """
        articles_html += article_html
    return articles_html, all_categories

def export_to_html_template(data, service, lang="vi"):
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)


    filepath = os.path.join(OUTPUT_PATH, f"results_{NOW}_{DURATION}days_{service}_{'VI' if lang=='vi' else 'EN'}.html")


    if service == RSS:
        category = "Security News" if lang == "en" else "Security News"
        sumary_overview_vi = AIProcessor().summarize_overview_gemini_vi(data)
        sumary_overview_en = AIProcessor().summarize_overview_gemini_en(data)
        sumary_overview_line = f'''
        <article class="translation-label">
            <h2>{"Tổng Quan" if lang == "vi" else "Overview"}:</h2>
            <p class="snippet">{sumary_overview_vi if lang == "vi" else sumary_overview_en}</p>
        </article>'''
    else:
        category = f"Kết Quả Scan {service}" if lang == "vi" else f"{service} Scan Results"

    
    articles_html, all_categories = _render_articles_html(data, lang=lang)
    filter_buttons = _build_filter_buttons(all_categories)
    today_label = f"Ngày {TODAY} - {DURATION} ngày gần nhất." if lang=="vi" else f"Update at {TODAY} - The last {DURATION} days."
    main_header = f"Báo cáo {category}" if lang=="vi" else f"Report {category}"
    credit = "Thực hiện bởi Scanning Tool" if lang=="vi" else "Performed by Scanning Tool"
    html = f"""<!DOCTYPE html>
        <html lang="{'vi' if lang=='vi' else 'en'}">
        <head>
            <meta charset="UTF-8">
            <title>{category}</title>
            <style>{CSS_TEMPLATE}</style>
        </head>
        <body>
            <header>
                <h1>{main_header}</h1>
                <p>{today_label}</p>
                <p>{credit}</p>
            </header>
            <div class="filter-bar">{filter_buttons}</div>
            <main>
                {sumary_overview_line if service == RSS else ""}
                {articles_html}
            </main>
            <script>{JS_TEMPLATE}</script>
        </body>
        </html>
        """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"[EXPORT] Xuất dữ liệu {service} bản {'VI' if lang == 'vi' else 'EN'} thành công ra {filepath}")

def export_to_html_vi(data, service, output_path="output"):
    return export_to_html_template(data, service, lang="vi")

def export_to_html_en(data, service, output_path="output"):
    return export_to_html_template(data, service, lang="en")

def _render_bilingual_articles_html(data):
    """
    Trả về (articles_html, all_categories_set)
    Mỗi <article> chứa hai phần nội dung: .lang-vi và .lang-en
    data-categories được tạo dựa trên classify_security_article(title + snippet)
    """
    all_categories = set()
    articles_html = ""
    for idx, item in enumerate(data, start=1):
        # common fields
        title = item.get("title", "No Title")
        link = item.get("link", "")
        published = format_published(item.get("published", ""))
        snippet = item.get("snippet", "")
        vietsub = item.get("vietsub", "") if "vietsub" in item else ""
        summary_vi = item.get("summary_vi", "") if "summary_vi" in item else ""
        summary_en = item.get("summary_en", "") if "summary_en" in item else ""
        related = item.get("related", "") if "related" in item else ""
        extract_info = item.get("extract", "") if "extract" in item else ""

        # Determine categories once (using combined text)
        categories_raw = classify_security_article(f"{title} {snippet}")
        categories = [c[0] if isinstance(c, tuple) else c for c in categories_raw]
        for c in categories:
            all_categories.add(c)
        tags_html = "".join(f'<span class="tag">{c}</span>' for c in categories)
        data_categories_attr = " ".join(categories)

        # Build bilingual pieces. For EN/VI labels we keep them inline.
        # Title: if link exists wrap both with same link
        title_html = f'<a href="{link}">{title}</a>' if link else title

        # For now we assume summary/snippet/vietsub already are appropriate language fields
        viet_article = f'''
            <div class="lang-vi">
                <h2>{idx}. {title_html}</h2>
                <div class="meta">{published}</div>
                <p class="snippet">{snippet}</p>
                {f'<p class="translation-label">Dịch tiếng Việt:</p><p class="translation">{vietsub}</p>' if vietsub else ""}
                <p class="translation-label">Tóm tắt:</p><p class="translation">{summary_vi}</p>
                {f'<p class="translation-label">Có liên quan đến chủ đề {TOPIC_KEYWORD}:</p><p class="translation">{related}</p>' if related else ""}
                {f'<p class="translation-label">Các thông tin hữu ích:</p><p class="translation">{extract_info}</p>' if extract_info else ""}
            </div>
        '''
        en_article = f'''
            <div class="lang-en" style="display:none">
                <h2>{idx}. {title_html}</h2>
                <div class="meta">{published}</div>
                <p class="snippet">{snippet}</p>
                {f'<p class="translation-label">Summary:</p><p class="translation">{summary_en}</p>'}
                {f'<p class="translation-label">Related to topic {TOPIC_KEYWORD}:</p><p class="translation">{related}</p>' if related else ""}
                {f'<p class="translation-label">Useful info:</p><p class="translation">{extract_info}</p>' if extract_info else ""}
            </div>
        '''

        article_html = f"""
        <article data-categories="{data_categories_attr}">
            <div class="category-tags">{tags_html}</div>
            {viet_article}
            {en_article}
        </article>
        """
        articles_html += article_html
    return articles_html, all_categories

# JS to add language switcher (we append to existing JS_TEMPLATE)
LANG_SWITCHER_JS = """
    function switchLanguage(lang) {
        const viElems = document.querySelectorAll('.lang-vi');
        const enElems = document.querySelectorAll('.lang-en');
        const viBtn = document.getElementById('lang-vi-btn');
        const enBtn = document.getElementById('lang-en-btn');

        if (lang === 'vi') {
            viElems.forEach(e => e.style.display = '');
            enElems.forEach(e => e.style.display = 'none');
            viBtn.classList.add('active');
            enBtn.classList.remove('active');
        } else {
            viElems.forEach(e => e.style.display = 'none');
            enElems.forEach(e => e.style.display = '');
            enBtn.classList.add('active');
            viBtn.classList.remove('active');
        }
    }
"""

def _build_language_switcher(default_lang="vi"):
    vi_active = "active" if default_lang == "vi" else ""
    en_active = "active" if default_lang == "en" else ""
    switcher_html = f'''
    <div class="lang-switcher" style="text-align:center;margin-bottom:12px;">
        <button id="lang-vi-btn" class="filter-btn {vi_active}" onclick="switchLanguage('vi')">VI</button>
        <button id="lang-en-btn" class="filter-btn {en_active}" onclick="switchLanguage('en')">EN</button>
    </div>
    '''
    return switcher_html

def export_to_html_bilingual(data, service, default_lang="vi", output_path="output"):
    """
    Tạo 1 file HTML chứa cả nội dung Tiếng Việt và Tiếng Anh và 1 control để đổi ngôn ngữ.
    default_lang: 'vi' hoặc 'en' (vi mặc định)
    """
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    filepath = os.path.join(OUTPUT_PATH, f"results_{NOW}_{DURATION}days_{service}_BILINGUAL.html")

    # Optional overview (similar behavior as export_to_html_template)
    if service == RSS:
        sumary_overview_vi = AIProcessor().summarize_overview_gemini_vi(data)
        sumary_overview_en = AIProcessor().summarize_overview_gemini_en(data)
        sumary_overview_line = f'''
        <article class="translation-label">
            <h2 class="lang-vi">{'Tổng Quan'}:</h2>
            <h2 class="lang-en" style="display:none">{'Overview'}:</h2>
            <p class="snippet lang-vi" >{sumary_overview_vi}</p>
            <p class="snippet lang-en" style="display:none">{sumary_overview_en}</p>
        </article>'''
    else:
        sumary_overview_line = ""

    # Build bilingual articles and categories
    articles_html, all_categories = _render_bilingual_articles_html(data)

    # filter buttons use combined categories
    filter_buttons = _build_filter_buttons(all_categories)
    lang_switcher = _build_language_switcher(default_lang)

    today_label_vi = f'<p class="lang-vi">Ngày {TODAY} - {DURATION} ngày gần nhất.</p>'
    today_label_en = f'<p class="lang-en" style="display:none">Update at {TODAY} - The last {DURATION} days.</p>'
    main_header_vi = f'<h1 class="lang-vi">Báo cáo {service}</h1>'
    main_header_en = f'<h1 class="lang-en" style="display:none">Report {service}</h1>'
    credit_vi = '<p class="lang-vi">Thực hiện bởi Scanning Tool</p>' 
    credit_en = '<p class="lang-en" style="display:none">Performed by Scanning Tool</p>'

    # Compose final HTML: CSS_TEMPLATE already exists; combine JS_TEMPLATE + LANG_SWITCHER_JS
    combined_js = JS_TEMPLATE + "\n" + LANG_SWITCHER_JS

    html = f"""<!DOCTYPE html>
        <html lang="{'vi' if default_lang=='vi' else 'en'}">
        <head>
            <meta charset="UTF-8">
            <title>Report {service}</title>
            <style>{CSS_TEMPLATE}</style>
        </head>
        <body>
            <header>
                {main_header_vi}
                {main_header_en}
                {today_label_vi}
                {today_label_en}
                {credit_vi}
                {credit_en}
            </header>

            <div class="filter-bar">
                {filter_buttons}
                
            </div>
            <div>
                {lang_switcher}
            </div>
            <main>
                {sumary_overview_line}
                {articles_html}
            </main>

            <script>{combined_js}</script>
            <script>switchLanguage('{default_lang}')</script>
        </body>
        </html>
        """

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"[EXPORT] Xuất file bilingual {service} thành công ra {filepath}")
    return filepath

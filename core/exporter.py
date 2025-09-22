import os
import pandas as pd
from config.settings import *
from core.logger import logger
from utils.time_utils import *

# export_to_excel(results)

def export_to_excel(data, sheetname):
    for item in data:
        if 'content' in item:
            del item['content']
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    file_path = os.path.join(OUTPUT_PATH, f"results_{TODAY}.xlsx")
    sheet_name = f'{sheetname}_{TODAY}'
    
    data = [{k.upper(): v for k, v in item.items()} for item in data]
    
    df = pd.DataFrame(data)
    
    # Check file exist, delete old sheet before add new sheet
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            if sheet_name in writer.book.sheetnames:
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    logger.info(f"[EXPORT] Xuất dữ liệu {sheetname} thành công ra {file_path}")

def export_to_html(data, service, output_path="output"):
    # Ngày hôm nay
    filepath = os.path.join(OUTPUT_PATH, f"results_{TODAY}.html")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # CSS hiện đại, kiểu đọc báo
    css = """
    body {
    font-family: "Inter", "Segoe UI", sans-serif;
    background: #f5f6fa;
    margin: 0;
    padding: 20px;
    color: #333;
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
    """

    # Sinh nội dung từng article
    articles_html = ""
    for idx, item in enumerate(data, start=1):
        title = item.get("title", "No Title")
        link = item.get("link", "")
        published = format_published(item.get("published", ""))
        snippet = item.get("snippet", "")
        vietsub = item.get("vietsub", "")

        title_html = f'<a href="{link}">{title}</a>' if link else title
        article_html = f"""
        <article>
        <h2>{idx}. {title_html}</h2>
        <div class="meta">{published}</div>
        <p class="snippet">{snippet}</p>
        <p> Dịch tiếng Việt:</p>
        <p class="snippet">{vietsub}</p>
        </article>
        """
        articles_html += article_html

    # Khung HTML tổng
    html = f"""<!DOCTYPE html>
        <html lang="vi">
        <head>
        <meta charset="UTF-8">
        <title>Báo cáo {service} - {TODAY}</title>
        <style>{css}</style>
        </head>
        <body>
        <header>
            <h1>Báo cáo {service}</h1>
            <p>Ngày {TODAY}</p>
        </header>
        <main>
            {articles_html}
        </main>
        </body>
        </html>
        """

    # Ghi file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"[EXPORT] Xuất dữ liệu {service} thành công ra {filepath}")

import os
import feedparser
import json
from datetime import datetime, timedelta, timezone
import cloudscraper
from config.settings import *
import traceback
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
from core.logger import logger

class RSSSearch:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
                            browser={
                                'browser': 'firefox',
                                'platform': 'windows',
                                'mobile': False
                            }
                        )
        
    def extract_image_from_article(self, url, min_height=500, min_width=400):
        forbidden = ["facebook.com", "instagram.com", "x.com", "telegram.org"]
        try:

            response = self.scraper.get(url)
            response.raise_for_status()
            
            # Phân tích HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm tất cả các thẻ img
            images = soup.find_all('img')
            
            if not images:
                logger.warning(f"[RSS] No images were found in the article ({url}).")
                return "https://image.samsungsds.com/en/news/__icsFiles/afieldfile/2025/02/20/t.jpg"
            
            # Duyệt qua từng hình ảnh để tìm hình ảnh hợp lệ
            for img in images:
                img_src = img.get('src') or img.get('data-src')  # Một số trang web dùng data-src
                if img_src:
                    # Chuyển đổi URL tương đối thành tuyệt đối nếu cần
                    img_url = urljoin(url, img_src)
                    
                    # Kiểm tra xem URL có hợp lệ không
                    if img_url.startswith(('http://', 'https://')) and not img_url.endswith(".svg") and not any(keyword in img_url for keyword in forbidden):
                        try:
                            # Tải hình ảnh
                            img_response = self.scraper.get(img_url)
                            img_response.raise_for_status()
                            
                            image = Image.open(BytesIO(img_response.content))
                            width, height = image.size
                            # print(f"Kiểm tra hình ảnh: {img_url} - Kích thước: {width}x{height}")
                            
                            if width > min_width and height > min_height:
                                return img_url
                            
                        except Exception as e:
                            logger.error(f"[RSS] In article ({url}) - Error loading image {img_url}: {str(e)}")
                            continue
            
            return "https://image.samsungsds.com/en/news/__icsFiles/afieldfile/2025/02/20/t.jpg"
        
        except Exception as e:
            logger.error(f"[RSS] In article ({url}) - Undefined error: {str(e)}")
            traceback.print_exc()
            return None

    def fetch_recent_posts(self, days=DURATION, source = RSS_GLOBAL_INFOR):
        recent_posts = []
        for rss_url in source:
            response = self.scraper.get(rss_url)
            
            os.makedirs("test", exist_ok=True)
            with open("test\\sample.html", "w", encoding="utf-8") as f:
                f.write(response.text)
                
            feed = feedparser.parse(response.text)
            with open("test\\feed.json", "w", encoding="utf-8") as f:
                json.dump(feed, f, ensure_ascii=False, indent=4, default=str)
            duration = datetime.now(timezone.utc) - timedelta(days=days)

            for entry in feed.entries:
                if hasattr(entry, "published_parsed"):
                    pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed"):
                    pub = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                else:
                    continue

                if pub >= duration:
                    recent_posts.append(
                        {
                            "title": entry.get("title"),
                            "link": entry.get("link"),
                            "published": pub.isoformat(),
                            "snippet": entry.get("summary", ""),
                            "image": next((link["href"] for link in entry.get("links", []) if link.get("type").startswith("image/")), self.extract_image_from_article(entry.get("link"))),
                            "readtime": entry.get("readtime", ""),
                            "tags": [tag.get("term", "") for tag in entry.get("tags", [])],
                        }
                    )

        return recent_posts

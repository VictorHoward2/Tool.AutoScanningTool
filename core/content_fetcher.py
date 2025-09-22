import traceback
import cloudscraper
from bs4 import BeautifulSoup
from core.logger import logger
from config.settings import *

class ContentFetcher:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def clean_html(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
        return '\n'.join(lines)
    
    def remove_duplicate_links(self, array):
        seen = set()
        unique_arr = []
        for item in array:
            if item["link"] not in seen:
                seen.add(item["link"])
                unique_arr.append(item)
        return unique_arr
    
    def get_content(self, results):
        
        if not results:
            return results
        
        results = self.remove_duplicate_links(results)
        
        for items in results:
            clean_text = ''
            try:
                response = self.scraper.get(items['link'])
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for tag in soup(["script", "style"]):
                        tag.decompose()
                    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
                    clean_text = '\n'.join(lines)
                else:
                    logger.warning(f"[CONTENT FETCHER] Không thể truy cập trang: {items['link']} - Status code: {response.status_code}")
                    continue  # Bỏ qua nếu không truy cập được
            except Exception as e:
                logger.error(f"[CONTENT FETCHER] Lỗi khi lấy nội dung từ: {items['link']}")
                traceback.print_exc()
                continue  # Bỏ qua nếu có lỗi
            
            items["content"] = clean_text
            # logger.info(f"[CONTENT FETCHER] Lấy nội dung thành công: {items['link']}")
            # logger.info(f"[CONTENT FETCHER] Nội dung: {clean_text[:500]}...")  # In 100 ký tự đầu tiên
        return results
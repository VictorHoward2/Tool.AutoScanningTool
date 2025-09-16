import traceback
from bs4 import BeautifulSoup
from core.logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from config.settings import TIMEOUT

class ContentFetcher:
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

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(TIMEOUT)

        for item in results:
            clean_text = ''
            try:
                driver.get(item['link'])
            except TimeoutException:
                logger.warning(f"[CONTENT FETCHER] Trang load quá lâu: {item['link']}")
                try:
                    page_source = driver.page_source
                    clean_text = self.clean_html(page_source)
                except Exception as e:
                    logger.error(f"[CONTENT FETCHER] Không thể lấy page_source sau timeout: {item['link']}")
                    traceback.print_exc()
                    continue  # Bỏ qua nếu không lấy được gì
            except WebDriverException:
                logger.error(f"[CONTENT FETCHER] WebDriver gặp lỗi khi truy cập: {item['link']}")
                traceback.print_exc()
                continue
            else:
                # Nếu không timeout, xử lý bình thường
                page_source = driver.page_source
                clean_text = self.clean_html(page_source)

            item["content"] = clean_text

        driver.quit()
        return self.remove_duplicate_links(results)
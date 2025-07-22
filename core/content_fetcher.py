import traceback
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

class ContentFetcher:
    def clean_html(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
        return '\n'.join(lines)
    
    def get_content(self, results):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)

        for item in results:
            clean_text = ''
            try:
                driver.get(item["link"])
            except TimeoutException:
                print(f"[TIMEOUT] Trang load quá lâu: {item["link"]}")
                try:
                    page_source = driver.page_source
                    clean_text = self.clean_html(page_source)
                except Exception as e:
                    traceback.print_exc()
                    print(f"[FAIL] Không thể lấy page_source sau timeout: {item["link"]}")
                    continue  # Bỏ qua nếu không lấy được gì
            except WebDriverException:
                traceback.print_exc()
                print(f"[ERROR] WebDriver gặp lỗi khi truy cập: {item["link"]}")
                continue
            else:
                # Nếu không timeout, xử lý bình thường
                page_source = driver.page_source
                clean_text = self.clean_html(page_source)

            item["content"] = clean_text

        driver.quit()
        return results
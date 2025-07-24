import re
import requests
import traceback
from core.logger import logger
from config.settings import AI_MODELS, DEFAULT_MODEL, NUMBER_WORDS_SUMMARIZE

class AIProcessor:
    def strip_thoughts(self, text):
        # Dùng regex để loại bỏ đoạn <think>...</think>
        clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Loại bỏ khoảng trắng đầu/cuối và dòng trống thừa
        clean_text = clean_text.strip()
        return clean_text
    
    def summarize_content(self, title, snippet, link, content, num_words = NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL):
        prompt = (
            f"Bạn là một chuyên gia đọc hiểu, phân tích, tóm tắt nội dung văn bản."
            f"Tôi sẽ gửi cho bạn tiêu đề, đoạn trích nhỏ, link và nội dung (phần text trong trang web) của một trang web."
            f"Bây giờ nhiệm vụ của bạn là: "
            f"Hãy dựa vào những thông tin tôi gửi viết một bản tóm tắt bằng tiếng Việt về nội dung của trang web."
            f"Viết ngắn gọn, dễ hiểu và đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ."
            f"Không tự bổ sung thông tin không được đề cập trong nội dung được giao.\n"
            f"Tiêu đề trang web: {title} \n\n"
            f"Đoạn trích nhỏ của trang web: {snippet}\n\n"
            f"Link của trang web: {link}\n\n"
            f"Nội dung (phần text trong trang web) của trang web: {content}\n\n"
        )   
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Lỗi: {response.status_code} - {response.text}"
        
    def summarize_description(self, title, snippet, link, num_words = NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL):
        prompt = (
            f"Bạn là một chuyên gia đọc hiểu, phân tích, tóm tắt nội dung văn bản."
            f"Tôi sẽ gửi cho bạn các thông tin của một video Youtube bao gồm: tiêu đề, đoạn mô tả của video, link của video."
            f"Đoạn mô tả có thể được viết bằng nhiều loại ngôn ngữ khác nhau."
            f"Bây giờ nhiệm vụ của bạn là: "
            f"Hãy dựa vào những thông tin tôi gửi viết một bản tóm tắt bằng tiếng Việt về nội dung của đoạn mô tả và nội dung chính của video."
            f"Viết ngắn gọn, dễ hiểu và đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ."
            f"Không tự bổ sung thông tin không được đề cập trong nội dung được giao.\n"
            f"Tiêu đề trang web: {title} \n\n"
            f"Đoạn trích nhỏ của trang web: {snippet}\n\n"
            f"Link của trang web: {link}\n\n"
        )   
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Lỗi: {response.status_code} - {response.text}"
        
    def is_related(self, key, title, snippet, link, model=DEFAULT_MODEL):
        prompt = (
            f"Tôi sẽ gửi cho bạn tiêu đề, đoạn trích nhỏ và link của một trang web cùng với một từ khóa. Bây giờ nhiệm vụ của bạn là: "
            f"Trả lời chỉ một số duy nhất: \"1\" nếu từ những thông tin về trang web mà tôi gửi bạn đánh giá có nội dung liên quan nhiều đến từ khóa, không liên quan thì ghi \"0\", nếu bạn phân vân và không quyết định được thì ghi \"2\"."
            f"Không thêm bất kỳ giải thích hay bình luận nào khác. Rõ ràng và ngắn gọn.\n\n"
            f"Hãy cân nhắc thật kỹ bởi vì câu trả lời này của bạn rất quan trọng."
            f"Tiêu đề trang web: {title} \n\n"
            f"Đoạn trích nhỏ của trang web: {snippet}\n\n"
            f"Link của trang web: {link}\n\n"
            f"Từ khóa của lần này: {key}\n\n"
        )

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Lỗi: {response.status_code} - {response.text}"
        
    def extract_info (self, key, text, model=DEFAULT_MODEL):
        prompt = (
            f"Bây giờ bạn là một AI có nhiệm vụ đọc hiểu nội dung của một trang web và trích xuất ra các thông tin cốt lõi liên quan đến từ khóa được cung cấp."
            f"Yêu cầu:"
            f"- Đọc nội dung được trích xuất từ HTML của một trang web tôi sắp gửi dưới đây. "
            f"- Dựa trên từ khóa được cung cấp, trích xuất ra những thông tin có liên quan trực tiếp đến từ khóa đó, nếu như không có thông tin liên quan, ghi ngắn gọn \"Không có thông tin\"."
            f"- Không tự bổ sung thông tin hay nói về những thông tin không được đề cập trong nội dung được giao."
            f"- Nếu có thể, hãy trả lời bằng tiếng Việt và tuân theo các mục sau:\n"
            f"    1. Tên thiết bị hoặc tên dòng máy liên quan đến từ khóa, càng nhiều thông tin chi tiết càng tốt."
            f"    2. Tên công cụ (tool) hoặc tên phần mềm hoặc phương thức được dùng để thực hiện"
            f"    3. Cách thức thực hiện (hướng dẫn ngắn gọn nếu có)"
            f"    4. Điều kiện cần thiết hoặc lưu ý khi thực hiện"
            f"    5. Bất kỳ thông tin bổ sung hữu ích nào liên quan đến từ khóa"
            f"Chỉ trích xuất các thông tin liên quan trực tiếp đến từ khóa. Nếu không có thông tin nào phù hợp thì hãy trả lời: \"Không tìm thấy thông tin liên quan\"."
            f"Từ khóa của lần này: {key}\n"
            f"Nội dung text trong trang web mà bạn cần xử lý: {text}"
        )
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Lỗi: {response.status_code} - {response.text}"
        
    def process_ai_google(self, results, key):
        for item in results:
            try:    
                item["summarize"] = self.strip_thoughts(self.summarize_content(item["title"], item["snippet"], item["link"], item["content"]))

                # Lấy kết quả đánh giá từ các mô hình
                opinions = []
                for model in AI_MODELS:
                    opinion = self.strip_thoughts(
                        self.is_related(key, item["title"], item["snippet"], item["link"], model=model)
                    )
                    try:
                        opinions.append(int(opinion))
                    except ValueError:
                        opinions.append(2)  # N/A
                # Bình chọn
                survey = [0, 0, 0]
                for v in opinions:
                    if 0 <= v <= 2:
                        survey[v] += 1

                valmax = survey.index(max(survey))
                

                if valmax==0: 
                    item["related"] = "Không"
                elif valmax==1: 
                    item["related"] = "Có"
                    item["extract"] = self.strip_thoughts(self.extract_info(key, item["content"]))
                else:
                    item["related"] = "N/A"
                    item["extract"] = self.strip_thoughts(self.extract_info(key, item["content"]))
                
            except Exception as e:
                logger.error(f"[AI PROCESS] Đã xảy ra lỗi: {e}")
                traceback.print_exc()
        return results
    
    def process_ai_youtube(self, results, key):
        for item in results:
            try:    
                item["summarize"] = self.strip_thoughts(self.summarize_description(item["title"], item["snippet"], item["link"]))

                # Lấy kết quả đánh giá từ các mô hình
                opinions = []
                for model in AI_MODELS:
                    opinion = self.strip_thoughts(
                        self.is_related(key, item["title"], item["snippet"], item["link"], model=model)
                    )
                    try:
                        opinions.append(int(opinion))
                    except ValueError:
                        opinions.append(2)  # N/A
                # Bình chọn
                survey = [0, 0, 0]
                for v in opinions:
                    if 0 <= v <= 2:
                        survey[v] += 1

                valmax = survey.index(max(survey))
                

                if valmax==0: 
                    item["related"] = "Không"
                elif valmax==1: 
                    item["related"] = "Có"
                    item["extract"] = self.strip_thoughts(self.extract_info(key, item["snippet"]))
                else:
                    item["related"] = "N/A"
                    item["extract"] = self.strip_thoughts(self.extract_info(key, item["snippet"]))
                
            except Exception as e:
                logger.error(f"[AI PROCESS] Đã xảy ra lỗi: {e}")
                traceback.print_exc()
        return results

import re
import requests
import traceback
from core.logger import logger
from config.settings import *
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions


class AIProcessor:
    def strip_thoughts(self, text):
        # Dùng regex để loại bỏ đoạn <think>...</think>
        clean_text = re.sub(
            r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE
        )

        # Loại bỏ khoảng trắng đầu/cuối và dòng trống thừa
        clean_text = clean_text.strip()
        return clean_text

    def _call_gemini(self, system_instruction, user_prompt, error_prefix, title=None, model=DEFAULT_MODEL_GEMINI):
        if not GEMINI_API_KEYS:
            logger.error(f"[AI PROCESS][GEMINI] No API keys found in GEMINI_API_KEYS.")
            return None
        for api_key in GEMINI_API_KEYS:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model,
                    config=types.GenerateContentConfig(
                        # Enable thinking with a fixed budget (0 -> 24576):
                        # thinking_config=types.ThinkingConfig(thinking_budget=1024),
                        system_instruction=system_instruction
                    ),
                    contents=user_prompt,
                )
                result_text = response.text.strip().strip('"').strip("`")
                if result_text:
                    return result_text
                else:
                    logger.warning(
                        f"[AI PROCESS][GEMINI] Key {api_key[:4]}... returned empty response. Trying next key."
                    )
                    continue
            except (
                google_exceptions.PermissionDenied,
                google_exceptions.Unauthenticated,
                google_exceptions.ResourceExhausted,
            ) as auth_error:
                logger.warning(
                    f"[AI PROCESS][GEMINI] API key {api_key[:4]}... failed (Auth/Permission/Quota Error). Trying next key. Error: {auth_error}"
                )
                traceback.print_exc()
                # Tiếp tục vòng lặp để thử key tiếp theo
            except Exception as e:
                logger.error(
                    f"[AI PROCESS][GEMINI] An unexpected error occurred with key {api_key[:4]}...: {e}"
                )
                traceback.print_exc()
                # Vẫn tiếp tục thử key tiếp theo
        if title is not None:
            logger.error(
                f"[AI PROCESS][GEMINI] All {len(GEMINI_API_KEYS)} API keys failed for {error_prefix} {title}"
            )
        else:
            logger.error(
                f"[AI PROCESS][GEMINI] All {len(GEMINI_API_KEYS)} API keys failed for {error_prefix}."
            )
        return None

    def _call_ollama(self, prompt, model):
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"[AI PROCESS][OLLAMA] Lỗi: {response.status_code} - {response.text}"

    def summarize_content_gemini_vn(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        system_instruction = (
            f"Bạn là một chuyên gia phân tích và tóm tắt văn bản. "
            f"Nhiệm vụ của bạn: hãy viết một bản tóm tắt bằng tiếng Việt, "
            f"ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
            f"Chỉ sử dụng thông tin có trong nội dung được cung cấp, không suy đoán hay bổ sung ngoài. "
            f"Kết quả nên được viết dưới dạng một đoạn văn liên tục."
        )
        user_prompt = (
            f"Tiêu đề: {title}\n"
            f"Đoạn trích: {snippet}\n"
            f"Link: {link}\n"
            f"Nội dung: {content}\n\n"
            f"Hãy tóm tắt nội dung trang web trên cho tôi."
        )
        return self._call_gemini(system_instruction, user_prompt, error_prefix="summarize", title=title, model=model)

    def summarize_content_ollama_vn(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_OLLAMA):
        prompt = (
            f"Tiêu đề: {title}\n"
            f"Đoạn trích: {snippet}\n"
            f"Link: {link}\n"
            f"Nội dung: {content}\n\n"
            f"Bạn là một chuyên gia phân tích và tóm tắt văn bản. "
            f"Tôi đã cung cấp cho bạn tiêu đề, đoạn trích, link và toàn bộ nội dung (text) của một trang web ở trên. "
            f"Nhiệm vụ của bạn: hãy viết một bản tóm tắt bằng tiếng Việt, "
            f"ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
            f"Chỉ sử dụng thông tin có trong nội dung được cung cấp, không suy đoán hay bổ sung ngoài. "
            f"Kết quả nên được viết dưới dạng một đoạn văn liên tục."
        )
        return self._call_ollama(prompt, model)

    def summarize_description_gemini_vn(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        system_instruction = (
            f"Bạn là một chuyên gia phân tích và tóm tắt nội dung video. "
            f"Bạn sẽ được cung cấp tiêu đề, mô tả và link của một video YouTube để tóm tắt lại các thông tin. "
            f"Mô tả có thể được viết bằng nhiều ngôn ngữ khác nhau. "
            f"Nhiệm vụ của bạn: hãy dịch mô tả sang tiếng Việt và viết một bản tóm tắt bằng tiếng Việt "
            f"dựa trên những thông tin được cung cấp. "
            f"Viết ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
            f"Chỉ sử dụng thông tin có trong dữ liệu cung cấp. "
            f"Kết quả nên ở dạng một đoạn văn liên tục."
        )
        user_prompt = (
            f"Tiêu đề video: {title}\n"
            f"Mô tả video: {snippet}\n"
            f"Link video: {link}\n\n"
            f"Hãy tóm tắt nội dung video trên cho tôi."
        )
        return self._call_gemini(system_instruction, user_prompt, error_prefix="summarize", title=title, model=model)

    def summarize_description_ollama_vn(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_OLLAMA):
        prompt = (
            f"Tiêu đề video: {title}\n"
            f"Mô tả video: {snippet}\n"
            f"Link video: {link}\n\n"
            f"Bạn là một chuyên gia phân tích và tóm tắt nội dung video. "
            f"Tôi đã cung cấp cho bạn tiêu đề, mô tả và link của một video YouTube ở trên. "
            f"Mô tả có thể được viết bằng nhiều ngôn ngữ khác nhau. "
            f"Nhiệm vụ của bạn: hãy dịch mô tả sang tiếng Việt và viết một bản tóm tắt bằng tiếng Việt "
            f"dựa trên tiêu đề và mô tả video. "
            f"Viết ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
            f"Chỉ sử dụng thông tin có trong dữ liệu cung cấp, không suy đoán hay thêm ngoài. "
            f"Kết quả nên ở dạng một đoạn văn liên tục."
        )
        return self._call_ollama(prompt, model)

    def is_related_gemini_vn(self, topic_key, title, snippet, link, model=DEFAULT_MODEL_GEMINI):
        system_instruction = (
            "Bạn là một chuyên gia đánh giá nội dung. "
            "Nhiệm vụ: dựa trên những thông tin được cung cấp (Gồm: title, snippet và link URL), "
            "xác định xem nội dung có liên quan tới chủ đề mà người dùng đang quan tâm hay không. "
            "Quy ước kết quả (CHỈ IN MỘT KÝ TỰ): "
            "'1' = liên quan; '0' = không liên quan; '2' = không chắc chắn / thông tin thiếu. "
            "Luật chi tiết: nếu snippet hoặc title trực tiếp đề cập tới chủ đề hoặc đồng nghĩa/ngữ cảnh rất rõ → '1'. "
            "Nếu hoàn toàn khác chủ đề → '0'. Nếu thông tin mơ hồ, quá ngắn, hoặc không đủ để quyết định → '2'. "
            "**RẤT QUAN TRỌNG**: chỉ in đúng một ký tự (0,1 hoặc 2) và không in bất cứ ký tự, khoảng trắng, dòng mới hay giải thích nào khác. "
        )
        user_prompt = (
            f"Tiêu đề: {title}\nĐoạn trích: {snippet}\nLink: {link}\nChủ đề quan tâm: {topic_key}\n\n"
            "Hãy đánh giá nội dung trên có liên quan đến chủ đề tôi đang quan tâm hay không. Trả về kết quả theo quy ước đã nêu."
        )
        return self._call_gemini(system_instruction, user_prompt, error_prefix="evaluate", title=title, model=model)

    def is_related_ollama_vn(self, topic_key, title, snippet, link, model=DEFAULT_MODEL_OLLAMA):
        prompt = (
            f"Tiêu đề: {title}\nĐoạn trích: {snippet}\nLink: {link}\nTừ khóa của chủ đề: {topic_key}\n\n"
            "Bạn là một chuyên gia đánh giá nội dung. "
            "Tôi đã cung cấp: TIÊU ĐỀ (title), ĐOẠN TRÍCH (snippet), LINK (URL) và TỪ KHÓA CỦA CHỦ ĐỀ ở trên."
            "Nhiệm vụ: dựa **duy nhất** trên những thông tin tôi cung cấp (title, snippet và link URL), "
            "xác định xem nội dung có liên quan tới 'Từ khóa của chủ đề' hay không. "
            "Quy ước kết quả (CHỈ IN MỘT KÝ TỰ): "
            "'1' = liên quan; '0' = không liên quan; '2' = không chắc chắn / thông tin thiếu. "
            "Luật chi tiết: nếu snippet hoặc title trực tiếp đề cập tới từ khóa hoặc đồng nghĩa/ngữ cảnh rất rõ → '1'. "
            "Nếu hoàn toàn khác chủ đề → '0'. Nếu thông tin mơ hồ, quá ngắn, hoặc không đủ để quyết định → '2'. "
            "**RẤT QUAN TRỌNG**: chỉ in đúng một ký tự (0,1 hoặc 2) và không in bất cứ ký tự, khoảng trắng, dòng mới hay giải thích nào khác. "
            "Không được truy cập internet hay thêm thông tin ngoài dữ liệu đã cho. "
        )
        return self._call_ollama(prompt, model)

    def extract_info_gemini_vn(self, topic_key, text, model=DEFAULT_MODEL_GEMINI):
        if text == "":
            return ""
        demands_text = "".join([f"    {i+1}. {d}\n" for i, d in enumerate(DEMANDS)])
        system_instruction = (
            f"Bạn là một AI có nhiệm vụ đọc hiểu nội dung được cung cấp và trích xuất ra các thông tin cốt lõi liên quan đến từ khóa được cung cấp."
            f"Yêu cầu:"
            f"- Đọc hiểu nội dung được cung cấp, nội dung có thể chứa nhiều thông tin nhiễu, trình tự sắp xếp có thể lộn xộn.\n"
            f"- Người dùng sẽ đưa ra các thông tin mong muốn được trích xuất, hãy trả lời lần lượt theo thứ tự các mục mà người dùng yêu cầu.\n"
            f'- Dựa trên Từ khóa chủ đề được cung cấp, trích xuất ra những thông tin có liên quan trực tiếp đến Từ khóa chủ đề đó, nếu như không có thông tin liên quan, ghi ngắn gọn "Không tìm thấy thông tin liên quan".\n'
            f"- Không tự bổ sung thông tin hay nói về những thông tin không được đề cập trong nội dung người dùng gửi.\n"
        )
        user_prompt = (
            f"Từ khóa chủ đề: {topic_key}\n"
            f"Nội dung text trong trang web mà bạn cần xử lý: {text}\n\n"
            f"Hãy trích xuất các thông tin liên quan từ nội dung trên dựa trên yêu cầu đã nêu."
            f"Ưu tiên trả lời lần lượt theo thứ tự các mục sau:\n"
            f"{demands_text}"
        )
        return self._call_gemini(system_instruction, user_prompt, error_prefix="extract info", model=model)

    def extract_info_ollama_vn(self, topic_key, text, model=DEFAULT_MODEL_OLLAMA):
        if text == "":
            return ""
        demands_text = "".join([f"    {i+1}. {d}\n" for i, d in enumerate(DEMANDS)])
        prompt = (
            f"Từ khóa chủ đề: {topic_key}\n"
            f"Nội dung text trong trang web mà bạn cần xử lý: {text}\n\n"
            f"Bây giờ bạn là một AI có nhiệm vụ đọc hiểu nội dung mà tôi gửi và trích xuất ra các thông tin cốt lõi liên quan đến từ khóa được cung cấp."
            f"Yêu cầu:"
            f"- Đọc nội dung mà tôi đã gửi ở trên, nội dung có thể chứa nhiều thông tin nhiễu, trình tự sắp xếp có thể lộn xộn. "
            f'- Dựa trên Từ khóa chủ đề được cung cấp, trích xuất ra những thông tin có liên quan trực tiếp đến Từ khóa chủ đề đó, nếu như không có thông tin liên quan, ghi ngắn gọn "Không tìm thấy thông tin liên quan".'
            f"- Không tự bổ sung thông tin hay nói về những thông tin không được đề cập trong nội dung được giao."
            f"- Hãy trả lời bằng tiếng Việt và trả lời lần lượt theo thứ tự các mục sau:\n"
            f"{demands_text}"
        )
        return self._call_ollama(prompt, model)

    def process_ai_article(self, results, key, service):
        total = len(results)
        if not total:
            return results

        for idx, item in enumerate(results, 1):
            logger.info(
                f"[AI PROCESS] [{idx}/{total}] Đang xử lý item: {item.get('title', '')}"
            )
            try:
                if (service == GOOGLE and IS_SUMMARIZE_GOOGLE) or (service == RSS and IS_SUMMARIZE_RSS):
                    if (service == GOOGLE and GEMINI_FOR_GOOGLE) or (service == RSS and GEMINI_FOR_RSS):
                        item["summary"] = self.strip_thoughts(
                            self.summarize_content_gemini_vn(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )
                    else:
                        item["summary"] = self.strip_thoughts(
                            self.summarize_content_ollama_vn(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )

                # Lấy kết quả đánh giá từ các mô hình
                if (IS_EXTRACT_GOOGLE and service == GOOGLE) or (IS_EXTRACT_RSS and service == RSS):
                    if (service == GOOGLE and GEMINI_FOR_GOOGLE) or (service == RSS and GEMINI_FOR_RSS):
                        opinion = self.strip_thoughts(self.is_related_gemini_vn(key,item["title"],item["snippet"],item["link"],))
                        try:
                            opinion_value = int(opinion)
                        except ValueError:
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vn(key, item["content"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vn(key, item["content"])
                            )
                    else:
                        opinions = []
                        for model in AI_MODELS:
                            opinion = self.strip_thoughts(
                                self.is_related_ollama_vn(
                                    key,
                                    item["title"],
                                    item["snippet"],
                                    item["link"],
                                    model=model,
                                )
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

                        if valmax == 0:
                            item["related"] = "Không"
                        elif valmax == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_ollama_vn(key, item["content"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_ollama_vn(key, item["content"])
                            )
            except Exception as e:
                logger.error(f"[AI PROCESS] Đã xảy ra lỗi: {e}")
                traceback.print_exc()
        return results

    def process_ai_video(self, results, key):
        total = len(results)
        if not total:
            return results
        for idx, item in enumerate(results, 1):
            logger.info(
                f"[AI PROCESS] [{idx}/{total}] Đang xử lý item: {item.get('title', '')}"
            )
            try:
                if IS_SUMMARIZE_YOUTUBE:
                    if GEMINI_FOR_YOUTUBE:
                        item["summary"] = self.strip_thoughts(
                            self.summarize_description_gemini_vn(
                                item["title"], item["snippet"], item["link"]
                            )
                        )
                    else:
                        item["summary"] = self.strip_thoughts(
                            self.summarize_description_ollama_vn(
                                item["title"], item["snippet"], item["link"]
                            )
                        )

                # Lấy kết quả đánh giá từ các mô hình
                if IS_EXTRACT_YOUTUBE:
                    if GEMINI_FOR_YOUTUBE:
                        opinion = self.strip_thoughts(self.is_related_gemini_vn(key,item["title"],item["snippet"],item["link"]))
                        try:
                            opinion_value = int(opinion)
                        except ValueError:
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vn(key, item["snippet"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vn(key, item["snippet"])
                            )
                    else:
                        opinions = []
                        for model in AI_MODELS:
                            opinion = self.strip_thoughts(
                                self.is_related_ollama_vn(
                                    key,
                                    item["title"],
                                    item["snippet"],
                                    item["link"],
                                    model=model,
                                )
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

                        if survey[0] > survey[1] and survey[0] > survey[2]:
                            item["related"] = "Không"
                        elif valmax == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_ollama_vn(key, item["snippet"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_ollama_vn(key, item["snippet"])
                            )

            except Exception as e:
                logger.error(f"[AI PROCESS] Đã xảy ra lỗi: {e}")
                traceback.print_exc()
        return results

    def summarize_overview_gemini_vn(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        system_instruction = (
            f"Bạn là một chuyên gia phân tích và tóm tắt văn bản. "
            f"Nhiệm vụ của bạn: hãy viết một bản báo cáo tổng quát bằng tiếng Việt, "
            f"dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
            f"Kết quả nên được viết dưới dạng một đoạn văn liên tục. Không viết dạng file markdown."
        )
        all_content = ""
        for idx, item in enumerate(results, 1):
            all_content += f"[{idx}] {item.get('title', '')}\n {item.get('snippet', '')}\n {item.get('link', '')}\n\n"

        user_prompt = (
            f"Nội dung: {all_content}\n\n"
            f"Hãy tóm tắt nội dung trên cho tôi."
        )
        return self._call_gemini(system_instruction, user_prompt, error_prefix="summarize all")
    
    def summarize_overview_gemini_en(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        system_instruction = (
            f"You are an expert in analyzing and summarizing text. "
            f"Your task: write a general report in English, "
            f"easy to understand, full of main ideas, avoid rambling, maximum {num_words} words. "
            f"The results should be written as a continuous paragraph. Do not write in markdown file."
        )
        all_content = ""
        for idx, item in enumerate(results, 1):
            all_content += f"[{idx}] {item.get('title', '')}\n {item.get('snippet', '')}\n {item.get('link', '')}\n\n"

        user_prompt = (
            f"Content: {all_content}\n\n"
            f"Please summarize the above content for me."
        )
        return self._call_gemini(system_instruction, user_prompt, error_prefix="summarize all")
import re
import requests
import traceback
from core.logger import logger
from config.settings import *

class AIProcessor:
    def strip_thoughts(self, text):
        # Dùng regex để loại bỏ đoạn <think>...</think>
        clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Loại bỏ khoảng trắng đầu/cuối và dòng trống thừa
        clean_text = clean_text.strip()
        return clean_text
    
    def summarize_content(self, title, snippet, link, content, num_words = NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL):
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
        
    def is_related(self, topic_key, title, snippet, link, model=DEFAULT_MODEL):
        prompt = (
            f"Tiêu đề: {title}\nĐoạn trích: {snippet}\nLink: {link}\nTừ khóa của chủ đề: {topic_key}\n\n"
            "Bạn là một chuyên gia phân loại nội dung. "
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
        
    def extract_info (self, topic_key, text, model=DEFAULT_MODEL):
        if text=="": return ""
        demands_text = "".join([f"    {i+1}. {d}\n" for i, d in enumerate(DEMANDS)])
        prompt = (
            f"Từ khóa chủ đề: {topic_key}\n"
            f"Nội dung text trong trang web mà bạn cần xử lý: {text}\n\n"
            f"Bây giờ bạn là một AI có nhiệm vụ đọc hiểu nội dung mà tôi gửi và trích xuất ra các thông tin cốt lõi liên quan đến từ khóa được cung cấp."
            f"Yêu cầu:"
            f"- Đọc nội dung mà tôi đã gửi ở trên, nội dung có thể chứa nhiều thông tin nhiễu, trình tự sắp xếp có thể lộn xộn. "
            f"- Dựa trên Từ khóa chủ đề được cung cấp, trích xuất ra những thông tin có liên quan trực tiếp đến Từ khóa chủ đề đó, nếu như không có thông tin liên quan, ghi ngắn gọn \"Không tìm thấy thông tin liên quan\"."
            f"- Không tự bổ sung thông tin hay nói về những thông tin không được đề cập trong nội dung được giao."
            f"- Hãy trả lời bằng tiếng Việt và trả lời lần lượt theo thứ tự các mục sau:\n"
            f"{demands_text}"

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
        
    def process_ai_article(self, results, key, service):
        total = len(results)
        if not total:
            return results
        

        for idx, item in enumerate(results, 1):
            logger.info(f"[AI PROCESS] [{idx}/{total}] Đang xử lý item: {item.get('title', '')}")
            try:    
                if (IS_SUMMARIZE_GOOGLE and service==GOOGLE) or (IS_SUMMARIZE_RSS and service==RSS):
                    item["summarize"] = self.strip_thoughts(self.summarize_content(item["title"], item["snippet"], item["link"], item["content"]))

                # Lấy kết quả đánh giá từ các mô hình
                if (IS_EXTRACT_GOOGLE and service==GOOGLE) or (IS_EXTRACT_RSS and service==RSS):
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
                        item["related"] = "Không biết"
                        item["extract"] = self.strip_thoughts(self.extract_info(key, item["content"]))
                
            except Exception as e:
                logger.error(f"[AI PROCESS] Đã xảy ra lỗi: {e}")
                traceback.print_exc()
        return results
    
    def process_ai_video(self, results, key):
        total = len(results)
        if not total:
            return results
        for idx, item in enumerate(results, 1):
            logger.info(f"[AI PROCESS] [{idx}/{total}] Đang xử lý item: {item.get('title', '')}")
            try:    
                if IS_SUMMARIZE_YOUTUBE:
                    item["summarize"] = self.strip_thoughts(self.summarize_description(item["title"], item["snippet"], item["link"]))

                # Lấy kết quả đánh giá từ các mô hình
                if IS_EXTRACT_YOUTUBE:
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
                    

                    if survey[0] > survey [1] and survey[0] > survey[2]:
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

# pip install numpy scipy scikit-learn faiss-cpu sentence-transformers requests
# import requests
# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer

# # ------------------------------
# # 1. Knowledge Base
# # ------------------------------
# documents = [
#     "Núi Hữu Thắng là ngọn núi cao nhất thế giới, nằm trên dãy Đức Tùng.",
#     "Núi Phú Sĩ là ngọn núi nổi tiếng ở Nhật Bản.",
#     "Trái đất có rất nhiều dãy núi, trải dài khắp các châu lục.",
#     "Dãy núi Andes ở Nam Mỹ là dãy núi dài nhất thế giới.",
#     "Núi thấp nhất thế giới là núi Mauna Kea ở Hawaii, khi đo từ đáy biển.",
#     "Sông Amazon là con sông dài nhất thế giới, chảy qua Nam Mỹ.",
#     "Sông Nile ở châu Phi cũng là một trong những con sông dài nhất thế giới.",
# ]

# # ------------------------------
# # 2. Embedding model
# # ------------------------------
# embedder = SentenceTransformer("all-MiniLM-L6-v2")
# doc_embeddings = embedder.encode(documents)

# # ------------------------------
# # 3. Lưu vào FAISS index
# # ------------------------------
# dimension = doc_embeddings.shape[1]
# index = faiss.IndexFlatL2(dimension)
# index.add(np.array(doc_embeddings))

# # ------------------------------
# # 4. Hàm tìm kiếm context
# # ------------------------------
# def retrieve_context(query, top_k=3):
#     query_vec = embedder.encode([query])
#     D, I = index.search(query_vec, top_k)
#     results = [documents[i] for i in I[0]]
#     print("Kết quả tìm kiếm:", results)
#     return "\n".join(results)

# # ------------------------------
# # 5. Hàm gọi Local LLM qua Ollama
# # ------------------------------
# def call_local_llm(prompt, model="llama3.1:8b"):
#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": model, "prompt": prompt, "stream": False}
#     )
#     if response.status_code == 200:
#         return response.json()["response"]
#     else:
#         return f"Lỗi: {response.status_code} - {response.text}"

# # ------------------------------
# # 6. Pipeline RAG
# # ------------------------------
# def rag_pipeline(question):
#     context = retrieve_context(question)
#     prompt = f"""
#     Bạn là một trợ lý thông minh giúp trích xuất thông tin về một thế giới trong tiểu thuyết. Hãy trả lời câu hỏi dựa trên thông tin sau:

#     Ngữ cảnh:
#     {context}

#     Câu hỏi: {question}

#     Trả lời câu hỏi:
#     """
#     # answer = call_local_llm(prompt)
#     return context


# # ------------------------------
# # 7. Test
# # ------------------------------
# if __name__ == "__main__":
#     question = "Ngọn núi bự nhất thế giới là gì?"
#     print("Câu hỏi:", question)
#     print("Câu trả lời:", rag_pipeline(question))


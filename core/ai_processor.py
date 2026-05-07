import re
import time
import requests
import traceback
from core.logger import logger
from config.settings import *
from config import ai_prompts as prompts
from google import genai
# from google.genai import types
# from google.api_core import exceptions as google_exceptions


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
                # traceback.print_exc()
                # Tiếp tục vòng lặp để thử key tiếp theo
            except Exception as e:
                logger.error(
                    f"[AI PROCESS][GEMINI] An unexpected error occurred with key {api_key[:4]}...: {e}"
                )
                # traceback.print_exc()
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

    def _call_gauss(self, system_instruction, user_prompt, error_prefix, title=None, model=None):
        model = model or DEFAULT_MODEL_GAUSS
        if not GAUSS_API_BASE_URL or not GAUSS_X_OPENAPI_TOKEN:
            logger.error(
                "[AI PROCESS][GAUSS] Missing GAUSS_API_BASE_URL or GAUSS_X_OPENAPI_TOKEN in settings."
            )
            return None
        if not GAUSS_X_GENERATIVE_AI_CLIENT or not GAUSS_X_GENERATIVE_AI_USER_EMAIL:
            logger.error(
                "[AI PROCESS][GAUSS] Missing GAUSS_X_GENERATIVE_AI_CLIENT or GAUSS_X_GENERATIVE_AI_USER_EMAIL."
            )
            return None

        url = f"{GAUSS_API_BASE_URL.rstrip('/')}/openapi/chat/v1/messages"
        headers = {
            "x-generative-ai-client": GAUSS_X_GENERATIVE_AI_CLIENT,
            "x-openapi-token": GAUSS_X_OPENAPI_TOKEN,
            "x-generative-ai-user-email": GAUSS_X_GENERATIVE_AI_USER_EMAIL,
        }
        payload = {
            "modelIds": [model],
            "contents": [user_prompt],
            "llmConfig": {
                "max_new_tokens": 2024,
                "return_full_text": False,
                "seed": None,
                "top_k": 14,
                "top_p": 0.94,
                "temperature": 0.4,
                "repetition_penalty": 1.04,
            },
            "isStream": False,
            "system_prompt": system_instruction,
        }

        time.sleep(GAUSS_API_DELAY)
        for attempt in range(GAUSS_MAX_RETRIES):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=90)
                if response.status_code == 200:
                    result = response.json()
                    raw = None
                    if "content" in result:
                        raw = result["content"]
                    elif (
                        "choices" in result
                        and len(result["choices"]) > 0
                        and "message" in result["choices"][0]
                    ):
                        raw = result["choices"][0]["message"].get("content")
                    if raw is None:
                        logger.error(
                            f"[AI PROCESS][GAUSS] Unexpected response shape for {error_prefix}: {result!r}"
                        )
                        return None
                    text = str(raw).strip().strip('"').strip("`")
                    if text:
                        return text
                    logger.warning(
                        f"[AI PROCESS][GAUSS] Empty content for {error_prefix}, attempt {attempt + 1}."
                    )
                    return None
                if response.status_code == 429:
                    if attempt < GAUSS_MAX_RETRIES - 1:
                        delay = GAUSS_API_DELAY * (GAUSS_BACKOFF_FACTOR**attempt)
                        logger.warning(
                            f"[AI PROCESS][GAUSS] Rate limited (429), retry in {delay}s "
                            f"(attempt {attempt + 1}/{GAUSS_MAX_RETRIES})."
                        )
                        time.sleep(delay)
                        continue
                    logger.error(f"[AI PROCESS][GAUSS] Rate limited after {GAUSS_MAX_RETRIES} attempts.")
                    return None
                logger.error(
                    f"[AI PROCESS][GAUSS] HTTP {response.status_code} for {error_prefix}: {response.text}"
                )
                return None
            except requests.RequestException as e:
                if attempt < GAUSS_MAX_RETRIES - 1:
                    delay = GAUSS_API_DELAY * (GAUSS_BACKOFF_FACTOR**attempt)
                    logger.warning(
                        f"[AI PROCESS][GAUSS] Request error for {error_prefix}, retry in {delay}s: {e}"
                    )
                    time.sleep(delay)
                    continue
                logger.error(f"[AI PROCESS][GAUSS] Request failed for {error_prefix}: {e}")
                return None
        if title is not None:
            logger.error(f"[AI PROCESS][GAUSS] All attempts failed for {error_prefix} {title}")
        else:
            logger.error(f"[AI PROCESS][GAUSS] All attempts failed for {error_prefix}.")
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

    def summarize_overview_gemini_vi(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        all_content = prompts.build_overview_articles_block(results)
        return self._call_gemini(
            prompts.summarize_overview_system_vi(num_words),
            prompts.summarize_overview_user_vi(all_content),
            error_prefix="summarize all",
        )
    
    def summarize_overview_sample_vi(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI summary for overview of all articles in Vietnamese."
    
    def summarize_overview_gemini_en(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        all_content = prompts.build_overview_articles_block(results)
        return self._call_gemini(
            prompts.summarize_overview_system_en(num_words),
            prompts.summarize_overview_user_en(all_content),
            error_prefix="summarize all",
        )
    
    def summarize_overview_sample_en(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI summary for overview of all articles in English."

    def summarize_overview_gauss_vi(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=None):
        all_content = prompts.build_overview_articles_block(results)
        return self._call_gauss(
            prompts.summarize_overview_system_vi(num_words),
            prompts.summarize_overview_user_vi(all_content),
            error_prefix="summarize all",
            model=model,
        )

    def summarize_overview_gauss_en(self, results, num_words=NUMBER_WORDS_SUMMARIZE, model=None):
        all_content = prompts.build_overview_articles_block(results)
        return self._call_gauss(
            prompts.summarize_overview_system_en(num_words),
            prompts.summarize_overview_user_en(all_content),
            error_prefix="summarize all",
            model=model,
        )

    def summarize_content_gemini_vi(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return self._call_gemini(
            prompts.summarize_content_system_vi(num_words),
            prompts.summarize_content_user_vi(title, snippet, link, content),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_content_sample_vi(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI summary for content of an artical in Vietnamese."

    def summarize_content_gemini_en(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return self._call_gemini(
            prompts.summarize_content_system_en(num_words),
            prompts.summarize_content_user_en(title, snippet, link, content),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_content_sample_en(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI summary for content of an artical in English."

    def summarize_content_gauss_vi(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=None):
        return self._call_gauss(
            prompts.summarize_content_system_vi(num_words),
            prompts.summarize_content_user_vi(title, snippet, link, content),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_content_gauss_en(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=None):
        return self._call_gauss(
            prompts.summarize_content_system_en(num_words),
            prompts.summarize_content_user_en(title, snippet, link, content),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_content_ollama_vi(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_OLLAMA):
        return self._call_ollama(
            prompts.summarize_content_ollama_vi(title, snippet, link, content, num_words),
            model,
        )

    def summarize_content_ollama_en(self, title, snippet, link, content, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_OLLAMA):
        return self._call_ollama(
            prompts.summarize_content_ollama_en(title, snippet, link, content, num_words),
            model,
        )

    def summarize_description_gemini_vi(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return self._call_gemini(
            prompts.summarize_video_system_vi(num_words),
            prompts.summarize_video_user_vi(title, snippet, link),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_description_sample_vi(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI summary for description of an artical in Vietnamese."

    def summarize_description_gemini_en(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return self._call_gemini(
            prompts.summarize_video_system_en(num_words),
            prompts.summarize_video_user_en(title, snippet, link),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_description_sample_en(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI summary for description of an artical in English."

    def summarize_description_gauss_vi(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=None):
        return self._call_gauss(
            prompts.summarize_video_system_vi(num_words),
            prompts.summarize_video_user_vi(title, snippet, link),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_description_gauss_en(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=None):
        return self._call_gauss(
            prompts.summarize_video_system_en(num_words),
            prompts.summarize_video_user_en(title, snippet, link),
            error_prefix="summarize",
            title=title,
            model=model,
        )

    def summarize_description_ollama_vi(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_OLLAMA):
        return self._call_ollama(
            prompts.summarize_video_ollama_vi(title, snippet, link, num_words),
            model,
        )

    def summarize_description_ollama_en(self, title, snippet, link, num_words=NUMBER_WORDS_SUMMARIZE, model=DEFAULT_MODEL_OLLAMA):
        return self._call_ollama(
            prompts.summarize_video_ollama_en(title, snippet, link, num_words),
            model,
        )

    def is_related_gemini_vi(self, topic_key, title, snippet, link, model=DEFAULT_MODEL_GEMINI):
        return self._call_gemini(
            prompts.is_related_system_vi(),
            prompts.is_related_user_vi(topic_key, title, snippet, link),
            error_prefix="evaluate",
            title=title,
            model=model,
        )

    def is_related_sample_vi(self, topic_key, title, snippet, link, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI evaluate is the artical contains related information in Vietnamese."

    def is_related_gauss_vi(self, topic_key, title, snippet, link, model=None):
        return self._call_gauss(
            prompts.is_related_system_vi(),
            prompts.is_related_user_vi(topic_key, title, snippet, link),
            error_prefix="evaluate",
            title=title,
            model=model,
        )

    def is_related_ollama_vi(self, topic_key, title, snippet, link, model=DEFAULT_MODEL_OLLAMA):
        return self._call_ollama(
            prompts.is_related_ollama_vi(topic_key, title, snippet, link),
            model,
        )

    def extract_info_gemini_vi(self, topic_key, text, model=DEFAULT_MODEL_GEMINI):
        if text == "":
            return ""
        demands_text = prompts.format_demands_text(DEMANDS)
        return self._call_gemini(
            prompts.extract_info_system_gemini_vi(),
            prompts.extract_info_user_gemini_vi(topic_key, text, demands_text),
            error_prefix="extract info",
            model=model,
        )

    def extract_info_gauss_vi(self, topic_key, text, model=None):
        if text == "":
            return ""
        demands_text = prompts.format_demands_text(DEMANDS)
        return self._call_gauss(
            prompts.extract_info_system_gemini_vi(),
            prompts.extract_info_user_gemini_vi(topic_key, text, demands_text),
            error_prefix="extract info",
            model=model,
        )

    def extract_info_sample_vi(self, topic_key, text, model=DEFAULT_MODEL_GEMINI):
        return "Sample AI extract related information in the artical in Vietnamese."

    def extract_info_ollama_vi(self, topic_key, text, model=DEFAULT_MODEL_OLLAMA):
        if text == "":
            return ""
        demands_text = prompts.format_demands_text(DEMANDS)
        return self._call_ollama(
            prompts.extract_info_ollama_vi(topic_key, text, demands_text),
            model,
        )

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
                    if (service == GOOGLE and IS_TEST_AI_PROCESS) or (service == RSS and IS_TEST_AI_PROCESS):
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_content_sample_vi(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )
                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_content_sample_en(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )
                    elif (service == GOOGLE and GAUSS_FOR_GOOGLE) or (service == RSS and GAUSS_FOR_RSS):
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_content_gauss_vi(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )
                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_content_gauss_en(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )
                    elif (service == GOOGLE and GEMINI_FOR_GOOGLE) or (service == RSS and GEMINI_FOR_RSS):
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_content_gemini_vi(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )
                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_content_gemini_en(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )

                    else:
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_content_ollama_vi(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )
                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_content_ollama_en(
                                item["title"],
                                item["snippet"],
                                item["link"],
                                item["content"],
                            )
                        )

                # Lấy kết quả đánh giá từ các mô hình
                if (IS_EXTRACT_GOOGLE and service == GOOGLE) or (IS_EXTRACT_RSS and service == RSS):
                    if (service == GOOGLE and IS_TEST_AI_PROCESS) or (service == RSS and IS_TEST_AI_PROCESS):
                        opinion = self.strip_thoughts(self.is_related_sample_vi(key,item["title"],item["snippet"],item["link"],))
                        try:
                            opinion_value = int(opinion)
                        except ValueError:
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_sample_vi(key, item["content"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_sample_vi(key, item["content"])
                            )
                    elif (service == GOOGLE and GAUSS_FOR_GOOGLE) or (service == RSS and GAUSS_FOR_RSS):
                        opinion = self.strip_thoughts(
                            self.is_related_gauss_vi(key, item["title"], item["snippet"], item["link"])
                        )
                        try:
                            opinion_value = int(opinion)
                        except (TypeError, ValueError):
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gauss_vi(key, item["content"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gauss_vi(key, item["content"])
                            )
                    elif (service == GOOGLE and GEMINI_FOR_GOOGLE) or (service == RSS and GEMINI_FOR_RSS):
                        opinion = self.strip_thoughts(self.is_related_gemini_vi(key,item["title"],item["snippet"],item["link"],))
                        try:
                            opinion_value = int(opinion)
                        except ValueError:
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vi(key, item["content"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vi(key, item["content"])
                            )
                    else:
                        opinions = []
                        for model in AI_MODELS:
                            opinion = self.strip_thoughts(
                                self.is_related_ollama_vi(
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
                                self.extract_info_ollama_vi(key, item["content"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_ollama_vi(key, item["content"])
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
                    if IS_TEST_AI_PROCESS:
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_description_sample_vi(
                                item["title"], item["snippet"], item["link"]
                            )
                        )
                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_description_sample_en(
                                item["title"], item["snippet"], item["link"]
                            )
                        )
                    elif GAUSS_FOR_YOUTUBE:
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_description_gauss_vi(
                                item["title"], item["snippet"], item["link"]
                            )
                        )
                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_description_gauss_en(
                                item["title"], item["snippet"], item["link"]
                            )
                        )
                    elif GEMINI_FOR_YOUTUBE:
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_description_gemini_vi(
                                item["title"], item["snippet"], item["link"]
                            )
                        )
                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_description_gemini_en(
                                item["title"], item["snippet"], item["link"]
                            )
                        )
                    else:
                        item["summary_vi"] = self.strip_thoughts(
                            self.summarize_description_ollama_vi(
                                item["title"], item["snippet"], item["link"]
                            )
                        )

                        item["summary_en"] = self.strip_thoughts(
                            self.summarize_description_ollama_en(
                                item["title"], item["snippet"], item["link"]
                            )
                        )

                # Lấy kết quả đánh giá từ các mô hình
                if IS_EXTRACT_YOUTUBE:
                    if IS_TEST_AI_PROCESS:
                        opinion = self.strip_thoughts(self.is_related_sample_vi(key,item["title"],item["snippet"],item["link"]))
                        try:
                            opinion_value = int(opinion)
                        except ValueError:
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_sample_vi(key, item["snippet"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_sample_vi(key, item["snippet"])
                            )
                    elif GAUSS_FOR_YOUTUBE:
                        opinion = self.strip_thoughts(
                            self.is_related_gauss_vi(key, item["title"], item["snippet"], item["link"])
                        )
                        try:
                            opinion_value = int(opinion)
                        except (TypeError, ValueError):
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gauss_vi(key, item["snippet"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gauss_vi(key, item["snippet"])
                            )
                    elif GEMINI_FOR_YOUTUBE:
                        opinion = self.strip_thoughts(self.is_related_gemini_vi(key,item["title"],item["snippet"],item["link"]))
                        try:
                            opinion_value = int(opinion)
                        except ValueError:
                            opinion_value = 2  # N/A
                        if opinion_value == 0:
                            item["related"] = "Không"
                        elif opinion_value == 1:
                            item["related"] = "Có"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vi(key, item["snippet"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_gemini_vi(key, item["snippet"])
                            )
                    else:
                        opinions = []
                        for model in AI_MODELS:
                            opinion = self.strip_thoughts(
                                self.is_related_ollama_vi(
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
                                self.extract_info_ollama_vi(key, item["snippet"])
                            )
                        else:
                            item["related"] = "Không biết"
                            item["extract"] = self.strip_thoughts(
                                self.extract_info_ollama_vi(key, item["snippet"])
                            )

            except Exception as e:
                logger.error(f"[AI PROCESS] Đã xảy ra lỗi: {e}")
                traceback.print_exc()
        return results
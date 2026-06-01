import json
import re
import time
import requests
import traceback
from copy import deepcopy
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

    def _parse_json_tags_response(self, text, max_tags):
        if not text:
            return None
        t = self.strip_thoughts(text)
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE | re.MULTILINE)
        t = re.sub(r"\s*```\s*$", "", t, flags=re.MULTILINE).strip()
        try:
            obj = json.loads(t)
        except json.JSONDecodeError:
            m = re.search(r"\{[\s\S]*\}", t)
            if not m:
                return None
            try:
                obj = json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
        tags = obj.get("tags")
        if not isinstance(tags, list):
            return None
        out = []
        seen = set()
        for x in tags:
            s = str(x).strip()
            if not s:
                continue
            if len(s) > 48:
                s = s[:48].rstrip()
            low = s.lower()
            if low in seen:
                continue
            seen.add(low)
            out.append(s)
            if len(out) >= max_tags:
                break
        return out

    def _finalize_normalized_tags(self, tags, max_tags):
        """
        Normalize tags using the 50 canonical tags system.
        Ensures all output tags are from the canonical list.
        """
        tags = [str(t).strip() for t in (tags or []) if str(t).strip()]
        
        # Filter to only canonical tags
        canonical_tags = []
        for t in tags:
            if t in prompts.TAG_CANONICAL_SET:
                canonical_tags.append(t)
            else:
                # Try case-insensitive match
                for ct in prompts.ALL_CANONICAL_TAGS:
                    if ct.lower() == t.lower():
                        canonical_tags.append(ct)
                        break
        
        # Deduplicate
        seen = set()
        deduped = []
        for t in canonical_tags:
            low = t.lower()
            if low in seen:
                continue
            seen.add(low)
            deduped.append(t)
        
        # Ensure exactly one device tag
        device_by_lower = {d.lower(): d for d in prompts.TAG_DEVICE_CANONICAL}
        device_tags = [t for t in deduped if t.lower() in device_by_lower]
        others = [t for t in deduped if t.lower() not in device_by_lower]
        
        if device_tags:
            device = device_by_lower[device_tags[0].lower()]
        else:
            # No device tag found - try to infer from context or use default
            device = "Multiple Devices"  # Safer default than "Other Electronics"
        
        # Build output with device tag first
        out = [device] + others
        
        # Limit to max_tags
        if len(out) > max_tags:
            out = [device] + others[: max_tags - 1]
        
        return out

    def normalize_tags_sample_json(self):
        return '{"tags": ["Phishing", "Smartphone", "Email Security"]}'

    def normalize_tags_gauss(
        self, topic_key, title, snippet, summary_en, tags_raw, max_tags, model=None
    ):
        return self._call_gauss(
            prompts.normalize_tags_system(),
            prompts.normalize_tags_user(
                topic_key, title, snippet, summary_en, tags_raw, max_tags
            ),
            error_prefix="normalize tags",
            title=title,
            model=model,
        )

    def normalize_tags_gemini(
        self, topic_key, title, snippet, summary_en, tags_raw, max_tags, model=DEFAULT_MODEL_GEMINI
    ):
        return self._call_gemini(
            prompts.normalize_tags_system(),
            prompts.normalize_tags_user(
                topic_key, title, snippet, summary_en, tags_raw, max_tags
            ),
            error_prefix="normalize tags",
            title=title,
            model=model,
        )

    def normalize_tags_ollama(
        self, topic_key, title, snippet, summary_en, tags_raw, max_tags, model=None
    ):
        model = model or (AI_MODELS[0] if AI_MODELS else DEFAULT_MODEL_OLLAMA)
        prompt = prompts.normalize_tags_ollama_prompt(
            topic_key, title, snippet, summary_en, tags_raw, max_tags
        )
        return self._call_ollama(prompt, model)

    def _normalize_rss_item_tags(self, item, topic_key):
        """Chuẩn hóa item['tags'] cho RSS; giữ tag cũ nếu API/parse lỗi."""
        raw = item.get("tags") or []
        if isinstance(raw, list):
            cleaned = [str(t).strip() for t in raw if str(t).strip()]
        else:
            cleaned = []
        title = str(item.get("title", "") or "")
        snippet = str(item.get("snippet", "") or "")
        summary_en = str(item.get("summary_en", "") or "")
        has_context = bool(title.strip() and (summary_en.strip() or snippet.strip()))
        if not cleaned and not has_context:
            return
        if cleaned:
            item["tags_raw"] = list(cleaned)
        max_tags = int(TAGS_NORMALIZE_MAX) if TAGS_NORMALIZE_MAX else 8
        if max_tags < 1:
            max_tags = 8
        if IS_TEST_AI_PROCESS:
            raw_json = self.normalize_tags_sample_json()
        elif GAUSS_FOR_RSS:
            raw_json = self.normalize_tags_gauss(
                topic_key, title, snippet, summary_en, cleaned, max_tags
            )
        elif GEMINI_FOR_RSS:
            raw_json = self.normalize_tags_gemini(
                topic_key, title, snippet, summary_en, cleaned, max_tags
            )
        else:
            raw_json = self.normalize_tags_ollama(
                topic_key, title, snippet, summary_en, cleaned, max_tags
            )
        if not raw_json:
            logger.warning(
                "[AI PROCESS][TAGS] Model trả rỗng/None, giữ tag hiện tại: %s",
                title[:80],
            )
            return
        parsed = self._parse_json_tags_response(raw_json, max_tags)
        if parsed is None:
            logger.warning(
                "[AI PROCESS][TAGS] Parse JSON thất bại, giữ tag hiện tại: %s",
                title[:80],
            )
            return
        item["tags"] = self._finalize_normalized_tags(parsed, max_tags)
        logger.info(
            "[AI PROCESS][TAGS] Đã chuẩn hóa %s tag cho: %s",
            len(item["tags"]),
            title[:60],
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

                if service == RSS and IS_NORMALIZE_TAGS_RSS:
                    self._normalize_rss_item_tags(item, key)
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

    def _normalize_related_value(self, raw_value):
        try:
            return int(str(raw_value).strip())
        except (TypeError, ValueError):
            return 2

    def _match_keywords(self, text, keywords):
        lowered = (text or "").lower()
        return [kw for kw in keywords if kw and kw.lower() in lowered]

    def _pick_fallback_target(self, profile):
        return profile.get("fallback_target_section") or RSS_ROUTING_DEFAULT_TARGET

    def _is_related_for_profile(self, profile, item):
        topic_key = profile.get("topic_key_for_ai", TOPIC_KEYWORD)
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")

        if IS_TEST_AI_PROCESS:
            opinion = self.strip_thoughts(
                self.is_related_sample_vi(topic_key, title, snippet, link)
            )
            return self._normalize_related_value(opinion)

        if GAUSS_FOR_RSS:
            opinion = self.strip_thoughts(
                self.is_related_gauss_vi(topic_key, title, snippet, link)
            )
            return self._normalize_related_value(opinion)

        if GEMINI_FOR_RSS:
            opinion = self.strip_thoughts(
                self.is_related_gemini_vi(topic_key, title, snippet, link)
            )
            return self._normalize_related_value(opinion)

        opinion = self.strip_thoughts(
            self.is_related_ollama_vi(topic_key, title, snippet, link)
        )
        return self._normalize_related_value(opinion)

    def route_section_items(self, items, profile):
        kept_items = []
        uncertain_items = []
        moved_items_by_target = {}
        metrics = {
            "total": len(items),
            "kept": 0,
            "moved": 0,
            "uncertain": 0,
            "rule_hits": 0,
            "ai_hits": 0,
            "ai_only": bool(profile.get("ai_only", False)),
        }

        fallback_target = self._pick_fallback_target(profile)
        uncertain_policy = (profile.get("uncertain_policy") or "keep").lower()
        ai_only = bool(profile.get("ai_only", False))
        positive_keywords = profile.get("positive_keywords", [])
        negative_keywords = profile.get("negative_keywords", [])

        for item in items:
            candidate = deepcopy(item)
            text_blob = " ".join(
                [
                    str(candidate.get("title", "")),
                    str(candidate.get("snippet", "")),
                    str(candidate.get("content", "")),
                ]
            )

            decision = None
            if not ai_only:
                pos_matches = self._match_keywords(text_blob, positive_keywords)
                neg_matches = self._match_keywords(text_blob, negative_keywords)
                if pos_matches and not neg_matches:
                    decision = 1
                    metrics["rule_hits"] += 1
                elif neg_matches and not pos_matches:
                    decision = 0
                    metrics["rule_hits"] += 1

            if decision is None:
                decision = self._is_related_for_profile(profile, candidate)
                metrics["ai_hits"] += 1

            if decision == 1:
                kept_items.append(candidate)
                metrics["kept"] += 1
                continue

            if decision == 0:
                moved_items_by_target.setdefault(fallback_target, []).append(candidate)
                metrics["moved"] += 1
                continue

            metrics["uncertain"] += 1
            uncertain_items.append(candidate)
            if uncertain_policy == "move":
                moved_items_by_target.setdefault(fallback_target, []).append(candidate)
                metrics["moved"] += 1
            else:
                kept_items.append(candidate)
                metrics["kept"] += 1

        return {
            "kept_items": kept_items,
            "moved_items_by_target": moved_items_by_target,
            "uncertain_items": uncertain_items,
            "metrics": metrics,
        }

    def route_rss_sections(self, sections_data, section_profiles):
        routed_sections = {name: list(items) for name, items in sections_data.items()}
        section_metrics = {}

        for section_name, profile in section_profiles.items():
            items = routed_sections.get(section_name, [])
            routed = self.route_section_items(items, profile)
            routed_sections[section_name] = routed["kept_items"]
            section_metrics[section_name] = routed["metrics"]

            for target_name, moved_items in routed["moved_items_by_target"].items():
                routed_sections.setdefault(target_name, [])
                routed_sections[target_name].extend(moved_items)

        for section_name, items in routed_sections.items():
            seen = set()
            deduped = []
            for item in items:
                dedupe_key = item.get("link") or f"{item.get('title','')}|{item.get('published','')}"
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                deduped.append(item)
            routed_sections[section_name] = deduped

        return routed_sections, section_metrics
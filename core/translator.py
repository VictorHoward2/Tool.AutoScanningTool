import urllib3
import requests
import traceback
from core.logger import logger
from config.settings import *
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

class Translator:
    def translate_using_api(self, text, from_lang="en", to_lang="vi"):
        try: 
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            url = "https://api.mymemory.translated.net/get"
            data = {
                "q": text[:490],  # Giới hạn độ dài để tránh lỗi
                "langpair": f"{from_lang}|{to_lang}"
            }
            response = requests.post(url, data=data, timeout=TIMEOUT)
            data = response.json()
            response.raise_for_status()  # Raise an exception for HTTP errors
            return data['responseData']['translatedText']
        except Exception as e:
            logger.error(f"[TRANSLATOR] Fail to translate to {to_lang} query: {text}")
            traceback.print_exc()
            return None
    
    def translate_using_gemini(self, text, from_lang="en", to_lang="vi"):
        prompt = (
            f"Translate the following text from {from_lang} to {to_lang}. "
            f"Only return the translated text itself, without any introduction, preamble, or markdown formatting.\n\n"
            f"Text to translate: \"{text}\""
        )
        system_instruction = (
            "You are a professional translator. Provide accurate and context-aware translations. "
            "You must only return the final translated text, with no other words or formatting."
        )


        model_name = "gemini-2.5-flash"
        if not GEMINI_API_KEYS:
            logger.error("[TRANSLATOR-GEMINI] No API keys found in GEMINI_API_KEYS.")
            return None
        

        for api_key in GEMINI_API_KEYS:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        # Enable thinking with a fixed budget (0 -> 24576):
                        # thinking_config=types.ThinkingConfig(thinking_budget=1024),
                        system_instruction=system_instruction
                    ),
                    contents=prompt,
                )
                translated_text = response.text.strip().strip('"').strip('`')

                if translated_text:
                    return translated_text
                else:
                    logger.warning(f"[TRANSLATOR-GEMINI] Key {api_key[:4]}... returned empty response. Trying next key.")
                    continue

            except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated, google_exceptions.ResourceExhausted) as auth_error:
                logger.warning(f"[TRANSLATOR-GEMINI] API key {api_key[:4]}... failed (Auth/Permission/Quota Error). Trying next key. Error: {auth_error}")
                traceback.print_exc()
                # Tiếp tục vòng lặp để thử key tiếp theo

            except Exception as e:
                logger.error(f"[TRANSLATOR-GEMINI] An unexpected error occurred with key {api_key[:4]}...: {e}")
                traceback.print_exc()
                # Vẫn tiếp tục thử key tiếp theo
            
        # Nếu tất cả các key đều thất bại
        logger.error(f"[TRANSLATOR-GEMINI] All {len(GEMINI_API_KEYS)} API keys failed for query: {text}")
        return None


    def make_queries(self, query, original_lang = "en"):
        queries = {}
        queries[original_lang] = query

        if not IS_TRANSLATE:
            return queries
        
        for lang in LANGUAGES:
            if lang == original_lang: continue
            queries[lang] = self.translate_using_gemini(query, to_lang=lang)
        return queries
        
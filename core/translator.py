import urllib3
import requests
import traceback
from core.logger import logger
from config.settings import *
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
        
    def make_queries(self, query, original_lang = "en"):
        queries = {}
        queries[original_lang] = query

        if not IS_TRANSLATE:
            return queries
        
        for lang in LANGUAGES:
            if lang == original_lang: continue
            queries[lang] = self.translate_using_api(query, to_lang=lang)
        return queries
        
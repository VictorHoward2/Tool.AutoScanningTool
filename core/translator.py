import urllib3
import requests
import traceback
from core.logger import logger
from config.settings import LANGUAGES, TIMEOUT
class Translator:
    def make_url_trans(self, text, from_lang, to_lang):
        return f"https://api.mymemory.translated.net/get?q={text}&langpair={from_lang}%7C{to_lang}"
    
    def translate_using_api(self, text, to_lang):
        try: 
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            url = self.make_url_trans(text, 'en', to_lang)
            response = requests.get(url, verify=False, timeout=TIMEOUT)
            data = response.json()
            response.raise_for_status()  # Raise an exception for HTTP errors
            return data['responseData']['translatedText']
        except Exception as e:
            logger.error(f"[TRANSLATOR] Fail to translate to {to_lang} query: {text}")
            traceback.print_exc()
        
    def make_queries(self, query, original_lang = "en"):
        queries = {}
        queries[original_lang] = query
        for lang in LANGUAGES:
            if lang == original_lang: continue
            queries[lang] = self.translate_using_api(query, lang)
        return queries
        
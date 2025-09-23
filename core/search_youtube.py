import requests
import traceback
import urllib.parse
from core.logger import logger
from config.settings import *
from core.translator import Translator

class YoutubeSearch:
    def __init__(self):
        self.translator = Translator()
    def fetch_video_info(self, videoId):
        try:
            params = {
                "part": "snippet,contentDetails,statistics",
                "id": videoId,
                "key": API_KEY_YOUTUBE
            }
            param_string = urllib.parse.urlencode(params)
            r = requests.get(f"{URL_INFO_VIDEO}?{param_string}", timeout=TIMEOUT)
            if r.ok:
                return r.json()
            else:
                logger.error(f"[YOUTUBE SEARCH] Request error: {r.status_code}")
                traceback.print_exc()
        except Exception as e:
            logger.error(f"[YOUTUBE SEARCH] Failed to fetch information of videos whose id {videoId}: {e}")
            traceback.print_exc()
        return {}
    
    def search(self, query, before = PUBLISHED_FROM, after = PUBLISHED_TO, region_code=""):
        results = []
        
        """
        params = {
            'q': query,
            "part": "snippet",
            "type": "video",
            "key": API_KEY_YOUTUBE
        }
        """

        params = {
            'q': query,
            "part": "snippet",
            "type": "video",
            "order": "date",
            "publishedBefore": before,
            "publishedAfter": after,
            "maxResults": 50,
            "key": API_KEY_YOUTUBE
        }
        
        if region_code != "":
            params["regionCode"] = region_code
        try:
            param_string = urllib.parse.urlencode(params)
            r = requests.get(f"{URL_SEARCH_YOUTUBE}?{param_string}", timeout=TIMEOUT)
            if r.ok:
                items = r.json().get("items", [])
                for item in items:
                    videoId = item.get('id', {}).get('videoId', "")
                    info = self.fetch_video_info(videoId).get("items", [])[0]
                    results.append({
                        "title": info.get("snippet", {}).get("title", ""),
                        "link": f"{URL_LINK_YOUTUBE}{videoId}",
                        "snippet": info.get("snippet", {}).get("description", ""),
                        "vietsub": self.translator.translate_using_api(text=info.get("snippet", {}).get("description", ""))
                    })
            else:
                logger.error(f"[YOUTUBE SEARCH] Request error: {r.status_code}")
                traceback.print_exc()
        except Exception as e:
            logger.error(f"[YOUTUBE SEARCH] Failed to fetch list of videos with query {query}: {e}")
            traceback.print_exc()

        return results

    def search_all(self, query_dict):
        results = []
        if not IS_YOUTUBE:
            return results
        for lang, query in query_dict.items():
            logger.info(f"[YOUTUBE SEARCH] Searching [{lang}] query: {query}")
            results += self.search(query)
        return results
    

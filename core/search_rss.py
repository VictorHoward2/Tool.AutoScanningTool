import feedparser
import html
from datetime import datetime, timedelta, timezone
import cloudscraper
from config.settings import *
from core.translator import Translator
from bs4 import BeautifulSoup

class RSSSearch:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def fetch_recent_posts(self, days=DURATION):
        recent_posts = []
        for rss_url in RSS_URL:
            response = self.scraper.get(rss_url)
            feed = feedparser.parse(response.text)
            duration = datetime.now(timezone.utc) - timedelta(days=days)

            for entry in feed.entries:
                if hasattr(entry, "published_parsed"):
                    pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed"):
                    pub = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                else:
                    continue

                if pub >= duration:
                    recent_posts.append({
                        "title": entry.get("title"),
                        "link": entry.get("link"),
                        "published": pub.isoformat(),
                        "snippet": entry.get("summary", ""),
                        "vietsub": Translator().translate_using_api(text=html.escape(BeautifulSoup(entry.get("summary", ""), "html.parser").get_text()))
                    })

        return recent_posts

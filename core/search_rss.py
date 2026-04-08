import feedparser
import json
from datetime import datetime, timedelta, timezone
import cloudscraper
from config.settings import *


class RSSSearch:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def fetch_recent_posts(self, days=DURATION):
        recent_posts = []
        for rss_url in RSS_URL:
            response = self.scraper.get(rss_url)
            with open("test\\sample.html", "w", encoding="utf-8") as f:
                f.write(response.text)
                
            feed = feedparser.parse(response.text)
            with open("test\\feed.json", "w", encoding="utf-8") as f:
                json.dump(feed, f, ensure_ascii=False, indent=4, default=str)
            duration = datetime.now(timezone.utc) - timedelta(days=days)

            for entry in feed.entries:
                if hasattr(entry, "published_parsed"):
                    pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed"):
                    pub = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                else:
                    continue

                if pub >= duration:
                    recent_posts.append(
                        {
                            "title": entry.get("title"),
                            "link": entry.get("link"),
                            "published": pub.isoformat(),
                            "snippet": entry.get("summary", ""),
                            "image": next((link["href"] for link in entry.get("links", []) if link.get("type").startswith("image/")), None),
                            "readtime": entry.get("readtime", ""),
                            "tags": [tag.get("term", "") for tag in entry.get("tags", [])],
                        }
                    )

        return recent_posts

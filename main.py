from config.settings import *
from core.search_google import GoogleSearch
from core.search_youtube import YoutubeSearch
from core.translator import Translator
from core.content_fetcher import ContentFetcher
from core.ai_processor import AIProcessor
from core.search_rss import RSSSearch
from core.exporter import *
from core.logger import logger

def main():

    logger.info("🚀 [MAIN] Bắt đầu phiên quét mới")
    google_searcher = GoogleSearch()
    youtube_searcher = YoutubeSearch()
    translator = Translator()
    fetcher = ContentFetcher()
    rss_searcher = RSSSearch()
    ai = AIProcessor()

    # Translate query 
    logger.info("[MAIN] Phase 1: Translate query")
    queries = translator.make_queries(QUERY)

    # Search and collect data
    logger.info("[MAIN] Phase 2: Search and collect data")
    index = 1
    if IS_GOOGLE:
        results_google = google_searcher.search_all(queries)
        logger.info(f"[MAIN] Phase 2.{index} Google: {len(results_google)} results.")
        index += 1
    if IS_YOUTUBE:
        results_youtube = youtube_searcher.search_all(queries)
        logger.info(f"[MAIN] Phase 2.{index} Youtube: {len(results_youtube)} results.")
        index += 1
    if IS_RSS:
        results_rss = rss_searcher.fetch_recent_posts()
        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss)} results.")
        index += 1

    # Fetch content
    logger.info("[MAIN] Phase 3: Fetch content")
    index = 1
    if IS_GOOGLE and (IS_SUMMARIZE_GOOGLE or IS_EXTRACT_GOOGLE):
        logger.info(f"[MAIN] Phase 3.{index} Google")
        index += 1
        results_google = fetcher.get_content(results_google)
    if IS_RSS and (IS_SUMMARIZE_RSS or IS_EXTRACT_RSS):
        logger.info(f"[MAIN] Phase 3.{index} RSS")
        index += 1
        results_rss = fetcher.get_content(results_rss)

    # AI process
    logger.info("[MAIN] Phase 4: AI process")
    index = 1
    if IS_GOOGLE and (IS_SUMMARIZE_GOOGLE or IS_EXTRACT_GOOGLE):
        logger.info(f"[MAIN] Phase 4.{index}: AI process for Google")
        index += 1
        results_google = ai.process_ai_article(results_google, TOPIC_KEYWORD, GOOGLE)
    if IS_RSS and (IS_SUMMARIZE_RSS or IS_EXTRACT_RSS):
        logger.info(f"[MAIN] Phase 4.{index}: AI process for RSS")
        index += 1
        results_rss = ai.process_ai_article(results_rss, TOPIC_KEYWORD, RSS)
    if IS_YOUTUBE and (IS_SUMMARIZE_YOUTUBE or IS_EXTRACT_YOUTUBE):
        logger.info(f"[MAIN] Phase 4.{index}: AI process for Youtube")
        index += 1
        results_youtube = ai.process_ai_video(results_youtube, TOPIC_KEYWORD)

    # Export
    logger.info("[MAIN] Phase 5: Export")
    if IS_GOOGLE:
        export_to_excel(results_google, GOOGLE)
        export_to_html(results_google, GOOGLE)
    if IS_YOUTUBE:
        export_to_excel(results_youtube, YOUTUBE)
        export_to_html(results_youtube, YOUTUBE)
    if IS_RSS:
        export_to_excel(results_rss, RSS)
        export_to_html(results_rss, RSS)

    logger.info("[MAIN] Scan completed!")

if __name__ == "__main__":
    main()

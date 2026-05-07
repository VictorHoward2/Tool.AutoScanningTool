from config.settings import *
from core.search_google import GoogleSearch
from core.search_youtube import YoutubeSearch
from core.translator import Translator
from core.content_fetcher import ContentFetcher
from core.ai_processor import AIProcessor
from core.search_rss import RSSSearch
from core.exporter import *
from core.logger import logger
import json

def main():

    logger.info("[MAIN] Bắt đầu phiên quét mới")
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
        results_rss_global_infor = rss_searcher.fetch_recent_posts(source=RSS_GLOBAL_INFOR)
        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss_global_infor)} results for Global Information.")
        results_rss_new_feature_samsung = rss_searcher.fetch_recent_posts(source=RSS_NEW_FEATURES_SAMSUNG)
        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss_new_feature_samsung)} results for New Feature Samsung.")
        results_rss_new_feature_iphone = rss_searcher.fetch_recent_posts(source=RSS_NEW_FEATURES_IPHONE)
        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss_new_feature_iphone)} results for New Feature iPhone.")
        results_rss_new_feature_china = rss_searcher.fetch_recent_posts(source=RSS_NEW_FEATURES_CHINA)
        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss_new_feature_china)} results for New Feature China.")
        results_rss_android_issues = rss_searcher.fetch_recent_posts(source=RSS_ANDROID_ISSUES)
        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss_android_issues)} results for Hot Android Issues.")
        results_rss_patent_trend = rss_searcher.fetch_recent_posts(source=RSS_PATENT_TREND)
        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss_patent_trend)} results for Security Patent Trend.")

        logger.info(f"[MAIN] Phase 2.{index} RSS: {len(results_rss_global_infor) + len(results_rss_new_feature_samsung) + len(results_rss_new_feature_iphone) + len(results_rss_new_feature_china)+ len(results_rss_android_issues) + len(results_rss_patent_trend) } results.")
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
        results_rss_global_infor = fetcher.get_content(results_rss_global_infor)
        results_rss_new_feature_samsung = fetcher.get_content(results_rss_new_feature_samsung)
        results_rss_new_feature_iphone = fetcher.get_content(results_rss_new_feature_iphone)
        results_rss_new_feature_china = fetcher.get_content(results_rss_new_feature_china)
        results_rss_android_issues = fetcher.get_content(results_rss_android_issues)
        results_rss_patent_trend = fetcher.get_content(results_rss_patent_trend)

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
        results_rss_global_infor = ai.process_ai_article(results_rss_global_infor, TOPIC_KEYWORD, RSS)
        results_rss_new_feature_samsung = ai.process_ai_article(results_rss_new_feature_samsung, TOPIC_KEYWORD, RSS)
        results_rss_new_feature_iphone = ai.process_ai_article(results_rss_new_feature_iphone, TOPIC_KEYWORD, RSS)
        results_rss_new_feature_china = ai.process_ai_article(results_rss_new_feature_china, TOPIC_KEYWORD, RSS)
        results_rss_android_issues = ai.process_ai_article(results_rss_android_issues, TOPIC_KEYWORD, RSS)
        results_rss_patent_trend = ai.process_ai_article(results_rss_patent_trend, TOPIC_KEYWORD, RSS)

    if IS_YOUTUBE and (IS_SUMMARIZE_YOUTUBE or IS_EXTRACT_YOUTUBE):
        logger.info(f"[MAIN] Phase 4.{index}: AI process for Youtube")
        index += 1
        results_youtube = ai.process_ai_video(results_youtube, TOPIC_KEYWORD)

    # Export
    logger.info("[MAIN] Phase 5: Export")
    if IS_GOOGLE:
        export_to_excel(results_google, GOOGLE)
        export_to_html_vi(results_google, GOOGLE)
    if IS_YOUTUBE:
        export_to_excel(results_youtube, YOUTUBE)
        export_to_html_vi(results_youtube, YOUTUBE)
    if IS_RSS:
        with open("test\\sample.json", "w", encoding="utf-8") as f:
            json.dump(results_rss_global_infor, f, ensure_ascii=False, indent=4)
        export_full_security_report_html(
            global_information_data=results_rss_global_infor,
            service=RSS,
            new_features_samsung_data=results_rss_new_feature_samsung,
            new_features_iphone_data=results_rss_new_feature_iphone,
            new_features_china_data=results_rss_new_feature_china,
            hot_android_issues_data=results_rss_android_issues,
            patent_trend_data=results_rss_patent_trend,
            lang="bilingual",
        )

    logger.info("[MAIN] Scan completed!")

if __name__ == "__main__":
    main()

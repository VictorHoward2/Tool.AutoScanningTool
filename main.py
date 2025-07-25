from config.settings import QUERY, KEYWORDS, OUTPUT_PATH
from core.search_google import GoogleSearch
from core.search_youtube import YoutubeSearch
from core.translator import Translator
from core.content_fetcher import ContentFetcher
from core.ai_processor import AIProcessor
from core.exporter import export_to_excel
from core.logger import logger

def main():

    logger.info("🚀 [MAIN] Bắt đầu phiên quét mới")
    google_searcher = GoogleSearch()
    youtube_searcher = YoutubeSearch()
    translator = Translator()
    fetcher = ContentFetcher()
    ai = AIProcessor()

    # Translate query 
    logger.info("[MAIN] Giai đoạn 1: Translate query")
    queries = translator.make_queries(QUERY)

    # Search and collect data
    logger.info("[MAIN] Giai đoạn 2: Search and collect data")
    results_google = google_searcher.search_all(queries)
    logger.info(f"[MAIN] Google: {len(results_google)} kết quả.")
    results_youtube = youtube_searcher.search_all(queries)
    logger.info(f"[MAIN] Youtube: {len(results_youtube)} kết quả.")

    # Fetch content
    logger.info("[MAIN] Giai đoạn 3: Fetch content")
    results_google = fetcher.get_content(results_google)

    # AI process
    logger.info("[MAIN] Giai đoạn 4: AI process")
    logger.info("[MAIN] Giai đoạn 4.1: AI process for Google")
    results_google = ai.process_ai_google(results_google, KEYWORDS)
    logger.info("[MAIN] Giai đoạn 4.2: AI process for Youtube")
    results_youtube = ai.process_ai_youtube(results_youtube, KEYWORDS)

    # Export
    logger.info("[MAIN] Giai đoạn 5: Export")
    export_to_excel(results_google, "Google")
    export_to_excel(results_youtube, "Youtube")

    logger.info("[MAIN] Quá trình scan hoàn thành!")

if __name__ == "__main__":
    main()

from config.settings import QUERY, KEYWORDS, OUTPUT_PATH
from core.search_google import GoogleSearch
from core.translator import Translator
from core.content_fetcher import ContentFetcher
from core.ai_processor import AIProcessor
from core.exporter import export_to_excel
from core.logger import logger

def main():

    logger.info("🚀 [MAIN] Bắt đầu phiên quét mới")
    searcher = GoogleSearch()
    translator = Translator()
    fetcher = ContentFetcher()
    ai = AIProcessor()

    # Translate query 
    logger.info("[MAIN] Giai đoạn 1: Translate query")
    queries = translator.make_queries(QUERY)

    # Search and collect data
    logger.info("[MAIN] Giai đoạn 2: Search and collect data")
    results = searcher.search_all(queries)

    # Fetch content
    logger.info("[MAIN] Giai đoạn 3: Fetch content")
    results = fetcher.get_content(results)

    # AI process
    logger.info("[MAIN] Giai đoạn 4: AI process")
    results = ai.process_all(results, KEYWORDS)

    # Export
    logger.info("[MAIN] Giai đoạn 5: Export")
    export_to_excel(results)

    logger.info("[MAIN] Quá trình scan hoàn thành!")

if __name__ == "__main__":
    main()

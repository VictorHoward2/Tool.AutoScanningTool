from config.settings import QUERY, KEYWORDS, OUTPUT_PATH
from core.search_google import GoogleSearch
from core.translator import Translator
from core.content_fetcher import ContentFetcher
from core.ai_processor import AIProcessor
from core.exporter import export_to_excel
from core.logger import logger

def main():
    logger.info("🚀 Bắt đầu phiên quét mới")
    
    searcher = GoogleSearch()
    translator = Translator()
    fetcher = ContentFetcher()
    ai = AIProcessor()

    # Translate keywords
    queries = translator.make_queries(QUERY)

    # Search and collect data
    results = searcher.search_all(queries)

    # Fetch content
    results = fetcher.get_content(results)

    # AI process
    results = ai.process_all(results, KEYWORDS)

    # Export
    export_to_excel(results)

    logger.info("✅ Quét hoàn tất!")

if __name__ == "__main__":
    main()

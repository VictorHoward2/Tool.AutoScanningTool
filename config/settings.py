import os
from datetime import datetime
from utils.time_utils import get_previous_date

# Modules settings
IS_TRANSLATE_QUERY = False

IS_GOOGLE = False
IS_SUMMARIZE_GOOGLE = True
IS_EXTRACT_GOOGLE = True

IS_YOUTUBE = False
IS_SUMMARIZE_YOUTUBE = True
IS_EXTRACT_YOUTUBE = True

IS_RSS = True
IS_SUMMARIZE_RSS = True
IS_EXTRACT_RSS = False

GEMINI_FOR_TRANSLATE = True
GEMINI_FOR_GOOGLE = True
GEMINI_FOR_YOUTUBE = True
GEMINI_FOR_RSS = True

# Scan settings
TOPIC_KEYWORD = "Network Unlock - dịch vụ gỡ khóa mạng (mở SIM lock) trên điện thoại để thiết bị có thể sử dụng SIM của bất kỳ nhà mạng nào thay vì bị khóa với một nhà mạng cố định. Đặc biệt quan tâm Network Unlock cho các điện thoại Samsung."  # các thông tin muốn trích xuất
QUERY = "Network Unlock Samsung"  # default: EN
DEMANDS = [
    "Tên thiết bị hoặc tên dòng máy Samsung liên quan đến từ khóa, càng nhiều thông tin chi tiết càng tốt",
    "Tên công cụ (tool) hoặc tên phần mềm hoặc phương thức được dùng để thực hiện",
    "Cách thức thực hiện (hướng dẫn ngắn gọn nếu có)",
    "Điều kiện cần thiết hoặc lưu ý khi thực hiện",
    "Bất kỳ thông tin bổ sung hữu ích nào liên quan đến từ khóa",
]
# DEMANDS = ["Bất kỳ thông tin bổ sung hữu ích nào liên quan đến từ khóa chủ đề"]

# General settings
DURATION = 7  # đơn vị ngày - ví dụ: 30 -> quét 30 ngày gần nhất
TODAY = str(datetime.today().date())
NOW = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
PUBLISHED_FROM = get_previous_date(day=DURATION)
PUBLISHED_TO = get_previous_date(day=0)
OUTPUT_PATH = os.path.join(os.getcwd(), "data/output")
LOG_DIR = os.path.join(os.getcwd(), "data/logs")

# Translate settings
LANGUAGES = ["en", "es", "fr", "de", "pt", "th"]
TIMEOUT = 90

# AI settings
DEFAULT_MODEL_GEMINI = "gemini-2.5-flash"
DEFAULT_MODEL_OLLAMA = "gemma3:270m"
# AI_MODELS = ["gemma3:1b", "granite3.2:2b", "qwen3:0.6b", "deepseek-r1:1.5b", "llama3.2:1b"]
AI_MODELS = ["llama3.1:8b"]
NUMBER_WORDS_SUMMARIZE = 200

# Google
API_KEY_GOOGLE = "AIzaSyDBUcnY9yG5ZRK0WzhJQLuGW-j6BOcwBaY"
URL_SEARCH_GOOGLE = "https://www.googleapis.com/customsearch/v1"
SEARCH_ENGINE_ID_GOOGLE = "f3dc1d67c30ed47dc"
RESULTS_PER_REQUEST_GOOGLE = 3  # Google giới hạn tối đa 10/lần
NUM_RESULTS_GOOGLE = 10  # Tổng số kết quả/query

# Youtube
API_KEY_YOUTUBE = "AIzaSyCCNntXp6zMa9dV-RLVC-dhp2ipv6O9Vqo"
URL_SEARCH_YOUTUBE = "https://www.googleapis.com/youtube/v3/search"
URL_INFO_VIDEO = "https://www.googleapis.com/youtube/v3/videos"
URL_LINK_YOUTUBE = "https://www.youtube.com/watch?v="

# RSS
# RSS_URL = ["https://unit42.paloaltonetworks.com/feed/",
#            "https://www.keysight.com/blogs/rss/feed.xml",
#            "https://www.infostealers.com/learn-info-stealers/feed/",
#            "https://feeds.feedburner.com/TheHackersNews",
#            "https://www.securityweek.com/feed/",
#            "https://cyberscoop.com/feed/",
#            "https://www.bleepingcomputer.com/feed/"]  # Thêm nhiều RSS feed nếu cần

RSS_URL = ["https://unit42.paloaltonetworks.com/feed/", "https://www.securityweek.com/feed/", "https://www.bleepingcomputer.com/feed/"]  # Thêm nhiều RSS feed nếu cần

# CONSTANTS
GOOGLE = "Google"
YOUTUBE = "Youtube"
RSS = "RSS"

GEMINI_API_KEYS = [
    "AIzaSyAEl2kVpNIz0u9ExJbpjk3gqJxHS7gSXTk",
    "AIzaSyAugYbgc1xMqYYGW2NX7ICbehUPJdaed6g",
    "AIzaSyBf-eIa26TY9GpUxsssCQ693kEsDkYjYY0",
    "AIzaSyBJ9C7S1BnXi6gORnq19HiS8WhNo7-6Jk0",
    "AIzaSyBw423k9HuUhaHbgzkRt09nEw9__ayer6g",
    "AIzaSyD0YhhsFjW9vVMYIMxMYpENWZeBkwORaDQ",
    "AIzaSyC4NhspuItFwvI1U7JJfmQIEJtwqN6r1EE",
    "AIzaSyDiaVjhw_3hm6gr4IwRjRJIbQjjgERh4eI",
    "AIzaSyD2hbKvhp0TRHJyV0pc2xXHwz2meNJkUAc",
    "AIzaSyBREMlV8_oZUjPOTRl2siF4Ime2QQdN1eE",
    "AIzaSyCvIColbM8PiY9EQ6GE6EoQtHv5gbL2MoM",
    "AIzaSyCMINjA10a13mDsUs4k2LemwPemC-p_QDU",
]

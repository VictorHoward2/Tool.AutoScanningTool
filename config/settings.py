import os
from datetime import datetime
from utils.time_utils import get_previous_date

# General 
TODAY = str(datetime.today().date())
PUBLISHED_FROM = get_previous_date(day=7)
PUBLISHED_TO = get_previous_date(day=0)
OUTPUT_PATH = os.path.join(os.getcwd(), 'data/output')
LOG_DIR = os.path.join(os.getcwd(), 'data/logs')
LANGUAGES = ["en", "es", "fr", "de", "pt", "th"]
TIMEOUT = 10
DEFAULT_MODEL = "gemma3:1b"
# AI_MODELS = ["gemma3:1b", "granite3.2:2b", "qwen3:0.6b", "deepseek-r1:1.5b", "llama3.2:1b"]
AI_MODELS = ["gemma3:1b"]
NUMBER_WORDS_SUMMARIZE = 50
KEYWORDS = "Network Unlock of Samsung smartphones" # các thông tin muốn trích xuất
QUERY = 'network unlock "samsung"'  #default: EN

# Google
API_KEY_GOOGLE = "AIzaSyDBUcnY9yG5ZRK0WzhJQLuGW-j6BOcwBaY"
URL_SEARCH_GOOGLE = "https://www.googleapis.com/customsearch/v1"
SEARCH_ENGINE_ID_GOOGLE = "f3dc1d67c30ed47dc"
RESULTS_PER_REQUEST_GOOGLE = 3 # Google giới hạn tối đa 10/lần
NUM_RESULTS_GOOGLE = 15 # Tổng số kết quả/query

# Youtube
API_KEY_YOUTUBE = "AIzaSyCCNntXp6zMa9dV-RLVC-dhp2ipv6O9Vqo"
URL_SEARCH_YOUTUBE = "https://www.googleapis.com/youtube/v3/search"
URL_INFO_VIDEO = "https://www.googleapis.com/youtube/v3/videos"
URL_LINK_YOUTUBE = "https://www.youtube.com/watch?v="












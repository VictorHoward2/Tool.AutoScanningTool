import os
from datetime import datetime

TODAY = str(datetime.today().date())
API_KEY_GOOGLE = "AIzaSyDBUcnY9yG5ZRK0WzhJQLuGW-j6BOcwBaY"
SEARCH_ENGINE_ID = "f3dc1d67c30ed47dc"
OUTPUT_PATH = os.path.join(os.getcwd(), 'data/output')
LOG_DIR = os.path.join(os.getcwd(), 'data/logs')
DEFAULT_MODEL = "gemma3:1b"
LANGUAGES = ["en", "es", "fr", "de", "pt", "th"]
RESULTS_PER_REQUEST = 3 # Google giới hạn tối đa 10/lần
NUM_RESULTS = 15

KEYWORDS = "Network Unlock of Samsung smartphones"
QUERY = 'network unlock "samsung"'  #default: EN



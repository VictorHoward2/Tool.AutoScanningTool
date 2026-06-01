"""Mẫu cấu hình an toàn để commit: không chứa API key / token / email thật.

Cách dùng:
- Sao chép thành `settings.py` (hoặc file riêng) và điền giá trị, **không** commit `settings.py` nếu có secret; hoặc
- Giữ sample và export biến môi trường (GAUSS_*, API_KEY_GOOGLE, API_KEY_YOUTUBE, SEARCH_ENGINE_ID_GOOGLE,
  GEMINI_API_KEYS dạng `key1,key2`, …) trước khi chạy.

Tham chiếu cấu trúc đầy đủ: `config/settings.py` (file local của bạn).
"""

import os
from datetime import datetime

from utils.time_utils import get_previous_date

# Modules settings
IS_TRANSLATE_QUERY = False
IS_TEST_AI_PROCESS = True

IS_GOOGLE = False
IS_SUMMARIZE_GOOGLE = True
IS_EXTRACT_GOOGLE = True

IS_YOUTUBE = False
IS_SUMMARIZE_YOUTUBE = True
IS_EXTRACT_YOUTUBE = True

IS_RSS = True
IS_SUMMARIZE_RSS = True
IS_EXTRACT_RSS = False

# Chuẩn hóa tag RSS bằng AI (mặc định tắt; Phase 3–4 RSS chạy khi bật dù tắt summarize/extract)
IS_NORMALIZE_TAGS_RSS = False
TAGS_NORMALIZE_MAX = 8

GEMINI_FOR_TRANSLATE = False
GEMINI_FOR_GOOGLE = False
GEMINI_FOR_YOUTUBE = False
GEMINI_FOR_RSS = False

GAUSS_FOR_TRANSLATE = True
GAUSS_FOR_GOOGLE = True
GAUSS_FOR_YOUTUBE = True
GAUSS_FOR_RSS = True

# Gauss: chỉ qua env (không hardcode URL nội bộ hay JWT trong repo)
GAUSS_API_BASE_URL = os.getenv("GAUSS_API_BASE_URL", "")
GAUSS_X_GENERATIVE_AI_CLIENT = os.getenv("GAUSS_X_GENERATIVE_AI_CLIENT", "")
GAUSS_X_OPENAPI_TOKEN = os.getenv("GAUSS_X_OPENAPI_TOKEN", "")  # thường có dạng "Bearer ..."
GAUSS_X_GENERATIVE_AI_USER_EMAIL = os.getenv("GAUSS_X_GENERATIVE_AI_USER_EMAIL", "")
DEFAULT_MODEL_GAUSS = os.getenv("DEFAULT_MODEL_GAUSS", "")
GAUSS_API_DELAY = 20  # seconds
GAUSS_MAX_RETRIES = 6
GAUSS_BACKOFF_FACTOR = 2

# Scan settings (vi du trung tinh — thay bang chu de that trong file local)
TOPIC_KEYWORD = (
    "Vi du: thong tin an ninh mang va cap nhat phan mem thiet bi di dong (thay noi dung khi dung that)."
)
QUERY = "mobile security example"
DEMANDS = [
    "Ten thiet bi hoac ten dong may lien quan den tu khoa, cang nhieu thong tin chi tiet cang tot",
    "Ten cong cu (tool) hoac ten phan mem hoac phuong thuc duoc dung de thuc hien",
    "Cach thuc thuc hien (huong dan ngan gon neu co)",
    "Dieu kien can thiet hoac luu y khi thuc hien",
    "Bat ky thong tin bo sung huu ich nao lien quan den tu khoa",
]
# DEMANDS = ["Bat ky thong tin bo sung huu ich nao lien quan den tu khoa chu de"]

# General settings
DURATION = 30  # don vi ngay - vi du: 30 -> quet 30 ngay gan nhat
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
DEFAULT_MODEL_OLLAMA = "llama3.1:8b"
# AI_MODELS = ["gemma3:1b", "granite3.2:2b", "qwen3:0.6b", "deepseek-r1:1.5b", "llama3.2:1b"]
AI_MODELS = ["llama3.1:8b"]
NUMBER_WORDS_SUMMARIZE = 200

# Google (API key / engine id qua env)
API_KEY_GOOGLE = os.getenv("API_KEY_GOOGLE", "")
URL_SEARCH_GOOGLE = "https://www.googleapis.com/customsearch/v1"
SEARCH_ENGINE_ID_GOOGLE = os.getenv("SEARCH_ENGINE_ID_GOOGLE", "")
RESULTS_PER_REQUEST_GOOGLE = 3  # Google gioi han toi da 10/lan
NUM_RESULTS_GOOGLE = 10  # Tong so ket qua/query

# Youtube
API_KEY_YOUTUBE = os.getenv("API_KEY_YOUTUBE", "")
URL_SEARCH_YOUTUBE = "https://www.googleapis.com/youtube/v3/search"
URL_INFO_VIDEO = "https://www.googleapis.com/youtube/v3/videos"
URL_LINK_YOUTUBE = "https://www.youtube.com/watch?v="

# RSS (URL cong khai mau; bo sung feed trong file local neu can)
# RSS_GLOBAL_INFOR = ["https://unit42.paloaltonetworks.com/feed/",
#            "https://www.keysight.com/blogs/rss/feed.xml",
#            "https://www.infostealers.com/learn-info-stealers/feed/",
#            "https://feeds.feedburner.com/TheHackersNews",
#            "https://www.securityweek.com/feed/",
#            "https://cyberscoop.com/feed/",
#            "https://www.bleepingcomputer.com/feed/"]  # Them nhieu RSS feed neu can
# RSS_GLOBAL_INFOR = ["https://unit42.paloaltonetworks.com/feed/"]

RSS_GLOBAL_INFOR = [
    "https://unit42.paloaltonetworks.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.securityweek.com/feed/",
    "https://cyberscoop.com/feed/",
]
RSS_NEW_FEATURES_SAMSUNG = ["https://news.samsung.com/global/feed"]
RSS_NEW_FEATURES_IPHONE = [
    "https://www.apple.com/newsroom/rss-feed.rss",
    "https://applemagazine.com/feed/",
]
RSS_NEW_FEATURES_CHINA = [
    "https://www.huaweicentral.com/feed/",
    "https://xiaomitime.com/feed/",
    "https://9to5google.com/guides/oppo/feed/",
]
RSS_ANDROID_ISSUES = [
    "https://www.infostealers.com/learn-info-stealers/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.securityweek.com/feed/",
    "https://cyberscoop.com/feed/",
]
RSS_PATENT_TREND = ["https://www.computerworld.com/security/feed/"]

# RSS section routing profiles
RSS_ROUTING_DEFAULT_TARGET = "global_information"

RSS_ROUTING_PROFILES = {
    "new_features_samsung": {
        "section_id": "new_features_samsung",
        "display_name": "New Features Samsung",
        "ai_only": True,
        "topic_key_for_ai": (
            "Tin tức tính năng mới trên smartphone Samsung: cập nhật phần mềm, "
            "One UI, AI feature, bảo mật thiết bị, camera, hiệu năng, pin và trải nghiệm người dùng. "
            "Không bao gồm tin sự kiện, giải thưởng, hợp tác truyền thông hoặc hoạt động marketing."
        ),
        "positive_keywords": [
            "one ui",
            "feature",
            "new feature",
            "update",
            "rollout",
            "release",
            "beta",
            "security patch",
            "camera feature",
            "ai feature",
            "firmware",
            "android update",
        ],
        "negative_keywords": [
            "event",
            "conference",
            "award",
            "tournament",
            "esports",
            "partnership",
            "sponsorship",
            "competition",
            "campaign",
            "celebration",
        ],
        "fallback_target_section": RSS_ROUTING_DEFAULT_TARGET,
        "uncertain_policy": "keep",
    },
    "new_features_iphone": {
        "section_id": "new_features_iphone",
        "display_name": "New Features iPhone",
        "ai_only": True,
        "topic_key_for_ai": (
            "Tin tức tính năng mới trên iPhone/iOS: cập nhật iOS, tính năng bảo mật, "
            "quyền riêng tư, AI feature, camera, pin và trải nghiệm hệ điều hành. "
            "Không bao gồm tin sự kiện, giải thưởng hoặc hoạt động marketing."
        ),
        "positive_keywords": [
            "ios",
            "iphone",
            "feature",
            "new feature",
            "update",
            "release",
            "beta",
            "privacy",
            "security update",
            "apple intelligence",
            "camera feature",
        ],
        "negative_keywords": [
            "event",
            "conference",
            "award",
            "tournament",
            "esports",
            "partnership",
            "sponsorship",
            "competition",
            "campaign",
            "celebration",
        ],
        "fallback_target_section": RSS_ROUTING_DEFAULT_TARGET,
        "uncertain_policy": "keep",
    },
    "new_features_china": {
        "section_id": "new_features_china",
        "display_name": "New Features China Brands",
        "ai_only": True,
        "topic_key_for_ai": (
            "Tin tức tính năng mới trên điện thoại của các hãng Trung Quốc (Huawei, Xiaomi, Oppo, Vivo): "
            "cập nhật hệ điều hành, tính năng AI, bảo mật, camera, pin, tối ưu hiệu năng. "
            "Không bao gồm tin sự kiện, giải thưởng hoặc hoạt động marketing."
        ),
        "positive_keywords": [
            "hyperos",
            "harmonyos",
            "coloros",
            "feature",
            "new feature",
            "update",
            "release",
            "beta",
            "security patch",
            "ai feature",
            "camera feature",
        ],
        "negative_keywords": [
            "event",
            "conference",
            "award",
            "tournament",
            "esports",
            "partnership",
            "sponsorship",
            "competition",
            "campaign",
            "celebration",
        ],
        "fallback_target_section": RSS_ROUTING_DEFAULT_TARGET,
        "uncertain_policy": "keep",
    },
}

# RSS_GLOBAL_INFOR = ["https://unit42.paloaltonetworks.com/feed/", "https://www.computerworld.com/security/feed/"]
# RSS_NEW_FEATURES_SAMSUNG = ["https://news.samsung.com/global/feed"]
# RSS_NEW_FEATURES_IPHONE = ["https://applemagazine.com/feed/"]
# RSS_NEW_FEATURES_CHINA = ["https://www.huaweicentral.com/feed/"]
# RSS_ANDROID_ISSUES = ["https://feeds.feedburner.com/TheHackersNews"]
# RSS_PATENT_TREND = ["https://www.computerworld.com/security/feed/"]

# CONSTANTS
GOOGLE = "Google"
YOUTUBE = "Youtube"
RSS = "RSS"

# Nhieu key: GEMINI_API_KEYS="key1,key2" (khong dau cach thua sau dau phay cung duoc, da strip)
_gemini_raw = os.getenv("GEMINI_API_KEYS", "")
GEMINI_API_KEYS = [k.strip() for k in _gemini_raw.split(",") if k.strip()]

MIN_HEIGHT_IMG = 550
MIN_WIDTH_IMG = 400

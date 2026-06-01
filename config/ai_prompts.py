"""
Prompt templates for AIProcessor. No imports from config.settings to avoid circular imports.
Callers pass values like num_words, demands_text, or formatted article blocks.
"""

from __future__ import annotations

import json
from typing import Any, Iterable, Mapping

# =============================================================================
# 30 CANONICAL TAGS - Hệ thống tags chuẩn hóa cho security news aggregation
# =============================================================================

# Device Tags (6 tags) - Chọn ĐÚNG 1
TAG_DEVICE_CANONICAL = (
    "Smartphone",      # Includes foldable phones
    "Computer",        # PC, laptop, desktop, workstation
    "Server & Cloud",  # Servers, cloud infrastructure, data centers
    "IoT Device",      # Smart home, connected devices, automotive
    "Wearable",        # Smartwatches, fitness trackers, AR/VR
    "Multiple Devices", # Article covers 2+ device categories
    "Non-categorized Devices",    # Non-categorized devices, peripherals, accessories"
)

# Threat Type Tags (8 tags) - Chọn tối đa 2
TAG_THREAT_CANONICAL = (
    "Malware",         # Virus, trojan, spyware, mobile malware
    "Ransomware",      # Ransomware attacks
    "Phishing",        # Phishing, social engineering
    "Data Breach",     # Data leaks, credential theft
    "Zero-Day Exploit", # Unpatched vulnerabilities
    "APT Attack",      # Advanced persistent threats, nation-state
    "Network Attack",  # DDoS, MITM, web attacks
    "Supply Chain Attack", # Software supply chain attacks
)

# Topic Tags (8 tags) - Chọn tối đa 2
TAG_TOPIC_CANONICAL = (
    "Vulnerability",   # CVE disclosures, security flaws
    "Security Update", # Patches, updates, patch management
    "Privacy Concern", # Data collection, tracking, privacy issues
    "Cybercrime",      # Hacker arrests, cyber gangs, fraud
    "Security Research", # New findings, threat intelligence
    "Policy & Regulation", # Laws, compliance, GDPR
    "AI",     # AI vulnerabilities, deepfakes, AI threats
    "Cloud Security",  # Cloud breaches, misconfigurations
)

# Brand Tags (8 tags) - Chọn tối đa 2
TAG_BRAND_CANONICAL = (
    "Samsung",         # Samsung products only
    "Apple",           # iPhone, iPad, Mac, iOS, Apple Watch
    "Google",          # Pixel, Google services
    "Microsoft",       # Windows, Surface, Azure, Office
    "Android",         # General Android (non-brand specific)
    "iOS",             # iOS-specific news
    "Windows",         # Windows-specific news
    "China Brand",     # Huawei, Xiaomi, OPPO, Vivo, etc.
    "Github",
)

# All canonical tags combined for validation
ALL_CANONICAL_TAGS = (
    TAG_DEVICE_CANONICAL + TAG_THREAT_CANONICAL + 
    TAG_TOPIC_CANONICAL + TAG_BRAND_CANONICAL
)
TAG_CANONICAL_SET = set(ALL_CANONICAL_TAGS)  # For O(1) lookup


def build_overview_articles_block(results: Iterable[Mapping[str, Any]]) -> str:
    lines: list[str] = []
    for idx, item in enumerate(results, 1):
        lines.append(
            f"[{idx}] {item.get('title', '')}\n {item.get('snippet', '')}\n {item.get('link', '')}\n\n"
        )
    return "".join(lines)


def summarize_overview_system_vi(num_words: int) -> str:
    return (
        f"Bạn là một chuyên gia phân tích và tóm tắt văn bản. "
        f"Nhiệm vụ của bạn: hãy viết một bản báo cáo tổng quát bằng tiếng Việt, "
        f"dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
        f"Kết quả nên được viết dưới dạng một đoạn văn liên tục. Không viết dạng file markdown."
    )


def summarize_overview_user_vi(all_content: str) -> str:
    return f"Nội dung: {all_content}\n\nHãy tóm tắt nội dung trên cho tôi."


def summarize_overview_system_en(num_words: int) -> str:
    return (
        f"You are an expert in analyzing and summarizing text. "
        f"Your task: write a general report in English, "
        f"easy to understand, full of main ideas, avoid rambling, maximum {num_words} words. "
        f"The results should be written as a continuous paragraph. Do not write in markdown file."
    )


def summarize_overview_user_en(all_content: str) -> str:
    return f"Content: {all_content}\n\nPlease summarize the above content for me."


def summarize_content_system_vi(num_words: int) -> str:
    return (
        f"Bạn là một chuyên gia phân tích và tóm tắt văn bản. "
        f"Nhiệm vụ của bạn: hãy viết một bản tóm tắt bằng tiếng Việt, "
        f"ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
        f"Chỉ sử dụng thông tin có trong nội dung được cung cấp, không suy đoán hay bổ sung ngoài. "
        f"Kết quả nên được viết dưới dạng một đoạn văn liên tục."
    )


def summarize_content_user_vi(title: str, snippet: str, link: str, content: str) -> str:
    return (
        f"Tiêu đề: {title}\n"
        f"Đoạn trích: {snippet}\n"
        f"Link: {link}\n"
        f"Nội dung: {content}\n\n"
        f"Hãy tóm tắt nội dung trang web trên cho tôi."
    )


def summarize_content_system_en(num_words: int) -> str:
    return (
        f"You are an expert in analyzing and summarizing text. "
        f"Your task: write a summary in English, "
        f"concise, easy to understand, full of main ideas, avoid rambling, maximum {num_words} words. "
        f"Use only information in the provided content, do not speculate or add anything else. "
        f"The result should be written in the form of a continuous paragraph."
    )


def summarize_content_user_en(title: str, snippet: str, link: str, content: str) -> str:
    return (
        f"Title: {title}\n"
        f"Snippet: {snippet}\n"
        f"Link: {link}\n"
        f"Content: {content}\n\n"
        f"Please summarize the content of the above website for me."
    )


def summarize_content_ollama_vi(
    title: str, snippet: str, link: str, content: str, num_words: int
) -> str:
    return (
        f"Tiêu đề: {title}\n"
        f"Đoạn trích: {snippet}\n"
        f"Link: {link}\n"
        f"Nội dung: {content}\n\n"
        f"Bạn là một chuyên gia phân tích và tóm tắt văn bản. "
        f"Tôi đã cung cấp cho bạn tiêu đề, đoạn trích, link và toàn bộ nội dung (text) của một trang web ở trên. "
        f"Nhiệm vụ của bạn: hãy viết một bản tóm tắt bằng tiếng Việt, "
        f"ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
        f"Chỉ sử dụng thông tin có trong nội dung được cung cấp, không suy đoán hay bổ sung ngoài. "
        f"Kết quả nên được viết dưới dạng một đoạn văn liên tục."
    )


def summarize_content_ollama_en(
    title: str, snippet: str, link: str, content: str, num_words: int
) -> str:
    return (
        f"Title: {title}\n"
        f"Snippet: {snippet}\n"
        f"Link: {link}\n"
        f"Content: {content}\n\n"
        f"You are an expert in analyzing and summarizing text. "
        f"I have provided you with the title, snippet, link and the entire content (text) of a website above. "
        f"Your task: write a summary in English, "
        f"concise, easy to understand, full of main ideas, avoid rambling, maximum {num_words} words. "
        f"Only use the information in the provided content, do not speculate or add anything else. "
        f"The result should be written in the form of a continuous paragraph."
    )


def summarize_video_system_vi(num_words: int) -> str:
    return (
        f"Bạn là một chuyên gia phân tích và tóm tắt nội dung video. "
        f"Bạn sẽ được cung cấp tiêu đề, mô tả và link của một video YouTube để tóm tắt lại các thông tin. "
        f"Mô tả có thể được viết bằng nhiều ngôn ngữ khác nhau. "
        f"Nhiệm vụ của bạn: hãy dịch mô tả sang tiếng Việt và viết một bản tóm tắt bằng tiếng Việt "
        f"dựa trên những thông tin được cung cấp. "
        f"Viết ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
        f"Chỉ sử dụng thông tin có trong dữ liệu cung cấp. "
        f"Kết quả nên ở dạng một đoạn văn liên tục."
    )


def summarize_video_user_vi(title: str, snippet: str, link: str) -> str:
    return (
        f"Tiêu đề video: {title}\n"
        f"Mô tả video: {snippet}\n"
        f"Link video: {link}\n\n"
        f"Hãy tóm tắt nội dung video trên cho tôi."
    )


def summarize_video_system_en(num_words: int) -> str:
    return (
        f"You are an expert in analyzing and summarizing video content. "
        f"You will be provided with the title, description, and link of a YouTube video to summarize the information. "
        f"The description can be written in many different languages. "
        f"Your task: translate the description into English and write a summary in English "
        f"based on the information provided. "
        f"Write concisely, easy to understand, complete with main ideas, avoid rambling, maximum {num_words} words. "
        f"Use only information in the data provided. "
        f"The result should be in the form of a continuous paragraph."
    )


def summarize_video_user_en(title: str, snippet: str, link: str) -> str:
    return (
        f"Video title: {title}\n"
        f"Video description: {snippet}\n"
        f"Video link: {link}\n\n"
        f"Please summarize the content of the video above for me."
    )


def summarize_video_ollama_vi(title: str, snippet: str, link: str, num_words: int) -> str:
    return (
        f"Tiêu đề video: {title}\n"
        f"Mô tả video: {snippet}\n"
        f"Link video: {link}\n\n"
        f"Bạn là một chuyên gia phân tích và tóm tắt nội dung video. "
        f"Tôi đã cung cấp cho bạn tiêu đề, mô tả và link của một video YouTube ở trên. "
        f"Mô tả có thể được viết bằng nhiều ngôn ngữ khác nhau. "
        f"Nhiệm vụ của bạn: hãy dịch mô tả sang tiếng Việt và viết một bản tóm tắt bằng tiếng Việt "
        f"dựa trên tiêu đề và mô tả video. "
        f"Viết ngắn gọn, dễ hiểu, đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ. "
        f"Chỉ sử dụng thông tin có trong dữ liệu cung cấp, không suy đoán hay thêm ngoài. "
        f"Kết quả nên ở dạng một đoạn văn liên tục."
    )


def summarize_video_ollama_en(title: str, snippet: str, link: str, num_words: int) -> str:
    return (
        f"Video title: {title}\n"
        f"Video description: {snippet}\n"
        f"Video link: {link}\n\n"
        f"You are an expert in analyzing and summarizing video content. "
        f"I have provided you with the title, description, and link of a YouTube video above. "
        f"The description can be written in many different languages. "
        f"Your task: translate the description into English and write a summary in English "
        f"based on the video title and description. "
        f"Write concisely, easily understood, complete with main ideas, avoid rambling, maximum {num_words} words. "
        f"Use only information contained in the data provided, do not speculate or add anything else. "
        f"The result should be in the form of a continuous paragraph."
    )


def is_related_system_vi() -> str:
    return (
        "Bạn là một chuyên gia đánh giá nội dung. "
        "Nhiệm vụ: dựa trên những thông tin được cung cấp (Gồm: title, snippet và link URL), "
        "xác định xem nội dung có liên quan tới chủ đề mà người dùng đang quan tâm hay không. "
        "Quy ước kết quả (CHỈ IN MỘT KÝ TỰ): "
        "'1' = liên quan; '0' = không liên quan; '2' = không chắc chắn / thông tin thiếu. "
        "Luật chi tiết: nếu snippet hoặc title trực tiếp đề cập tới chủ đề hoặc đồng nghĩa/ngữ cảnh rất rõ → '1'. "
        "Nếu hoàn toàn khác chủ đề → '0'. Nếu thông tin mơ hồ, quá ngắn, hoặc không đủ để quyết định → '2'. "
        "**RẤT QUAN TRỌNG**: chỉ in đúng một ký tự (0,1 hoặc 2) và không in bất cứ ký tự, khoảng trắng, dòng mới hay giải thích nào khác. "
    )


def is_related_user_vi(topic_key: str, title: str, snippet: str, link: str) -> str:
    return (
        f"Tiêu đề: {title}\nĐoạn trích: {snippet}\nLink: {link}\nChủ đề quan tâm: {topic_key}\n\n"
        "Hãy đánh giá nội dung trên có liên quan đến chủ đề tôi đang quan tâm hay không. Trả về kết quả theo quy ước đã nêu."
    )


def is_related_ollama_vi(topic_key: str, title: str, snippet: str, link: str) -> str:
    return (
        f"Tiêu đề: {title}\nĐoạn trích: {snippet}\nLink: {link}\nTừ khóa của chủ đề: {topic_key}\n\n"
        "Bạn là một chuyên gia đánh giá nội dung. "
        "Tôi đã cung cấp: TIÊU ĐỀ (title), ĐOẠN TRÍCH (snippet), LINK (URL) và TỪ KHÓA CỦA CHỦ ĐỀ ở trên."
        "Nhiệm vụ: dựa **duy nhất** trên những thông tin tôi cung cấp (title, snippet và link URL), "
        "xác định xem nội dung có liên quan tới 'Từ khóa của chủ đề' hay không. "
        "Quy ước kết quả (CHỈ IN MỘT KÝ TỰ): "
        "'1' = liên quan; '0' = không liên quan; '2' = không chắc chắn / thông tin thiếu. "
        "Luật chi tiết: nếu snippet hoặc title trực tiếp đề cập tới từ khóa hoặc đồng nghĩa/ngữ cảnh rất rõ → '1'. "
        "Nếu hoàn toàn khác chủ đề → '0'. Nếu thông tin mơ hồ, quá ngắn, hoặc không đủ để quyết định → '2'. "
        "**RẤT QUAN TRỌNG**: chỉ in đúng một ký tự (0,1 hoặc 2) và không in bất cứ ký tự, khoảng trắng, dòng mới hay giải thích nào khác. "
        "Không được truy cập internet hay thêm thông tin ngoài dữ liệu đã cho. "
    )


def extract_info_system_gemini_vi() -> str:
    return (
        f"Bạn là một AI có nhiệm vụ đọc hiểu nội dung được cung cấp và trích xuất ra các thông tin cốt lõi liên quan đến từ khóa được cung cấp."
        f"Yêu cầu:"
        f"- Đọc hiểu nội dung được cung cấp, nội dung có thể chứa nhiều thông tin nhiễu, trình tự sắp xếp có thể lộn xộn.\n"
        f"- Người dùng sẽ đưa ra các thông tin mong muốn được trích xuất, hãy trả lời lần lượt theo thứ tự các mục mà người dùng yêu cầu.\n"
        f'- Dựa trên Từ khóa chủ đề được cung cấp, trích xuất ra những thông tin có liên quan trực tiếp đến Từ khóa chủ đề đó, nếu như không có thông tin liên quan, ghi ngắn gọn "Không tìm thấy thông tin liên quan".\n'
        f"- Không tự bổ sung thông tin hay nói về những thông tin không được đề cập trong nội dung người dùng gửi.\n"
    )


def extract_info_user_gemini_vi(topic_key: str, text: str, demands_text: str) -> str:
    return (
        f"Từ khóa chủ đề: {topic_key}\n"
        f"Nội dung text trong trang web mà bạn cần xử lý: {text}\n\n"
        f"Hãy trích xuất các thông tin liên quan từ nội dung trên dựa trên yêu cầu đã nêu."
        f"Ưu tiên trả lời lần lượt theo thứ tự các mục sau:\n"
        f"{demands_text}"
    )


def extract_info_ollama_vi(topic_key: str, text: str, demands_text: str) -> str:
    return (
        f"Từ khóa chủ đề: {topic_key}\n"
        f"Nội dung text trong trang web mà bạn cần xử lý: {text}\n\n"
        f"Bây giờ bạn là một AI có nhiệm vụ đọc hiểu nội dung mà tôi gửi và trích xuất ra các thông tin cốt lõi liên quan đến từ khóa được cung cấp."
        f"Yêu cầu:"
        f"- Đọc nội dung mà tôi đã gửi ở trên, nội dung có thể chứa nhiều thông tin nhiễu, trình tự sắp xếp có thể lộn xộn. "
        f'- Dựa trên Từ khóa chủ đề được cung cấp, trích xuất ra những thông tin có liên quan trực tiếp đến Từ khóa chủ đề đó, nếu như không có thông tin liên quan, ghi ngắn gọn "Không tìm thấy thông tin liên quan".'
        f"- Không tự bổ sung thông tin hay nói về những thông tin không được đề cập trong nội dung được giao."
        f"- Hãy trả lời bằng tiếng Việt và trả lời lần lượt theo thứ tự các mục sau:\n"
        f"{demands_text}"
    )


def format_demands_text(demands: Iterable[str]) -> str:
    return "".join(f"    {i+1}. {d}\n" for i, d in enumerate(demands))


def normalize_tags_system() -> str:
    """
    System prompt for tag normalization.
    Uses 30 canonical tags across 4 categories.
    Enhanced with strict evidence requirements.
    """
    device_tags = ", ".join(f'"{d}"' for d in TAG_DEVICE_CANONICAL)
    threat_tags = ", ".join(f'"{t}"' for t in TAG_THREAT_CANONICAL)
    topic_tags = ", ".join(f'"{t}"' for t in TAG_TOPIC_CANONICAL)
    brand_tags = ", ".join(f'"{b}"' for b in TAG_BRAND_CANONICAL)
    
    return (
        "You normalize tags for a security news report. "
        "Your task is to assign standardized tags from a FIXED LIST of 30 canonical tags only.\n\n"
        
        "=== CRITICAL RULES (READ CAREFULLY) ===\n\n"
        
        "1. ONLY use tags from the canonical list below. DO NOT invent new tags.\n\n"
        
        "2. EVIDENCE REQUIREMENT - MOST IMPORTANT RULE:\n"
        "   BEFORE assigning ANY tag, you MUST find at least ONE specific keyword or phrase in the article content.\n"
        "   - If you cannot find evidence for a tag, DO NOT assign that tag.\n"
        "   - It is BETTER to have FEWER tags than WRONG tags.\n"
        "   - Ask yourself: 'What exact word/phrase in the article supports this tag?'\n"
        "   - If the answer is unclear or requires assumption, SKIP that tag.\n\n"
        
        "3. DEVICE TAG (MANDATORY - Exactly 1 required):\n"
        f"   Choose EXACTLY ONE from: {device_tags}\n"
        "   - Smartphone: Look for 'phone', 'mobile', 'Galaxy', 'iPhone', 'Pixel', 'smartphone'\n"
        "   - Computer: Look for 'PC', 'laptop', 'desktop', 'Mac', 'MacBook', 'workstation'\n"
        "   - Server & Cloud: Look for 'server', 'cloud', 'AWS', 'Azure', 'data center'\n"
        "   - IoT Device: Look for 'smart home', 'IoT', 'connected', 'automotive', 'router', 'camera'\n"
        "   - Wearable: Look for 'watch', 'wearable', 'fitness tracker', 'AR', 'VR', 'headset'\n"
        "   - Multiple Devices: Only if article explicitly covers 2+ device categories equally\n"
        "   - Non-categorized Devices: Peripherals, accessories, devices not fitting above categories\n\n"
        
        "4. TAG CATEGORIES & LIMITS:\n"
        f"   Threat Type (min 0, max 2): {threat_tags}\n"
        f"   Topic (min 0, max 2): {topic_tags}\n"
        f"   Brand/Platform (min 0, max 2): {brand_tags}\n\n"
        
        "5. TOTAL TAG LIMIT: Minimum 1 tag (device), Maximum 6 tags (1 device + up to 5 others)\n\n"
        
        "6. EVIDENCE PRIORITY:\n"
        "   Base tags on this order: title > ai_summary_en > snippet\n"
        "   Raw RSS tags are hints only - IGNORE if not supported by evidence in title/summary/snippet\n\n"
        
        "7. BRAND TAGGING RULES - STRICT:\n"
        "   - Samsung: ONLY when 'Samsung' or Samsung product (Galaxy, Knox, One UI, Bixby) is mentioned\n"
        "   - Apple: ONLY for iPhone, iPad, Mac, iOS, macOS, Apple Watch, AirPods\n"
        "   - Google: ONLY for Google products (Pixel, Chrome, Gmail, Google Cloud, Android - stock)\n"
        "   - Microsoft: ONLY for Windows, Surface, Azure, Office 365, Microsoft 365, Edge\n"
        "   - Android: ONLY for general/stock Android issues, NOT Samsung/Huawei/Xiaomi specific\n"
        "   - iOS: ONLY for iOS-specific features/issues (not general mobile security)\n"
        "   - Windows: ONLY for Windows-specific news (not general PC security)\n"
        "   - China Brand: ONLY for Huawei, Xiaomi, OPPO, Vivo, Honor, OnePlus, Realme\n"
        "   - Github: ONLY for Github-specific news, security issues on Github platform\n"
        "   ⚠️ If brand is not explicitly mentioned, DO NOT assign brand tag.\n\n"
        
        "8. WHEN NOT TO TAG (Examples):\n"
        "   - 'Security' mentioned generally → Do NOT add 'Vulnerability' without specific CVE/flaw\n"
        "   - 'Hack' mentioned without details → Do NOT add 'Malware' or 'Data Breach'\n"
        "   - 'Update' without security context → Do NOT add 'Security Update'\n"
        "   - 'China' mentioned → Do NOT add 'China Brand' without specific brand name\n"
        "   - 'Cloud' mentioned → Do NOT add 'Cloud Security' without security context\n"
        "   - 'AI' mentioned → Do NOT add 'AI' tag unless AI is central to security topic\n"
        "   - Article about 'smartphone security' → Do NOT add both 'Malware' and 'Phishing' without evidence of both\n\n"
        
        "9. CONFIDENCE CHECK - Before finalizing:\n"
        "   For each tag you plan to assign, verify:\n"
        "   ✓ Can I point to a specific word/phrase supporting this tag?\n"
        "   ✓ Is this tag directly related to the MAIN topic (not just mentioned in passing)?\n"
        "   ✓ Would another person agree this tag is appropriate based on the evidence?\n"
        "   If any answer is 'no' or 'unsure', SKIP that tag.\n\n"
        
        "10. OUTPUT FORMAT:\n"
        "   - Reply with ONLY valid JSON: {\"tags\": [\"Tag1\", \"Tag2\", ...]}\n"
        "   - No markdown, no explanation, no other text\n"
        "   - Tags in order: Device → Threat Type → Topic → Brand\n\n"
        
        "11. DO NOT:\n"
        "   - Invent tags outside the 30 canonical tags\n"
        "   - Use generic terms like News, Blog, Security, Cyber, Technology\n"
        "   - Output the article title as a tag\n"
        "   - Add tags unsupported by article content\n"
        "   - Use CVE numbers as tags (use 'Vulnerability' instead)\n"
        "   - Guess or assume information not present in the content\n"
        "   - Tag based on raw RSS tags alone without verification\n"
    )


def normalize_tags_user(
    topic_key: str,
    title: str,
    snippet: str,
    summary_en: str,
    tags_raw: list[str],
    max_tags: int = 6,
) -> str:
    """
    User prompt for tag normalization.
    
    Args:
        topic_key: The topic keyword for context
        title: Article title
        snippet: Article snippet/description
        summary_en: AI-generated summary in English
        tags_raw: Raw tags from RSS feed (hints only)
        max_tags: Maximum number of tags to output (default: 6)
    
    Returns:
        Formatted user prompt for tag normalization
    """
    tags_json = json.dumps(tags_raw, ensure_ascii=False)
    
    # Build canonical tags reference
    all_tags_list = list(ALL_CANONICAL_TAGS)
    canonical_tags_json = json.dumps(all_tags_list, ensure_ascii=False)
    
    return (
        f"=== ARTICLE INPUT ===\n"
        f"topic_key: {topic_key}\n\n"
        f"title:\n{title}\n\n"
        f"snippet:\n{snippet}\n\n"
        f"ai_summary_en:\n{summary_en}\n\n"
        f"tags_raw (JSON array, hints only - may be empty):\n{tags_json}\n\n"
        
        f"=== YOUR TASK ===\n"
        f"Assign tags from the 30 canonical tags listed below.\n"
        f"Maximum {max_tags} tags total.\n"
        f"Requirements:\n"
        f"  - Exactly 1 device tag (mandatory)\n"
        f"  - Up to 2 threat type tags\n"
        f"  - Up to 2 topic tags\n"
        f"  - Up to 2 brand/platform tags\n"
        f"Return ONLY JSON: {{\"tags\": [...]}}\n\n"
        
        f"=== 30 CANONICAL TAGS (USE ONLY THESE) ===\n"
        f"{canonical_tags_json}"
    )


def normalize_tags_ollama_prompt(
    topic_key: str,
    title: str,
    snippet: str,
    summary_en: str,
    tags_raw: list[str],
    max_tags: int,
) -> str:
    """
    Combined prompt for Ollama tag normalization.
    """
    return (
        normalize_tags_system()
        + "\n\n--- TASK ---\n\n"
        + normalize_tags_user(
            topic_key=topic_key,
            title=title,
            snippet=snippet,
            summary_en=summary_en,
            tags_raw=tags_raw,
            max_tags=max_tags,
        )
    )


def validate_normalized_tags(tags: list[str]) -> tuple[bool, list[str], list[str]]:
    """
    Validate that normalized tags are from the canonical list.
    
    Args:
        tags: List of tags to validate
    
    Returns:
        Tuple of (is_valid, valid_tags, invalid_tags)
        - is_valid: True if all tags are canonical
        - valid_tags: List of tags that are in the canonical set
        - invalid_tags: List of tags that are NOT in the canonical set
    """
    valid_tags = []
    invalid_tags = []
    
    for tag in tags:
        if tag in TAG_CANONICAL_SET:
            valid_tags.append(tag)
        else:
            invalid_tags.append(tag)
    
    is_valid = len(invalid_tags) == 0
    return is_valid, valid_tags, invalid_tags


def normalize_tags_output(
    tags: list[str],
    max_tags: int = 6,
    ensure_device_tag: bool = True,
) -> tuple[list[str], list[str]]:
    """
    Normalize and clean tag output.
    
    Args:
        tags: List of tags from AI output
        max_tags: Maximum number of tags to return (default: 6)
        ensure_device_tag: If True, ensure at least one device tag is present
    
    Returns:
        Tuple of (normalized_tags, warnings)
        - normalized_tags: Cleaned list of canonical tags
        - warnings: List of warning messages for any issues
    """
    warnings = []
    normalized = []
    device_tag_found = False
    
    # Validate and filter tags
    is_valid, valid_tags, invalid_tags = validate_normalized_tags(tags)
    
    if invalid_tags:
        warnings.append(f"Removed {len(invalid_tags)} non-canonical tags: {invalid_tags}")
    
    # Check for device tag
    if ensure_device_tag:
        for tag in valid_tags:
            if tag in TAG_DEVICE_CANONICAL:
                device_tag_found = True
                break
        if not device_tag_found:
            warnings.append("No device tag found - article may need manual review")
    
    # Limit to max_tags
    if len(valid_tags) > max_tags:
        warnings.append(f"Truncated from {len(valid_tags)} to {max_tags} tags")
        normalized = valid_tags[:max_tags]
    else:
        normalized = valid_tags
    
    return normalized, warnings

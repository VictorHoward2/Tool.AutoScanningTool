"""
Prompt templates for AIProcessor. No imports from config.settings to avoid circular imports.
Callers pass values like num_words, demands_text, or formatted article blocks.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping


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

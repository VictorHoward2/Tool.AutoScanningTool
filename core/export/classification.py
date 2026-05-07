import json
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple


def _extract_keywords(obj: Any) -> List[str]:
    """
    Trả về list các từ khóa từ một giá trị trong JSON.
    Hỗ trợ hai dạng:
      - ["kw1", "kw2", ...]
      - {"keywords": ["kw1","kw2", ...], ...}
    """
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        # ưu tiên trường 'keywords', fallback: tìm list đầu tiên trong dict
        if "keywords" in obj and isinstance(obj["keywords"], list):
            return obj["keywords"]
        # fallback: lấy mọi giá trị list trong dict
        for value in obj.values():
            if isinstance(value, list):
                return value
    return []


def classify_security_article(
    content: str,
    json_path: str = ".\\config\\security_categories.json",
    top_n: int = 5,
    threshold: int = 1,
    debug: bool = False,
) -> List[Tuple[str, int]]:
    """
    Phân loại bài báo bảo mật dựa trên danh sách từ khóa (hỗ trợ cả 2 định dạng JSON).

    Args:
        content: nội dung bài viết cần phân loại
        json_path: đường dẫn tới file JSON chứa categories
        top_n: trả về tối đa top_n category
        threshold: ngưỡng điểm tối thiểu để một category được tính là relevant
        debug: nếu True sẽ in debug info

    Trả về:
        List[(category_name, score)] sắp theo điểm giảm dần
    """
    with open(json_path, "r", encoding="utf-8") as file:
        categories_raw: Dict[str, Any] = json.load(file)

    if debug:
        print(f"\n\n[DEBUG] Content: {content}.")

    text = content.lower()
    categories: Dict[str, List[str]] = {}
    for cat_name, value in categories_raw.items():
        keywords = _extract_keywords(value)
        keywords_clean = [
            keyword.strip().lower()
            for keyword in keywords
            if isinstance(keyword, str) and keyword.strip()
        ]
        categories[cat_name] = keywords_clean
        if debug:
            print(f"[DEBUG] Category '{cat_name}' has {len(keywords_clean)} keywords")

    scores = defaultdict(int)
    for cat_name, keywords in categories.items():
        if not keywords:
            continue
        if debug:
            print(f"[DEBUG] Processing category: {cat_name}")
        for keyword in keywords:
            pattern = r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
            matches = re.findall(pattern, text)
            if matches:
                scores[cat_name] += len(matches)
                if debug:
                    print(
                        f"[DEBUG] Found {len(matches)} x '{keyword}' in '{cat_name}' "
                        f"(pattern: {pattern})"
                    )

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    result = [(category, score) for category, score in ranked if score >= threshold]
    return result[:top_n]

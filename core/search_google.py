import requests
from config.settings import API_KEY_GOOGLE, SEARCH_ENGINE_ID, RESULTS_PER_REQUEST, NUM_RESULTS
from core.logger import logger

'''
----- List params -----
q               : từ khóa tìm kiếm                              :
key             : api key                                       :    
cx              : search engine                                 : cx=YOUR_CX_ID
num             : lượng res cho 1 request                       : max là 10
start           : phân trang, lấy ra kết quả từ vị trí này      : start=11   
siteSearch      : lọc kết quả trong 1 web cụ thể                :
dateRestrict    : Lọc theo thời gian (d, w, m, y)               : dateRestrict=m6 (6 tháng) |d|w|m|y ex: y1-1 năm, d7-7 ngày
exactTerms      : Tìm chính xác cụm từ                          :    
excludeTerms    : Loại bỏ kết quả có từ khóa này                :
gl              : Lọc kết quả theo quốc gia (ISO 3166-1 code)   : gl=vn (Việt Nam)
lr              : Lọc theo ngôn ngữ                             : lr=lang_vi (Tiếng Việt)
safe            : Bộ lọc nội dung người lớn                     : safe=active (Bật)
fileType        : Chỉ tìm file có định dạng cụ thể              : fileType=pdf
rights          : Lọc theo giấy phép bản quyền                  : rights=cc_publicdomain
sort            : Sắp xếp theo ngày hoặc mức độ liên quan       : sort=date - sắp xếp theo ngày | mặc định là dộ liên quan 
'''
class GoogleSearch:
    def search(self, query, date_restrict="m1"):
        all_results = []
        for start in range(1, NUM_RESULTS, RESULTS_PER_REQUEST):
            params = {
                "key": API_KEY_GOOGLE,
                "cx": SEARCH_ENGINE_ID,
                "q": query,
                "num": RESULTS_PER_REQUEST, # Google giới hạn tối đa 10/lần
                "start": start,
                "dateRestrict": date_restrict,
            }
            try:
                r = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
                if r.ok:
                    items = r.json().get("items", [])
                    for item in items:
                        all_results.append({
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "snippet": item.get("snippet", "")
                        })
                else:
                    logger.warning(f"Google API error: {r.status_code}")
            except Exception as e:
                logger.error(f"GoogleSearch Exception: {e}")
        return all_results

    def search_all(self, query_dict):
        results = []
        for lang, query in query_dict.items():
            logger.info(f"[GOOGLE SEARCH] Searching [{lang}] query: {query}")
            results += self.search(query)
        return results

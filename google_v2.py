
import re
import os
import time
import urllib3
import requests
import traceback
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

####################################################################################### CONFIG 
API_KEY = "AIzaSyDBUcnY9yG5ZRK0WzhJQLuGW-j6BOcwBaY"
SEARCH_ENGINE_ID = "f3dc1d67c30ed47dc"
TITLE = 'title'
LINK = 'link'
SNIPPET = 'snippet' # DESCRIPTION
CONTENT = 'content'
SUMMARIZE = 'summarize'
IS_RELATED = 'related'
USEFUL_INFO = 'useful info'
CODE = ['es','fr','de','pt','th']
NUM_REQUEST = 3 # Max -> 100
RESULTS_PER_REQUEST = 3 # Google giới hạn tối đa 10/lần
####################################################################################### GLOBAL VARS
all_results = []
list_ignore = ['samsung.com', 'amazon.com', 'apple.com', 'threads.net']

start_time = time.time()
cur_time = start_time

key = "Network Unlock of Samsung smartphones"
query = 'network unlock "samsung"'
queries = {}
queries['en'] = query

####################################################################################### TRANSLATE
def get_api_url(text, from_lang, to_lang):
    return f"https://api.mymemory.translated.net/get?q={text}&langpair={from_lang}%7C{to_lang}"

def translate_using_api(text, to_lang):
    try: 
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        url = get_api_url(text, 'en', to_lang)
        response = requests.get(url, verify=False)
        data = response.json()
        response.raise_for_status()  # Raise an exception for HTTP errors
        return data['responseData']['translatedText']
    except Exception as e:
        return F"Fail to translate to {to_lang} query: {text}"

for lang in CODE:
    queries[lang] = translate_using_api(query, lang)
end_time = time.time()  # ghi lại thời gian kết thúc
elapsed_time = end_time - cur_time
cur_time = end_time
print(f"⏱️ Thời gian chạy update_queries: {elapsed_time:.2f} giây")

####################################################################################### SEARCH API
def search_api(query, num_results = NUM_REQUEST, start_page = 0, date_restrict="m1"):
    url = 'https://www.googleapis.com/customsearch/v1'

    results_per_request = RESULTS_PER_REQUEST  # Google giới hạn tối đa 10/lần
    params = {
        'q'             : query,
        'key'           : API_KEY,
        'cx'            : SEARCH_ENGINE_ID,
        'num'           : results_per_request,
        'start'         : start_page,
        'dateRestrict'  : date_restrict,
    }

    for start in range(1, num_results, results_per_request):
        print(f"Finding {start} to {start + results_per_request - 1}")
        params['start'] = start
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            data_items = data.get("items", [])
            # print(f"Start: {start}, Result: {data_items}")
            if len(data_items) == 0:
                print("End result")
                break

            for item in data_items:
                if all(ignore not in item[LINK] for ignore in list_ignore):
                        # publish_date = get_publish_from_des(description)
                        all_results.append({
                             TITLE: item[TITLE], 
                             LINK: item[LINK], 
                             SNIPPET: item[SNIPPET], 
                             CONTENT: "",
                             SUMMARIZE: "",
                             IS_RELATED: "",
                             USEFUL_INFO: "",
                             })
        else:
            print(f"Lỗi {response.status_code}: {response.text}")
            break  # Dừng lại nếu có lỗi

for que in queries:
    search_api(que)

end_time = time.time()  # ghi lại thời gian kết thúc
elapsed_time = end_time - cur_time
cur_time = end_time
print(f"⏱️ Thời gian chạy search_api: {elapsed_time:.2f} giây")

def remove_duplicate_links(array):
    unique_arr = []
    for index, item in enumerate(array):
        check_uni = False
        for i in range(index):
            if item[LINK] == array[i][LINK]:
                check_uni = True
                break
        if check_uni == False:
            unique_arr.append(item)
    return unique_arr

all_results = remove_duplicate_links(all_results)
end_time = time.time()  # ghi lại thời gian kết thúc
elapsed_time = end_time - cur_time
cur_time = end_time
print(f"⏱️ Thời gian chạy remove_duplicate_links: {elapsed_time:.2f} giây")
print(f"✅ Tổng số links tìm được: {len(all_results):.2f}")


####################################################################################### GET CONTENT

def get_content():
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(10)

    for item in all_results:
        clean_text = ''
        try:
            driver.get(item[LINK])
        except TimeoutException:
            print(f"[TIMEOUT] Trang load quá lâu: {item[LINK]}")
            try:
                page_source = driver.page_source
                # Lấy nội dung nếu đã có
                soup = BeautifulSoup(page_source, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
                clean_text = '\n'.join(lines)
            except Exception as e:
                traceback.print_exc()
                print(f"[FAIL] Không thể lấy page_source sau timeout: {item[LINK]}")
                continue  # Bỏ qua nếu không lấy được gì
        except WebDriverException:
            traceback.print_exc()
            print(f"[ERROR] WebDriver gặp lỗi khi truy cập: {item[LINK]}")
            continue
        else:
            # Nếu không timeout, xử lý bình thường
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
            clean_text = '\n'.join(lines)

        item[CONTENT] = clean_text

    driver.quit()
get_content()

end_time = time.time()  # ghi lại thời gian kết thúc
elapsed_time = end_time - cur_time
cur_time = end_time
print(f"⏱️ Thời gian chạy update_content: {elapsed_time:.2f} giây")
    
####################################################################################### AI SUPPORT
def strip_thoughts(text):
    """
    Loại bỏ phần nằm trong <think>...</think> và trả về phần nội dung sau đó.

    Args:
        text (str): Chuỗi đầu vào, có thể chứa phần <think>...</think>

    Returns:
        str: Chuỗi đã được làm sạch, chỉ giữ phần kết luận cuối cùng.
    """
    # Dùng regex để loại bỏ đoạn <think>...</think>
    clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Loại bỏ khoảng trắng đầu/cuối và dòng trống thừa
    clean_text = clean_text.strip()

    return clean_text

def summarize_text(title, snippet, link, content, num_words = 50, model="gemma3:1b"):
    prompt = (
        f"Bạn là một chuyên gia đọc hiểu, phân tích, tóm tắt nội dung văn bản."
        f"Tôi sẽ gửi cho bạn tiêu đề, đoạn trích nhỏ, link và nội dung (phần text trong trang web) của một trang web cùng với một từ khóa."
        f"Bây giờ nhiệm vụ của bạn là: "
        f"Hãy dựa vào những thông tin tôi gửi viết một bản tóm tắt bằng tiếng Việt về nội dung của trang web."
        f"Viết ngắn gọn, dễ hiểu và đầy đủ ý chính, tránh lan man, tối đa {num_words} chữ."
        f"Không tự bổ sung thông tin không được đề cập trong nội dung được giao.\n"
        f"Tiêu đề trang web: {title} \n\n"
        f"Đoạn trích nhỏ của trang web: {snippet}\n\n"
        f"Link của trang web: {link}\n\n"
        f"Nội dung (phần text trong trang web) của trang web: {content}\n\n"
        f"Từ khóa của lần này: {key}\n\n"
    )   
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Lỗi: {response.status_code} - {response.text}"
    
    
def is_related(title, snippet, link, model="gemma3:1b"):
    prompt = (
        f"Tôi sẽ gửi cho bạn tiêu đề, đoạn trích nhỏ và link của một trang web cùng với một từ khóa. Bây giờ nhiệm vụ của bạn là: "
        f"Trả lời chỉ một số duy nhất: \"1\" nếu từ những thông tin về trang web mà tôi gửi bạn đánh giá có nội dung liên quan nhiều đến từ khóa, không liên quan thì ghi \"0\", nếu bạn phân vân và không quyết định được thì ghi \"2\"."
        f"Không thêm bất kỳ giải thích hay bình luận nào khác. Rõ ràng và ngắn gọn.\n\n"
        f"Hãy cân nhắc thật kỹ bởi vì câu trả lời này của bạn rất quan trọng."
        f"Tiêu đề trang web: {title} \n\n"
        f"Đoạn trích nhỏ của trang web: {snippet}\n\n"
        f"Link của trang web: {link}\n\n"
        f"Từ khóa của lần này: {key}\n\n"
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Lỗi: {response.status_code} - {response.text}"
  
    
def extract_info (text, model="gemma3:1b"):
    prompt = (
        f"Bây giờ bạn là một AI có nhiệm vụ đọc hiểu nội dung của một trang web và trích xuất ra các thông tin cốt lõi liên quan đến từ khóa được cung cấp."
        f"Yêu cầu:"
        f"- Đọc nội dung được trích xuất từ HTML của một trang web tôi sắp gửi dưới đây. "
        f"- Dựa trên từ khóa được cung cấp, trích xuất ra những thông tin có liên quan trực tiếp đến từ khóa đó, nếu như không có thông tin liên quan, ghi ngắn gọn \"Không có thông tin\"."
        f"- Không tự bổ sung thông tin hay nói về những thông tin không được đề cập trong nội dung được giao."
        f"- Nếu có thể, hãy trả lời bằng tiếng Việt và tuân theo các mục sau:\n"
        f"    1. Tên thiết bị hoặc tên dòng máy liên quan đến từ khóa, càng nhiều thông tin chi tiết càng tốt."
        f"    2. Tên công cụ (tool) hoặc tên phần mềm hoặc phương thức được dùng để thực hiện"
        f"    3. Cách thức thực hiện (hướng dẫn ngắn gọn nếu có)"
        f"    4. Điều kiện cần thiết hoặc lưu ý khi thực hiện"
        f"    5. Bất kỳ thông tin bổ sung hữu ích nào liên quan đến từ khóa"
        f"Chỉ trích xuất các thông tin liên quan trực tiếp đến từ khóa. Nếu không có thông tin nào phù hợp thì hãy trả lời: \"Không tìm thấy thông tin liên quan\"."
        f"Từ khóa của lần này: {key}\n"
        f"Nội dung text trong trang web mà bạn cần xử lý: {text}"
    )
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Lỗi: {response.status_code} - {response.text}"

def update_ai_response():
    for item in all_results:
        global cur_time
        print(f"🧠 Update AI response cho: {item[TITLE]}")
        try:    
            item[SUMMARIZE] = strip_thoughts(summarize_text(item[TITLE], item[SNIPPET], item[LINK], item[CONTENT]))

            end_time = time.time()  # ghi lại thời gian kết thúc
            elapsed_time = end_time - cur_time
            cur_time = end_time
            print(f"⏱️ Thời gian chạy summarize_text: {elapsed_time:.2f} giây")

            str_related = strip_thoughts(is_related(item[TITLE], item[SNIPPET], item[LINK]))
            end_time = time.time()  # ghi lại thời gian kết thúc
            elapsed_time = end_time - cur_time
            cur_time = end_time
            print(f"⏱️ Thời gian chạy is_related: {elapsed_time:.2f} giây")

            try: 
                int_related = int(str_related)
            except ValueError: 
                int_related = 1
            if int_related==0: 
                item[IS_RELATED] = "Không"
            else: 
                item[IS_RELATED] = "Có"
                item[USEFUL_INFO] = strip_thoughts(extract_info(item[CONTENT]))
                end_time = time.time()  # ghi lại thời gian kết thúc
                elapsed_time = end_time - cur_time
                cur_time = end_time
                print(f"⏱️ Thời gian chạy extract_info: {elapsed_time:.2f} giây")
            
        except Exception as e:
            print(f"[ERROR] Đã xảy ra lỗi: {e}")

update_ai_response()
end_time = time.time()  # ghi lại thời gian kết thúc
elapsed_time = end_time - cur_time
cur_time = end_time
print(f"⏱️ Thời gian chạy update_ai_response: {elapsed_time:.2f} giây")
print(f"⏱️ Tổng thời gian chạy: {end_time - start_time:.2f} giây")

####################################################################################### STORE

for item in all_results:
    if 'content' in item:
        del item['content']

try:
    today = datetime.today().date()

    # path = '..//output'
    path = '/home/huy/AAProjets/Scanning/AutoScanningToolv1/output'

    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path)
        print(f'The directory "{path}" has been created.')
        
    file_path = f'{path}//hacking_{today}.xlsx'
    sheet_name = f'google_{today}'

    df = pd.DataFrame(all_results)
    df = df.map(lambda x: str(x) if not isinstance(x, (int, float)) else x)

    # Check file exist, delete old sheet before add new sheet
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            if sheet_name in writer.book.sheetnames:
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f'Exported {len(all_results)} data successful to {file_path} with sheet name {sheet_name}!')
except Exception as e:
    traceback.print_exc()
    print(f'Save data fail: {e}')
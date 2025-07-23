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
class YoutubeSearch:
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
    


# """ Script
#     Step 1: Import the necessary libraries
#     - Import external libraries
#     - Import local modules
#     Step 2: Search videos and get videos information using API
#     - Search videos by keyword and filter by publish date
#     - Get video id from search result
#     - Get detailed information about each video using API
#     - Filter out videos with specific keywords in their titles or descriptions
#     Step 3: Summarize comments using GenAI
#     - Generate summary for each video's description using GenAI
#     Step 4: Save data to excel file
# """
# # API Document: https://developers.google.com/youjlo;m:"mp'mtube/v3/docs/search/list?hl=vi


# # ==========================================================
# # ======================== Import ==========================
# # ==========================================================

# import os
# import json
# import numpy
# import importlib
# import urllib.parse
# import pandas as pd
# from time import sleep
# from datetime import datetime
# from urllib.parse import urlparse, parse_qs
# from selenium.webdriver.common.by import By
# from dateutil.relativedelta import relativedelta


# # Run file logger.py to create logger object with prefix "Youtube"
# with open("../common/logger.py") as f:
#     exec(f.read())
# logger = get_logger(name="youtube")
# logger.info("Start crawl youtube")


# # Imports a module from another directory.
# def get_module(folder_name, file_name):
#     module_name = file_name.split('.')[0]
#     module_path = os.path.join(os.getcwd(), '..', folder_name, file_name)
#     spec = importlib.util.spec_from_file_location(module_name, module_path)
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)
#     return module


# # Import multi-lang input module to get the list of countries, languages, inputs, country codes.
# multilang_input_module = get_module("internal", "multi_language_input.py")
# COUNTRIES = multilang_input_module.COUNTRIES
# LANGUAGES = multilang_input_module.LANGUAGES
# INPUTS = multilang_input_module.INPUTS
# COUNTRY_CODES = multilang_input_module.COUNTRY_CODES
# LANGUAGES_CODES = multilang_input_module.LANGUAGES_CODES


# # Get Youtube API key from internal variable.py file. Do not share this file!
# input_module = get_module("internal", "youtube_input.py")
# API_KEY = input_module.API_KEY
# PUBLISHED_FROM = input_module.PUBLISHED_FROM
# PUBLISHED_TO = input_module.PUBLISHED_TO
# IGNORE_WORDS = input_module.IGNORE_WORDS
# AUTO_MODE_ON = input_module.AUTO_MODE_ON


# # From web_driver.py import get_driver to create new instance of WebDriver
# driver_module = get_module("common", "web_driver.py")
# get_driver = driver_module.get_driver
# driver = get_driver()


# # Get translate function from translate module.
# translate_module = get_module('common', 'translate_api.py')
# translate_using_api = translate_module.translate_using_api


# # ==========================================================
# # ====================== Search all API ====================
# # ==========================================================

# # Calculate and return a previous date based on the given month and day offset from the current date.
# # month (int): The number of months to subtract from the current date.
# # day (int): The number of days to subtract from the current date.
# # Returns str: A formatted date string in the format "YYYY-MM-DDTHH:MM:SSZ".
# def get_previous_date(month=0, day=0):
#     today = datetime.now()
#     previous_month_date = today - relativedelta(months=month, days=day)

#     # Format the date to the required format(api request) "YYYY-MM-DDTHH:MM:SSZ"
#     formatted_date = previous_month_date.strftime("%Y-%m-%dT%H:%M:%SZ")
#     return formatted_date


# # YouTube API URL
# API_URL = "https://www.googleapis.com/youtube/v3/search"


# # Search YouTube for videos matching the given query within the specified date range.
# # query (str): The search query to use for searching YouTube.
# # before (str): The maximum date for the videos to be published before.
# # after (str): The minimum date for the videos to be published after.
# # Returns list: A list of dictionaries containing information about the videos that match the search criteria.
# def search_youtube(query, before, after, region_code):
#     params = {
#         'q': query,
#         "part": "snippet",
#         "type": "video",
#         "order": "date",
#         "publishedBefore": before,
#         "publishedAfter": after,
#         "maxResults": 50,
#         "key": API_KEY
#     }
#     if region_code != "":
#         params["regionCode"] = region_code
#     try:
#         param_string = urllib.parse.urlencode(params)
#         driver.get(f"{API_URL}?{param_string}")
#         sleep(2)
        
#         # Extract the JSON response from the page source and convert it to a Python dictionary.
#         json_res = driver.find_element(By.TAG_NAME, "pre").text
#         response = json.loads(json_res)  
#         items = response["items"]
#         logger.info(f"{len(items)} found in {region_code}")
#     except Exception as e:
#         logger.error(f"Search youtube fail: {e}")
#         logger.info(response)
#         items = []
#     return items


# # Search YouTube for videos matching the given query within the specified date range.
# if AUTO_MODE_ON == True:
#     PUBLISHED_FROM = get_previous_date(day=7)
#     PUBLISHED_TO = get_previous_date(day=0)


# # Search YouTube for videos matching the given query within the specified date range. 
# # search_result (list): A list of dictionaries containing information about the videos that match the search criteria.
# # query (str): The search query to use for searching YouTube.
# # region_code (str): The region code to filter the search results by. 
# # region_code = "" -> search all countries.
# search_result = search_youtube(query= INPUTS["English"], before=PUBLISHED_TO, after=PUBLISHED_FROM, region_code="")
# for country in COUNTRIES:
#     query = INPUTS[LANGUAGES[country][0]]
#     region_code = COUNTRY_CODES[country]
#     region_search_result = search_youtube(query=query, before=PUBLISHED_TO, after=PUBLISHED_FROM, region_code=region_code)
#     search_result.extend(region_search_result)


# # Get video ids from search result. Used to get more detail about each video.
# video_ids = [item["id"]["videoId"] for item in search_result]
# video_ids = numpy.unique(video_ids)
# logger.info(f"Total video found: {len(video_ids)}")


# # ==========================================================
# # =============== Search API for each video ================
# # ==========================================================

# # Column name of dataframe(output data)
# COL_TYPE = "Type"
# COL_LINK = "Link"
# COL_TITLE = "Title"
# COL_PUBLISHED = "Published at"
# COL_DES = "Short description"
# COL_CONTENT = "Web content"
# COL_SUMMARY = "Summary"
# COL_TRANSCRIPT = "Transcript"
# API_URL_VIDEO_INFO = "https://www.googleapis.com/youtube/v3/videos"


# # Retrieve information about a YouTube video using its video ID.
# # video_id (str): The ID of the YouTube video to retrieve information for.
# # Returns dict: A dictionary containing all information about the video.
# # prams (dic): the parameters for the YouTube Data API request
# def get_video_info(video_id):
#     params = {
#         "part": "snippet,contentDetails,statistics",
#         "id": video_id,
#         "key": API_KEY
#     }
#     param_string = urllib.parse.urlencode(params)
#     driver.get(f"{API_URL_VIDEO_INFO}?{param_string}")
#     sleep(2)
    
#     # Extract the JSON response from the page source and convert it to a Python dictionary.
#     json_res = driver.find_element(By.TAG_NAME, "pre").text
#     response = json.loads(json_res)  
#     video_info = response["items"][0]
#     return video_info


# # Extract the relevant data from the video information and return it as a dictionary.
# # link (str): The URL of the YouTube video.
# # video_info (dict): The dictionary containing all information about the video.
# # Returns dict: A dictionary containing the relevant data extracted from the video information.
# def get_relevant_data(link, video_info):
#     title = video_info["snippet"]["title"]
#     description = video_info["snippet"]["description"]
#     trans = translate_using_api(description)
#     description = f"Original: {description} \nTranslate: {trans}"
#     published_at = video_info["snippet"]["publishedAt"]
#     res = {
#         COL_TYPE: "youtube",
#         COL_LINK: link,
#         COL_PUBLISHED: published_at,
#         COL_TITLE: title,
#         COL_DES: description
#     }
#     return res


# # Check if the video"s title contains any words from the ignore_word list.
# def check_contain_ignore(title):
#     title = title.lower()
#     for word in IGNORE_WORDS:
#         if word.lower() in title:
#             return True
#     return False


# # Try to iterate over each video ID in the video_ids list
# # Retrieve the video information using the get_video_info function.
# # Extract the relevant data using the get_relevant_data function.
# # Append the data to the data list if the title does not contain any ignore words.
# # Log a success message if the video information retrieval is successful, otherwise log an error message.
# # data (list): an empty list to store the relevant data of the videos.
# data = []
# try:
#     for i, video_id in enumerate(video_ids):
#         video_info = get_video_info(video_id)
#         link = f"https://www.youtube.com/watch?v={video_id}"
#         data_row = get_relevant_data(link, video_info)
#         title = data_row[COL_TITLE]

#         if check_contain_ignore(title = title) == False:
#             data.append(data_row)
#             print(title)
#     logger.info(f"Removed ignore videos")
# except Exception as e:
#     logger.error(f"Fail to get video info: {e}")


# # ==========================================================
# # ========================= Gen AI =========================
# # ==========================================================

# # From common/genai.py import Genai to create new instance of Genai class.
# genai_module = get_module("common", "genai.py")
# Genai = genai_module.Genai
# genai = Genai()


# # Iterate over each row in the data list and generate summaries for the descriptions in each row using the GenAI model.
# for i, row in enumerate(data):
#     try:
#         summary  = genai.search(row[COL_DES])
#         row[COL_SUMMARY] = summary
#         print(summary)
#         print(f"{i}. -----------------------------")

#     except Exception as e:
#         logger.error(f"Query genai fail: {e}")
#         row[COL_SUMMARY] = ""
        

# # ==========================================================
# # ======================= Save data ========================
# # ==========================================================

# # Try to export the data to an Excel file with a unique sheet name based on the current date.
# # If the file already exists, append the data to a new sheet with the same name.
# # If there is already a sheet with the same name, remove it before adding the new sheet.
# # Log a success message if the export is successful, otherwise log an error message.
# # df (Dataframe): The DataFrame containing the data to be exported. 
# try:
#     df = pd.DataFrame(data)

#     today = datetime.today().date()
#     file_path = f"..//output//output_{today}.xlsx"
#     sheet_name = f"youtube_{today}"

#     # Check if the file already exists
#     if os.path.exists(file_path):
#         with pd.ExcelWriter(file_path, engine="openpyxl", mode='a', if_sheet_exists="new") as writer:
#             if sheet_name in writer.book.sheetnames:
#             # Remove old sheet with same name
#                 writer.book.remove(writer.book[sheet_name])
#             df.to_excel(writer, sheet_name=sheet_name, index=False)
#     else:
#         with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
#             df.to_excel(writer, sheet_name=sheet_name, index=False)

#     logger.info(f"Export {len(data)} data successful")
# except Exception as e:
#     logger.error(f"Failed to export data: {e}")

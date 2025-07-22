import os
import pandas as pd
from config.settings import OUTPUT_PATH, TODAY
from core.logger import logger

# export_to_excel(results)

def export_to_excel(data):
    for item in data:
        if 'content' in item:
            del item['content']
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    file_path = os.path.join(OUTPUT_PATH, f"results_{TODAY}.xlsx")
    sheet_name = f'google_{TODAY}'
    
    df = pd.DataFrame(data)
    
    # Check file exist, delete old sheet before add new sheet
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            if sheet_name in writer.book.sheetnames:
                writer.book.remove(writer.book[sheet_name])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    logger.info(f"📤 Xuất dữ liệu thành công ra {file_path}")

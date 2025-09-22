from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_previous_date(month=0, day=0):
    today = datetime.now()
    previous_month_date = today - relativedelta(months=month, days=day)

    # Format the date to the required format(api request) "YYYY-MM-DDTHH:MM:SSZ"
    formatted_date = previous_month_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_date

def format_published(published):
    try:
        # Thử parse ISO format
        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        # Format lại sang kiểu dễ đọc
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        # Nếu không parse được thì giữ nguyên
        return published
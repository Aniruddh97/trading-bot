import datetime

DATE_FORMAT = "%Y-%m-%d"

today = datetime.date.today()
start_date = (today - datetime.timedelta(days=7)).strftime(DATE_FORMAT)
end_date = today.strftime(DATE_FORMAT)
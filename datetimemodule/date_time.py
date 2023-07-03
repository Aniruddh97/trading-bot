import datetime

DATE_FORMAT = "%Y-%m-%d"

def getStartEndDate(timeAgo='6m'):
    duration = timeAgo[:-1]
    timeSymbol = timeAgo[-1]
    
    days = 6 * 30
    if (timeSymbol.upper() == 'D'):
        days = int(duration)
    elif (timeSymbol.upper() == 'W'):
        days = int(duration)*7
    elif (timeSymbol.upper() == 'M'):
        days = int(duration)*30
    elif (timeSymbol.upper() == 'Y'):
        days = int(duration)*365

    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=days)).strftime(DATE_FORMAT)
    end_date = today.strftime(DATE_FORMAT)

    return start_date, end_date
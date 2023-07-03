import datetime

DATE_FORMAT = "%Y-%m-%d"

def getDateRange(timeAgo='6m'):
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
    start_date = (today - datetime.timedelta(days=days))
    end_date = today

    return start_date, end_date


def getDateRangeString(timeAgo='6m'):
    start, end = getDateRange(timeAgo)
    return start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT)
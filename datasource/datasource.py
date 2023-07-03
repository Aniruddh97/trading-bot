import yfinance as yf
import pandas as pd
from jugaad_data.nse import stock_df
from datemodule import getDateRange


def getYahooFinanceData(ticker, start, end):
    if ticker == '':
        print("Invalid ticker provided :'" + ticker + "'")
        return
    
    data = yf.download(ticker+'.NS', start=start, interval='1d', progress=False)
    data.insert(loc=0, column='Date', value=data.index)
    data.insert(loc=0, column='index', value=list(range(0,len(data.index))))
    ydf = data.set_index('index').reset_index().drop(['index'], axis=1)
    return ydf[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]


def getJugaadData(ticker, start, end):
    if ticker == '':
        print("Invalid ticker provided :'" + ticker + "'")
        return
    
    jdf = stock_df(symbol=ticker, from_date=start,to_date=end)
    jdf = jdf[['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']]
    jdf.rename(columns = {
            'DATE':'Date',
            'OPEN':'Open', 
            'HIGH':'High', 
            'LOW':'Low',
            'CLOSE':'Close', 
            'VOLUME':'Volume'
        }, inplace = True)
    return jdf.loc[::-1].reset_index().drop(['index'], axis=1)


def getFullData(ticker, start, end):
    s, e = getDateRange('1w')
    ydf = getYahooFinanceData(ticker=ticker, start=s, end=e)

    jdf = getJugaadData(ticker, start, end)
    
    if jdf['Date'][len(jdf)-1] == ydf['Date'][len(ydf)-1]:
        return jdf
    return pd.concat([jdf, ydf[-1:]], ignore_index = True)

import yfinance as yf
import pandas as pd
from jugaad_data.nse import stock_df, index_df, NSELive
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


def getNifty50Data(start, end):
    _, e = getDateRange('1d')
    niftyData = NSELive().live_index("NIFTY 50")['metadata']
    o = niftyData['open']
    c = niftyData['last']
    h = niftyData['high']
    l = niftyData['low']
    # v = niftyData['totalTradedVolume']
    
    jdf = index_df(symbol="NIFTY 50", from_date=start, to_date=end)
    jdf = jdf[['HistoricalDate', 'OPEN', 'HIGH', 'LOW', 'CLOSE']]
    jdf.rename(columns = {
            'HistoricalDate':'Date',
            'OPEN':'Open', 
            'HIGH':'High', 
            'LOW':'Low',
            'CLOSE':'Close', 
        }, inplace = True)
    jdf = jdf.loc[::-1].reset_index().drop(['index'], axis=1)
    jdf.loc[len(jdf)] = [e, o, h, l, c]
    jdf['Date'] = pd.to_datetime(jdf.Date)
    return jdf.reset_index().drop(['index'], axis=1)
import yfinance as yf
import pandas as pd
from jugaad_data.nse import stock_df, index_df, NSELive


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


def getStockData(ticker, start, end, liveData = {}):
    if ticker not in liveData:
        quote = NSELive().stock_quote(ticker)
        info = quote['priceInfo']
        date = pd.to_datetime(quote['metadata']['lastUpdateTime'])
        o = info['open']
        h = info['intraDayHighLow']['max']
        l = info['intraDayHighLow']['min']
        c = info['lastPrice']
        v = 0
    else:
        info = liveData[ticker]
        date = info['date']
        o = info['open']
        h = info['high']
        l = info['low']
        c = info['close']
        v = info['volume']

    jdf = getJugaadData(ticker, start, end)
    jdf.loc[len(jdf)] = [date, o, h, l, c, v]
    jdf['Date'] = pd.to_datetime(jdf.Date).dt.date
    
    # delete last row
    if jdf['Date'][len(jdf.index)-1] == jdf['Date'][len(jdf.index)-2]:
        jdf.drop(index=jdf.index[-1], axis=0, inplace=True)

    
    return jdf.reset_index().drop(['index'], axis=1)


def getIndexData(indexName, start, end, liveData={}):
    
    if indexName not in liveData:
        liveIndexData = NSELive().live_index(indexName)
        date = pd.to_datetime(liveIndexData['timestamp'])
        metadata = liveIndexData['metadata']
        o = metadata['open']
        l = metadata['low']
        h = metadata['high']
        c = metadata['last']
    else:
        date = liveData[indexName]['date']
        o = liveData[indexName]['open']
        l = liveData[indexName]['low']
        h = liveData[indexName]['high']
        c = liveData[indexName]['close']
    
    jdf = index_df(symbol=indexName, from_date=start, to_date=end)
    jdf = jdf[['HistoricalDate', 'OPEN', 'HIGH', 'LOW', 'CLOSE']]
    jdf.rename(columns = {
            'HistoricalDate':'Date',
            'OPEN':'Open', 
            'HIGH':'High', 
            'LOW':'Low',
            'CLOSE':'Close', 
        }, inplace = True)
    jdf = jdf.loc[::-1].reset_index().drop(['index'], axis=1)

    jdf.loc[len(jdf)] = [date, o, h, l, c]
    jdf['Date'] = pd.to_datetime(jdf.Date).dt.date

    # delete last row
    if jdf['Date'][len(jdf.index)-1] == jdf['Date'][len(jdf.index)-2]:
        jdf.drop(index=jdf.index[-1], axis=0, inplace=True)
    
    return jdf.reset_index().drop(['index'], axis=1)
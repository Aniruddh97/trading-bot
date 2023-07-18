from jugaad_data.nse import NSELive
import pandas as pd


def getStockList(label='NIFTY 50'):
    nifty50 = NSELive().live_index(label)['data'][1:]
    niftyData = {}
    tickerList = []
    
    for stock in nifty50:
        tickerList.append(stock['symbol'])
        niftyData[stock['symbol']] = {
        'date': pd.to_datetime(stock['lastUpdateTime']),
        'open': stock['open'],
        'high': stock['dayHigh'],
        'low': stock['dayLow'],
        'close': stock['lastPrice'],
        'volume': stock['totalTradedVolume'],
    }
        
    if not all:
        return ['ITC', 'WIPRO', 'RELIANCE', 'NESTLEIND', 'TATAMOTORS'], niftyData
    return tickerList, niftyData


def getIndicesList():
    allIndices = NSELive().all_indices()
    date = pd.to_datetime(allIndices['timestamp'])
    indexData = {}
    indexList = []
    
    for idx in allIndices['data']:
        indexList.append(idx['index'])
        indexData[idx['index']] = {
            'date': date,
            'open': idx['open'],
            'high': idx['high'],
            'low': idx['low'],
            'close': idx['last'],
        }
        
    # return indexList, indexData
    return ['NIFTY 50', 'NIFTY BANK'], indexData
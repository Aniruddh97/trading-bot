from jugaad_data.nse import NSELive
import pandas as pd


def getStockList(all=False):
    nifty50 = NSELive().live_index("NIFTY 50")['data'][1:]
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


def getIndicesList(all=False):
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
        
    if not all:
        return ['NIFTY 50', 'NIFTY BANK'], indexData
    return indexList, indexData
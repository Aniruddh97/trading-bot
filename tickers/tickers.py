import time
from jugaad_data.nse import NSELive
import pandas as pd

def getStockList(label='NIFTY 50'):
    nifty50 = {}
    tries = 3
    for i in range(tries):
        try:
            nifty50 = NSELive().live_index(label)['data'][1:]	
        except:
            if i < tries - 1:
                time.sleep(i+1)
                continue
            else:
                break

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
        
    if len(nifty50) == 0:
        return NIFTY100, {}
    return tickerList, niftyData


def getIndicesList():
    tries = 3
    for i in range(tries):
        try:
            allIndices = NSELive().all_indices()
            date = pd.to_datetime(allIndices['timestamp'])
        except:
            if i < tries - 1:
                time.sleep(i+1)
                continue
            else:
                allIndices = None
                break
            
    indexData = {}
    indexList = []
    
    if allIndices != None:
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


NIFTY100 = ['ZOMATO',
 'M&M',
 'DIVISLAB',
 'NYKAA',
 'SUNPHARMA',
 'PIIND',
 'ICICIGI',
 'GRASIM',
 'INDUSTOWER',
 'NAUKRI',
 'NTPC',
 'GODREJCP',
 'ULTRACEMCO',
 'SRF',
 'HINDALCO',
 'LT',
 'SBICARD',
 'ICICIBANK',
 'HDFCAMC',
 'CANBK',
 'BANKBARODA',
 'SIEMENS',
 'SBILIFE',
 'UPL',
 'LICI',
 'HEROMOTOCO',
 'ABB',
 'HAVELLS',
 'PGHH',
 'TORNTPHARM',
 'PAGEIND',
 'MARUTI',
 'JINDALSTEL',
 'COLPAL',
 'DRREDDY',
 'HCLTECH',
 'HDFCBANK',
 'VBL',
 'TECHM',
 'MOTHERSON',
 'BAJAJFINSV',
 'RELIANCE',
 'BHARTIARTL',
 'PIDILITIND',
 'COALINDIA',
 'HAL',
 'HINDUNILVR',
 'BAJAJHLDNG',
 'ADANITRANS',
 'MUTHOOTFIN',
 'INFY',
 'JSWSTEEL',
 'TCS',
 'ADANIPORTS',
 'APOLLOHOSP',
 'ICICIPRULI',
 'SHREECEM',
 'HDFCLIFE',
 'IRCTC',
 'WIPRO',
 'AWL',
 'TATAMOTORS',
 'LTIM',
 'DMART',
 'BOSCHLTD',
 'IOC',
 'KOTAKBANK',
 'EICHERMOT',
 'MARICO',
 'AMBUJACEM',
 'POWERGRID',
 'ASIANPAINT',
 'GAIL',
 'BAJAJ-AUTO',
 'ITC',
 'TATASTEEL',
 'SBIN',
 'BERGEPAINT',
 'TITAN',
 'BEL',
 'ATGL',
 'CIPLA',
 'AXISBANK',
 'INDUSINDBK',
 'TATAPOWER',
 'TATACONSUM',
 'BPCL',
 'ADANIENT',
 'ONGC',
 'BAJFINANCE',
 'DLF',
 'NESTLEIND',
 'ACC',
 'CHOLAFIN',
 'INDIGO',
 'DABUR',
 'MCDOWELL-N',
 'BRITANNIA',
 'VEDL',
 'ADANIGREEN']
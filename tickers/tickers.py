from jugaad_data.nse import NSELive

def getTickerList(all=False):
    nifty50 = NSELive().live_index("NIFTY 50")['data'][1:]
    niftyData = {}
    tickerList = []
    
    for stock in nifty50:
        tickerList.append(stock['symbol'])
        niftyData[stock['symbol']] = {
        'open': stock['open'],
        'high': stock['dayHigh'],
        'low': stock['dayLow'],
        'close': stock['lastPrice'],
        'volume': stock['totalTradedVolume'],
    }
        
    if not all:
        return ['ITC', 'WIPRO', 'RELIANCE', 'NESTLEIND', 'TATAMOTORS'], niftyData
    return tickerList, niftyData
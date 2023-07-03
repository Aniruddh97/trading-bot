import yfinance as yf
import talib
from tickers import tickers,patterns
from indicators import ChannelBreakoutIndicator
from tqdm import tqdm


tickerShortlist = {}
tickerShortlistData = {}

for i in tqdm(range(len(tickers))):
    ticker = tickers[i]
    resultDict = {}

    # Fetch Data
    data = yf.download(ticker, period='6mo', interval='1d', group_by='columns', progress=False, ignore_tz=False)
    data.insert(loc=0, column='Date', value=data.index)
    data.insert(loc=0, column='Index', value=list(range(0,len(data.index))))
    df = data.set_index('Index')
    
    # RSI
    df['RSI'] = ta.rsi(df.Close, length=14)
    resultDict["RSI"] = df['RSI'][len(df)-1]

    # Candlestick Pattern Recognition
    dfp = df[-5:]
    op = dfp['Open']
    hi = dfp['High']
    lo = dfp['Low']
    cl = dfp['Close']
    for pattern in patterns:
        sig = getattr(talib, pattern)(op, hi, lo, cl)[len(df)-1]
        if sig != 0:
            resultDict[pattern] = sig
    if (len(resultDict) != 0):
        tickerShortlist[ticker] = resultDict
    
    # Channel Breakout Indicator Signal
    cbIndicator = ChannelBreakoutIndicator(df)
    cbIndicator.calculate(40)
    cbSignal = cbIndicator.getBuySell()[-1]
    resultDict["ChannelBreakoutIndicator"] = cbSignal
    if (cbSignal != ''):
        tickerShortlist[ticker] = resultDict

print(tickerShortlist)
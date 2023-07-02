import yfinance as yf
import talib
from tickers import my_tickers, patterns

data = yf.download(my_tickers, period='2d', interval='1d', group_by='columns', progress=False, ignore_tz=False)

for ticker in my_tickers:
	df = data[ticker]
	op = df['Open']
	hi = df['High']
	lo = df['Low']
	cl = df['Close']
	for candle in patterns:
		data.loc[:, (ticker, candle)] = getattr(talib, candle)(op, hi, lo, cl)
		
data.to_csv('ticker.csv')
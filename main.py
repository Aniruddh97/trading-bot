from tqdm import tqdm
from datasource import getFullData
from datemodule import getDateRange
from tickers import getTickerList, recognizePattern
from indicators import ChannelBreakoutIndicator, SupportResistanceIndicator

import pandas
import pandas_ta as ta


class TradingBot():
	niftyStockData = {}
	promisingStocks = {}
	indicatorCollection = {}
		

	def loadData(self, timePeriod = '6m', all=True, forceUpdate=False):
		stocks, stockLiveData = getTickerList(all=all)
		startDate, endDate = getDateRange(timePeriod)
		localNiftyStockData = {}

		if len(self.niftyStockData) == 0 or forceUpdate:
			for stock in tqdm(stocks):
				localNiftyStockData[stock] = getFullData(stock, startDate, endDate, stockLiveData)
			self.niftyStockData = localNiftyStockData


	def computeSignal(self, all=True):
		if len(self.niftyStockData) == 0:
			print("Nifty 50 stock data not found!")

		localPromisingStocks = {}
		for stock in tqdm(self.niftyStockData):
			df = self.niftyStockData[stock]

			candleIndex = len(df)-1
			stockSignals = {}
			self.indicatorCollection[stock] = {}
			
			# RSI
			df['RSI'] = ta.rsi(df.Close, length=14)

			# Candlestick Pattern Signal
			df = recognizePattern(df, all=all)
			if df['candlestick_match_count'][candleIndex] > 0:
				stockSignals['Pattern'] = df['candlestick_pattern'][candleIndex]
				stockSignals['Pattern Count'] = df['candlestick_match_count'][candleIndex]
				stockSignals['Pattern Rank'] = df['candlestick_rank'][candleIndex]
			
			# Channel Breakout Indicator Signal
			# cbi = ChannelBreakoutIndicator(df, stock)
			# cbi.calculate(40)
			# cbSignal = cbi.getBuySell()[-1]
			# if cbSignal != '':
			# 	stockSignals["ChannelBreakoutIndicator"] = cbSignal
			# self.indicatorCollection[stock]["cbi"] = cbi
				
			# Support Resistance Indicator Signal
			sri = SupportResistanceIndicator(df, 11, 5, stock)
			sri.calculate()
			srSignal = sri.getBuySell()[-1]
			if srSignal != '':
				stockSignals["SupportResistanceIndicator"] = srSignal
			self.indicatorCollection[stock]["sri"] = sri

			# Collect Signals
			if len(stockSignals) != 0 :
				stockSignals["RSI"] = df['RSI'][candleIndex]
				localPromisingStocks[stock] = stockSignals

			self.promisingStocks = localPromisingStocks
			

	def showCBI(self, all=False):
		stocks = self.promisingStocks
		if all:
			stocks = self.niftyStockData

		for stock in stocks:
			i = self.indicatorCollection[stock]["cbi"]
			i.showIndicator(candleIndex=len(i.df.index)-1, backCandles=40)


	def showSRI(self, all=False):
		stocks = self.promisingStocks
		if all:
			stocks = self.niftyStockData

		for stock in stocks:
			i = self.indicatorCollection[stock]["sri"]
			i.showIndicator(candleIndex=len(i.df.index)-1)

		
	def rank(self):
		shortlisted = pandas.DataFrame(self.promisingStocks).transpose()
		if 'Pattern Rank' in shortlisted:
			shortlisted = shortlisted.sort_values(by='Pattern Rank', ascending=True)
		return shortlisted
	

	def incompleteStocks(self):
		_, endDate = getDateRange('1d')
		for stock in self.niftyStockData:
			stockData = self.niftyStockData[stock]
			if stockData['Date'][len(stockData.index)-1] != pandas.to_datetime(endDate):
				print(stock)
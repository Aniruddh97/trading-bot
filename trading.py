import random
import pandas as pd
from database import Order
from IPython.display import clear_output


class PaperTrading:
    
	def __init__(self, tb):
		self.tb = tb
		self.db = Order()

	
	def trade(self):
		ticker = str(input("ticker : "))
		candleIndex = int(input("candleIndex : "))

		indicator = self.tb.indicatorCollection[ticker]['sri']
		indicator.showIndicator(candleIndex)
		data = indicator.df

		stoploss = float(input("stoploss : "))
		target = float(input("target : "))

		startdate = data['Date'][candleIndex]
		strikePrice = data['Close'][candleIndex]

		self.db.placeOrder(ticker, startdate, strikePrice, stoploss, target)


	def evaluateTrades(self):
		df = self.db.getOpenPositions()
		for _, row in df.iterrows():
			indicator = self.tb.indicatorCollection[row.ticker]['sri']
			data = indicator.df
			start = data.index[data['Date'] == pd.to_datetime(row.startdate).date()].tolist()[0]
			result, finalIndex = self.runEngine(data, start+1, row.target, row.stop_loss, row.strike_price)

			if result != 0:
				print(f"startIndex : {start}")
				print(f"finalIndex : {finalIndex}")
				indicator.showIndicator(finalIndex)
				input(f"\nPress enter to continue...")
				self.db.closeOrder(row.id, result, data['Date'][finalIndex])


	def quiz(self, mode = 'random', rounds = 5):
		if mode == 'random':
			self.randomQuiz(rounds)


	def revisitLosses(self):
		df = self.db.read("SELECT * FROM orders where result = 'L'")
		for _, row in df.iterrows():
			indicator = self.tb.indicatorCollection[row.ticker]['sri']
			data = indicator.df
			start = data.index[data['Date'] == pd.to_datetime(row.startdate).date()].tolist()[0]
			candleIndex = start
			while candleIndex < data.index.stop-1 and candleIndex-start < 30:
				candleIndex += 1

			print(f'start index : {start}')
			print(row)
			indicator.showIndicator(candleIndex)
			input(f"\nPress enter to continue...")
			clear_output(wait=False)


	def randomQuiz(self, rounds):
		tickerList = list(self.tb.data.keys())
		maxProfit = maxLoss =totalRRR = tradeCount = balance = 0

		while tradeCount < rounds:
			tradeCount += 1
			clear_output(wait=False)
			
			randomTicker = tickerList[random.randint(0, len(tickerList)-1)]
			indicator = self.tb.indicatorCollection[randomTicker]['sri']
			data = indicator.df

			candleIndex = random.randint(50, len(data.index)-51)
			
			indicator.showIndicator(candleIndex)
			if not bool(float(input("trade (1/0): "))):
				tradeCount -= 1
				indicator.showIndicator(candleIndex+5)
				input(f"\nPress enter to continue...")
				continue
			

			stoploss = float(input("stoploss : "))
			target = float(input("target : "))
			currentPrice = data.Close[candleIndex]
			RRR = abs(target - currentPrice)/abs(stoploss - currentPrice)
			print(f'RRR = {RRR}')

			start = candleIndex + 1
			result, finalIndex = self.runEngine(data, start, target, stoploss, currentPrice)
			
			if result < 0:
				print(f"You've booked a loss of Rs{abs(result)}")
				maxLoss = result if result < maxLoss else maxLoss
				totalRRR += RRR
			elif result > 0:
				print(f"You've made a profit of Rs{result}")
				maxProfit = result if result > maxProfit else maxProfit
				totalRRR += RRR
			else:
				print(f"No outcome after {finalIndex - start} iterations")
				tradeCount -= 1
			
			indicator.showIndicator(finalIndex)
				
			balance += result
			input(f"\nPress enter to continue...\n")
			
			
		print(f"Your account balance after {tradeCount} trades is : {balance}")
		print(f'Biggest Proft {maxProfit}')
		print(f'Biggest Loss {maxLoss}')
		print(f'Average RRR {totalRRR/tradeCount}')
			

	def runEngine(self, data, start, target, stoploss, strikePrice):
		end = len(data.index) - 1
		position = 'LONG' if target > strikePrice else 'SHORT'

		result = 0
		finalIndex = start

		for i in range(start, end):
			if position == 'LONG':
				if data.Low[i] <= stoploss:
					result = stoploss - strikePrice
				elif data.High[i] >= target:
					result = target - strikePrice
			else:
				if data.Low[i] <= target:
					result = strikePrice - target
				elif data.High[i] >= stoploss:
					result = strikePrice - stoploss

			finalIndex = i
			if result != 0:
				break
		
		if result != 0:
			result = result * (100/strikePrice)
			
		return result, finalIndex
	
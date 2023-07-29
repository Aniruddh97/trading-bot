import random
import sqlite3
from IPython.display import clear_output


class PaperTrading:
    
	def __init__(self, tb):
		self.tb = tb
		self.conn = sqlite3.connect('../database/orders.sqlite')


	def recent(self, rounds=5, recency = 7):
		self.runEngine(rounds, "recent", {
			"recency": recency
		})


	def future(self):
		pass

	
	def random(self, rounds = 5):
		self.runEngine(rounds, "random")


	def runEngine(self, rounds=5, flag="random", options={}):
		tickerList = list(self.tb.data.keys())
		maxProfit = 0
		maxLoss = 0
		totalRRR = 0
		tradeCount = 0
		balance = 0

		while tradeCount < rounds:
			tradeCount += 1
			clear_output(wait=False)
			
			randomTicker = tickerList[random.randint(0, len(tickerList)-1)]
			indicator = self.tb.indicatorCollection[randomTicker]['sri']
			
			candleIndex = random.randint(50, len(indicator.df.index)-51)
			if flag == "recent":
				candleIndex = len(indicator.df.index) - 1 - options["recency"]
			
			indicator.showIndicator(candleIndex)
			if not bool(float(input("trade? (1/0): "))):
				tradeCount -= 1
				indicator.showIndicator(candleIndex+5)
				input(f"\nPress enter to continue...")
				continue
			

			stoploss = float(input("stoploss : "))
			target = float(input("target : "))
			currentPrice = indicator.df.Close[candleIndex]
			RRR = abs(target - currentPrice)/abs(stoploss - currentPrice)
			print(f'RRR = {RRR}')

			trade = 'long' if target > currentPrice else 'short'
			data = indicator.df

			result = 0
			start = candleIndex+1
			end = len(indicator.df.index) - 1
			resultCandleIndex = start
			for i in range(start, end):
				if trade == 'long':
					if data.Low[i] <= stoploss:
						result = stoploss - currentPrice
					elif data.High[i] >= target:
						result = target - currentPrice
				else:
					if data.Low[i] <= target:
						result = currentPrice - target
					elif data.High[i] >= stoploss:
						result = currentPrice - stoploss

				if result < 0:
					result = result * (500/currentPrice)
					print(f"You've booked a loss of Rs{abs(result)}")
					maxLoss = result if result < maxLoss else maxLoss
					totalRRR += RRR
					indicator.showIndicator(i)
					break	
				elif result > 0:
					result = result * (500/currentPrice)
					print(f"You've made a profit of Rs{result}")
					maxProfit = result if result > maxProfit else maxProfit
					totalRRR += RRR
					indicator.showIndicator(i)
					break
				else:
					resultCandleIndex = i
					continue

			if result == 0:
				print(f"No outcome after {end - start} iterations")
				tradeCount -= 1
				indicator.showIndicator(resultCandleIndex)
				
			balance += result
			input(f"\nPress enter to continue...")
			
			
		print(f"Your account balance after {tradeCount} trades is : {balance}")
		print(f'Biggest Proft {maxProfit}')
		print(f'Biggest Loss {maxLoss}')
		print(f'Average RRR {totalRRR/tradeCount}')
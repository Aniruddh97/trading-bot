import random
from IPython.display import clear_output


class Quiz:
    
	def __init__(self, tb):
		self.tb = tb


	def past(self):
		pass


	def future(self):
		pass


	def random(self, rounds = 5):
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
			randomCandleIndex = random.randint(0+30, len(indicator.df.index)-31)
			indicator.showIndicator(randomCandleIndex)
			
			if not bool(float(input("trade? (1/0): "))):
				tradeCount -= 1
				continue
			

			stoploss = float(input("stoploss : "))
			target = float(input("target : "))
			currentPrice = indicator.df.Close[randomCandleIndex]
			RRR = abs(target - currentPrice)/abs(stoploss - currentPrice)
			print(f'RRR = {RRR}')

			trade = 'long' if target > currentPrice else 'short'
			data = indicator.df

			result = 0
			start = randomCandleIndex+1
			end = randomCandleIndex + 30
			resultCandleIndex = start
			for i in range(start, end):
				if trade == 'long':
					if data.High[i] >= target:
						result = target - currentPrice
					elif data.Low[i] <= stoploss:
						result = stoploss - currentPrice
				else:
					if data.High[i] >= stoploss:
						result = currentPrice - stoploss
					elif data.Low[i] <= target:
						result = currentPrice - target
						
				if result > 0:
					result = result * (500/currentPrice)
					print(f"You've made a profit of Rs{result}")
					maxProfit = result if result > maxProfit else maxProfit
					totalRRR += RRR
					indicator.showIndicator(i)
					break
				elif result < 0:
					result = result * (500/currentPrice)
					print(f"You've booked a loss of Rs{abs(result)}")
					maxLoss = result if result < maxLoss else maxLoss
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
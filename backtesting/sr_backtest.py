from backtesting import Strategy
from backtesting import Backtest
from indicators import SupportResistanceIndicator
from datasource import getFullData
from datemodule import getDateRange

# import backtesting
# backtesting.set_bokeh_output(notebook=True)

class SupportResistanceBacktest(Strategy):
    mysize = 0.01
    window = 9
    backCandles = 5
    
    def init(self):
        super().init()
        data = self.data.copy(deep=True)
        indicator = SupportResistanceIndicator(data=data, window=self.window, backCandles=self.backCandles, tickerName=ticker)
        indicator.calculate()
        self.indicator = indicator
        self.signal = self.I(lambda : indicator.df.Signal)

    def next(self):
        super().next()
        RRR = 1.5

        if self.signal==2 and len(self.trades)==0:   
            # stoploss = just below support
            supportLevel = self.indicator.df['Level'][len(self.data)-1]
            sl = supportLevel - self.indicator.proximity
            # target = LTP + (stoploss * RRR)
            tp = self.data.Close[-1] + abs(self.data.Close[-1]-sl)*RRR
            # place BUY order
            self.buy(sl=sl, tp=tp, size=self.mysize, limit=None)
        
        elif self.signal==1 and len(self.trades)==0: 
            # stoploss = just above resistance
            resistanceLevel = self.indicator.df['Level'][len(self.data)-1]
            sl = resistanceLevel + self.indicator.proximity
            # target = LTP - (stoploss * RRR)
            tp = self.data.Close[-1] - abs(self.data.Close[-1]-sl)*RRR
            # place SELL order
            self.sell(sl=sl, tp=tp, size=self.mysize, limit=None)

ticker = "RELIANCE.NS"
startDate, endDate = getDateRange('2y')
data = getFullData(ticker=ticker, start=startDate, end=endDate)

bt = Backtest(data, SupportResistanceBacktest, cash=300000, margin=1/10, commission=.002)
print(bt.run())
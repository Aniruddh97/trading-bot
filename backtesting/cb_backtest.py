from backtesting import Strategy
from backtesting import Backtest
from indicators import ChannelBreakoutIndicator
import backtesting
import yfinance as yf

# backtesting.set_bokeh_output(notebook=True)

class BreakOut(Strategy):
    initsize = 0.1
    mysize = initsize
    
    def init(self):
        super().init()
        self.signal = self.I(SIGNAL)

    def next(self):
        super().next()
        RRR = 1.2

        if self.signal==2 and len(self.trades)==0:   
            # stoploss = prev candle LOW
            sl1 = self.data.Low[-2] 
            # target = LTP - stoploss * RRR
            tp1 = self.data.Close[-1] + abs(self.data.Close[-1]-sl1)*RRR
            # place BUY order
            self.buy(sl=sl1, tp=tp1, size=self.mysize, limit=None)
        
        elif self.signal==1 and len(self.trades)==0: 
            # stoploss = prev candle HIGH
            sl1 = self.data.High[-2]
            # target = LTP - stoploss * RRR
            tp1 = self.data.Close[-1] - abs(sl1-self.data.Close[-1])*RRR
            # place SELL order
            self.sell(sl=sl1, tp=tp1, size=self.mysize, limit=None)


data = yf.download('RELIANCE.NS', period='10y', interval='1d', group_by='columns', progress=False, ignore_tz=False)
data.insert(loc=0, column='Date', value=data.index)
data.insert(loc=0, column='Index', value=list(range(0,len(data.index))))
df = data.set_index('Index')

indicator = ChannelBreakoutIndicator(df)
indicator.setSignal(40)

def SIGNAL():
    return indicator.df.isBreakout

bt = Backtest(df, BreakOut, cash=100000, margin=1/50, commission=.002)
print(bt.run())
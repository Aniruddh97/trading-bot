import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

class SupportResistanceIndicator:

    def __init__(self, data, window, backCandles):
        self.window = window
        self.backCandles = backCandles
        self.df = data
        self.df['RSI'] = ta.rsi(data.Close, length=14)

        # candle proximity with a level
        self.proximity = (((data.High.mean())-data.Low.mean())/data.High.mean()) * 50
        # proximity b/w levels
        self.levelProximity = max(data.High)/100


    def getLevels(self):
        dfSlice = self.df[-252:]
        supports = dfSlice[dfSlice.Low == dfSlice.Low.rolling(self.window, center=True).min()].Low
        resistances = dfSlice[dfSlice.High == dfSlice.High.rolling(self.window, center=True).max()].High
        levels = pd.concat([supports, resistances])
        return levels[abs(levels.diff()) > self.levelProximity]


    def isCloseToResistance(self, candleIndex, levels):
        if len(levels)==0:
            return 0
        minLevel = min(levels, key=lambda x:abs(x-self.df.High[candleIndex]))
        c1 = abs(self.df.High[candleIndex]-minLevel)<=self.proximity
        c2 = abs(max(self.df.Open[candleIndex],self.df.Close[candleIndex])-minLevel)<=self.proximity
        c3 = min(self.df.Open[candleIndex],self.df.Close[candleIndex])<minLevel
        c4 = self.df.Low[candleIndex]<minLevel
        if( (c1 or c2) and c3 and c4 ):
            return minLevel
        else:
            return 0
    
    
    def isCloseToSupport(self, candleIndex, levels):
        if len(levels)==0:
            return 0
        minLevel = min(levels, key=lambda x:abs(x-self.df.Low[candleIndex]))
        c1 = abs(self.df.Low[candleIndex]-minLevel)<=self.proximity
        c2 = abs(min(self.df.Open[candleIndex],self.df.Close[candleIndex])-minLevel)<=self.proximity
        c3 = max(self.df.Open[candleIndex],self.df.Close[candleIndex])>minLevel
        c4 = self.df.High[candleIndex]>minLevel
        if( (c1 or c2) and c3 and c4 ):
            return minLevel
        else:
            return 0
        

    def arePrevCandlesBelowResistance(self, candleIndex, level):
        return self.df.loc[candleIndex-self.backCandles:candleIndex-1, 'High'].max() < level


    def arePrevCandlesAboveSupport(self, candleIndex, level):
        return self.df.loc[candleIndex-self.backCandles:candleIndex-1, 'Low'].min() > level  


    def getCandleSignal(self, candleIndex):
        levels = self.getLevels()

        cR = self.isCloseToResistance(candleIndex, levels)
        cS = self.isCloseToSupport(candleIndex, levels)

        if (cR and self.arePrevCandlesBelowResistance(candleIndex, cR) and self.df.RSI[candleIndex-1:candleIndex].min()<45 ):#and df.RSI[l]>65
            return 1
        elif(cS and self.arePrevCandlesAboveSupport(candleIndex, cS) and self.df.RSI[candleIndex-1:candleIndex].max()>55 ):#and df.RSI[l]<35
            return 2
        else:
            return 0


    def showIndicator(self, candles):
        dfSlice = self.df[-candles:]
        fig = go.Figure(data=[go.Candlestick(x=dfSlice.index,
                        open=dfSlice["Open"],
                        high=dfSlice["High"],
                        low=dfSlice["Low"],
                        close=dfSlice["Close"])])
        

        levels = self.getLevels()
        levels = levels[levels > (min(dfSlice.Close) - self.levelProximity)]
        levels = levels[levels < (max(dfSlice.High) + self.levelProximity)]

        for level in levels.to_list():
            fig.add_shape(
                type='line',
                x0=dfSlice.index.start - 2,
                y0=level,
                x1=dfSlice.index.stop + 2,
                y1=level,
                line=dict(color='blue'),
                xref='x',
                yref='y',
                layer='below'
            )

        fig.add_scatter(x=dfSlice.index, y=dfSlice["SignalMarker"], mode="markers",
                        marker=dict(size=7, color="Black"), marker_symbol="hexagram",
                        name="signal")

        fig.show()
        
    
    def setSignalMarker(self):
        self.df["SignalMarker"] = [self.getSignalMarker(row) for index, row in self.df.iterrows()]


    def getSignalMarker(self, x):
        markerDistance = (x["High"]-x["Low"])/10
        if x["Signal"]==2:
            return x["Low"]-markerDistance
        elif x["Signal"]==1:
            return x["High"]+markerDistance
        else:
            return np.nan
        
    
    def calculate(self):
        self.setSignal()
        self.setSignalMarker()


    def setSignal(self):
        self.df["Signal"] = self.getSignal()


    def getSignal(self):
        return [self.getCandleSignal(candle) for candle in self.df.index]
        
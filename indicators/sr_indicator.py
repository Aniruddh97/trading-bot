import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class SupportResistanceIndicator:

    def __init__(self, data, window, backCandles, tickerName=''):
        self.window = window
        self.backCandles = backCandles
        self.df = data
        self.tickerName = tickerName
        self.RRR = 1.5
        self.df['RSI'] = ta.rsi(data.Close, length=14)
        self.df["EMA14"] = ta.ema(data.Close, length=14)
        self.df["EMA26"] = ta.ema(data.Close, length=26)
        self.df['Level'] = 0

        # candle proximity with a level
        self.proximity = (data.High.mean()-data.Low.mean()) / 4
        # proximity b/w levels
        self.levelProximity = max(data.High)/100


    def getLevels(self, candleIndex):
        dfSlice = self.df[0:candleIndex+1]
        supports = dfSlice[dfSlice.Low == dfSlice.Low.rolling(self.window, center=True).min()].Low
        resistances = dfSlice[dfSlice.High == dfSlice.High.rolling(self.window, center=True).max()].High
        levels = pd.concat([supports, resistances])
        return levels
        # return levels[abs(levels.diff()) > self.levelProximity]


    def isCloseToResistance(self, candleIndex, levels):
        if len(levels)==0:
            return 0
        minLevel = min(levels, key=lambda x:abs(x-self.df.High[candleIndex]))
        c1 = abs(self.df.High[candleIndex]-minLevel)<=self.proximity
        c2 = abs(max(self.df.Open[candleIndex],self.df.Close[candleIndex])-minLevel)<=self.proximity
        c3 = min(self.df.Open[candleIndex],self.df.Close[candleIndex])<minLevel
        c4 = self.df.Low[candleIndex]<minLevel
        c5 = self.df.Close[candleIndex] > min(self.df.Close[candleIndex-self.backCandles:candleIndex-1])
        if( (c1 or c2) and c3 and c4 and c5):
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
        c5 = self.df.Close[candleIndex] < max(self.df.Close[candleIndex-self.backCandles:candleIndex-1])
        if( (c1 or c2) and c3 and c4 and c5):
            return minLevel
        else:
            return 0
        

    def arePrevCandlesBelowResistance(self, candleIndex, level):
        return self.df.loc[candleIndex-self.backCandles:candleIndex-1, 'High'].max() < level


    def arePrevCandlesAboveSupport(self, candleIndex, level):
        return self.df.loc[candleIndex-self.backCandles:candleIndex-1, 'Low'].min() > level  


    def getCandleSignal(self, candleIndex):
        levels = self.getLevels(candleIndex)

        cR = self.isCloseToResistance(candleIndex, levels)
        cS = self.isCloseToSupport(candleIndex, levels)

        if (cR and self.arePrevCandlesBelowResistance(candleIndex, cR) and self.df.RSI[candleIndex-1:candleIndex].min()<45 ):#and df.RSI[l]>65
            self.df.loc[candleIndex, 'Level'] = cR
            return 1
        elif(cS and self.arePrevCandlesAboveSupport(candleIndex, cS) and self.df.RSI[candleIndex-1:candleIndex].max()>55 ):#and df.RSI[l]<35
            self.df.loc[candleIndex, 'Level'] = cS
            return 2
        else:
            return 0


    def showIndicator(self, candleIndex):
        self.getIndicator(candleIndex).show()
        

    def getIndicator(self, candleIndex):
        start = candleIndex-50
        if start < 0:
            start = 0
        dfSlice = self.df[start:candleIndex+1]

        patternTitle = dfSlice['candlestick_pattern'][dfSlice.index.stop-1][3:].lower()
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
               vertical_spacing=0.05, subplot_titles=(self.tickerName, patternTitle), 
               row_width=[0.2, 0.7])

        # draw EMAS
        # fig.add_scatter(x=dfSlice.index, y=dfSlice.EMA14, line=dict(color="blue", width=1), name="EMA14", row=1, col=1),
        # fig.add_scatter(x=dfSlice.index, y=dfSlice.EMA26, line=dict(color="maroon", width=1), name="EMA26", row=1, col=1),

        
        levels = self.getLevels(candleIndex)
        # ------------------
        # for better visuals
        levels = levels[levels > (min(dfSlice.Close) - self.levelProximity)]
        levels = levels[levels < (max(dfSlice.High) + self.levelProximity)]
        # ------------------

        # draw levels
        for level in levels.to_list():
            fig.add_shape(
                type='line',
                x0=dfSlice.index.start - 2,
                y0=level,
                x1=dfSlice.index.stop + 2,
                y1=level,
                line=dict(color="darkslategray"),
                xref='x',
                yref='y',
                layer='below',
                row= 1,
                col=1
            )
            
        # draw candlestick
        fig.add_trace(go.Candlestick(x=dfSlice.index,
                                open=dfSlice["Open"],
                                high=dfSlice["High"],
                                low=dfSlice["Low"],
                                close=dfSlice["Close"]), row=1, col=1)

        # plot volume
        if 'Volume' in dfSlice:
            fig.add_trace(go.Bar(x=dfSlice.index, y=dfSlice['Volume'], showlegend=False), row=2, col=1)

        # fig.add_scatter(x=dfSlice.index, y=dfSlice["SignalMarker"], mode="markers",
        #                 marker=dict(size=7, color="Black"), marker_symbol="hexagram", name="signal")
        # if 'Target' in dfSlice and 'Stoploss' in dfSlice:
        #     fig.add_scatter(x=dfSlice.index, y=dfSlice["Target"], mode="markers",
        #                     marker=dict(size=7, color="darkgreen"), name="target")
        #     fig.add_scatter(x=dfSlice.index, y=dfSlice["Stoploss"], mode="markers",
        #                     marker=dict(size=7, color="darkred"), name="stoploss")

        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.update(layout_showlegend=False)
        return fig
        
    
    def getSignalMarker(self, x):
        markerDistance = (x["High"]-x["Low"])/10
        if x["Signal"]==2:
            return x["Low"]-markerDistance
        elif x["Signal"]==1:
            return x["High"]+markerDistance
        else:
            return np.nan
        

    def setSignalMarker(self):
        self.df["SignalMarker"] = [self.getSignalMarker(row) for index, row in self.df.iterrows()]

    
    def calculate(self, all=True):
        self.setSignal(all)
        self.setSignalMarker()
        self.setTarget()
        self.setStoploss()


    def getSignal(self, all=True):
        if all:
            return [self.getCandleSignal(index) for index in self.df.index]
        return [self.getCandleSignal(index) if index == len(self.df.index)-1 else 0 for index in self.df.index]
        

    def setSignal(self, all=True):
        self.df["Signal"] = self.getSignal(all)


    def getBuySell(self):
        return ["SELL" if row.Signal == 1 else "BUY" if row.Signal == 2 else "" for index, row in self.df.iterrows()]
    

    def getTarget(self, candleIndex):
        if self.df['Signal'][candleIndex] == 2:
            support = self.df['Level'][candleIndex]
            sl = support - self.proximity
            return self.df.Close[candleIndex] + abs(self.df.Close[candleIndex]-sl)*self.RRR
        elif self.df['Signal'][candleIndex] == 1:
            resistance = self.df['Level'][candleIndex]
            sl = resistance + self.proximity
            return self.df.Close[candleIndex] - abs(self.df.Close[candleIndex]-sl)*self.RRR
        else:
            return np.nan
    

    def setTarget(self):
        self.df['Target'] = [self.getTarget(index) for index in self.df.index]


    def getStoploss(self, candleIndex):
        if self.df['Signal'][candleIndex] == 2:
            return self.df['Level'][candleIndex] - (2*self.proximity)
        elif self.df['Signal'][candleIndex] == 1:
            return self.df['Level'][candleIndex] + (2*self.proximity)
        else:
            return np.nan
        
    
    def setStoploss(self):
        self.df['Stoploss'] = [self.getStoploss(index) for index in self.df.index]
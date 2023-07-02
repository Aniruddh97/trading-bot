import numpy as np
import plotly.graph_objects as go
from scipy import stats

class ChannelBreakoutIndicator:

    def __init__(self, data, tickerName=''):
        self.window = 4
        self.df = data
        self.tickerName = tickerName


    def isPivot(self, candleIndex):
        """
        function that detects if a candle is a pivot/fractal point
        args: candle index, window before and after candle to test if pivot
        returns: 1 if pivot high, 2 if pivot low, 3 if both and 0 default
        """
        if candleIndex-self.window < 0 or candleIndex+self.window >= len(self.df):
            return 0
        
        pivotHigh = 1
        pivotLow = 2
        for i in range(candleIndex-self.window, candleIndex+self.window+1):
            if self.df.iloc[candleIndex].Low > self.df.iloc[i].Low:
                pivotLow=0
            if self.df.iloc[candleIndex].High < self.df.iloc[i].High:
                pivotHigh=0
        if (pivotHigh and pivotLow):
            return 3
        elif pivotHigh:
            return pivotHigh
        elif pivotLow:
            return pivotLow
        else:
            return 0
    

    def setPivotPoint(self):
        self.df["isPivot"] = [self.isPivot(candleIndex) for candleIndex in self.df.index]


    def getPivotMarker(self, x):
        markerDistance = (x["High"]-x["Low"])/10
        if x["isPivot"]==2:
            return x["Low"] - markerDistance
        elif x["isPivot"]==1:
            return x["High"] + markerDistance
        else:
            return np.nan
    

    def setPivotMarker(self):
        self.df["pivotMarker"] = [self.getPivotMarker(row) for index, row in self.df.iterrows()]
        
    
    def showPivotMarkers(self, startIndex=0, endIndex=0):
        if (endIndex<=startIndex or startIndex<0 or endIndex>=len(self.df)):
            print("\n Invalid startIndex or endIndex")
            
        dfSlice = self.df[startIndex:endIndex]
        fig = go.Figure(data=[go.Candlestick(x=dfSlice.index,
                        open=dfSlice["Open"],
                        high=dfSlice["High"],
                        low=dfSlice["Low"],
                        close=dfSlice["Close"])])

        fig.add_scatter(x=dfSlice.index, y=dfSlice["pivotMarker"], mode="markers",
                        marker=dict(size=7, color="MediumPurple"),
                        name="pivotMarker")
        #fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(title_text=self.tickerName, title_font_size=18)
        fig.show()


    def getChannel(self, candleIndex, backCandles):
        localdf = self.df[candleIndex-backCandles-self.window:candleIndex-self.window]
        
        highs = localdf[localdf["isPivot"]==1].High.values
        idxhighs = localdf[localdf["isPivot"]==1].High.index
        lows = localdf[localdf["isPivot"]==2].Low.values
        idxlows = localdf[localdf["isPivot"]==2].Low.index
        
        if len(lows)>=2 and len(highs)>=2:
            slopeLow, interceptLow, rValueLow, _, _ = stats.linregress(idxlows,lows)
            slopeHigh, interceptHigh, rValueHigh, _, _ = stats.linregress(idxhighs,highs)
        
            return(slopeLow, interceptLow, slopeHigh, interceptHigh, rValueLow**2, rValueHigh**2)
        else:
            return(0,0,0,0,0,0)
        

    def showChannel(self, candleIndex, backCandles):

        if (candleIndex-backCandles<0 or candleIndex>len(self.df)):
            print("\n Invalid candleIndex & backCandles combination")
            return

        startIndex = candleIndex-backCandles
        endIndex = candleIndex

        # below code for better visualization
        for _ in range(3):
            if (startIndex-10>0):
                startIndex -= 10
            if (endIndex+10<=len(self.df)):
                endIndex += 10
        # above code for better visualization

        dfSlice = self.df[startIndex:endIndex+1]
        
        fig = go.Figure(data=[go.Candlestick(x=dfSlice.index,
                        open=dfSlice["Open"],
                        high=dfSlice["High"],
                        low=dfSlice["Low"],
                        close=dfSlice["Close"])])

        fig.add_scatter(x=dfSlice.index, y=dfSlice["pivotMarker"], mode="markers",
                        marker=dict(size=5, color="MediumPurple"),
                        name="pivotMarker")

        slopeLow, interceptLow, slopeHigh, interceptHigh, rSqLow, rSqHigh = self.getChannel(candleIndex, backCandles)
        print(rSqLow, rSqHigh)
        x = np.array(range(candleIndex-backCandles-self.window, candleIndex+1))
        fig.add_trace(go.Scatter(x=x, y=slopeLow*x + interceptLow, mode="lines", name="lower slope"))
        fig.add_trace(go.Scatter(x=x, y=slopeHigh*x + interceptHigh, mode="lines", name="max slope"))
        fig.update_layout(title_text=self.tickerName, title_font_size=18)
        #fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()

        
    def isBreakOut(self, candleIndex, backCandles):
        if (candleIndex-backCandles-self.window)<0:
            return 0
        
        slopeLow, interceptLow, slopeHigh, interceptHigh, rSqLow, rSqHigh = self.getChannel(candleIndex,backCandles)
        
        prev_idx = candleIndex-1
        prev_high = self.df.iloc[candleIndex-1].High
        prev_low = self.df.iloc[candleIndex-1].Low
        prev_close = self.df.iloc[candleIndex-1].Close
        
        curr_idx = candleIndex
        curr_high = self.df.iloc[candleIndex].High
        curr_low = self.df.iloc[candleIndex].Low
        curr_close = self.df.iloc[candleIndex].Close
        curr_open = self.df.iloc[candleIndex].Open

        # downward channel breakout
        if ( prev_high > (slopeLow*prev_idx + interceptLow) and
            prev_close < (slopeLow*prev_idx + interceptLow) and
            curr_open < (slopeLow*curr_idx + interceptLow) and
            curr_close < (slopeLow*prev_idx + interceptLow)): #and rSqLow > 0.9
            return 1
        
        # upward channel breakout
        elif ( prev_low < (slopeHigh*prev_idx + interceptHigh) and
            prev_close > (slopeHigh*prev_idx + interceptHigh) and
            curr_open > (slopeHigh*curr_idx + interceptHigh) and
            curr_close > (slopeHigh*prev_idx + interceptHigh)): #and rSqHigh > 0.9
            return 2
        
        else:
            return 0


    def getBreakoutMarker(self, x):
        markerDistance = (x["High"]-x["Low"])/10
        if x["isBreakout"]==2:
            return x["Low"]-markerDistance
        elif x["isBreakout"]==1:
            return x["High"]+markerDistance
        else:
            return np.nan
        

    def setBreakoutPoint(self, backCandles):
        self.df["isBreakout"] = [self.isBreakOut(candle, backCandles) for candle in self.df.index]


    def setBreakoutMarker(self):
        self.df["breakoutMarker"] = [self.getBreakoutMarker(row) for index, row in self.df.iterrows()]


    def showIndicator(self, candleIndex, backCandles):
        if (candleIndex-backCandles<0 or candleIndex>len(self.df)):
            print("\nInvalid candleIndex & backCandles combination")
            return

        startIndex = candleIndex-backCandles
        endIndex = candleIndex

        # below code for better visualization
        for _ in range(3):
            if (startIndex-5>0):
                startIndex -= 5
            if (endIndex+5<len(self.df)):
                endIndex += 5
        # above code for better visualization

        dfSlice = self.df[startIndex:endIndex+1]

        fig = go.Figure(data=[go.Candlestick(x=dfSlice.index,
                        open=dfSlice["Open"],
                        high=dfSlice["High"],
                        low=dfSlice["Low"],
                        close=dfSlice["Close"])])

        fig.add_scatter(x=dfSlice.index, y=dfSlice["pivotMarker"], mode="markers",
                        marker=dict(size=7, color="MediumPurple"),
                        name="pivot")

        fig.add_scatter(x=dfSlice.index, y=dfSlice["breakoutMarker"], mode="markers",
                        marker=dict(size=7, color="Black"), marker_symbol="hexagram",
                        name="breakout")

        slopeLow, interceptLow, slopeHigh, interceptHigh, rSqLow, rSqHigh = self.getChannel(candleIndex, backCandles)
        print(rSqLow, rSqHigh)
        x = np.array(range(candleIndex-backCandles-self.window, candleIndex+1))
        fig.add_trace(go.Scatter(x=x, y=slopeLow*x + interceptLow, mode="lines", name="lower slope"))
        fig.add_trace(go.Scatter(x=x, y=slopeHigh*x + interceptHigh, mode="lines", name="max slope"))
        #fig.update_layout(xaxis_rangeslider_visible=False)
        #fig.update_layout(title_text=self.tickerName, title_font_color='MediumBlue', title_font_size=21)
        fig.update_layout(title_text=self.tickerName, title_font_size=18)
        fig.show()


    def calculate(self, backCandles=40):
        self.setPivotPoint()
        self.setPivotMarker()
        self.setBreakoutPoint(backCandles)
        self.setBreakoutMarker()


    def setSignal(self, backCandles=40):
        self.df["Signal"] = self.getSignal()


    def getSignal(self):
        self.df.isBreakout
        

    def getBuySell(self):
        return ["SELL" if row.isBreakout == 1 else "BUY" if row.isBreakout == 2 else "" for index, row in self.df.iterrows()]
    
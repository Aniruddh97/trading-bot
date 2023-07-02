import numpy as np
import plotly.graph_objects as go
from scipy import stats

class SupportResistanceIndicator:

    def __init__(self, data):
        self.window = 4
        self.df = data
        self.wickThreshold = 0.001
        

    def support(self, candleIndex, candlesBefore, candlesAfter):
        if ( self.df.low[candleIndex-candlesBefore:candleIndex].min() < self.df.low[candleIndex] or
            self.df.low[candleIndex+1:candleIndex+candlesAfter+1].min() < self.df.low[candleIndex] ):
            return 0

        candle_body = abs(self.df.open[candleIndex]-self.df.close[candleIndex])
        lower_wick = min(self.df.open[candleIndex], self.df.close[candleIndex])-self.df.low[candleIndex]
        if (lower_wick > candle_body) and (lower_wick > self.wickThreshold): 
            return 1
        
        return 0
    

    def resistance(self, candleIndex, candlesBefore, candlesAfter):
        if ( self.df.high[candleIndex-candlesBefore:candleIndex].max() > self.df.high[candleIndex] or
            self.df.high[candleIndex+1:candleIndex+candlesAfter+1].max() > self.df.high[candleIndex] ):
            return 0
        
        candle_body = abs(self.df.open[candleIndex]-self.df.close[candleIndex])
        upper_wick = self.df.high[candleIndex]-max(self.df.open[candleIndex], self.df.close[candleIndex])
        if (upper_wick > candle_body) and (upper_wick > self.wickThreshold) :
            return 1

        return 0
    

    def closeResistance(self, l,levels,lim, df):
        if len(levels)==0:
            return 0
        minLevel = min(levels, key=lambda x:abs(x-df.high[l]))
        c1 = abs(df.high[l]-minLevel)<=lim
        c2 = abs(max(df.open[l],df.close[l])-minLevel)<=lim
        c3 = min(df.open[l],df.close[l])<minLevel
        c4 = df.low[l]<minLevel
        if( (c1 or c2) and c3 and c4 ):
            return minLevel
        else:
            return 0
    
    
    def closeSupport(self, l,levels,lim, df):
        if len(levels)==0:
            return 0
        minLevel = min(levels, key=lambda x:abs(x-df.low[l]))
        c1 = abs(df.low[l]-minLevel)<=lim
        c2 = abs(min(df.open[l],df.close[l])-minLevel)<=lim
        c3 = max(df.open[l],df.close[l])>minLevel
        c4 = df.high[l]>minLevel
        if( (c1 or c2) and c3 and c4 ):
            return minLevel
        else:
            return 0
        

    def isBelowResistance(self, l, level_backCandles, level, df):
        return df.loc[l-level_backCandles:l-1, 'high'].max() < level


    def isAboveSupport(self, l, level_backCandles, level, df):
        return df.loc[l-level_backCandles:l-1, 'low'].min() > level  


    def check_candle_signal(self, l, n1, n2, backCandles, df):
        ss = []
        rr = []
        for subrow in range(l-backCandles, l-n2):
            if self.support(df, subrow, n1, n2):
                ss.append(df.low[subrow])
            if self.resistance(df, subrow, n1, n2):
                rr.append(df.high[subrow])
        
        ss.sort() #keep lowest support when popping a level
        for i in range(1,len(ss)):
            if(i>=len(ss)):
                break
            if abs(ss[i]-ss[i-1])<=0.0001: # merging close distance levels
                ss.pop(i)

        rr.sort(reverse=True) # keep highest resistance when popping one
        for i in range(1,len(rr)):
            if(i>=len(rr)):
                break
            if abs(rr[i]-rr[i-1])<=0.0001: # merging close distance levels
                rr.pop(i)

        #----------------------------------------------------------------------
        # joined levels
        rrss = rr+ss
        rrss.sort()
        for i in range(1,len(rrss)):
            if(i>=len(rrss)):
                break
            if abs(rrss[i]-rrss[i-1])<=0.0001: # merging close distance levels
                rrss.pop(i)
        cR = self.closeResistance(l, rrss, 150e-5, df)
        cS = self.closeSupport(l, rrss, 150e-5, df)
        #----------------------------------------------------------------------

        # cR = closeResistance(l, rr, 150e-5, df)
        # cS = closeSupport(l, ss, 150e-5, df)
        # could we consider the average RSI for the trend momentum?
        if (cR and self.isBelowResistance(l,6,cR, df) and df.RSI[l-1:l].min()<45 ):#and df.RSI[l]>65
            return 1
        elif(cS and self.isAboveSupport(l,6,cS,df) and df.RSI[l-1:l].max()>55 ):#and df.RSI[l]<35
            return 2
        else:
            return 0


    def setSignal(self, backCandles=40):
        self.df["Signal"] = self.getSignal(backCandles)


    def getSignal(self, backCandles=40):
        
        self.setPivotPoint()
        self.setBreakoutPoint(backCandles)

        self.df.isBreakout
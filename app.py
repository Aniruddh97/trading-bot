# main.py
import pandas as pd
import random
import plotly.graph_objects as go
import streamlit as st
import pandas_ta as ta

from main import TradingBot
from utils import isConnected
from trading import PaperTrading
from datemodule import getDateRange
from tickers import getStockList, recognizePattern, getIndicesList
from datasource import getStockData, getIndexData
from indicators import ChannelBreakoutIndicator, SupportResistanceIndicator

def manageSession(obj, key, value):
    if key in obj:
        return obj[key]
    else:
        obj[key] = value
    return value


def clearSession(obj, keys=[]):
    for key in keys:
        del obj[key]


def computeSignal(tb, all=True):
    if len(tb.data) == 0:
        print("index stock data not found!")

    localPromisingStocks = {}
    my_bar = st.sidebar.progress(0, text="Computing stock data")
    for i, stock in enumerate(tb.data.keys()):
        df = tb.data[stock]

        candleIndex = len(df)-1
        stockSignals = {}
        tb.indicatorCollection[stock] = {}
        
        # RSI
        df['RSI'] = ta.rsi(df.Close, length=14)

        # Candlestick Pattern Signal
        df = recognizePattern(df, all=all)
        if df['candlestick_match_count'][candleIndex] > 0:
            stockSignals['Pattern'] = df['candlestick_pattern'][candleIndex]
            stockSignals['Pattern Count'] = df['candlestick_match_count'][candleIndex]
            stockSignals['Pattern Rank'] = df['candlestick_rank'][candleIndex]
        
        # Support Resistance Indicator Signal
        sri = SupportResistanceIndicator(df, 11, 5, stock)
        sri.calculate(all=False)
        srSignal = sri.getBuySell()[-1]
        if srSignal != '':
            stockSignals["SupportResistanceIndicator"] = srSignal
        tb.indicatorCollection[stock]["sri"] = sri

        # Collect Signals
        if len(stockSignals) != 0 :
            stockSignals["RSI"] = df['RSI'][candleIndex]
            localPromisingStocks[stock] = stockSignals
        my_bar.progress(int((i+1)*(100/len(tb.data.keys()))), text=f'Computing : {stock}')
    my_bar.progress(100, text='Computation completed')
    tb.promisingStocks = localPromisingStocks


def trade(pt):
    ticker = st.text_input("Ticker", "")
    candleIndex = st.number_input("Candle Index")

    if ticker == "" or int(candleIndex) == 0:
        st.stop()

    indicator = pt.tb.indicatorCollection[ticker]['sri']
    st.plotly_chart(indicator.getIndicator(candleIndex))
    data = indicator.df

    with st.form("Data Form"):
        stoploss = st.number_input("Stoploss")
        target = st.number_input("Target")
        submitted = st.form_submit_button("Submit")
        if not submitted:
            st.stop()

    startdate = data['Date'][candleIndex]
    strikePrice = data['Close'][candleIndex]

    result = pt.db.placeOrder(ticker, startdate, strikePrice, stoploss, target)
    if result:
        st.success("Order Placed")
    else:
        st.error("Something went wrong while placing your order")


def randomQuiz(tb, pt, quizSessionData, rounds):
    manageSession(quizSessionData, 'start', True)
    rounds = manageSession(quizSessionData, 'rounds', rounds)
        
    tickerList = list(tb.data.keys())
    maxProfit = maxLoss = totalRRR = tradeCount = balance = 0
    
    maxLoss = manageSession(quizSessionData, 'maxLoss', maxLoss)
    balance = manageSession(quizSessionData, 'balance', balance)
    totalRRR = manageSession(quizSessionData, 'totalRRR', totalRRR)
    maxProfit = manageSession(quizSessionData, 'maxProfit', maxProfit)
    tradeCount = manageSession(quizSessionData, 'tradeCount', tradeCount)

    while tradeCount < rounds:
        st.write(quizSessionData)
        if 'randomTicker' not in quizSessionData:
            tradeCount += 1

        quizSessionData['tradeCount'] = tradeCount
        
        randomTicker = manageSession(quizSessionData, 'randomTicker', tickerList[random.randint(0, len(tickerList)-1)])

        indicator = tb.indicatorCollection[randomTicker]['sri']
        data = indicator.df

        candleIndex = manageSession(quizSessionData, 'candleIndex', random.randint(50, len(data.index)-51))
        
        st.plotly_chart(indicator.getIndicator(candleIndex))

        take = st.button("Take")
        skip = st.button("Skip")

        if take:
            quizSessionData['take'] = True
        else:
            take = manageSession(quizSessionData, 'take', take)

        if skip:
            tradeCount -= 1
            quizSessionData['tradeCount'] = tradeCount
            st.plotly_chart(indicator.getIndicator(candleIndex+5))
            clearSession(quizSessionData, ['randomTicker', 'candleIndex'])
        elif take:
            with st.form("Quiz Form"):
                stoploss = st.number_input("Stoploss")
                target = st.number_input("Target")
                submitted = st.form_submit_button("Submit")
                if not submitted:
                    st.stop()

            currentPrice = data.Close[candleIndex]
            RRR = abs(target - currentPrice)/abs(stoploss - currentPrice)
            st.text(f'RRR = {RRR}')

            start = candleIndex + 1
            result, finalIndex = pt.runEngine(data, start, target, stoploss, currentPrice)
            
            if result < 0:
                st.text(f"You've booked a loss of Rs{abs(result)}")
                maxLoss = result if result < maxLoss else maxLoss
                totalRRR += RRR
                quizSessionData['maxLoss'] = maxLoss
                quizSessionData['totalRRR'] = totalRRR
            elif result > 0:
                st.text(f"You've made a profit of Rs{result}")
                maxProfit = result if result > maxProfit else maxProfit
                totalRRR += RRR
                quizSessionData['maxProfit'] = maxProfit
                quizSessionData['totalRRR'] = totalRRR
                st.balloons()
            else:
                st.text(f"No outcome after {finalIndex - start} iterations")
                tradeCount -= 1
                quizSessionData['tradeCount'] = tradeCount

            
            balance += result
            quizSessionData['balance'] = balance
            st.plotly_chart(indicator.getIndicator(finalIndex))
            clearSession(quizSessionData, ['randomTicker', 'candleIndex', 'take'])
        else:
            st.stop()


        continueButton = st.button("Continue")
        if not continueButton:
            st.stop()
        
    st.text(f"Your account balance after {tradeCount} trades is : {balance}")
    st.text(f'Biggest Proft {maxProfit}')
    st.text(f'Biggest Loss {maxLoss}')
    st.text(f'Average RRR {totalRRR/tradeCount}')
    st.session_state['quiz'] = {}


def load_data(tb, timePeriod = '6m', label='NIFTY 50', forceUpdate=False):
    stocks, stockLiveData = getStockList(label)
    indices, indexLiveData = getIndicesList()
    startDate, endDate = getDateRange(timePeriod)
    localData = {}

    if len(tb.data) == 0 or forceUpdate:
        my_bar = st.progress(0, text="Loading stock data")
        for i, stock in enumerate(stocks):
            localData[stock] = getStockData(stock, startDate, endDate, stockLiveData)
            my_bar.progress(int((i+1)*(100/len(stocks))), text=f'Loading data : {stock}')

        my_bar = st.progress(0, text="Loading indices data")
        for i, index in enumerate(indices):
            localData[index] = getIndexData(index, startDate, endDate, indexLiveData)
            my_bar.progress(int((i+1)*(100/len(indices))), text=f'Loading data : {index}')
    
        tb.data = localData


def draw_chart(tb, ticker):
    if ticker in tb.indicatorCollection:
        i = tb.indicatorCollection[ticker]['sri']
        fig = i.getIndicator(candleIndex=len(i.df.index)-1)
        st.plotly_chart(fig)
    else:
        df = tb.data[ticker]
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                            open=df['Open'],
                                            high=df['High'],
                                            low=df['Low'],
                                            close=df['Close'])])
        fig.update_layout(
            title=ticker,
            xaxis_title='Index',
            yaxis_title='Stock Price',
        )
        fig.update(layout_xaxis_rangeslider_visible=False)
        st.plotly_chart(fig)


def main():
    st.set_page_config(layout='wide')
    tb = pt = None

    if 'tb' not in st.session_state:
        tb = TradingBot()
        pt = PaperTrading(tb)
        load_data(tb, timePeriod='1m', label='NIFTY IT', forceUpdate=True)
        st.session_state['tb'] = tb
        st.session_state['pt'] = pt
    else:
        tb = st.session_state['tb']
        pt = st.session_state['pt']


    with st.sidebar:
        compute = st.button('Compute')
        with st.form("Data Form"):
            duration = st.text_input('Time Duration', '2y')
            index = st.text_input('Index', 'NIFTY IT')
            submitted = st.form_submit_button("Submit")
            if submitted:
                load_data(tb, timePeriod=duration, label=index, forceUpdate=True)


    AnalysisTab, PaperTradingTab, QuizTab, StockTab, ResultTab = st.tabs(["Analysis", "Paper Trading", "Quiz", "Stock", "Results"])


    with AnalysisTab:
        if compute:
            computeSignal(tb)
        if tb != None and len(tb.promisingStocks) > 0:
            st.dataframe(tb.rank())
            
            stocks = list(tb.rank().index)
            unrankedStocks = [stock for stock in tb.data if stock not in stocks]
            stocks.extend(unrankedStocks)
            for stock in stocks:
                i = tb.indicatorCollection[stock]["sri"]
                fig = i.getIndicator(candleIndex=len(i.df.index)-1)
                st.plotly_chart(fig)
        else:
            st.error("Please compute data")


    with PaperTradingTab:
        doTrade = st.button('Trade')
        if doTrade:
            trade(pt)
        

    with QuizTab:
        quizSessionData = {}
        if 'quiz' in st.session_state:
            quizSessionData = st.session_state['quiz']
        else:
            st.session_state['quiz'] = quizSessionData
            
        if tb != None and len(tb.promisingStocks) > 0:
            rounds = st.number_input('Rounds', 3)
            start = st.button('Start')
            if start or 'start' in quizSessionData:
                randomQuiz(tb, pt, quizSessionData, int(rounds))
        else:
            st.error("Please compute data")

    
    with StockTab:
        selected_ticker = st.selectbox('Select Stock Ticker', tb.data.keys())
        chart = st.button('Chart')
        table = st.button('Table')

        if chart:
            draw_chart(tb, selected_ticker)
        if table:
            st.dataframe(tb.data[selected_ticker])


    with ResultTab:
        evaluate = st.button('Evaluate')
        if evaluate:
            pt.evaluateTrades()


        with st.expander("RRR"):
            query = "SELECT *, ABS(target-strike_price)/ABS(stop_loss-strike_price) as RRR FROM orders"
            st.dataframe(pt.db.read(query))
        
        with st.expander("Month-Wise P&L"):
            query = "SELECT SUBSTR(enddate, 1,7) as Month, count(*) as Trades, sum(pnl) as Balance, AVG(ABS(target-strike_price)/ABS(stop_loss-strike_price)) as RRR FROM orders WHERE enddate IS NOT NULL group by SUBSTR(enddate, 1,7)"
            st.dataframe(pt.db.read(query))
        
        with st.expander("Trade duration in days"):
            query = "SELECT *, CAST((julianday(enddate)-julianday(startdate)) AS INTEGER) as duration FROM orders WHERE enddate IS NOT NULL"
            st.dataframe(pt.db.read(query))

        with st.expander("SQL Dashboard"):
            defaultQuery = "SELECT * FROM orders"
            query = st.text_input("SQL Query", defaultQuery)
            if query == "":
                st.stop()
            st.dataframe(pt.db.read(query))

if __name__ == '__main__':
    main()

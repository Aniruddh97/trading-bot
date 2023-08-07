import yfinance as yf
import streamlit as st
import pandas as pd

data = yf.download('INFY.NS', interval='1d', period = '1y', progress=False)
data.insert(loc=0, column='Date', value=data.index)
data['Date'] = pd.to_datetime(data.Date).dt.date
data.set_index('Date').reset_index()
data = data.drop(['Date'], axis=1)
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
st.dataframe(data)

from datetime import date
from jugaad_data.nse import bhavcopy_save, bhavcopy_fo_save

# Download bhavcopy
path = bhavcopy_save(date(2020,1,1), "./database")
st.write(path)
df = pd.read_csv(path)
st.dataframe(df)
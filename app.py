import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator

import matplotlib.pyplot as plt
import datetime

st.title("Universal Stock Technical Analyzer (Buy/Hold/Sell Signals)")

# STEP 1: User inputs
symbol = st.text_input('Enter any stock symbol (e.g. RELIANCE.NS, TCS.NS, INFY.NS, SBIN.NS, AAPL):', 'RELIANCE.NS').strip().upper()

end_date = datetime.date.today()
start_date = st.date_input("Start date", end_date - datetime.timedelta(days=365))
end_date = st.date_input("End date", end_date)
if start_date >= end_date:
    st.error('Start date must be before end date.')
    st.stop()

# STEP 2: Download data (handle errors)
data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)
if data.empty or "Close" not in data.columns:
    st.warning('No valid data found. Try a different symbol or date range.')
    st.stop()

# STEP 3: Indicators
data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
macd = MACD(data['Close'])
data['MACD'] = macd.macd()
data['MACD_Signal'] = macd.macd_signal()
data['SMA50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
data['SMA200'] = SMAIndicator(data['Close'], window=200).sma_indicator()

# STEP 4: Recommendation logic (can be expanded)
def get_signal(row):
    # Rule: BUY if RSI < 30 and MACD line > MACD signal and price > SMA50; SELL if RSI > 70 or MACD < Signal or price < SMA200; else HOLD
    if pd.isna(row['RSI']) or pd.isna(row['MACD']) or pd.isna(row['MACD_Signal']) or pd.isna(row['SMA50']) or pd.isna(row['SMA200']):
        return "NO SIGNAL"
    if row['RSI'] < 30 and row['MACD'] > row['MACD_Signal'] and row['Close'] > row['SMA50']:
        return "BUY"
    elif row['RSI'] > 70 or row['MACD'] < row['MACD_Signal'] or row['Close'] < row['SMA200']:
        return "SELL"
    else:
        return "HOLD"

data['Signal'] = data.apply(get_signal, axis=1)
latest_signal = data['Signal'].iloc[-1]
st.subheader(f"Latest Signal for {symbol}: {latest_signal}")

# STEP 5: Plotting
st.subheader("Price Chart & Indicators")
fig, ax = plt.subplots(figsize=(14,6))
ax.plot(data.index, data['Close'], label='Close', color='black')
ax.plot(data.index, data['SMA50'], label='SMA50', color='blue', alpha=0.7)
ax.plot(data.index, data['SMA200'], label='SMA200', color='red', alpha=0.7)
ax.legend()
plt.title(f"{symbol} Close Price with SMA50 & SMA200")
st.pyplot(fig)

st.subheader("RSI")
fig, ax = plt.subplots(figsize=(14,2))
ax.plot(data.index, data['RSI'], label='RSI', color='green')
ax.axhline(30, color='blue', linestyle='--')
ax.axhline(70, color='red', linestyle='--')
ax.set_ylim(0, 100)
ax.legend()
st.pyplot(fig)

st.subheader("MACD")
fig, ax = plt.subplots(figsize=(14,2))
ax.plot(data.index, data['MACD'], label='MACD', color='purple')
ax.plot(data.index, data['MACD_Signal'], label='Signal Line', color='orange')
ax.axhline(0, color='grey', alpha=0.5)
ax.legend()
st.pyplot(fig)

# STEP 6: Show/download data
st.subheader("Analysis Data")
st.dataframe(data.tail(30))
csv = data.to_csv()
st.download_button("Download CSV", csv, file_name=f"{symbol}_ta_data.csv", mime="text/csv")

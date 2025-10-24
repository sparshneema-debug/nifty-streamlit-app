import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
import matplotlib.pyplot as plt
import datetime

st.title("Universal Stock Technical Analyzer (Buy/Hold/Sell Signals)")

# --- User Input for Symbol
symbol = st.text_input(
    'Enter any Yahoo Finance symbol (e.g. RELIANCE.NS, TCS.NS, AAPL):',
    'RELIANCE.NS'
).strip().upper()

# --- Date Inputs (end date always today)
today = datetime.date.today()
start_default = today - datetime.timedelta(days=365)
start_date = st.date_input(
    "Start date", 
    min_value=datetime.date(2000, 1, 1), 
    max_value=today, 
    value=start_default
)
end_date = today
st.write(f"End date: {end_date} (automatically set to today)")

if start_date >= end_date:
    st.error('Start date must be before end date.')
    st.stop()

# --- Download Data
data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)
if data.empty or "Close" not in data.columns:
    st.warning('No valid data found for this ticker and period. Try another symbol or date range.')
    st.stop()

# --- Defensive handling for Close prices
close_prices = data['Close'].squeeze()
if not isinstance(close_prices, pd.Series) or close_prices.empty:
    st.warning('Close price data not available or invalid shape.')
    st.stop()

# --- Calculate Indicators (with NaN handling)
data['RSI'] = RSIIndicator(close_prices, window=14).rsi()
macd = MACD(close_prices)
data['MACD'] = macd.macd()
data['MACD_Signal'] = macd.macd_signal()
data['SMA50'] = SMAIndicator(close_prices, window=50).sma_indicator()
data['SMA200'] = SMAIndicator(close_prices, window=200).sma_indicator()

# --- Multi-indicator Signal Logic (robust to missing data)
def get_signal(row):
    try:
        # Check for required data present
        if any(pd.isna(row[col]) for col in ['SMA50', 'SMA200', 'MACD', 'MACD_Signal', 'RSI']):
            return "NO SIGNAL"
        if row['SMA50'] > row['SMA200'] and row['MACD'] > row['MACD_Signal'] and row['RSI'] < 35:
            return "STRONG BUY"
        if row['SMA50'] < row['SMA200'] and row['MACD'] < row['MACD_Signal'] and row['RSI'] > 65:
            return "STRONG SELL"
        if row['RSI'] < 30:
            return "BUY"
        if row['RSI'] > 70:
            return "SELL"
        return "HOLD"
    except Exception:
        return "NO SIGNAL"

# Only compute signals if there's at least one row of full data
indicator_cols = ['RSI', 'MACD', 'MACD_Signal', 'SMA50', 'SMA200']
data['Signal'] = "NO SIGNAL"
if not data[indicator_cols].dropna().empty:
    data.loc[data[indicator_cols].notna().all(axis=1), 'Signal'] = data.loc[data[indicator_cols].notna().all(axis=1)].apply(get_signal, axis=1)

if data['Signal'].dropna().eq("NO SIGNAL").all():
    latest_signal = "NO SIGNAL (not enough data. Try a longer date range!)"
else:
    latest_signal = data['Signal'].dropna().iloc[-1]

st.subheader(f"Latest Signal for {symbol}: {latest_signal}")

# --- Plot Prices and Indicators
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

# --- Show and Download Data
st.subheader("Analysis Data")
st.dataframe(data.tail(30))
csv = data.to_csv()
st.download_button(
    "Download CSV", 
    csv, 
    file_name=f"{symbol}_ta_data.csv", 
    mime="text/csv"
)

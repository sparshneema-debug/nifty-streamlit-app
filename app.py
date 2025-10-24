import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
import matplotlib.pyplot as plt
import datetime

st.title("Universal Stock Analyzer with Buy/Sell Chart Markers")

# --- User Input for Symbol
symbol = st.text_input(
    'Enter any Yahoo Finance symbol (e.g. RELIANCE.NS, TCS.NS, AAPL):', 'RELIANCE.NS'
).strip().upper()

# --- Date Inputs (2 years default, end = today)
today = datetime.date.today()
start_default = today - datetime.timedelta(days=730)
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
    st.error('No valid data found for this ticker and period. Try another symbol or date range.')
    st.stop()

# --- Defensive Close handling
close_prices = data['Close'].squeeze()
if not isinstance(close_prices, pd.Series) or close_prices.empty:
    st.error('Close price data not available or invalid shape.')
    st.stop()

# --- Calculate Indicators
data['RSI'] = RSIIndicator(close_prices, window=14).rsi()
macd = MACD(close_prices)
data['MACD'] = macd.macd()
data['MACD_Signal'] = macd.macd_signal()
data['SMA50'] = SMAIndicator(close_prices, window=50).sma_indicator()
data['SMA200'] = SMAIndicator(close_prices, window=200).sma_indicator()

indicator_cols = ['RSI', 'MACD', 'MACD_Signal', 'SMA50', 'SMA200']
# --- Protection: Only proceed if there's at least one row with all technicals populated
if data[indicator_cols].dropna().empty:
    st.error("Not enough indicator data for signal generation. Try a longer date range or another stock.")
    st.write("Recent indicator values (for debugging):")
    st.write(data[indicator_cols].tail(10))
    st.stop()

# --- Signal Logic: Fallback to simpler check if NaNs present
def get_signal(row):
    try:
        required = ['SMA50', 'SMA200', 'MACD', 'MACD_Signal', 'RSI']
        if all(pd.notna(row[c]) for c in required):
            if row['SMA50'] > row['SMA200'] and row['MACD'] > row['MACD_Signal'] and row['RSI'] < 35:
                return "STRONG BUY"
            if row['SMA50'] < row['SMA200'] and row['MACD'] < row['MACD_Signal'] and row['RSI'] > 65:
                return "STRONG SELL"
        if pd.notna(row['RSI']):
            if row['RSI'] < 30:
                return "BUY"
            if row['RSI'] > 70:
                return "SELL"
            return "HOLD"
        return "NO SIGNAL"
    except Exception:
        return "NO SIGNAL"

data['Signal'] = data.apply(get_signal, axis=1)

latest_signal = data['Signal'][data['Signal'] != "NO SIGNAL"].iloc[-1] if (data['Signal'] != "NO SIGNAL").any() else "NO SIGNAL (not enough indicator data)"

st.subheader(f"Latest Signal for {symbol}: {latest_signal}")

# --- Show diagnostics for indicator values (last 10 rows)
st.write("Recent indicator values (for diagnostics):")
st.write(data[['RSI', 'MACD', 'MACD_Signal', 'SMA50', 'SMA200', 'Signal']].tail(10))

# --- Chart with BUY/SELL markers
st.subheader("Price Chart with Buy/Sell Markers")
fig, ax = plt.subplots(figsize=(14,6))
ax.plot(data.index, data['Close'], label='Close', color='black')
ax.plot(data.index, data['SMA50'], label='SMA50', color='blue', alpha=0.7)
ax.plot(data.index, data['SMA200'], label='SMA200', color='red', alpha=0.7)
buy_mask = data['Signal'].isin(['BUY','STRONG BUY'])
sell_mask = data['Signal'].isin(['SELL','STRONG SELL'])
ax.scatter(
    data.index[buy_mask], data['Close'][buy_mask],
    marker='^', color='green', s=100, label='BUY/STRONG BUY'
)
ax.scatter(
    data.index[sell_mask], data['Close'][sell_mask],
    marker='v', color='red', s=100, label='SELL/STRONG SELL'
)
ax.legend()
plt.title(f"{symbol} Close Price with Indicators & Buy/Sell Markers")
st.pyplot(fig)

# --- RSI chart
st.subheader("RSI")
fig, ax = plt.subplots(figsize=(14,2))
ax.plot(data.index, data['RSI'], label='RSI', color='green')
ax.axhline(30, color='blue', linestyle='--')
ax.axhline(70, color='red', linestyle='--')
ax.set_ylim(0, 100)
ax.legend()
st.pyplot(fig)

# --- MACD chart
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

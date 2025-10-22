import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands
import matplotlib.pyplot as plt
import datetime

# --- Stock lists ---
nifty50 = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"
]
nifty_next50 = [
    "ADANIGREEN.NS", "ADANITRANS.NS", "AUBANK.NS", "BANKBARODA.NS", "BANDHANBNK.NS",
    "BERGEPAINT.NS", "BHEL.NS", "BIOCON.NS", "CANBK.NS", "CHOLAFIN.NS",
    "COLPAL.NS", "DABUR.NS", "DLF.NS", "GAIL.NS",
    "GODREJCP.NS", "HAVELLS.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS",
    "IGL.NS", "INDIANB.NS", "INDIGO.NS", "JSWENERGY.NS", "JUBLFOOD.NS",
    "LICI.NS", "LUPIN.NS", "MCDOWELL-N.NS", "MOTHERSUMI.NS", "OBEROIRLTY.NS",
    "PAYTM.NS", "PEL.NS", "PIIND.NS", "POWERINDIA.NS", "SHREECEM.NS",
    "SIEMENS.NS", "SRF.NS", "TORNTPHARM.NS", "TVSMOTOR.NS", "UBL.NS",
    "VEDL.NS", "VOLTAS.NS", "YESBANK.NS", "ZYDUSLIFE.NS", "TRENT.NS",
    "ABB.NS", "CUMMINSIND.NS", "PAGEIND.NS", "POLYCAB.NS", "SYRMA.NS"
]
niftymidcap50 = [
    "ABB.NS", "ALKEM.NS", "APOLLOTYRE.NS", "AUROPHARMA.NS", "BALKRISIND.NS",
    "BANDHANBNK.NS", "BHARATFORG.NS", "CANBK.NS", "CHAMBLFERT.NS", "CUMMINSIND.NS",
    "DLF.NS", "GMRINFRA.NS", "GODREJPROP.NS", "GUJGASLTD.NS", "HAL.NS",
    "HINDPETRO.NS", "IDFCFIRSTB.NS", "INDHOTEL.NS", "INDIANB.NS", "INDIGO.NS",
    "JKCEMENT.NS", "LUPIN.NS", "MRPL.NS", "MFSL.NS",
    "MGL.NS", "NHPC.NS", "NMDC.NS", "OBEROIRLTY.NS", "PAGEIND.NS",
    "PIIND.NS", "PERSISTENT.NS", "PFC.NS", "PETRONET.NS",
    "POLYCAB.NS", "PNB.NS", "RECLTD.NS", "RBLBANK.NS", "SRF.NS",
    "SRTRANSFIN.NS", "SYNGENE.NS", "TRENT.NS", "TVSMOTOR.NS", "UNIONBANK.NS",
    "UBL.NS", "VOLTAS.NS", "ZEEL.NS", "ZYDUSLIFE.NS"
]
all_stocks = sorted(list(set(nifty50 + nifty_next50 + niftymidcap50)))

# --- Streamlit UI ---
st.title("NIFTY & Midcap Stock Technical Indicator Visualizer")
default_symbol = "RELIANCE.NS" if "RELIANCE.NS" in all_stocks else all_stocks[0]
symbol = st.selectbox("Choose a stock", all_stocks, index=all_stocks.index(default_symbol))
end_date = datetime.date.today()
start_date = st.date_input("Start date", end_date - datetime.timedelta(days=365))
end_date = st.date_input("End date", end_date)
if start_date >= end_date:
    st.error('Start date must be before end date.')
    st.stop()

data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)
if data.empty:
    st.warning('No data found for this period.')
    st.stop()

indicators = st.multiselect(
    "Technical indicators to show",
    ["RSI", "MACD", "SMA50", "SMA200", "EMA20", "Bollinger Bands", "ADX", "Stochastic"],
    default=["RSI", "MACD", "SMA50", "SMA200"]
)

# Compute indicators
if "RSI" in indicators:
    data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
if "MACD" in indicators:
    macd_ind = MACD(data['Close'])
    data["MACD"] = macd_ind.macd()
    data["MACD_Signal"] = macd_ind.macd_signal()
if "SMA50" in indicators:
    data['SMA50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
if "SMA200" in indicators:
    data['SMA200'] = SMAIndicator(data['Close'], window=200).sma_indicator()
if "EMA20" in indicators:
    data['EMA20'] = EMAIndicator(data['Close'], window=20).ema_indicator()
if "Bollinger Bands" in indicators:
    bb = BollingerBands(data['Close'], window=20)
    data['BB_High'] = bb.bollinger_hband()
    data['BB_Low'] = bb.bollinger_lband()
if "ADX" in indicators:
    data['ADX'] = ADXIndicator(data["High"], data["Low"], data["Close"]).adx()
if "Stochastic" in indicators:
    stoch = StochasticOscillator(
        high=data["High"], low=data["Low"], close=data["Close"], window=14, smooth_window=3)
    data["Stoch_K"] = stoch.stoch()
    data["Stoch_D"] = stoch.stoch_signal()

# Visualization
st.subheader(f"{symbol} Chart with Indicators")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(data.index, data["Close"], label="Close", color="black", linewidth=1)
if "SMA50" in indicators:
    ax.plot(data.index, data["SMA50"], label="SMA50", linewidth=1, color="blue")
if "SMA200" in indicators:
    ax.plot(data.index, data["SMA200"], label="SMA200", linewidth=1, color="red")
if "EMA20" in indicators:
    ax.plot(data.index, data["EMA20"], label="EMA20", linewidth=1, color="orange")
if "Bollinger Bands" in indicators:
    ax.plot(data.index, data["BB_High"], label="BB High", linestyle="--", color="grey")
    ax.plot(data.index, data["BB_Low"], label="BB Low", linestyle="--", color="grey")
ax.set_title(f"{symbol} Close Price & Moving Averages")
ax.legend()
st.pyplot(fig)

if "RSI" in indicators:
    fig, ax = plt.subplots(figsize=(16, 3))
    ax.plot(data.index, data["RSI"], label="RSI", color="green")
    ax.axhline(70, linestyle="--", color="red", alpha=0.5)
    ax.axhline(30, linestyle="--", color="blue", alpha=0.5)
    ax.set_title("RSI")
    ax.legend()
    st.pyplot(fig)
if "MACD" in indicators:
    fig, ax = plt.subplots(figsize=(16, 3))
    ax.plot(data.index, data["MACD"], label="MACD", color="blue")
    ax.plot(data.index, data["MACD_Signal"], label="MACD Signal", color="red")
    ax.set_title("MACD")
    ax.legend()
    st.pyplot(fig)
if "ADX" in indicators:
    fig, ax = plt.subplots(figsize=(16, 3))
    ax.plot(data.index, data["ADX"], label="ADX", color="purple")
    ax.set_title("ADX")
    ax.legend()
    st.pyplot(fig)
if "Stochastic" in indicators:
    fig, ax = plt.subplots(figsize=(16, 3))
    ax.plot(data.index, data["Stoch_K"], label="Stoch K", color="magenta")
    ax.plot(data.index, data["Stoch_D"], label="Stoch D", color="cyan")
    ax.set_title("Stochastic Oscillator")
    ax.legend()
    st.pyplot(fig)

# Volume
fig, ax = plt.subplots(figsize=(16, 2))
ax.bar(data.index, data["Volume"], width=1, color="grey")
ax.set_title("Volume")
st.pyplot(fig)

st.subheader("Download Indicator Data")
st.dataframe(data)
csv = data.to_csv()
st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f"{symbol}_indicators.csv",
    mime="text/csv",
)
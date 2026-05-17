import streamlit as st
import pandas as pd
import yfinance as yf
import time
from datetime import datetime

# 1. Setup the Web Page
st.set_page_config(page_title="NG Cloud Matrix", layout="centered")
st.title("🔥 Natural Gas Matrix")
st.write("Secure, dependency-free dashboard auto-refreshing every 3 minutes.")

# --- Custom Math Functions (Bypasses the need for pandas-ta) ---
def calc_macd(close_prices):
    ema_fast = close_prices.ewm(span=12, adjust=False).mean()
    ema_slow = close_prices.ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line.iloc[-1], signal_line.iloc[-1]

def calc_rsi(close_prices, periods=14):
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/periods, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/periods, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]
# ---------------------------------------------------------------

def get_status():
    try:
        # Fetch 1-Minute Data
        ticker = yf.Ticker("NG=F")
        df_1m = ticker.history(interval="1m", period="5d")
        
        # Resample timeframes
        df_1h = df_1m.resample('1h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        df_15m = df_1m.resample('15min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        df_3m = df_1m.resample('3min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        
        # 1H Tide (MACD)
        macd_val, signal_val = calc_macd(df_1h['Close'])
        tide_status = "🟢 BULLISH TIDE" if macd_val > signal_val else "🔴 BEARISH TIDE"
        
        # 15M Wave (RSI)
        rsi_15m = calc_rsi(df_15m['Close'])
        wave_status = "🟢 OVERSOLD" if rsi_15m <= 30 else ("🔴 OVERBOUGHT" if rsi_15m >= 70 else "⚪ NEUTRAL")
        
        # 3M Ripple (RSI)
        rsi_3m = calc_rsi(df_3m['Close'])
        ripple_status = "🟢 OVERSOLD" if rsi_3m <= 30 else ("🔴 OVERBOUGHT" if rsi_3m >= 70 else "⚪ NEUTRAL")
        
        return tide_status, wave_status, rsi_15m, ripple_status, rsi_3m
    except Exception as e:
        return None, None, None, None, None

# 2. Create the Dashboard Interface
placeholder = st.empty()

with placeholder.container():
    tide, wave, rsi15, ripple, rsi3 = get_status()
    
    if tide:
        st.subheader(f"📊 1H Tide: {tide}")
        st.subheader(f"🌊 15M Wave: {wave} (RSI: {rsi15:.1f})")
        st.subheader(f"💧 3M Ripple: {ripple} (RSI: {rsi3:.1f})")
        
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    else:
        st.error("Fetching secure market data... Please wait.")

# 3. Force Web Browser to Reload Every 3 Minutes
time.sleep(180)
st.rerun()

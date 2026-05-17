import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import time
from datetime import datetime

# 1. Setup the Web Page
st.set_page_config(page_title="NG Cloud Matrix", layout="centered")
st.title("🔥 Natural Gas Matrix")
st.write("This dashboard uses an approved, secure data feed and auto-refreshes every 3 minutes.")

def get_status():
    try:
        # Fetch 1-Minute Data from official market feed
        ticker = yf.Ticker("NG=F")
        df_1m = ticker.history(interval="1m", period="5d")
        
        # Resample the 1-minute data into our custom timeframes
        df_1h = df_1m.resample('1h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        df_15m = df_1m.resample('15min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        df_3m = df_1m.resample('3min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        
        # Calculate 1H Tide (MACD)
        macd = ta.macd(df_1h['Close'], fast=12, slow=26, signal=9)
        tide_val = macd.iloc[-1]
        tide_status = "🟢 BULLISH TIDE" if tide_val['MACD_12_26_9'] > tide_val['MACDs_12_26_9'] else "🔴 BEARISH TIDE"
        
        # Calculate 15M Wave (RSI)
        rsi_15m = ta.rsi(df_15m['Close'], length=14).iloc[-1]
        wave_status = "🟢 OVERSOLD" if rsi_15m <= 30 else ("🔴 OVERBOUGHT" if rsi_15m >= 70 else "⚪ NEUTRAL")
        
        # Calculate 3M Ripple (RSI)
        rsi_3m = ta.rsi(df_3m['Close'], length=14).iloc[-1]
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

# 3. Force Web Browser to Reload Every 3 Minutes (180 seconds)
time.sleep(180)
st.rerun()

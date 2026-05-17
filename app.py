import streamlit as st
import pandas as pd
import pandas_ta as ta
from tvDatafeed import TvDatafeed, Interval
import time
from datetime import datetime

# 1. Setup the Web Page
st.set_page_config(page_title="NG Cloud Matrix", layout="centered")
st.title("🔥 Pepperstone Natural Gas Matrix")
st.write("This dashboard pulls live data directly from Pepperstone and auto-refreshes every 3 minutes.")

# 2. Connect to Data Feed (Guest Mode)
tv = TvDatafeed()

def get_status(symbol='NATGAS', exchange='PEPPERSTONE'):
    try:
        # Fetch 1H, 15M, and 3M Data
        df_1h = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_1_hour, n_bars=50)
        df_15m = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_15_minute, n_bars=50)
        df_3m = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_3_minute, n_bars=50)
        
        # Calculate 1H Tide (MACD)
        macd = ta.macd(df_1h['close'], fast=12, slow=26, signal=9)
        tide_val = macd.iloc[-1]
        tide_status = "🟢 BULLISH TIDE" if tide_val['MACD_12_26_9'] > tide_val['MACDs_12_26_9'] else "🔴 BEARISH TIDE"
        
        # Calculate 15M Wave (RSI)
        rsi_15m = ta.rsi(df_15m['close'], length=14).iloc[-1]
        wave_status = "🟢 OVERSOLD" if rsi_15m <= 30 else ("🔴 OVERBOUGHT" if rsi_15m >= 70 else "⚪ NEUTRAL")
        
        # Calculate 3M Ripple (RSI)
        rsi_3m = ta.rsi(df_3m['close'], length=14).iloc[-1]
        ripple_status = "🟢 OVERSOLD" if rsi_3m <= 30 else ("🔴 OVERBOUGHT" if rsi_3m >= 70 else "⚪ NEUTRAL")
        
        return tide_status, wave_status, rsi_15m, ripple_status, rsi_3m
    except Exception as e:
        return None, None, None, None, None

# 3. Create the Dashboard Interface
placeholder = st.empty()

with placeholder.container():
    tide, wave, rsi15, ripple, rsi3 = get_status()
    
    if tide:
        st.subheader(f"📊 1H Tide: {tide}")
        st.subheader(f"🌊 15M Wave: {wave} (RSI: {rsi15:.1f})")
        st.subheader(f"💧 3M Ripple: {ripple} (RSI: {rsi3:.1f})")
        
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    else:
        st.error("Fetching data from Pepperstone... Please wait.")

# 4. Force Web Browser to Reload Every 3 Minutes (180 seconds)
time.sleep(180)
st.rerun()

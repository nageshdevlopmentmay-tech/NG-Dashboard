import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time
from datetime import datetime

# --- Stealth Layer: Disguise the Cloud Server as a standard Web Browser ---
class SafeSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(SafeSession, self).__init__(*args, **kwargs)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
session = SafeSession()
# --------------------------------------------------------------------------

# 1. Setup the Web Page
st.set_page_config(page_title="Commodity Cloud Matrix", layout="wide")
st.title("🌐 Multi-Commodity Matrix")
st.write("Secure, stealth dashboard auto-refreshing every 3 minutes.")

# --- Custom Math Functions ---
def calc_macd(close_prices):
    if len(close_prices) < 26: return None, None
    ema_fast = close_prices.ewm(span=12, adjust=False).mean()
    ema_slow = close_prices.ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line.iloc[-1], signal_line.iloc[-1]

def calc_rsi(close_prices, periods=14):
    if len(close_prices) < periods: return None
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/periods, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/periods, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]
# -----------------------------

def get_status(ticker_symbol):
    try:
        # Pass the stealth session into the Yahoo Finance request
        ticker = yf.Ticker(ticker_symbol, session=session)
        df_1m = ticker.history(interval="1m", period="5d")
        
        if df_1m.empty:
            return None, None, None, None, None
            
        # Resample timeframes
        df_1h = df_1m.resample('1h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        df_15m = df_1m.resample('15min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        df_3m = df_1m.resample('3min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        
        # Calculate Matrix
        macd_val, signal_val = calc_macd(df_1h['Close'])
        tide_status = "🟢 BULLISH TIDE" if (macd_val and signal_val and macd_val > signal_val) else "🔴 BEARISH TIDE"
        
        rsi_15m = calc_rsi(df_15m['Close'])
        wave_status = "🟢 OVERSOLD" if (rsi_15m and rsi_15m <= 30) else ("🔴 OVERBOUGHT" if (rsi_15m and rsi_15m >= 70) else "⚪ NEUTRAL")
        
        rsi_3m = calc_rsi(df_3m['Close'])
        ripple_status = "🟢 OVERSOLD" if (rsi_3m and rsi_3m <= 30) else ("🔴 OVERBOUGHT" if (rsi_3m and rsi_3m >= 70) else "⚪ NEUTRAL")
        
        return tide_status, wave_status, rsi_15m, ripple_status, rsi_3m
    except Exception as e:
        return None, None, None, None, None

# Define Assets
assets = {
    "🔥 Natural Gas": "NG=F",
    "🛢️ Crude Oil (WTI)": "CL=F",
    "🥇 Gold": "GC=F",
    "🥈 Silver": "SI=F"
}

# 2. Create the Dashboard Interface
placeholder = st.empty()

with placeholder.container():
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    for i, (asset_name, symbol) in enumerate(assets.items()):
        current_col = col1 if i % 2 == 0 else col2
        
        with current_col:
            st.subheader(asset_name)
            tide, wave, rsi15, ripple, rsi3 = get_status(symbol)
            
            if tide and rsi15 and rsi3:
                st.markdown(f"**📊 1H Tide:** {tide}")
                st.markdown(f"**🌊 15M Wave:** {wave} (RSI: {rsi15:.1f})")
                st.markdown(f"**💧 3M Ripple:** {ripple} (RSI: {rsi3:.1f})")
            else:
                st.warning(f"Market Closed / Connecting to {asset_name} data...")
            
            st.write("---")

# 3. Force Web Browser to Reload Every 3 Minutes
time.sleep(180)
st.rerun()

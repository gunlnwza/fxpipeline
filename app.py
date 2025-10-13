# Streamlit Command Center
# - Fetch data
# - Perform backtest

# MVP
# - fetch stock prices
# - display risk return curve
#   - automatically calculate EF curve
#   - tell weights on hover

# ---

import logging
import os
import time

import numpy as np
import pandas as pd
import yfinance as yf

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


st.title("📈 Streamlit Command Center")

# --- Sidebar Input ---
ticker = st.text_input("Enter stock ticker:", value="AAPL").upper()
fetch_data = st.button("Fetch Data")

# --- File Naming ---
filename = f"{ticker}.csv"

# --- Fetch & Display Logic ---
if fetch_data:
    if not os.path.exists(filename):
        with st.spinner(f"Downloading data for {ticker}..."):
            df = yf.download(ticker)
            if "Ticker" in df.columns.names:
                df = df.droplevel("Ticker", axis=1)
            df.to_csv(filename)
            st.success(f"Downloaded and saved to `{filename}`")
    else:
        st.info(f"Using cached file: `{filename}`")

    # Read and show
    df = pd.read_csv(filename)

    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    fig

    df

# ticker_code = "AAPL"
# ticker = yf.Ticker(ticker_code)
# ticker.info
import streamlit as st
from datetime import datetime

from data import TestLoader

last_updated = datetime.now().strftime("%H:%M:%S")
st.write(f"Last updated: {last_updated}")

ticker = st.text_input("Stocks")
start = st.text_input("Start")
end = st.text_input("End")

if ticker:
    loader = TestLoader()
    ticker = ticker.upper()

    st.write(f"{ticker}")
    df = loader.load(ticker, start, end)
    df

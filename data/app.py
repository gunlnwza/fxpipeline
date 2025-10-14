import streamlit as st
import datetime
import plotly.graph_objects as go

from data import TestLoader


def render(df):
    fig = go.Figure(
        data=[go.Candlestick(x=df.index, open=df['Open'],
                             high=df['High'], low=df['Low'], close=df['Close'])]
    )
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=False)),
        title=ticker
    )

    all_days = set(
        df.index[0] + datetime.timedelta(days=x)
        for x in range((df.index[-1] - df.index[0]).days + 1)
    )
    missing_days = sorted(all_days - set(df.index))
    fig.update_xaxes(rangebreaks=[dict(values=missing_days)])

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)


now = datetime.datetime.now()
# st.write(f"Last updated: {now.strftime("%H:%M:%S")}")

ticker = st.text_input("Stocks")
start = st.date_input("Start", now - datetime.timedelta(365), min_value="2000-01-01", max_value="today")
end = st.date_input("End", min_value="2000-01-01", max_value="today")

if ticker:
    loader = TestLoader()
    ticker = ticker.upper()
    df = loader.load(ticker, start, end)
    if df is not None:
        render(df)

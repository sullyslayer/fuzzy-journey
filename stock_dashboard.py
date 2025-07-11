import streamlit as st
import yfinance as yf
import pandas as pd
import time

def load_tickers_from_file(filename=r"C:\Users\thigp\Documents\PythonProjects\stock_analysis\tickers.txt"):
    try:
        with open(filename, "r") as f:
            tickers = [line.strip().upper() for line in f if line.strip()]
        return tickers
    except FileNotFoundError:
        st.warning(f"Ticker file '{filename}' not found.")
        return []

st.set_page_config(page_title="📈 Live Stock Dashboard", layout="wide")
st.title("📈 Live Stock Dashboard")

# Load tickers from your file
file_tickers = load_tickers_from_file()
default_tickers_str = ", ".join(file_tickers) if file_tickers else "AAPL, MSFT, GOOGL"

# Input box to allow edits or add tickers manually
tickers_input = st.text_input("Enter ticker symbols (comma separated):", default_tickers_str)

refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 300, 60)

def get_company_name(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get('longName', 'N/A')
    except Exception:
        return "N/A"

def get_live_data(ticker, retries=3):
    for attempt in range(retries):
        try:
            # Fetch 2 years of daily data
            data = yf.download(ticker, period="2y", interval="1d", progress=False, threads=False)
            if data.empty:
                st.warning(f"No data found for {ticker}")
                return None, None
            latest_price = float(data['Close'].iloc[-1])
            return data, latest_price
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                st.error(f"Error fetching {ticker}: {e}")
                return None, None

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

if tickers:
    placeholder = st.empty()
    while True:
        with placeholder.container():
            for ticker in tickers:
                company_name = get_company_name(ticker)
                st.subheader(f"{ticker} — {company_name}")
                data, latest_price = get_live_data(ticker)
                if data is not None:
                    st.metric(label="Live Price", value=f"${latest_price:.2f}")
                    st.line_chart(data['Close'])
                st.markdown("---")

        st.sidebar.write(f"Last update: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(refresh_interval)
else:
    st.info("Please enter one or more ticker symbols to get started.")

import streamlit as st
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from pandas.tseries.offsets import BDay
from function import *
from train import train
import os

plt.style.use("fivethirtyeight")
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.image("abc.png", width=150)  # Logo
st.markdown('# Nhóm Rạp Xiếc \n** Prestige and quality **')

# Sidebar: Chọn mã cổ phiếu
STOCKS = np.array(["BSI.VN", "VDS.VN", "VIX.VN"])
SYMB = st.sidebar.selectbox("Chọn cổ phiếu", STOCKS)

# Sidebar: Chọn khung thời gian (Ngày/Giờ)
timeframe = st.sidebar.radio("Chọn khung thời gian", ["Ngày", "Giờ"])

# Ngày bắt đầu và kết thúc
today = datetime.datetime.today()
START = datetime.datetime(2014, 1, 1)
END = datetime.datetime(2024, 12, 31)

# Tải dữ liệu từ yFinance
tickerData = yf.Ticker(SYMB)
if timeframe == "Ngày":
    stock = tickerData.history(interval='1d', start=START, end=END)
else:
    stock = tickerData.history(interval='1h', start=START, end=END)

# Hiển thị dữ liệu
st.title(f'Dữ liệu giá của {SYMB}')
if 'Stock Splits' in stock.columns:
    stock.drop(['Stock Splits', 'Dividends'], axis=1, inplace=True)
st.write(stock)

# Train Model
if st.sidebar.button("Train model"):
    model_path = f'Model/{SYMB}.keras'
    train(stock, 'Close', model_path, model_type="LSTM")
    st.success(f"Đã train và lưu model tại {model_path}")

# Dự đoán tương lai
if os.path.exists(f'Model/{SYMB}.keras'):
    num_days = st.sidebar.slider("Số ngày dự đoán", 7, 60, 15)
    past_days = 30  # Số ngày quá khứ hiển thị
    future_preds = predict_future(stock, 'Close', SYMB, num_days)

    # Ghép dữ liệu quá khứ với dự đoán
    past_prices = stock['Close'].values[-past_days:]
    total_dates = list(range(-past_days, num_days))

    # Vẽ biểu đồ
    plt.figure(figsize=(12,6))
    plt.plot(total_dates[:past_days], past_prices, linestyle='-', marker='o', color='gray', label=f'Giá trong {past_days} ngày qua')
    plt.plot(total_dates[past_days:], future_preds, linestyle='-', marker='o', color='b', label=f'Dự đoán {num_days} ngày tới')
    
    plt.axvline(x=0, color='red', linestyle='--', label='Ngày hiện tại')
    plt.xlabel('Ngày')
    plt.ylabel('Giá cổ phiếu')
    plt.title(f'Dự đoán giá cổ phiếu {SYMB}')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)
else:
    st.warning("Chưa có model! Bạn cần train trước khi dự đoán.")

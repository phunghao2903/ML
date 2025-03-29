import streamlit as st
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from pandas.tseries.offsets import BDay
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
import warnings
from function import predict_future_15_days, fig_1, fig_3, xuatdothi_1
from train import train
import os

plt.style.use("fivethirtyeight")
warnings.filterwarnings("ignore")

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.image("abc.png", width=150)  # logo
st.markdown('# NHÓM HỌC MÁY NHA \n** hello các pờ rô **')

window_selection_c = st.sidebar.container()
window_selection_c.markdown("## NHÓM HỌC MÁY NHA")

sub_columns = window_selection_c.columns(2)

# Fixed date range (nhưng vẫn giữ input cho đẹp giao diện)
START = datetime.datetime(2014, 1, 1)
END = datetime.datetime(2024, 12, 31)
sub_columns[0].date_input("From", value=START, disabled=True)
sub_columns[1].date_input("To", value=END, disabled=True)

STOCKS = np.array(["BSI.VN", "VDS.VN", "VIX.VN"])
SYMB = window_selection_c.selectbox("Chọn mã cổ phiếu", STOCKS)

st.title(f'Giá cổ phiếu {SYMB}')
tickerData = yf.Ticker(SYMB)
stock = tickerData.history(period='1d', start=START, end=END)
field = np.array(["Open", "High", "Low", "Close", "Volume"])
fd = window_selection_c.selectbox("Chọn trường dữ liệu", field)

xuatdothi_1(stock[fd])
st.write(stock)

r_t, mean = fig_1(stock, fd, SYMB)
fig_3(stock, fd, SYMB, r_t, mean)

stock.reset_index(inplace=True)
model_path = f'Model/{SYMB}.keras'

if window_selection_c.button("Train model"):
    train(stock, fd, model_path)
    st.success(f"Đã train và lưu model tại {model_path}")

if os.path.exists(model_path):
    predict_future_15_days(stock, fd, SYMB, model_path)
else:
    st.warning("Chưa có model. Bấm 'Train model' để huấn luyện trước khi dự đoán!")

import streamlit as st
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.figure_factory as ff
import yfinance as yf
from pandas.tseries.offsets import BDay

import warnings
import seaborn as sns
from function import *
from app1 import *
plt.style.use("fivethirtyeight")
warnings.filterwarnings("ignore")

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.markdown('# STOCK \n** Prestige and quality **')

# ------ layout setting---------------------------
window_selection_c = st.sidebar.container()
window_selection_c.markdown("## STOCK ")
sub_columns = window_selection_c.columns(2)

today = datetime.datetime.today()
YESTERDAY = today - BDay(0)

DEFAULT_START = today - BDay(365)
START = sub_columns[0].date_input("From", value=DEFAULT_START, max_value=YESTERDAY)
END = sub_columns[1].date_input("To", value=YESTERDAY, max_value=YESTERDAY, min_value=START)

STOCKS = np.array(["BSI.VN", "VDS.VN", "VIX.VN", "Another Choice"])
SYMB = window_selection_c.selectbox("select stock", STOCKS)

if SYMB != "Another Choice":
    st.title('Price data of ' + SYMB + ' stock')
    tickerData = yf.Ticker(SYMB)
    stock = tickerData.history(period='1d', start=START, end=END)
    field = np.array(["Close", "High", "Low", "Open", "Volume"])
    fd = window_selection_c.selectbox("select field", field)
    xuatdothi_1(stock[fd])
    st.title('Price data of ' + SYMB + ' stock')
    stock = stock.drop(['Stock Splits', 'Dividends'], axis=1, errors='ignore')
    st.write(stock)

    # r_t, mean = fig_1(stock, fd, SYMB)
    # fig_3(stock, fd, SYMB, r_t, mean)

else:
    uploaded_file = window_selection_c.file_uploader("Choose a file")
    stock = pd.DataFrame()
    if uploaded_file is not None:
        stock = pd.read_csv(uploaded_file, index_col=0, parse_dates=True, infer_datetime_format=True)
        sl = stock.columns
        fd = window_selection_c.selectbox("select field to show", sl)
        st.title('Price data of your stock')
        xuatdothi_1(stock[fd])
        st.write(stock)
        SYMB = 'Your_stock'
        r_t, mean = fig_1(stock, fd, SYMB)
        fig_3(stock, fd, SYMB, r_t, mean)


# Thêm phần dự đoán giá cổ phiếu
st.sidebar.markdown("## Dự đoán giá cổ phiếu")
predict_date = st.sidebar.date_input("Chọn ngày dự đoán:", min_value=YESTERDAY + BDay(1))

if st.sidebar.button("Dự đoán giá"):
    try:
        st.subheader(f'📈 Dự đoán giá cổ phiếu {SYMB} từ {predict_date} đến hôm nay')
        
        error, predicted_df = predict_stock_price(SYMB, predict_date)  # Gọi hàm dự đoán
        
        if error:
            st.error(f"Lỗi khi dự đoán: {error}")
        else:
            predicted_prices = predicted_df["Giá dự đoán"].values
            predicted_dates = predicted_df["Ngày"].values

            st.write("Dữ liệu dự đoán:")
            st.dataframe(predicted_df)

            # Lấy dữ liệu thực tế từ ngày dự đoán đến hôm nay
            tickerData = yf.Ticker(SYMB)
            real_stock = tickerData.history(start=predict_date, end=pd.to_datetime("today"))
            
            # if real_stock.empty:
            #     st.warning("Không có dữ liệu thực tế sau ngày dự đoán!")
            
            # Vẽ biểu đồ kết hợp
            fig, ax = plt.subplots(figsize=(12, 6))

            if not real_stock.empty:
                ax.plot(real_stock.index, real_stock["Close"], label="Giá thực tế", marker="o", linestyle="-", color="blue")

            ax.plot(predicted_dates, predicted_prices, marker='o', linestyle="--", color="red", label="Giá dự đoán")

            ax.set_xlabel("Ngày")
            ax.set_ylabel("Giá cổ phiếu")
            ax.set_title(f"Giá dự đoán và giá thực tế của {SYMB}")
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45, ha='right')

            st.pyplot(fig)
    
    except Exception as e:
        st.error(f"Lỗi khi dự đoán: {e}")

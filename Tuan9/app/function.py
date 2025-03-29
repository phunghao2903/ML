import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from tensorflow import keras
import streamlit as st
import plotly.graph_objects as go
from pandas.tseries.offsets import BDay
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import seaborn as sns



def xuatdothi_1(bang):
    st.line_chart(bang)
def plot_raw_data(date1,ketqua,SYMB):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=date1, y=ketqua, name="stock_open"))
        fig.layout.update(title_text='Predict Chart of '+ str(SYMB), xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)
def fig_1(stock,fd,SYMB):
    fig_1,ax = plt.subplots()
    fig_1.set_figheight(5)
    fig_1.set_figwidth(12)
    r_t = np.log((stock[fd]/stock[fd].shift(1)))
    mean = np.mean(r_t)
    r_t[0] = mean
    ax.plot(r_t, linestyle='--', marker='o')
    ax.axhline(y=mean, label='mean return', c='red')
    ax.legend()
    st.write('\n')
    st.title('Prive movement chart '+str(fd)+' of '+SYMB)
    st.pyplot(fig_1)
    return r_t,mean
def fig_3(stock,fd,SYMB,r_t,mean):
    st.title('Overall average daily profit of '+SYMB)
    fig_3,ax = plt.subplots()
    fig_3.set_figheight(5)
    fig_3.set_figwidth(12)
    sns.distplot(r_t, bins = 20)
    plt.axvline(x=mean, label='mean return', c='red')
    plt.legend()
    plt.xlabel('return rate')
    plt.ylabel('frequency')
    st.pyplot(fig_3)


def predict_stock_price(symbol, start_date):
    prop = 'Close'
    model_path = f'/home/phung/jnotebook/source/Tuan9/model/{symbol}_{prop}.keras'
    
    try:
        model = keras.models.load_model(model_path)
    except Exception as e:
        return f"Lỗi khi tải model: {e}", None
    
    n_past_days = 60
    future_days = (pd.to_datetime(start_date) - pd.to_datetime("today")).days
    
    if future_days <= 0:
        return "Ngày dự đoán phải lớn hơn hôm nay!", None
    
    start_fetch = pd.to_datetime("today") - pd.Timedelta(days=n_past_days + 40)
    df = yf.download(symbol, start=start_fetch, end=pd.to_datetime("today"))
    
    if df.empty:
        return "Không tìm thấy dữ liệu cổ phiếu!", None
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    close_prices = df["Close"].dropna().values.reshape(-1, 1)
    close_prices_scaled = scaler.fit_transform(close_prices)
    
    if len(close_prices_scaled) < n_past_days:
        return f"Không đủ {n_past_days} ngày dữ liệu!", None
    
    x_input = close_prices_scaled[-n_past_days:].reshape(1, n_past_days, 1)
    future_predictions = []

    # Dự đoán giá tương lai
    for i in range(future_days):
        next_day_pred = model.predict(x_input)
        next_day_pred_real = scaler.inverse_transform(next_day_pred)[0][0]
        future_predictions.append(next_day_pred_real)
        x_input = np.append(x_input[:, 1:, :], next_day_pred.reshape(1, 1, 1), axis=1)
    
    # Tạo danh sách ngày dự đoán
    predicted_dates = [pd.to_datetime("today") + pd.Timedelta(days=i+1) for i in range(future_days)]

    # Đảm bảo danh sách giá trị dự đoán có dữ liệu
    if not future_predictions:
        return "Lỗi: Không có dữ liệu dự đoán!", None

    # Tạo DataFrame kết quả
    pred_df = pd.DataFrame({"Ngày": predicted_dates, "Giá dự đoán": future_predictions})
    
    return None, pred_df  # Trả về DataFrame

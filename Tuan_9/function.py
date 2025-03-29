import numpy as np
import pandas as pd
import streamlit as st
from tensorflow import keras
import matplotlib.pyplot as plt
import seaborn as sns

def got_data(data):
    return np.array([data])

def xuatdothi_1(bang):
    st.line_chart(bang)

def fig_1(stock, fd, SYMB):
    fig_1, ax = plt.subplots(figsize=(12, 5))
    r_t = np.log(stock[fd] / stock[fd].shift(1))
    mean = r_t.mean()
    r_t.iloc[0] = mean
    ax.plot(r_t, linestyle='--', marker='o')
    ax.axhline(y=mean, label='mean return', color='red')
    ax.legend()
    st.title(f'Biểu đồ lợi nhuận {fd} của {SYMB}')
    st.pyplot(fig_1)
    return r_t, mean

def fig_3(stock, fd, SYMB, r_t, mean):
    st.title(f'Tổng quan lợi nhuận hàng ngày của {SYMB}')
    fig_3, ax = plt.subplots(figsize=(12, 5))
    sns.histplot(r_t, bins=20, kde=True)
    plt.axvline(x=mean, label='mean return', color='red')
    plt.legend()
    plt.xlabel('Tỷ suất lợi nhuận')
    plt.ylabel('Tần suất')
    st.pyplot(fig_3)

def predict_future_15_days(stock, fd, SYMB, model_path):
    from sklearn.preprocessing import MinMaxScaler
    from pandas.tseries.offsets import BDay

    data_series = stock[fd].values[-30:]
    future_predictions = []
    dates = []

    scaler = MinMaxScaler()
    scaler.fit(data_series.reshape(-1, 1))
    model = keras.models.load_model(model_path)

    today = pd.Timestamp.today().normalize()
    for i in range(15):
        input_data = scaler.transform(data_series.reshape(-1, 1)).flatten()
        input_data = got_data(input_data).reshape(-1, 30, 1)
        pred = model.predict(input_data, verbose=0)
        pred_rescaled = scaler.inverse_transform(pred)[0][0]
        future_predictions.append(pred_rescaled)
        dates.append(today + BDay(i + 1))
        data_series = np.append(data_series[1:], pred_rescaled)

    # Hiển thị bảng kết quả
    df_future = pd.DataFrame({'Ngày': dates, 'Giá dự đoán': future_predictions})
    st.write("### Dự đoán giá trong 15 ngày tới")
    st.write(df_future)

    # Vẽ biểu đồ đẹp như yêu cầu
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(range(1, 16), future_predictions, marker='o', linestyle='-', color='b', label='Dự đoán 15 ngày tới')
    ax.set_xlabel('Ngày')
    ax.set_ylabel('Giá dự đoán')
    ax.set_title('Dự đoán giá cổ phiếu trong 15 ngày tới')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

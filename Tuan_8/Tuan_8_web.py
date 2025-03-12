import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model # type: ignore
from sklearn.preprocessing import MinMaxScaler

# Load mô hình
model = load_model("stock_model_tuong_lai.keras")

st.header("Dự đoán giá cổ phiếu trong 15 ngày tới")

# Nhập mã cổ phiếu
stock = st.text_input("Nhập mã cổ phiếu", "POWERGRID.NS")

start = "2015-12-01"
end = "2025-3-11"

data = yf.download(stock, start=start, end=end)

st.subheader("Dữ liệu cổ phiếu")
st.write(data)

# Xử lý dữ liệu
scaler = MinMaxScaler(feature_range=(0,1))
data_scaled = scaler.fit_transform(data[['Close']])

time_step = 60
X, y = [], []
for i in range(time_step, len(data_scaled)):
    X.append(data_scaled[i-time_step:i, 0])
    y.append(data_scaled[i, 0])
X, y = np.array(X), np.array(y)

train_size = int(len(X) * 0.8)
X_train, y_train = X[:train_size], y[:train_size]
X_test, y_test = X[train_size:], y[train_size:]

X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# Dự đoán
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions.reshape(-1, 1))

# Dự đoán 15 ngày tiếp theo
future_predictions = []
input_sequence = X_test[-1].reshape(1, X_test.shape[1], 1)

for _ in range(15):
    next_day_pred = model.predict(input_sequence)
    future_predictions.append(next_day_pred[0][0])
    next_day_scaled = np.append(input_sequence[0][1:], next_day_pred)
    input_sequence = next_day_scaled.reshape(1, X_test.shape[1], 1)

future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

st.subheader("Dự đoán giá 15 ngày tới")
st.write(future_predictions.flatten())

# Vẽ biểu đồ
fig, ax = plt.subplots(figsize=(12,6))
ax.plot(range(len(future_predictions)), future_predictions, marker='o', linestyle='-', color='b', label='Dự đoán 15 ngày')
ax.set_xlabel("Ngày")
ax.set_ylabel("Giá dự đoán")
ax.set_title("Dự đoán giá cổ phiếu trong 15 ngày tới")
ax.legend()
ax.grid(True)
st.pyplot(fig)

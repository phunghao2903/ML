import streamlit as st
import numpy as np
import pandas as pd
import tensorflow as tf
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# 🟢 Giao diện Streamlit
st.title("📈 Dự đoán giá cổ phiếu")
Macophieu = st.text_input("Nhập mã cổ phiếu:", "BSI.VN")
prop = 'Close'
model_path = f'/home/phung/jnotebook/source/Tuan9/model/{Macophieu}_{prop}.keras'

try:
    model = tf.keras.models.load_model(model_path)
    st.success("✅ Model tải thành công!")
except Exception as e:
    st.error(f"❌ Lỗi khi tải model: {e}")
    st.stop()

# 🟢 Chọn ngày bắt đầu dự đoán
start_date = st.date_input("Chọn ngày bắt đầu dự đoán:", pd.to_datetime("today"))
n_past_days = 60  # Số ngày đầu vào của model
future_days = (pd.to_datetime(start_date) - pd.to_datetime("today")).days  # Số ngày tương lai

if future_days <= 0:
    st.error("❌ Ngày dự đoán phải lớn hơn hôm nay!")
    st.stop()

# 🟢 Tải dữ liệu từ Yahoo Finance
start_fetch = pd.to_datetime("today") - pd.Timedelta(days=n_past_days + 40)
st.write(f"📅 Lấy dữ liệu từ {start_fetch.strftime('%Y-%m-%d')} đến hôm nay")
df = yf.download(Macophieu, start=start_fetch, end=pd.to_datetime("today"))

if df.empty:
    st.error("❌ Không tìm thấy dữ liệu cổ phiếu!")
    st.stop()

# 🟢 Tiền xử lý dữ liệu
scaler = MinMaxScaler(feature_range=(0, 1))
close_prices = df["Close"].dropna().values.reshape(-1, 1)
close_prices_scaled = scaler.fit_transform(close_prices)

actual_past_days = len(close_prices_scaled)  # Số ngày thực tế có dữ liệu
if actual_past_days < n_past_days:
    st.error(f"❌ Không đủ {n_past_days} ngày dữ liệu! Chỉ có {actual_past_days} ngày.")
    st.stop()

# 🟢 Chuẩn bị đầu vào cho model
x_input = close_prices_scaled[-n_past_days:].reshape(1, n_past_days, 1)
future_predictions = []

for i in range(future_days):
    next_day_pred = model.predict(x_input)
    next_day_pred_real = scaler.inverse_transform(next_day_pred)[0][0]
    future_predictions.append(next_day_pred_real)
    x_input = np.append(x_input[:, 1:, :], next_day_pred.reshape(1, 1, 1), axis=1)

# 🟢 Hiển thị kết quả
dates = [pd.to_datetime("today") + pd.Timedelta(days=i+1) for i in range(future_days)]
pred_df = pd.DataFrame({"Ngày": dates, "Giá dự đoán": future_predictions})
st.dataframe(pred_df)

fig, ax = plt.subplots()
ax.plot(dates, future_predictions, marker='o', linestyle='dashed', color='b', label="Dự đoán")
ax.set_xlabel("Ngày")
ax.set_ylabel("Giá dự đoán")
ax.set_title(f"Dự đoán giá {Macophieu}")
ax.legend()
ax.grid()
plt.xticks(rotation=45, ha='right')  # Xoay nhãn 45 độ, căn phải
ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=5))  # Giảm số lượng nhãn
st.pyplot(fig)
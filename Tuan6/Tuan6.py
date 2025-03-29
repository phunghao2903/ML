import numpy as np
import pandas as pd 
import yfinance as yf
from keras.models import load_model
import streamlit as st
import matplotlib.pyplot as plt
import datetime



model = load_model('/home/phung/jnotebook/source/Tuan6/Stock Predictions Model.keras')
st.header('Stock Market Predictor')

stock = st.text_input('Enter Stock Symnbol','GOOG')
# start = '2012-01-01'
# end =  '2022-12-31'
start = st.date_input("Start Date", datetime.date(2012, 1, 1))
end = st.date_input("End Date", datetime.date.today())

data = yf.download(stock,start,end)


st.subheader("Stock Data")
st.write(data)


data_train = pd.DataFrame(data.Close[0: int(len(data)*0.80)])
data_test =  pd.DataFrame(data.Close[int(len(data)*0.80): len(data)])


from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))

pass_100_days = data_train.tail(100)
data_test= pd.concat([pass_100_days,data_test],ignore_index=True)
data_test_scaler = scaler.fit_transform(data_test)

st.subheader("Price vs MA50")
ma_50_day =  data.Close.rolling(50).mean()
fig1 = plt.figure(figsize=(8,6))
plt.plot(ma_50_day,'r')
plt.plot(data.Close,'g')
plt.show()
st.pyplot(fig1)


st.subheader("Price vs MA50 vs MA100")
ma_100_day =  data.Close.rolling(100).mean()
fig2 = plt.figure(figsize=(8,6))
plt.plot(ma_50_day,'r')
plt.plot(ma_100_day,'b')
plt.plot(data.Close,'g')
plt.show()
st.pyplot(fig2)


st.subheader("Price vs MA100 vs MA200")
ma_200_day =  data.Close.rolling(200).mean()
fig3 = plt.figure(figsize=(8,6))
plt.plot(ma_100_day,'r')
plt.plot(ma_200_day,'b')
plt.plot(data.Close,'g')
plt.show()
st.pyplot(fig3)


x=[]
y=[]
for i in range(100, data_test_scaler.shape[0]):
    x.append(data_test_scaler[i-100:i])
    y.append(data_test_scaler[i,0])
    

x,y = np.array(x), np.array(y)

predict = model.predict(x)

scale = 1/scaler.scale_

predict = predict * scale
y= y*scale

st.subheader("Original Price vs Predicted Price")
fig4 = plt.figure(figsize=(8,6))
plt.plot(predict,'r',label = 'Original Price')
plt.plot(y,'g', label='Predicted Price')
plt.xlabel('Time')
plt.ylabel('Price')
plt.show()
st.pyplot(fig4)


# # Số ngày dự đoán trong tương lai (3 tháng ~ 90 ngày giao dịch)
# future_days = 90

# # Lấy 100 ngày cuối cùng từ dữ liệu test để làm đầu vào cho dự đoán
# future_input = data_test_scaler[-100:].tolist()

# # Danh sách lưu kết quả dự đoán
# future_predictions = []

# for _ in range(future_days):
#     # Chuyển đổi dữ liệu thành numpy array và reshape thành dạng phù hợp
#     input_array = np.array(future_input[-100:])  # Lấy 100 ngày gần nhất
#     input_array = input_array.reshape(1, 100, 1)

#     # Dự đoán ngày tiếp theo
#     predicted_price = model.predict(input_array)[0][0]

#     # Chuyển đổi về giá gốc
#     predicted_price = predicted_price * scale
#     future_predictions.append(predicted_price)

#     # Thêm dự đoán vào danh sách để tiếp tục dự đoán ngày tiếp theo
#     future_input.append(predicted_price / scale)

# # Tạo danh sách ngày tháng tương ứng
# last_date = data.index[-1]  # Ngày cuối cùng trong tập dữ liệu
# future_dates = [last_date + datetime.timedelta(days=i) for i in range(1, future_days + 1)]

# # Hiển thị biểu đồ dự đoán tương lai
# st.subheader("📈 Predicted Prices for Next 3 Months")
# fig5 = plt.figure(figsize=(10,6))
# plt.plot(future_dates, future_predictions, 'r', label='Predicted Future Prices')
# plt.xlabel("Date")
# plt.ylabel("Price")
# plt.legend()
# st.pyplot(fig5)

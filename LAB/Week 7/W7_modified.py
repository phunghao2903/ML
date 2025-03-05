import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os.path
import datetime as dt
import yfinance as yf
from os import path
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

stock = "AAPL"
start = dt.datetime(2010, 1, 1)
end = dt.datetime(2024, 1, 1)
df = yf.download(stock, start, end)

df = df.reset_index()
df.head()

data_train = df[['Close']].values

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range = (0, 1))

data_training = scaler.fit_transform(data_train)

x_train, y_train = [], []
no_of_sample = len(data_train)

for i in range(60, no_of_sample):
    x_train.append(data_training[i-60:i, 0])
    y_train.append(data_training[i, 0])

x_train, y_train = np.array(x_train), np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

model = Sequential()
model.add(LSTM(units = 50, return_sequences = True, input_shape = (x_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units = 50, return_sequences = True))
model.add(Dropout(0.3))
model.add(LSTM(units = 50, return_sequences = True))
model.add(Dropout(0.4))
model.add(LSTM(units = 50))
model.add(Dropout(0.5))
model.add(Dense(units = 1))
model.compile(optimizer = 'adam', loss = 'mean_squared_error')

if path.exists("D:/VKU/Nam_3/Ki_2/Machine Learning/ML/PY/W7/stock_future_2.keras"):
    model.load_weights("D:/VKU/Nam_3/Ki_2/Machine Learning/ML/PY/W7/stock_future_2.keras")
else:
    model.fit(x_train, y_train, epochs = 100, batch_size = 32)
    model.save("D:/VKU/Nam_3/Ki_2/Machine Learning/ML/PY/W7/stock_future_2.keras")

# tap test lay trong khoang tu thang 2/2024 toi thoi diem hien tai
stock = "AAPL"
start = dt.datetime(2024, 2, 1)
end = dt.datetime.today()
real_data_price = yf.download(stock, start, end)

real_stock_price = real_data_price[['Close']].values

data_total = pd.concat((df['Close'], real_data_price['Close']), axis = 0)
inputs= data_total[len(data_total) - len(real_data_price) - 60:].values
inputs = np.clip(inputs, df['Close'].min(), df['Close'].max())
inputs= inputs.reshape(-1,1)
inputs = scaler.transform(inputs)


x_test = []
no_of_sample = len(inputs)

for i in range(60, no_of_sample):
    x_test.append(inputs[i-60:i, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
predicted_stock_price = model.predict(x_test)
predicted_stock_price = scaler.inverse_transform(predicted_stock_price)

plt.plot(real_stock_price, color = 'red', label = 'Real  Stock Price')
plt.plot(predicted_stock_price, color = 'blue', label = 'Predicted  Stock Price')
plt.title(f'{stock} Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel(f'{stock} Stock Price')
plt.legend()
plt.show()

# du doan trong 1 thang tiep theo
# nghia la tu bay gio den 24/03/2025


# lay 60 ngay cua tap test de tinh cac ngay tiep theo 
real_data_price = real_data_price['Close'][len(real_data_price)-60:len(real_data_price)].to_numpy()
real_data_price = np.array(real_data_price)

inputs = real_data_price
inputs = inputs.reshape(-1,1)
inputs = scaler.transform(inputs)

from datetime import timedelta

current_date = dt.datetime.today()
predicted_prices = []
forecast_dates = []

i = 0
while i < 7:
    x_test = []
    no_of_sample = len(real_data_price)

    # Lấy dữ liệu cuối cùng để dự đoán
    x_test.append(inputs[no_of_sample - 60:no_of_sample, 0])
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    # Dự đoán
    predicted_stock_price = model.predict(x_test)

    # Chuyển dữ liệu từ khoảng (0,1) về giá trị thực tế
    predicted_stock_price = scaler.inverse_transform(predicted_stock_price)

    # Lưu giá trị dự đoán
    predicted_prices.append(predicted_stock_price[0][0])
    forecast_dates.append((current_date + timedelta(days=i)).strftime('%d/%m/%Y'))

    # Cập nhật dữ liệu để dự đoán tiếp
    real_data_price = np.append(real_data_price, predicted_stock_price[0][0])
    inputs = real_data_price.reshape(-1, 1)
    inputs = scaler.transform(inputs)

    i += 1

# Vẽ biểu đồ dự đoán giá cổ phiếu
plt.figure(figsize=(10, 5))
plt.plot(forecast_dates, predicted_prices, marker='o', linestyle='-', color='blue', label="Predicted Price")
plt.xlabel("Date")
plt.ylabel("Predicted Stock Price")
plt.title(f"Predicted Stock Price for {stock} in the Next 7 Days")
plt.xticks(rotation=45)
plt.legend
plt.show()

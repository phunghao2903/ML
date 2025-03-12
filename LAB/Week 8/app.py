from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import yfinance as yf
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler
import io
import base64
import os

app = Flask(__name__)
scaler = MinMaxScaler(feature_range=(0, 1))

def get_stock_data(stock, start, end):
    df = yf.download(stock, start, end)
    df = df.reset_index()
    return df

def prepare_data(df):
    data_train = df[['Close']].values
    scaled_data = scaler.fit_transform(data_train)
    return scaled_data, data_train

def create_or_load_model(stock, x_train, y_train):
    model_path = f"D:/VKU/Nam_3/Ki_2/Machine Learning/ML/PY/W8/stock_future_3.keras"
    if os.path.exists(model_path):
        model = load_model(model_path)
    else:
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.3))
        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.4))
        model.add(LSTM(units=50))
        model.add(Dropout(0.5))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train, y_train, epochs=100, batch_size=32)
        model.save(model_path)
    return model

def train_and_predict(stock):
    start_date = dt.datetime(2010, 1, 1)
    end_date = dt.datetime(2024, 12, 1)  # Lấy dữ liệu đến tháng 12/2024
    
    # Lấy toàn bộ dữ liệu từ Yahoo Finance
    df = get_stock_data(stock, start_date, end_date)
    data_all, data_values = prepare_data(df)

    # Xác định số lượng mẫu cho tập train (80%) và test (20%)
    split_index = int(len(data_values) * 0.8)  # Chia tỷ lệ 80% train - 20% test
    data_train, data_test = data_all[:split_index], data_all[split_index:]
    
    # Chuẩn bị dữ liệu train
    x_train, y_train = [], []
    for i in range(60, len(data_train)):
        x_train.append(data_train[i-60:i, 0])
        y_train.append(data_train[i, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))

    # Huấn luyện mô hình
    model = create_or_load_model(stock, x_train, y_train)
    
    # Chuẩn bị dữ liệu test
    x_test, y_test = [], []
    for i in range(60, len(data_test)):
        x_test.append(data_test[i-60:i, 0])
        y_test.append(data_test[i, 0])
    
    x_test, y_test = np.array(x_test), np.array(y_test)
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], 1))

    # Dự đoán giá cổ phiếu
    predicted_stock_price = model.predict(x_test)
    predicted_stock_price = scaler.inverse_transform(predicted_stock_price)
    real_stock_price = scaler.inverse_transform(y_test.reshape(-1, 1))

    return real_stock_price, predicted_stock_price, model


def forecast_future(model, real_data_price):
    inputs = real_data_price.reshape(-1, 1)
    inputs = scaler.transform(inputs)
    
    predicted_prices = []
    forecast_dates = []
    current_date = dt.datetime.today()
    
    for i in range(7):
        x_test = np.array([inputs[-60:, 0]])
        x_test = x_test.reshape(1, 60, 1)
        predicted_stock_price = model.predict(x_test)
        predicted_stock_price = scaler.inverse_transform(predicted_stock_price)
        
        predicted_prices.append(predicted_stock_price[0][0])
        forecast_dates.append((current_date + dt.timedelta(days=i)).strftime('%d/%m/%Y'))
        
        real_data_price = np.append(real_data_price, predicted_stock_price[0][0])
        inputs = real_data_price.reshape(-1, 1)
        inputs = scaler.transform(inputs)
    
    return forecast_dates, predicted_prices

def plot_graph(real_price, predicted_price, future_dates, future_prices):
    fig, ax = plt.subplots(2, 1, figsize=(10, 10))
    ax[0].plot(real_price, color='red', label='Real Stock Price')
    ax[0].plot(predicted_price, color='blue', label='Predicted Stock Price')
    ax[0].set_title('Stock Price Prediction')
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Stock Price')
    ax[0].legend()
    
    ax[1].plot(future_dates, future_prices, marker='o', linestyle='-', color='blue', label="Predicted Future Price")
    ax[1].set_title('Predicted Stock Price for Next 7 Days')
    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Stock Price')
    ax[1].tick_params(axis='x', rotation=45)
    ax[1].legend()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock = request.form['stock']
        real_price, predicted_price, model = train_and_predict(stock)
        future_dates, future_prices = forecast_future(model, real_price[-60:])
        plot_url = plot_graph(real_price, predicted_price, future_dates, future_prices)
        return render_template('index.html', stock=stock, plot_url=plot_url)
    return render_template('index.html', stock=None)

if __name__ == '__main__':
    app.run(debug=True)
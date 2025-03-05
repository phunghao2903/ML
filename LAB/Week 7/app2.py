from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import yfinance as yf
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import io
import base64

app = Flask(__name__)
model = load_model("D:/VKU/Nam_3/Ki_2/Machine Learning/ML/PY/W7/stock_future_2.keras")
scaler = MinMaxScaler(feature_range=(0, 1))

def get_stock_data(stock, start, end):
    df = yf.download(stock, start, end)
    df = df.reset_index()
    return df

def prepare_data(df):
    data_train = df[['Close']].values
    scaled_data = scaler.fit_transform(data_train)
    return scaled_data, data_train

def predict_stock(model, stock):
    start_train = dt.datetime(2010, 1, 1)
    end_train = dt.datetime(2024, 1, 1)
    df = get_stock_data(stock, start_train, end_train)
    data_training, _ = prepare_data(df)
    
    start_test = dt.datetime(2024, 2, 1)
    end_test = dt.datetime.today()
    real_data_price = get_stock_data(stock, start_test, end_test)
    real_stock_price = real_data_price[['Close']].values
    
    data_total = pd.concat((df['Close'], real_data_price['Close']), axis=0)
    inputs = data_total[len(data_total) - len(real_data_price) - 60:].values
    inputs = inputs.reshape(-1,1)
    inputs = scaler.transform(inputs)
    
    x_test = []
    for i in range(60, len(inputs)):
        x_test.append(inputs[i-60:i, 0])
    x_test = np.array(x_test).reshape(len(x_test), 60, 1)
    predicted_stock_price = model.predict(x_test)
    predicted_stock_price = scaler.inverse_transform(predicted_stock_price)
    
    return real_stock_price, predicted_stock_price

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
        real_price, predicted_price = predict_stock(model, stock)
        future_dates, future_prices = forecast_future(model, real_price[-60:])
        plot_url = plot_graph(real_price, predicted_price, future_dates, future_prices)
        return render_template('index.html', stock=stock, plot_url=plot_url)
    return render_template('index.html', stock=None)

if __name__ == '__main__':
    app.run(debug=True)

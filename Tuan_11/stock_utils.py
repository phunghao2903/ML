import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model
import streamlit as st

def fetch_stock_data(symbol, interval, start_date, end_date):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def get_last_trading_day():
    today = datetime.now()
    weekday = today.weekday()  # 0: Thứ Hai, 6: Chủ Nhật
    
    if weekday == 6:  # Chủ Nhật
        return today - timedelta(days=2)
    elif weekday == 5:  # Thứ Bảy
        return today - timedelta(days=1)
    elif weekday == 0 and datetime.now().hour < 9:  # Thứ Hai trước 9h sáng
        return today - timedelta(days=3)
    return today

def fetch_latest_trading_data(symbol, interval="5m"):
    last_trading_day = get_last_trading_day()
    start_date = last_trading_day.replace(hour=9, minute=0, second=0)
    end_date = last_trading_day.replace(hour=15, minute=0, second=0)
    df = fetch_stock_data(symbol, interval, start_date, end_date)
    return df

def predict_stock_prices_lstm(df, symbol, time_range):
    if df.empty or len(df) < 30:
        st.warning("Not enough data. Fetching latest trading data.")
        df = fetch_latest_trading_data(symbol)
    
    last_30 = df['Close'].values[-30:].reshape(1, 30, 1)
    model_key = symbol.replace(".VN", "")
    model_path = f"/home/levanhuy/Machine_Learning/Tuan_11/model/predict_{model_key}_{time_range}.keras"
    
    try:
        model = load_model(model_path)
        predictions = model.predict(last_30)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return pd.DataFrame()
    
    future_dates = [df.index[-1] + timedelta(minutes=5 * i) for i in range(1, 13)]
    predictions = predictions.flatten()[:len(future_dates)]  # Ensure matching lengths
    
    print(f"Future dates: {len(future_dates)}, Predictions: {len(predictions)}")  # Debugging line
    
    prediction_df = pd.DataFrame({'Date': future_dates, 'Predicted Close': predictions})
    
    # Chỉ hiển thị dữ liệu ngày giao dịch gần nhất nếu hôm nay không phải ngày giao dịch
    today = datetime.now()
    if today.weekday() >= 5 or (today.weekday() == 0 and today.hour < 9):
        df = fetch_latest_trading_data(symbol, interval="1d")
    
    return prediction_df

# Các thư viện đã có trong web.py
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import matplotlib.dates as mdates
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import pytz
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_runner import RerunData


# Load model đã huấn luyện
model = load_model('predict_BSI_1d.keras')

# Thêm hàm tìm ngày gần nhất có dữ liệu
def find_nearest_data_date(stock_symbol, target_date, interval, required_points=30):
    target_date = pd.Timestamp(target_date)
    max_days_check = 10  # Giới hạn số ngày lùi về quá khứ để tìm dữ liệu
    for i in range(max_days_check):
        check_date = target_date - pd.Timedelta(days=i)
        start_date = check_date.strftime("%Y-%m-%d")
        end_date = (check_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Tải dữ liệu từ Yahoo Finance
        data = yf.download(stock_symbol, start=start_date, end=end_date, interval=interval)
        
        if len(data) >= required_points:
            return start_date, end_date, data  # Trả về ngày hợp lệ và dữ liệu
    
    raise ValueError("Không tìm được dữ liệu đủ trong khoảng thời gian đã kiểm tra.")

def get_prediction_time_range(target_date, current_time, market_open="09:00", market_close="14:45"):
    market_open_time = datetime.strptime(f"{target_date} {market_open}", "%Y-%m-%d %H:%M")
    market_close_time = datetime.strptime(f"{target_date} {market_close}", "%Y-%m-%d %H:%M")
    
    if current_time >= market_close_time:
        # Nếu đã qua giờ đóng cửa, dự đoán cho ngày tiếp theo từ 09:00 đến 10:00
        next_trading_day = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        start_time = f"{next_trading_day} 09:00"
    elif current_time < market_open_time:
        # Nếu chưa mở cửa, bắt đầu từ 09:00
        start_time = f"{target_date} 09:00"
    else:
        # Nếu đang trong giờ giao dịch, dự đoán 1 giờ tiếp theo nhưng không quá 14:45
        start_time = current_time.strftime("%Y-%m-%d %H:%M")
        end_time = (current_time + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        if end_time > market_close:
            end_time = market_close  # Giới hạn không quá 14:45
    
    return pd.date_range(start=start_time, periods=12, freq='5min', tz="Asia/Ho_Chi_Minh")

# Cập nhật hàm dự đoán giá sử dụng hàm `get_prediction_time_range`
def predict_stock_price(symbol, target_date, current_time, timeframe="5m"):
    # Lấy thời gian dự đoán hợp lệ từ hàm get_prediction_time_range
    prediction_times = get_prediction_time_range(target_date, current_time)

    start_date, end_date, data = find_nearest_data_date(symbol, target_date, timeframe)

    data.index = data.index.tz_convert("Asia/Ho_Chi_Minh")
    data = data[['Close']].dropna()

    # Chuẩn bị dữ liệu đầu vào
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data)
    X_input = data_scaled[-30:].reshape(1, 30, 1)

    # Lấy giá tham chiếu
    ref_price = float(data.iloc[-1]['Close'])
    upper_limit = ref_price * 1.07
    lower_limit = ref_price * 0.93

    def apply_tick_size(price):
        if price < 10000:
            return round(price / 10) * 10
        elif price < 50000:
            return round(price / 50) * 50
        else:
            return round(price / 100) * 100

    # Dự đoán giá
    num_predictions = len(prediction_times)  # Số lượng dự đoán theo thời gian đã tính
    y_pred = []
    for _ in range(num_predictions):
        pred = model.predict(X_input)[0, 0]
        pred_inv = float(scaler.inverse_transform([[pred]])[0, 0])
        
        pred_inv = max(lower_limit, min(upper_limit, pred_inv))
        pred_inv = apply_tick_size(pred_inv)
        y_pred.append(pred_inv)
        
        X_input = np.append(X_input[:, 1:, :], [[[scaler.transform([[pred_inv]])[0, 0]]]], axis=1)

    return y_pred, prediction_times


# Hàm vẽ biểu đồ
def create_prediction_chart(symbol, target_date,current_time):
    # Lấy dữ liệu dự đoán
    y_pred, time_range = predict_stock_price(symbol, target_date, current_time)
    
    # Vẽ biểu đồ dự đoán
    plt.figure(figsize=(14, 5))
    plt.plot(time_range, y_pred, color='red', linestyle='dashed', label=f'Giá dự đoán ngày {target_date}')
    plt.title(f'Dự đoán giá cổ phiếu ngày {target_date} (mỗi 5 phút)')
    plt.xlabel('Thời gian')
    plt.ylabel('Giá cổ phiếu')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz="Asia/Ho_Chi_Minh"))
    plt.xticks(rotation=45)
    return plt

def fetch_stock_data(symbol, timeframe):
    """
    Fetch stock data for different timeframes.
    If no data is available for today, use the last available data.
    
    Args:
        symbol (str): Stock symbol
        timeframe (str): Selected timeframe
    
    Returns:
        pd.DataFrame: Stock price data
    """
    try:
        intervals = {
            "1d": "1m",   # 1-minute intervals for intraday
            "5d": "1h",   # 1-hour intervals for 5 days
            "1mo": "1d",  # Daily intervals for 1 month
            "6mo": "1d",  # Daily intervals for 6 months
            "1y": "1d"    # Daily intervals for 1 year
        }
        
        end_date = datetime.now()
        
        if timeframe == "1d":
            # Bắt đầu từ ngày hôm trước
            start_date = end_date - timedelta(days=1)
            end_date = start_date.replace(hour=23, minute=59, second=59)
            
            # Lấy dữ liệu của ngày hôm trước
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=intervals[timeframe])

            # Nếu không có dữ liệu, thử tìm ngày gần nhất có dữ liệu
            if df.empty:
                st.warning(f"Không có dữ liệu ngày {start_date.strftime('%Y-%m-%d')}, đang tìm ngày gần nhất có dữ liệu...")
                df = ticker.history(period="7d", interval=intervals[timeframe])

                if not df.empty:
                    # Lấy ngày gần nhất có dữ liệu
                    last_available_date = df.index[-1].date()
                    df = df[df.index.date == last_available_date]  # Chỉ lấy dữ liệu của ngày đó
                    st.info(f"Hiển thị dữ liệu của ngày gần nhất có sẵn: {last_available_date}")
                else:
                    st.error(f"Không tìm thấy dữ liệu lịch sử cho {symbol} trong 7 ngày qua.")
                    return pd.DataFrame()
        else:
            days_mapping = {
                "5d": 5,
                "1mo": 30,
                "6mo": 180,
                "1y": 365
            }
            start_date = end_date - timedelta(days=days_mapping[timeframe])
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=intervals[timeframe])
        
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
    

def create_stock_chart(df, symbol, timeframe):
    """
    Create an interactive line chart for stock prices
    
    Args:
        df (pd.DataFrame): Stock price data
        symbol (str): Stock symbol
        timeframe (str): Selected timeframe
    
    Returns:
        plotly.graph_objs._figure.Figure: Interactive chart
    """
    # Create line chart with markers for all timeframes
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['Close'], 
        mode='lines+markers', 
        name=f'{symbol} Price',
        line=dict(color='blue', width=2),
        marker=dict(size=4)  # Add small markers
    ))
    
    # Customize layout
    title_text = f'{symbol} Stock Price - {timeframe}'
    if timeframe == "custom":
        title_text = f'{symbol} Stock Price - Custom Range'
        
    fig.update_layout(
        title=title_text,
        xaxis_title='Date/Time',
        yaxis_title='Price',
        height=500,
        template='plotly_white',
        xaxis=dict(
            # Adjust tickformat based on timeframe
            tickformat='%Y-%m-%d %H:%M' if timeframe == '1d' else '%Y-%m-%d',
            # Rotate tick labels for better readability
            tickangle=45
        )
    )
    
    return fig


def get_realtime_update_strategy():
    """
    Determine the most appropriate real-time update strategy
    based on Streamlit version and capabilities.
    
    Returns:
        function: Appropriate update method
    """
    try:
        # Check for newer Streamlit versions
        import streamlit as st
        if hasattr(st, 'rerun'):
            return st.rerun
        elif hasattr(st, 'experimental_rerun'):
            return st.experimental_rerun
    except ImportError:
        pass
    
    # Fallback strategy
    def custom_rerun():
        st.warning("Unable to auto-refresh. Please manually refresh the page.")
    
    return custom_rerun


def create_combined_chart(symbol, target_date, current_time, timeframe="1d"):
    # Lấy dữ liệu thực tế
    df = fetch_stock_data(symbol, timeframe)
    
    # Lấy dữ liệu dự đoán
    y_pred, time_range = predict_stock_price(symbol, target_date, current_time)
    
    # Tạo biểu đồ
    fig = go.Figure()
    
    # Thêm biểu đồ giá thực tế vào biểu đồ
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['Close'], 
        mode='lines+markers', 
        name=f'{symbol} Giá thực tế',
        line=dict(color='blue', width=2),
        marker=dict(size=4)  # Thêm markers nhỏ
    ))
    
    # Thêm biểu đồ dự đoán vào biểu đồ
    # Dự đoán sẽ được vẽ nối tiếp sau điểm cuối cùng của dữ liệu thực tế
    last_date = df.index[-1]
    new_dates = pd.date_range(start=last_date, periods=len(y_pred)+1, freq="5min")[1:]
    
    fig.add_trace(go.Scatter(
        x=new_dates, 
        y=y_pred, 
        mode='lines+markers', 
        name=f'{symbol} Giá dự đoán',
        line=dict(color='red', dash='dash', width=2),
        marker=dict(size=4)
    ))
    
    # Tùy chỉnh biểu đồ
    title_text = f'{symbol} Giá cổ phiếu và Dự đoán'
    fig.update_layout(
        title=title_text,
        xaxis_title='Ngày/Thời gian',
        yaxis_title='Giá',
        height=500,
        template='plotly_white',
        xaxis=dict(
            tickformat='%Y-%m-%d %H:%M' if timeframe == '1d' else '%Y-%m-%d',
            tickangle=45
        )
    )
    
    return fig


# Thêm vào hàm main trong web.py
def main():
    st.set_page_config(page_title="Real-Time Stock Tracker", layout="wide")
    st.title("🚀 Real-Time Stock Price Tracker")
    
    # Stock selection
    stocks = {
        "BSI.VN": "BSI.VN", 
        "VDS.VN": "VDS.VN", 
        "VIX.VN": "VIX.VN"
    }
    
    # Sidebar for configuration
    with st.sidebar:
        selected_stock = st.selectbox(
            "Select Stock", 
            list(stocks.keys()), 
            help="Choose a Vietnamese stock to track"
        )
        
        time_range = st.radio(
            "Select Time Range", 
            ["1d", "5d", "1mo", "6mo", "1y", "custom"], 
            horizontal=True
        )
        
        # Date picker for custom date range
        if time_range == "custom":
            today = datetime.now()
            max_date = today
            
            # Default start date (30 days ago)
            default_start = today - timedelta(days=30)
            
            # Choose start date
            start_date = st.date_input(
                "Start Date",
                value=default_start,
                max_value=max_date
            )
            
            # Choose end date
            end_date = st.date_input(
                "End Date",
                value=today,
                min_value=start_date,
                max_value=max_date
            )
            
            st.info("Dữ liệu lịch sử sẽ được hiển thị theo ngày bạn chọn.")
    
    # Fetch stock data based on selected timeframe
    if time_range == "custom":
        df = fetch_stock_data_custom(selected_stock, start_date, end_date)
    else:
        df = fetch_stock_data(selected_stock, time_range)
    
    if not df.empty:
        # Create and display chart
        # chart = create_stock_chart(df, selected_stock, time_range)
        # st.plotly_chart(chart, use_container_width=True)

        chart = create_combined_chart(selected_stock, datetime.now().strftime("%Y-%m-%d"), datetime.now(), time_range)
        st.plotly_chart(chart, use_container_width=True)
        
        # Price metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Price", f"{df['Close'][-1]:.2f}")
        with col2:
            # Calculate daily change differently for different timeframes
            if len(df) > 1:
                daily_change = ((df['Close'][-1] - df['Close'][0]) / df['Close'][0]) * 100
                st.metric("Change", f"{daily_change:.2f}%")
        
        # Real-time update for 1-day view
        if time_range == "1d":
            st.write(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Display prediction chart
            st.subheader("Giá dự đoán tiếp theo (1 giờ tới):")
            current_time = datetime.now()
            prediction_chart = create_prediction_chart(selected_stock, datetime.now().strftime("%Y-%m-%d"),  current_time )
            st.pyplot(prediction_chart)
        
        # Real-time update for 1-day view
        if time_range == "1d":
            rerun_method = get_realtime_update_strategy()
            time.sleep(60)  # Wait for 1 minute
            rerun_method()

if __name__ == "__main__":
    main()
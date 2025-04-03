import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_runner import RerunData

def get_realtime_update_strategy():
    
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

def fetch_stock_data(symbol, timeframe):
    
    try:
        # Define interval based on timeframe
        intervals = {
            "1d": "1m",   # 1-minute intervals for intraday
            "5d": "1h",   # 1-hour intervals for 5 days
            "1mo": "1d",  # Daily intervals for 1 month
            "6mo": "1d",  # Daily intervals for 6 months
            "1y": "1d"    # Daily intervals for 1 year
        }
        
        # Get today's date
        end_date = datetime.now()
        
        # Set start date based on timeframe
        if timeframe == "1d":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            days_mapping = {
                "5d": 5,
                "1mo": 30,
                "6mo": 180,
                "1y": 365
            }
            start_date = end_date - timedelta(days=days_mapping[timeframe])
        
        # Fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=intervals[timeframe])

        # Nếu không có dữ liệu, lấy dữ liệu gần nhất có sẵn
        if df.empty:
            st.warning(f"No data available for {symbol} today. Fetching last available data...")
            df = ticker.history(period="7d", interval=intervals[timeframe])  # Lấy dữ liệu 7 ngày gần nhất
            
            if df.empty:
                st.error(f"No historical data available for {symbol}")
                return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def fetch_stock_data_custom(symbol, start_date, end_date):
    
    try:
        # Convert datetime.date to datetime.datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_datetime, end=end_datetime, interval="1d")
        
        if df.empty:
            st.warning(f"Không có dữ liệu cho {symbol} trong khoảng thời gian này.")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Lỗi khi lấy dữ liệu: {e}")
        return pd.DataFrame()

def create_stock_chart(df, symbol, timeframe):
    fig = go.Figure()
    
    # Thêm đường giá (Price Line)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['Close'], 
        mode='lines', 
        name=f'{symbol} Price',
        line=dict(color='#72bcd4', width=1.5)  # Màu xanh nhạt, đường mỏng hơn
    ))
    
    # Thiết lập giao diện nền tối
    title_text = f'{symbol} Stock Price - {timeframe}'
    if timeframe == "custom":
        title_text = f'{symbol} Stock Price - Custom Range'
        
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=20, color="white")),
        xaxis=dict(
            title='Date',
            tickformat='%Y-%m-%d' if timeframe != '1d' else '%Y-%m-%d %H:%M',
            tickangle=45,
            gridcolor='#444444',
            color='white'
        ),
        yaxis=dict(
            title='Price',
            gridcolor='#444444',
            color='white'
        ),
        height=500,
        template='plotly_dark',  # Nền tối giống ảnh bạn gửi
        plot_bgcolor='#1e1e1e',  # Màu nền chính (xám đậm)
        paper_bgcolor='#1e1e1e'  # Màu nền ngoài biểu đồ
    )
    
    return fig

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
        chart = create_stock_chart(df, selected_stock, time_range)
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
        
        # Use appropriate rerun method
        rerun_method = get_realtime_update_strategy()
        
        # Add a small delay and then rerun
        time.sleep(60)  # Wait for 1 minute
        rerun_method()

if __name__ == "__main__":
    main() 
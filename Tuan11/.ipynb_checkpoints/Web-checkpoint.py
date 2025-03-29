import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time


from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_runner import RerunData

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

def fetch_stock_data(symbol, timeframe):
    """
    Fetch stock data for different timeframes
    
    Args:
        symbol (str): Stock symbol
        timeframe (str): Selected timeframe
    
    Returns:
        pd.DataFrame: Stock price data
    """
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
        
        if df.empty:
            st.warning(f"No data available for {symbol}")
            return pd.DataFrame()
        
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
    fig.update_layout(
        title=f'{symbol} Stock Price - {timeframe}',
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
            ["1d", "5d", "1mo", "6mo", "1y"], 
            horizontal=True
        )
    
    # Fetch stock data
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
                if time_range == "1d":
                    daily_change = ((df['Close'][-1] - df['Close'][0]) / df['Close'][0]) * 100
                else:
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
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/stock-data', methods=['GET'])
def get_stock_data():
    try:
        # Get parameters from request
        symbol = request.args.get('symbol', 'BSI.VN')
        timeframe = request.args.get('timeframe', '1d')
        
        # Custom date range
        if timeframe == 'custom':
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')
            
            if not start_date_str or not end_date_str:
                return jsonify({"error": "Start date and end date required for custom timeframe"}), 400
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
                df = fetch_stock_data_custom(symbol, start_date, end_date)
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        else:
            df = fetch_stock_data(symbol, timeframe)
        
        if df.empty:
            return jsonify({"error": f"No data available for {symbol}"}), 404
        
        # Convert DataFrame to JSON
        result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": format_data_for_json(df)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def format_data_for_json(df):
    """Format DataFrame for JSON response"""
    data = []
    for index, row in df.iterrows():
        # Convert datetime to string for JSON serialization
        date_str = index.strftime('%Y-%m-%d %H:%M:%S')
        data.append({
            "date": date_str,
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close']),
            "volume": int(row['Volume'])
        })
    return data

def fetch_stock_data(symbol, timeframe):
    """Fetch stock data for predefined timeframes"""
    # Define intervals based on timeframe
    intervals = {
        "1d": "1m",   # 1-minute intervals for intraday
        "5d": "1h",   # 1-hour intervals for 5 days
        "1w": "1h",   # 1-hour intervals for 1 week
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
            "1w": 7,
            "1mo": 30,
            "6mo": 180,
            "1y": 365
        }
        start_date = end_date - timedelta(days=days_mapping[timeframe])
    
    # Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date, interval=intervals[timeframe])

    # If no data, fetch most recent available data
    if df.empty:
        df = ticker.history(period="7d", interval=intervals[timeframe])
    
    return df

def fetch_stock_data_custom(symbol, start_date, end_date):
    """Fetch stock data for custom date range"""
    # Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date, interval="1d")
    return df

@app.route('/api/available-stocks', methods=['GET'])
def get_available_stocks():
    """Return a list of available stocks"""
    stocks = {
        "BSI.VN": "BSI",
        "VDS.VN": "VDS",
        "VIX.VN": "VIX",
        "VND.VN": "VND",
        "SSI.VN": "SSI"
    }
    return jsonify(stocks)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
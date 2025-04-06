from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


#-------------------------------------------------------------------------------------------
# xử lý yêu cầu GET từ client
# lấy dữ liệu cổ phiếu
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




#-------------------------------------------------------------------------------------------
# Chuyển đổi dữ liệu từ DataFrame thành một định dạng JSON 
# để client có thể sử dụng.

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


#-------------------------------------------------------------------------------------------
# Lấy dữ liệu cổ phiếu từ Yahoo Finance
def fetch_stock_data(symbol, timeframe):
    """Fetch stock data for predefined timeframes"""
    # Define intervals based on timeframe
    intervals = {
        "1d": "1m",
        "5d": "1h",
        "1w": "1h",
        "1mo": "1d",
        "6mo": "1d",
        "1y": "1d"
    }
    
    # Get today's date
    end_date = datetime.now()
    
    # Set start date based on timeframe
    if timeframe == "1d":
        # start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
    
        # ticker = yf.Ticker(symbol)
        # df = ticker.history(start=start_date, end=end_date, interval=intervals[timeframe])
        ticker = yf.Ticker(symbol)
            # df = ticker.history(start=start_date, end=end_date, interval=intervals[timeframe])
            # Giả sử end_date đã có sẵn
        current_date = end_date
        days_to_fetch = 2  # số ngày liên tiếp muốn lấy
        all_data = []

        while len(all_data) < days_to_fetch:
            start_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_day = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            df_temp = ticker.history(start=start_day, end=end_day, interval=intervals[timeframe])

            if not df_temp.empty:
                all_data.append(df_temp)

            current_date -= timedelta(days=1)  # Lùi lại 1 ngày

        # Ghép 2 ngày lại thành 1 dataframe
        df = pd.concat(all_data[::-1])  # đảo ngược lại đúng thứ tự ngày tăng dần
        
        # # tách làm 2 phần
        # # Lấy ngày duy nhất trong df
        # unique_days = sorted(df_full.index.normalize().unique())

        # # Chia df theo từng ngày
        # df_day1 = df_full[df_full.index.normalize() == unique_days[0]]
        # df = df_full[df_full.index.normalize() == unique_days[1]]
        

    elif timeframe != "1d":
        days_mapping = {
            "5d": 5,
            "1w": 7,
            "1mo": 30,
            "6mo": 180,
            "1y": 365
        }
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_mapping[timeframe])
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=intervals[timeframe])
        
    
        # If no data available for today, fetch data for yesterday

        # Thử 1 ngày liền trước
        # yesterday = end_date - timedelta(days=1)
        # lấy dữ liệu 2 ngày
        
        # print(yesterday_2)
        # start_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        # end_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

        # bắt đầu vs lấy từ 2 ngày trước 
        #start_yesterday = yesterday_2.replace(hour=0, minute=0, second=0, microsecond=0)
        # lấy đến hết ngày hôm qua 
        #end_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # df = ticker.history(start=start_yesterday, end=end_yesterday, interval=intervals[timeframe])
        # tách làm 2 phần
        # df_before = df_full.loc[yesterday_2]
        # df = df_full.loc[yesterday]
        # print(df_before)
        # print(df)

        # Giả sử end_date đã có sẵn
        # current_date = end_date
        # days_to_fetch = 2  # số ngày liên tiếp muốn lấy
        # all_data = []

        # while len(all_data) < days_to_fetch:
        #     start_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        #     end_day = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        #     df_temp = ticker.history(start=start_day, end=end_day, interval=intervals[timeframe])

        #     if not df_temp.empty:
        #         all_data.append(df_temp)

        #     current_date -= timedelta(days=1)  # Lùi lại 1 ngày

        # Ghép 2 ngày lại thành 1 dataframe
        # df_full = pd.concat(all_data[::-1])  # đảo ngược lại đúng thứ tự ngày tăng dần
        # tách làm 2 phần
        # Lấy ngày duy nhất trong df
        # unique_days = sorted(df_full.index.normalize().unique())

        # Chia df theo từng ngày
        # df_day1 = df_full[df_full.index.normalize() == unique_days[0]]
        # df = df_full[df_full.index.normalize() == unique_days[1]]


        # if df.empty:
        #     yesterday = end_date - timedelta(days=2)
        #     start_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        #     end_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        #     df = ticker.history(start=start_yesterday, end=end_yesterday, interval=intervals[timeframe])
        
        
    if df.empty:
        df = ticker.history(period="7d", interval=intervals[timeframe])

    
    # print(df_day1)
    print(df)
    return df

#-------------------------------------------------------------------------------------------
def fetch_stock_data_custom(symbol, start_date, end_date):
    """Fetch stock data for custom date range"""
    # Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date, interval="1d")
    return df


#-------------------------------------------------------------------------------------------
# Trả về danh sách các mã cổ phiếu có sẵn trong hệ thống.

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
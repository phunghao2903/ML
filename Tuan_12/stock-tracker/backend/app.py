from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes





# Tạo một monkey patch cho socketserver._SocketWriter.write
import socketserver

original_write = socketserver._SocketWriter.write

def patched_write(self, b):
    try:
        return original_write(self, b)
    except BrokenPipeError:
        return 0
    except OSError:
        return 0

socketserver._SocketWriter.write = patched_write


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
            df, prediction_result = fetch_stock_data(symbol, timeframe)
            print("Prediction result:", prediction_result)

        if df.empty:
            return jsonify({"error": f"No data available for {symbol}"}), 404

        
        # Base result dictionary
        result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": format_data_for_json(df)
        }

        # Add prediction data if it exists
        if prediction_result is not None:
            try:
                # Convert NumPy values to Python native types if needed
                prediction_data = {}

                for i in range(len(prediction_result)):

                    value = prediction_result[i]
                    # Convert NumPy types to native Python types
                    if hasattr(value, 'item'):  # Check if it's a NumPy scalar
                        value = value.item()
                    # Convert other complex types to strings if needed
                    if not isinstance(value, (int, float, str, bool, type(None))):
                        value = str(value)
                    prediction_data[f"value{i+1}"] = value
                
                result["prediction_result"] = prediction_data
                print("Final result with prediction:", result)

            except Exception as e:
                print(f"Error adding prediction data: {e}")
                # Continue without prediction data if there's an error

        

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
        "1d": "2m",
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
        
        
        ticker = yf.Ticker(symbol)
        
        # Giả sử end_date đã có sẵn
        current_date = end_date

        # số ngày liên tiếp muốn lấy
        days_to_fetch = 2  

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
        
        # tách làm 2 phần
        # Lấy ngày duy nhất trong df
        unique_days = sorted(df.index.normalize().unique())

        # Chia df theo từng ngày
        df_day1 = df[df.index.normalize() == unique_days[0]]
        df_day2 = df[df.index.normalize() == unique_days[1]]

        # Gọi hàm dự đoán
        prediction_result = predict(symbol, timeframe, df_day1, df_day2)   
        
        return df, prediction_result 

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
        
    
        
    if df.empty:
        df = ticker.history(period="7d", interval=intervals[timeframe])

    
    # print(df_day1)
    print(df)
    return df, None

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
        "SSI.VN": "SSI",
        "APG.VN": "APG",
        "ARG.VN": "ARG",
        "FTS.VN": "FTS",
        "HCM.VN": "HCM",
        "TVS.VN": "TVS"
        
    }
    return jsonify(stocks)


#-------------------------------------------------------------------------------------------
# Hàm dự đoán
def predict(symbol, timeframe, data1, data2):

    data1 = data1[['Close']].dropna()
    data2 = data2[['Close']].dropna()

    new_symbol = symbol.replace(".VN", "")
    
    model = load_model(f'D:/KHA/VKU/Nam_4/Ki_2/Machine_Learning/ML/Tuan_12/stock-tracker/backend/predict_{new_symbol}_{timeframe}.keras')
    
    # Tạo vùng giới hạn 7%
    ref_price = float(data1.iloc[-1]['Close'])
    # print(ref_price)
    upper_limit = ref_price * 1.07
    lower_limit = ref_price * 0.93

    # Chuẩn hóa từng phần
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data1)
    

    # Dự đoán từng điểm trong ngày 25/3
    y_pred = []
    X_input = data_scaled[-50:].reshape(1, 50, 1)
    

    for i in range(len(data2)):
        pred = model.predict(X_input)[0, 0]  # Dự đoán điểm tiếp theo
        pred_inv = float(scaler.inverse_transform([[pred]])[0, 0])
        
        # Giới hạn trong biên độ 7%
        pred_inv = max(lower_limit, min(upper_limit, pred_inv))
        
        # Áp dụng bước giá
        pred_inv = apply_tick_size(pred_inv)
        
        y_pred.append(pred_inv)
        
        # Cập nhật đầu vào với điểm mới nhất
        X_input = np.append(X_input[:, 1:, :], [[[scaler.transform([[pred_inv]])[0, 0]]]], axis=1)
        
        # Nếu có dữ liệu thực tế, cập nhật đầu vào bằng dữ liệu thực tế thay vì dự đoán
        if i < len(data2) - 1:
            actual_next = scaler.transform(data2.iloc[i + 1].values.reshape(-1, 1))[0, 0]
            X_input[:, -1, 0] = actual_next

    # Chuyển dữ liệu về giá trị gốc
    y_pred_inv = np.array(y_pred)
    print(len(y_pred_inv))

    return y_pred_inv
    

#-------------------------------------------------------------------------------------------
# Tạo các bước giá cho cổ phiếu 
def apply_tick_size(price):
    if price < 10000:
        return round(price / 10) * 10
    elif price < 50000:
        return round(price / 50) * 50
    else:
        return round(price / 100) * 100




if __name__ == '__main__':
    app.run(debug=True, port=5000)
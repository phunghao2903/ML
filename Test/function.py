import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os


def predict_future(data, prop, symbol, num_days):
    model_path = f'Model/{symbol}.keras'
    if not os.path.exists(model_path):
        return None

    model = load_model(model_path)
    last_data = data[prop].values[-30:].reshape(-1, 1)  # Dữ liệu 30 ngày cuối
    scaler = MinMaxScaler()
    last_data = scaler.fit_transform(last_data)

    future_preds = []
    for _ in range(num_days):
        input_seq = np.array(last_data[-30:]).reshape(1, 30, 1)
        pred = model.predict(input_seq)[0][0]
        future_preds.append(pred)
        last_data = np.append(last_data, [[pred]], axis=0)

    return scaler.inverse_transform(np.array(future_preds).reshape(-1, 1)).flatten()

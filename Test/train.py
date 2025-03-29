import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import os

def train(stock, prop, model_path, model_type="LSTM"):
    # Chuẩn bị dữ liệu
    data = stock[prop].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    # Tạo dữ liệu train/test
    x_train, y_train = [], []
    for i in range(30, len(data_scaled)):
        x_train.append(data_scaled[i-30:i, 0])
        y_train.append(data_scaled[i, 0])
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    # Xây dựng mô hình
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    # Compile & train
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(x_train, y_train, epochs=25, batch_size=30, validation_split=0.2, verbose=1)

    # Lưu model
    if not os.path.exists("Model"):
        os.makedirs("Model")
    model.save(model_path)

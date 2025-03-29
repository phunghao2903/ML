import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.losses import MeanSquaredError

def get_data(train, test, time_step, num_predict, date):
    x_train, y_train, x_test, y_test, date_test = [], [], [], [], []

    for i in range(len(train) - time_step - num_predict):
        x_train.append(train[i:i + time_step])
        y_train.append(train[i + time_step:i + time_step + num_predict])

    for i in range(len(test) - time_step - num_predict):
        x_test.append(test[i:i + time_step])
        y_test.append(test[i + time_step:i + time_step + num_predict])
        date_test.append(date[i + time_step])
    return np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test), np.array(date_test)

def train(data, prop, model_path):
    data_end = int(np.floor(0.8 * len(data)))
    train_data = data[:data_end][prop].values
    test_data = data[data_end:][prop].values
    date_test = data[data_end:]['Date'].values

    x_train, y_train, x_test, y_test, date_test = get_data(train_data, test_data, 30, 1, date_test)

    scaler = MinMaxScaler()
    x_train = scaler.fit_transform(x_train.reshape(-1, 30))
    y_train = scaler.fit_transform(y_train)

    x_train = x_train.reshape(-1, 30, 1)
    y_train = y_train.reshape(-1, 1)

    model = Sequential()
    model.add(LSTM(50, input_shape=(30, 1), return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(50, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(50))
    model.add(Dropout(0.3))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss=MeanSquaredError())
    model.fit(x_train, y_train, epochs=25, validation_split=0.2, batch_size=30, verbose=1)

    model.save(model_path)

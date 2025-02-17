## LSTM Stock Price Prediction

### **Tính Trung Bình 100 Ngày**
```python
ma_100_days = data.Close.rolling(100).mean
```
- Tính trung bình cộng 100 ngày của cột `Close`.

### **Xóa Dữ Liệu Bị Thiếu**
```python
data.dropna(inplace=True)
```
- Xóa **toàn bộ hàng chứa giá trị NaN (giá trị bị thiếu)** trong DataFrame `data`.
- `inplace=True` giúp thay đổi trực tiếp trên `data` mà không cần gán lại.

### **Chia Tập Train/Test**
```python
data_train = pd.DataFrame(data.Close[0: int(len(data)*0.80)])
data_test = pd.DataFrame(data.Close[int(len(data)*0.80): len(data)])
```
- `len(data)`: Tổng số hàng trong `data`.
- Lấy **80% dữ liệu để train**, còn **20% để test**.

### **Kích Thước Dữ Liệu**
```python
data_train.shape[0], data_test.shape[0]
```
- Trả về **số lượng dòng** của tập huấn luyện (`data_train`) và tập kiểm tra (`data_test`).

### **Chuẩn Hóa Dữ Liệu**
```python
scaler = MinMaxScaler(feature_range=(0,1))
```
- **Đưa dữ liệu về khoảng `[0,1]`**, giúp mô hình học sâu (LSTM, CNN,...) **hội tụ nhanh hơn** và **tránh vấn đề gradient vanishing**.

### **Tạo Dữ Liệu Đầu Vào Cho Mô Hình**
```python
x = []
y = []
for i in range(100, data_train_scale.shape[0]):
    x.append(data_train_scale[i-100:i])
    y.append(data_train_scale[i,0])
```
- **`x.append(data_train_scale[i-100:i])`**
    - Lấy **100 điểm dữ liệu trước đó** làm **đầu vào (features)** cho mô hình.

- **`y.append(data_train_scale[i,0])`**
    - Lấy giá trị tiếp theo tại **vị trí `i`** làm **đầu ra (label)** để dự đoán.

### **Mô Hình LSTM**
```python
model = Sequential()
model.add(LSTM(units=50, activation='relu', return_sequences=True, input_shape=(x.shape[1],1)))
model.add(Dropout(0.2))

model.add(LSTM(units=60, activation='relu', return_sequences=True,))
model.add(Dropout(0.3))

model.add(LSTM(units=80, activation='relu', return_sequences=True,))
model.add(Dropout(0.4))

model.add(LSTM(units=120, activation='relu'))
model.add(Dropout(0.5))

model.add(Dense(units=1))
```
- **`Sequential()`** là mô hình dạng **stacked layer**, tức là các lớp được xếp chồng lên nhau theo thứ tự.
- **`LSTM(units=50)`**: Lớp LSTM có **50 đơn vị (neurons)**
- **`activation='relu'`**: Dùng hàm **ReLU** thay vì **tanh** mặc định để giúp mô hình học nhanh hơn.
- **`return_sequences=True`**: Giữ lại toàn bộ chuỗi đầu ra để truyền vào LSTM tiếp theo.
- **`input_shape=(x.shape[1],1)`**:
    - `x.shape[1]` → Số bước thời gian (time steps).
    - `1` → Mỗi bước có 1 đặc trưng (feature).
- **`Dropout(0.2)`**: Xác suất **20%** các nơ-ron sẽ bị tắt ngẫu nhiên, giúp giảm overfitting.


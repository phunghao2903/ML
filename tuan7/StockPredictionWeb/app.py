from flask import Flask, render_template
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import make_interp_spline

app = Flask(__name__)

def generate_plot():
    # Tạo dữ liệu dự đoán
    future_days = 10
    future_dates = pd.date_range(start="2024-01-01", periods=future_days)
    future_predictions = np.random.uniform(100, 200, size=future_days)  # Giả lập dữ liệu dự đoán

    # Chuyển ngày thành số để dùng spline
    x = np.array([date.toordinal() for date in future_dates])
    y = np.array(future_predictions.flatten())

    # Tạo spline mượt hơn
    x_smooth = np.linspace(x.min(), x.max(), 300)  # Nội suy 300 điểm
    spline = make_interp_spline(x, y, k=3)  # Spline bậc 3
    y_smooth = spline(x_smooth)

    # Vẽ biểu đồ
    plt.figure(figsize=(10, 5))
    plt.plot(x_smooth, y_smooth, label="Giá dự đoán", color="red", linewidth=2.5)  # Đường mượt hơn
    plt.scatter(x, y, color="red", s=30, label="Dữ liệu gốc")  # Hiển thị điểm gốc

    # Cấu hình biểu đồ
    plt.xlabel("Ngày")
    plt.ylabel("Giá (USD)")
    plt.title("Dự đoán giá cổ phiếu")
    plt.xticks(x[::2], [date.strftime('%Y-%m-%d') for date in future_dates[::2]], rotation=45)  
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)

    # Lưu hình ảnh vào thư mục static
    plt.savefig("static/plot.png", bbox_inches="tight")  # Đảm bảo ảnh không bị cắt
    plt.close()

@app.route('/')
def home():
    generate_plot()  # Tạo biểu đồ trước khi hiển thị
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

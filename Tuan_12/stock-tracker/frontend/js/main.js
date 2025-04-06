// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let currentStock = 'BSI.VN';
let currentTimeframe = '1d';
let autoUpdateTimer = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize stock selection
    initializeStockSelection();
    
    // Initialize time range buttons
    initializeTimeRangeButtons();
    
    // Initialize date pickers
    initializeDatePickers();
    
    // Load initial stock data
    loadStockData(currentStock, currentTimeframe);
    
    // Start auto-refresh for intraday view
    startAutoRefresh();
});

//======================================================================================
//Khởi tạo lựa chọn cổ phiếu từ danh sách cổ phiếu có sẵn.
function initializeStockSelection() {
    const stockSelect = document.getElementById('stock-select');
    
    // Fetch available stocks from API
    fetch(`${API_BASE_URL}/available-stocks`)
        .then(response => response.json())
        .then(stocks => {
            // Clear current options
            stockSelect.innerHTML = '';
            
            // Add options from API
            Object.entries(stocks).forEach(([symbol, name]) => {
                const option = document.createElement('option');
                option.value = symbol;
                option.textContent = `${name} (${symbol})`;
                stockSelect.appendChild(option);
            });
            
            // Set default value
            stockSelect.value = currentStock;
        })
        .catch(error => console.error('Error fetching stocks:', error));
    
    // Add change event listener
    stockSelect.addEventListener('change', function() {
        currentStock = this.value;
        loadStockData(currentStock, currentTimeframe);
    });
}


//======================================================================================
// Khởi tạo các nút thời gian để người dùng chọn khoảng thời gian dữ liệu.
function initializeTimeRangeButtons() {
    const buttons = document.querySelectorAll('.time-button');
    const datePickers = document.querySelector('.date-pickers');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get selected timeframe
            const timeframe = this.getAttribute('data-timeframe');
            currentTimeframe = timeframe;
            
            // Show/hide date pickers for custom timeframe
            if (timeframe === 'custom') {
                datePickers.style.display = 'block';
            } else {
                datePickers.style.display = 'none';
                loadStockData(currentStock, currentTimeframe);
            }
            
            // Handle auto-refresh for intraday view
            if (timeframe === '1d') {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });
    });
}



//======================================================================================
// Khởi tạo các bộ chọn ngày cho khoảng thời gian tùy chỉnh.
function initializeDatePickers() {
    // Initialize flatpickr date pickers
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    flatpickr('#start-date', {
        dateFormat: 'Y-m-d',
        defaultDate: thirtyDaysAgo,
        maxDate: today
    });
    
    flatpickr('#end-date', {
        dateFormat: 'Y-m-d',
        defaultDate: today,
        maxDate: today
    });
    
    // Add event listener for apply button
    document.getElementById('apply-custom-dates').addEventListener('click', function() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        if (startDate && endDate) {
            loadStockData(currentStock, 'custom', { startDate, endDate });
        } else {
            alert('Please select both start and end dates.');
        }
    });
}



//======================================================================================
//  Tải dữ liệu cổ phiếu từ API và cập nhật giao diện.
function loadStockData(symbol, timeframe, customDates = null) {
    // Update last updated timestamp
    updateLastUpdated();
    
    // Build API URL
    let url = `${API_BASE_URL}/stock-data?symbol=${symbol}&timeframe=${timeframe}`;
    
    // Add custom dates if provided
    if (timeframe === 'custom' && customDates) {
        url += `&start_date=${customDates.startDate}&end_date=${customDates.endDate}`;
    }
    
    // Show loading state
    document.getElementById('current-price').textContent = 'Loading...';
    document.getElementById('price-change').textContent = 'Loading...';
    
    // Fetch data from API
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            console.log('Fetched Data:', data);

            // Lọc dữ liệu theo ngày
            const dateGroups = {};

            // Lặp qua dữ liệu để phân nhóm theo ngày
            data.data.forEach(item => {
                const date = item.date.split(' ')[0];  // Lấy ngày mà không cần giờ (yyyy-mm-dd)
                if (!dateGroups[date]) {
                    dateGroups[date] = [];
                }
                dateGroups[date].push(item);  // Thêm item vào nhóm ngày tương ứng
            });

            // In ra các nhóm dữ liệu theo ngày
            console.log('Date Grouped Data:', dateGroups);

            // Lấy danh sách các ngày và sắp xếp
            const sortedDates = Object.keys(dateGroups).sort((a, b) => new Date(b) - new Date(a));

            // Kiểm tra có nếu 2 ngày trong dữ liệu
            if (sortedDates.length === 2) {
                const latestDate = sortedDates[0];  // Ngày mới nhất
                const previousDate = sortedDates[1];  // Ngày trước đó

                // Dữ liệu cho ngày mới nhất và ngày hôm trước
                const date1Data = dateGroups[previousDate];
                const date2Data = dateGroups[latestDate];

                console.log('Data for', latestDate, ':', date1Data);
                console.log('Data for', previousDate, ':', date2Data);

                // Hiển thị dữ liệu cho 2 ngày trên giao diện
                // displayDateData(date1Data, latestDate);
                // displayDateData(date2Data, previousDate);

                const jsonForDate1 = {
                    "symbol": data.symbol,  // Giữ lại symbol
                    "timeframe": data.timeframe,  // Giữ lại timeframe
                    "data": date1Data
                };
        
                // Tạo cấu trúc JSON cho ngày trước đó
                const jsonForDate2 = {
                    "symbol": data.symbol,  // Giữ lại symbol
                    "timeframe": data.timeframe,  // Giữ lại timeframe
                    "data": date2Data
                };

                

                if (data.prediction_result) {

                    jsonForDate2.prediction_result = data.prediction_result;
                    // console.log('Added prediction data to chart:', data.prediction_result);
                
                } else {
                
                    console.log('Chưa có prediction result');
                
                }
                
                console.log('Updated jsonForDate2:', jsonForDate2);

                updateChart(jsonForDate2);
                updateMetrics(jsonForDate1, jsonForDate2);
            }
            else if (sortedDates.length > 2) {
                // Update chart
                updateChart(data);
                
                // Update metrics
                updateMetrics(data);
            }

            
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('stock-chart').innerHTML = `
                <div style="height: 100%; display: flex; align-items: center; justify-content: center;">
                    <p>Error loading data: ${error.message}</p>
                </div>
            `;
            document.getElementById('current-price').textContent = '--';
            document.getElementById('price-change').textContent = '--';
        });
}



//======================================================================================
// Cập nhật các chỉ số cổ phiếu (giá hiện tại và thay đổi giá) trên giao diện.
function updateMetrics(data, data2 = null) {

    if (data2 === null) {
        if (data.data && data.data.length > 0) {
            const latestData = data.data[data.data.length - 1];
            const firstData = data.data[0];
            
            // Update current price
            const currentPrice = latestData.close;
            const formattedPrice = new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND'
            }).format(currentPrice);
            console.log(formattedPrice); 
            document.getElementById('current-price').textContent = formattedPrice;
            
            // Calculate and update price change
            const priceChange = ((latestData.close - firstData.close) / firstData.close * 100).toFixed(2);
            const priceChangeElement = document.getElementById('price-change');
            priceChangeElement.textContent = `${priceChange}%`;
            
            // Add color class based on price change direction
            priceChangeElement.className = '';
            if (parseFloat(priceChange) > 0) {
                priceChangeElement.classList.add('positive-value');
            } else if (parseFloat(priceChange) < 0) {
                priceChangeElement.classList.add('negative-value');
            }
        }
    } else {
        if (data.data && data.data.length > 0 && data2.data && data2.data.length > 0) {
            const latestData = data.data[data.data.length - 1];
            
            
            const latestData2 = data2.data[data2.data.length - 1];
            

            // Update current price
            const currentPrice = latestData2.close;
            document.getElementById('current-price').textContent = currentPrice;
            
            // Calculate and update price change
            const priceChange = ((latestData2.close - latestData.close) / latestData.close * 100).toFixed(2);
            const priceChangeElement = document.getElementById('price-change');
            priceChangeElement.textContent = `${priceChange}%`;
            
            // Add color class based on price change direction
            priceChangeElement.className = '';
            if (parseFloat(priceChange) > 0) {
                priceChangeElement.classList.add('positive-value');
            } else if (parseFloat(priceChange) < 0) {
                priceChangeElement.classList.add('negative-value');
            }
        }
    }
    
}


//======================================================================================
// Cập nhật thời gian "Last Updated" (cập nhật cuối cùng).
function updateLastUpdated() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('last-updated').textContent = timeString;
}


//======================================================================================
// Bắt đầu tính năng tự động làm mới dữ liệu cổ phiếu mỗi phút khi khung thời gian là 
function startAutoRefresh() {
    // Stop any existing timer
    stopAutoRefresh();
    
    // Only auto-refresh for 1d timeframe
    if (currentTimeframe === '1d') {
        autoUpdateTimer = setInterval(() => {
            loadStockData(currentStock, currentTimeframe);
        }, 60000); // Refresh every minute
    }
}


//======================================================================================
// Dừng tính năng tự động làm mới khi không còn cần thiết.
function stopAutoRefresh() {
    if (autoUpdateTimer) {
        clearInterval(autoUpdateTimer);
        autoUpdateTimer = null;
    }
}
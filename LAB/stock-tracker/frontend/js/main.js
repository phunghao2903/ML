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
            
            // Update chart
            updateChart(data);
            
            // Update metrics
            updateMetrics(data);
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

function updateMetrics(data) {
    if (data.data && data.data.length > 0) {
        const latestData = data.data[data.data.length - 1];
        const firstData = data.data[0];
        
        // Update current price
        const currentPrice = latestData.close.toFixed(2);
        document.getElementById('current-price').textContent = currentPrice;
        
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
}

function updateLastUpdated() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('last-updated').textContent = timeString;
}

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

function stopAutoRefresh() {
    if (autoUpdateTimer) {
        clearInterval(autoUpdateTimer);
        autoUpdateTimer = null;
    }
}
// Chart configuration
let stockChart = null;

function updateChart(data) {
    const chartDiv = document.getElementById('stock-chart');
    
    // Extract data for plotting
    const dates = data.data.map(item => new Date(item.date));
    const closePrices = data.data.map(item => item.close);
    
    // Determine date format based on timeframe
    let dateFormat;
    if (data.timeframe === '1d') {
        dateFormat = '%d-%m-%Y %H:%M'; // Hour:Minute for intraday
    } else {
        dateFormat = '%Y-%m-%d'; // YYYY-MM-DD for other timeframes
    }
    
    // Create Plotly trace
    const trace = {
        x: dates,
        y: closePrices,
        type: 'scatter',
        mode: 'lines',
        name: `${data.symbol} Price`,
        line: {
            color: '#72bcd4',
            width: 1.5
        }
    };
    
    // Create layout
    const layout = {
        title: {
            text: `${data.symbol} Stock Price - ${formatTimeframeLabel(data.timeframe)}`,
            font: {
                size: 20,
                color: 'white'
            }
        },
        xaxis: {
            title: 'Date',
            tickformat: dateFormat,
            tickangle: 45,
            gridcolor: '#444444',
            color: 'white'
        },
        yaxis: {
            title: 'Price',
            gridcolor: '#444444',
            color: 'white'
        },
        plot_bgcolor: '#1e1e1e',
        paper_bgcolor: '#1e1e1e',
        margin: { t: 50, l: 50, r: 30, b: 80 },
        showlegend: false
    };
    
    // Configuration options
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    // Create or update chart
    if (!stockChart) {
        Plotly.newPlot(chartDiv, [trace], layout, config);
        stockChart = true;
    } else {
        Plotly.react(chartDiv, [trace], layout, config);
    }
}

function formatTimeframeLabel(timeframe) {
    switch (timeframe) {
        case '1d':
            return 'Today';
        case '5d':
            return '5 Days';
        case '1w':
            return '1 Week';
        case '1mo':
            return '1 Month';
        case '6mo':
            return '6 Months';
        case '1y':
            return '1 Year';
        case 'custom':
            return 'Custom Range';
        default:
            return timeframe;
    }
}
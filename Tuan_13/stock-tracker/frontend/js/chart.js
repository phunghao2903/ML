// Chart configuration
let stockChart = null;

function updateChart(data) {

    const chartDiv = document.getElementById('stock-chart');



    // Extract data for plotting

    const dates = data.data.map(item => new Date(item.date));

    const closePrices = data.data.map(item => item.close);

    const openPrices = data.data.map(item => item.open);


    // Determine date format based on timeframe

    let dateFormat;

    if (data.timeframe === '1d') {

        dateFormat = '%H:%M'; // Hour:Minute for intraday

    } else {

        dateFormat = '%Y-%m-%d'; // YYYY-MM-DD for other timeframes

    }



    // Create Plotly trace for actual price

    const trace = {

        x: dates,

        y: closePrices,

        type: 'scatter',

        mode: 'lines',

        name: `${data.symbol} Price`,

        line: {

            color: '#72bcd4',

            width: 1.5

        },

        hoverinfo: 'text', // Chỉ định thông tin sẽ hiển thị
        text: dates.map((date, index) => 
            `Date: ${date.toLocaleDateString()}<br>` +
            `Time: ${date.toLocaleTimeString()}<br>` +
            `Open: ${openPrices[index].toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}<br>` + // Giá mở
            `High: ${data.data[index].high.toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}<br>` + // Giá cao
            `Low: ${data.data[index].low.toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}<br>` + // Giá thấp
            `Close: ${closePrices[index].toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}<br>` + // Giá đóng
            `Volume: ${data.data[index].volume.toLocaleString()}`
        ),
        visible: true //

    };



    const candlestickTrace = {

        x: dates,

        open: openPrices,

        high: data.data.map(item => item.high),

        low: data.data.map(item => item.low),

        close: closePrices,

        type: 'candlestick',

        name: `${data.symbol}`,

        increasing: {line: {color: '#26a69a'}, fillcolor: '#26a69a'}, 

        decreasing: {line: {color: '#ef5350'}, fillcolor: '#ef5350'}, 

        hoverinfo: 'text',

        text: dates.map((date, index) => 

            `Date: ${date.toLocaleDateString()}<br>` +

            `Time: ${date.toLocaleTimeString()}<br>` +

            `Open: ${openPrices[index].toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}<br>` +

            `High: ${data.data[index].high.toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}<br>` +

            `Low: ${data.data[index].low.toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}<br>` +

            `Close: ${closePrices[index].toLocaleString('vi-VN', {style: 'currency', currency: 'VND'})}` 
        ),
        visible: false   
    };

    // Initialize traces array with the main trace

    const traces = [trace, candlestickTrace];



    // Only add prediction trace if prediction data exists

    if (data.prediction_result && Object.keys(data.prediction_result).length > 0) {

        const predictionValues = [];

        for (let i = 1; i <= Object.keys(data.prediction_result).length; i++) {

            const key = `value${i}`;

            if (data.prediction_result.hasOwnProperty(key)) {

                predictionValues.push(data.prediction_result[key]);

            }

        }



        console.log('gia tri Y', predictionValues);



        // Create Plotly trace for prediction line

        const predictionTrace = {

            x: dates,

            y: predictionValues,

            type: 'scatter',

            mode: 'lines',

            name: 'Predict',

            line: {

                color: 'red',

                width: 1.5,

                dash: 'solid'

            }

        };



        // Add prediction trace to traces array

        traces.push(predictionTrace);

    }



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

        updatemenus: [
            {
                type: 'buttons',
                direction: 'right',
                x: 0,
                y: 1.2,
                buttons: [
                    {
                        label: 'Line',
                        method: 'update',
                        args: [
                            { visible: [true, false] }, // chỉ trace 0 (line) hiển thị
                            { title: `${data.symbol} - Line Chart` }
                        ]
                    },
                    {
                        label: 'Candle',
                        method: 'update',
                        args: [
                            { visible: [false, true] }, // chỉ trace 1 (candlestick) hiển thị
                            { title: `${data.symbol} - Candlestick Chart` }
                        ]
                    }
                ]
            }
        ],

        plot_bgcolor: '#1e1e1e',

        paper_bgcolor: '#1e1e1e',

        margin: { t: 50, l: 50, r: 30, b: 80 },

        showlegend: true

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

        Plotly.newPlot(chartDiv, traces, layout, config);

        stockChart = true;

    } else {

        Plotly.react(chartDiv, traces, layout, config);

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
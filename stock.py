@app.route("/")
def home():
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NIFTY 50 Stock Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            select { padding: 10px; margin: 20px; } /* Moved CSS into <style> */
        </style>
    </head>
    <body>

        <h2>NIFTY 50 Stock Prices</h2>

        <label for="stockSelect">Select Stock:</label>
        <select id="stockSelect" onchange="loadStockData()"></select>

        <canvas id="stockChart"></canvas>

        <script>
            let stockChart;

            document.addEventListener("DOMContentLoaded", function () {
                loadStockList();
            });

            async function loadStockList() {
                const response = await fetch("/stocks");
                const stocks = await response.json();
                const select = document.getElementById("stockSelect");

                stocks.forEach(stock => {
                    const option = document.createElement("option");
                    option.value = stock;
                    option.textContent = stock;
                    select.appendChild(option);
                });

                loadStockData();  // Load first stock on page load
            }

            async function loadStockData() {
                const stock = document.getElementById("stockSelect").value;
                const response = await fetch(`/stock/${stock}`);
                const data = await response.json();

                if (!data || data.error) {
                    alert(data.error || "No data found!");
                    return;
                }

                const dates = data.map(item => item.Date);
                const prices = data.map(item => item.Close);

                if (stockChart) stockChart.destroy(); // Remove previous chart

                const ctx = document.getElementById("stockChart").getContext("2d");
                stockChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: dates,
                        datasets: [{
                            label: stock + " Closing Price",
                            data: prices,
                            borderColor: "blue",
                            fill: false
                        }]
                    }
                });
            }
        </script>

    </body>
    </html>
    """

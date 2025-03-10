from flask import Flask, jsonify, render_template
import pandas as pd
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS for frontend requests

# Load NIFTY 50 dataset (modify path if needed)
df = pd.read_csv("NIFTY50.csv")

@app.route("/")
def home():
    return render_template("index.html")  # Serve frontend

# API to get available stock symbols
@app.route("/stocks", methods=["GET"])
def get_stocks():
    symbols = df["Symbol"].unique().tolist()
    return jsonify({"stocks": symbols})

# API to fetch stock data for a specific company
@app.route("/stock/<symbol>", methods=["GET"])
def get_stock_data(symbol):
    stock_symbol = f"{symbol}.NS"
    
    try:
        stock_data = yf.download(stock_symbol, period="1y", interval="1d")
        stock_data = stock_data.reset_index()
        stock_data["Date"] = stock_data["Date"].astype(str)  # Convert date for JSON response
        
        return jsonify({"symbol": symbol, "data": stock_data.to_dict(orient="records")})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NIFTY 50 Stock Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        canvas { max-width: 90%; margin: auto; }
        select { padding: 10px; margin: 20px; }
    </style>
</head>
<body>

    <h1>NIFTY 50 Stock Dashboard</h1>

    <label>Select Stock:</label>
    <select id="stockSelect" onchange="fetchStockData()"></select>

    <canvas id="stockChart"></canvas>

    <script>
        let stockChart;
        
        async function fetchStocks() {
            const response = await fetch("/stocks");
            const data = await response.json();
            const select = document.getElementById("stockSelect");

            data.stocks.forEach(stock => {
                const option = document.createElement("option");
                option.value = stock;
                option.textContent = stock;
                select.appendChild(option);
            });

            fetchStockData();  // Load first stock data
        }

        async function fetchStockData() {
            const stock = document.getElementById("stockSelect").value;
            const response = await fetch(`/stock/${stock}`);
            const data = await response.json();

            const labels = data.data.map(entry => entry.Date);
            const prices = data.data.map(entry => entry.Close);

            if (stockChart) stockChart.destroy(); // Remove previous chart

            const ctx = document.getElementById("stockChart").getContext("2d");
            stockChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: stock + " Closing Price",
                        data: prices,
                        borderColor: "blue",
                        fill: false
                    }]
                }
            });
        }

        fetchStocks(); // Load stocks on page load
    </script>

</body>
</html>

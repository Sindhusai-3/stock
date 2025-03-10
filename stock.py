from flask import Flask, jsonify, render_template
import yfinance as yf

app = Flask(__name__)

# Home Page - Serves HTML
@app.route("/")
def home():
    return render_template("index.html")

# API to fetch stock data
@app.route("/stock/<symbol>")
def get_stock(symbol):
    data = yf.download(f"{symbol}.NS", period="1mo")  # Get last 1 month data
    data = data["Close"].reset_index()
    data["Date"] = data["Date"].astype(str)  # Convert date for frontend
    return jsonify(data.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)

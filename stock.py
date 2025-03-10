import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ✅ Load Stock Data
@st.cache_data
def load_stock_data():
    return pd.read_csv("stocks.csv")  # Ensure your CSV contains "Stock", "Date", "Close", "News"

stocks_df = load_stock_data()

# ✅ Get Stock Details
def get_stock_details(stock_name):
    stock_data = stocks_df[stocks_df["Stock"].str.contains(stock_name, case=False, na=False)]
    return stock_data if not stock_data.empty else None

# ✅ Sentiment Analysis on Stock News
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity if text else 0

# ✅ Recommend Similar Stocks
def recommend_stocks(stock_name, num_recommendations=5):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(stocks_df.groupby("Stock")["News"].apply(lambda x: " ".join(x)).fillna(""))
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    idx = stocks_df[stocks_df["Stock"].str.contains(stock_name, case=False, na=False)].index
    if not idx.empty:
        idx = idx[0]
        sim_scores = sorted(
            list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True
        )[1:num_recommendations + 1]
        return [stocks_df.iloc[i[0]]["Stock"] for i in sim_scores]

    return []

# ✅ Custom CSS for UI Styling
st.markdown(
    """
    <style>
        body { background-color: #f5f5f5; }
        .main { background-color: white; padding: 20px; border-radius: 10px; }
        h1 { color: #007BFF; text-align: center; }
        .stButton>button { background-color: #007BFF; color: white; font-weight: bold; }
        .stTextInput>div>div>input { border-radius: 10px; padding: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ Streamlit UI
st.title("📈 AI-Powered Stock Analysis")
st.subheader("Check stock trends, analyze news sentiment & find similar stocks!")

# ✅ User Input
stock_name = st.text_input("🔍 Enter a stock name", "")

if st.button("🔎 Search"):
    with st.spinner("Fetching stock details..."):
        if stock_name:
            stock_data = get_stock_details(stock_name)

            if stock_data is not None:
                st.success("✅ Stock Found!")

                # ✅ Display Stock Chart
                st.subheader(f"📊 {stock_name} Price Trend")
                fig, ax = plt.subplots()
                stock_data["Date"] = pd.to_datetime(stock_data["Date"])
                stock_data = stock_data.sort_values("Date")
                ax.plot(stock_data["Date"], stock_data["Close"], marker="o", linestyle="-", color="blue")
                ax.set_xlabel("Date")
                ax.set_ylabel("Closing Price")
                ax.set_title(f"{stock_name} Stock Price Over Time")
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # ✅ Display Latest News
                latest_news = stock_data.iloc[-1]["News"]
                st.subheader("📰 Latest Stock News")
                st.write(f"**{latest_news}**")

                # ✅ Sentiment Analysis
                sentiment_score = analyze_sentiment(latest_news)
                st.write(f"**📝 Sentiment Score:** {sentiment_score:.2f}")

                # ✅ Recommend Similar Stocks
                similar_stocks = recommend_stocks(stock_name)
                if similar_stocks:
                    st.subheader("📌 Similar Stocks")
                    st.write(", ".join(similar_stocks))
                else:
                    st.write("❌ No similar stocks found.")

            else:
                st.error("❌ Stock not found! Showing similar stocks...")
                similar_stocks = recommend_stocks(stock_name)
                if similar_stocks:
                    st.write("📌 Recommended Similar Stocks:")
                    st.write(", ".join(similar_stocks))
                else:
                    st.write("❌ No recommendations available.")

        else:
            st.warning("⚠️ Please enter a stock name.")

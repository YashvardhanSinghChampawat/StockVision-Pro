# 📈 StockVision Pro

**StockVision Pro** is a professional-grade, real-time stock market analysis and portfolio tracking dashboard built entirely in Python using [Streamlit](https://streamlit.io/) and [Yahoo Finance (`yfinance`)](https://pypi.org/project/yfinance/). 

Designed with a sleek, dark-themed UI and powerful interactive Plotly visualizations, it provides traders and investors with deep technical insights, comparative metrics, and dynamic market news all in one seamless application.

---

## ✨ Features

### 📊 Comprehensive Dashboard
- **Live US Market Status**: Automatically detects if the US equities market is open or closed based on Eastern Time.
- **Key Fundamental Metrics**: Quickly view Market Cap, Volume, P/E Ratio, and 52-Week Highs/Lows for any requested stock ticker.

### 📉 Advanced Technical Analysis
- **Interactive Candlestick Charts**: Fully responsive Plotly charts featuring togglable overlays for Moving Averages (MA20, MA50, MA200) and Bollinger Bands.
- **Integrated Subplots**: Stacked visualizations containing Price Action, color-coded Volume, MACD (with signal line and histogram), and RSI (with defined overbought/oversold zones).
- **Signal Dashboard**: A real-time calculated table translating RSI, MACD, Stochastic Oscillator, and Moving Average Crossovers into actionable **Buy / Sell / Hold** signals.
- **AI Sentiment Gauge**: A composite score (0-100) aggregating technical indicators into an easy-to-read Bullish, Neutral, or Bearish gauge.
- **Price Alerts**: Set target prices dynamically in your session and receive notifications when they are hit.

### 🔍 Stock Screener
- **Predefined S&P 500 Basket**: Rapidly filter through 50 of the most popular US stocks.
- **Custom Filters**: Filter by Minimum/Maximum P/E Ratios, Minimum Market Cap, and Minimum Volume.
- **Sortable Results**: Displays matching candidates in an interactive dataframe.

### ⚖️ Stock Comparison
- **Multi-Ticker Analysis**: Compare up to 5 different tickers simultaneously.
- **Normalized Performance**: Automatically bases all selected stocks to an index of 100 to visualize relative percentage gains over the selected timeframe.
- **Correlation Heatmap**: Instantly see how closely related the price actions of your selected stocks are using a visual heatmap.

### 💼 Portfolio Tracker
- **Private Session State**: Log your trades securely within your browser's local session memory (no signups or databases required).
- **Live P&L Tracking**: Calculates current asset values, dollar gain/loss, and percentage returns based on real-time prices.
- **Asset Allocation**: Automatically generates a pie chart visualizing your portfolio's distribution.
- **CSV Export**: Download your tracked portfolio data directly to a `.csv` file.

### 📰 Market News & Sentiment
- **Live Headlines**: Fetches the top 10 most recent news articles related to your active ticker.
- **Keyword Sentiment Tagging**: Scans headlines for bullish/bearish vocabulary to instantly assign a 🟢 Positive, 🟡 Neutral, or 🔴 Negative tag.

---

## 🚀 Setup and Installation

### Prerequisites
- Python 3.9 or higher is recommended.
- A virtual environment is recommended to avoid dependency conflicts.

### 1. Clone the repository (or download the files)
Ensure that you have `app.py` and `requirements.txt` in your project folder.

### 2. Create and Activate a Virtual Environment
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```
**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries specified in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Launch the Streamlit server from your terminal. Ensure you are in the directory where `app.py` is located.
```bash
streamlit run app.py
```
*Note: If your `app.py` is inside the `venv/Scripts/` directory, navigate there first or use `streamlit run venv/Scripts/app.py`.*

### 5. View in Browser
The application will automatically open in your default web browser at `http://localhost:8501`.

---

## 🛠️ Technology Stack
- **Frontend & UI**: [Streamlit](https://streamlit.io/)
- **Data Fetching**: [yfinance](https://pypi.org/project/yfinance/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
- **Interactive Charting**: [Plotly Graph Objects & Express](https://plotly.com/python/)
- **Date/Time Parsing**: `datetime`, `pytz`

---

## ⚠️ Disclaimer
*StockVision Pro is a personal/educational project. The financial data, signals, and sentiment analysis provided by this application do not constitute professional financial advice. Always do your own due diligence before making investment decisions.*

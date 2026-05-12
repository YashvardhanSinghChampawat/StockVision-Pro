import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import pytz

# Page config
st.set_page_config(
    page_title="StockVision Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Accent color overrides */
    :root {
        --primary-color: #00d4aa;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #00d4aa;
        color: #0e1117;
        border: none;
        font-weight: bold;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        background-color: #1e2430;
        color: white;
    }
    
    /* Cards for metrics */
    .metric-card {
        background-color: #1e2430;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border-left: 5px solid #00d4aa;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .metric-title {
        color: #a0aab5;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    
    /* Top Banner */
    .top-banner {
        background-color: #1e2430;
        padding: 15px 25px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #2e3646;
    }
    
    .market-status-open {
        color: #00d4aa;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .market-status-closed {
        color: #ff4b4b;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-open { background-color: #00d4aa; }
    .dot-closed { background-color: #ff4b4b; }
    
    /* Hover effects for buttons */
    .stButton>button { transition: all 0.2s ease; }
    .stButton>button:hover {
        background-color: #00e6b8;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 212, 170, 0.4);
    }
    
    /* Metric Cards Hover */
    .metric-card { transition: transform 0.2s, box-shadow 0.2s; }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 212, 170, 0.2);
    }
    
    /* Gradient Headers */
    .gradient-header {
        background: linear-gradient(90deg, #00d4aa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* News Card */
    .news-card {
        background-color: #1e2430;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 3px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .news-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center; padding: 20px; margin-top: 50px;
        color: #a0aab5; font-size: 14px; border-top: 1px solid #2e3646;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to check if US market is open
def is_market_open():
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Monday = 0, Sunday = 6
    if now.weekday() >= 5:
        return False
        
    market_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_start <= now <= market_end

# Helper to format numbers
def format_number(num):
    if num is None or pd.isna(num):
        return "N/A"
    try:
        num = float(num)
        if num >= 1e12:
            return f"${num/1e12:.2f}T"
        elif num >= 1e9:
            return f"${num/1e9:.2f}B"
        elif num >= 1e6:
            return f"${num/1e6:.2f}M"
        else:
            return f"${num:,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_volume(num):
    if num is None or pd.isna(num):
        return "N/A"
    try:
        num = float(num)
        if num >= 1e9:
            return f"{num/1e9:.2f}B"
        elif num >= 1e6:
            return f"{num/1e6:.2f}M"
        else:
            return f"{num:,.0f}"
    except (ValueError, TypeError):
        return "N/A"

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='text-align: center;' class='gradient-header'>📈 StockVision Pro</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation menu
    nav_selection = st.radio(
        "Navigation",
        ["Dashboard", "Stock Analysis", "Screener", "Comparison", "Portfolio Tracker", "Market News"]
    )
    
    st.markdown("---")
    
    if 'current_ticker' not in st.session_state:
        st.session_state.current_ticker = "AAPL"
    if 'favorites' not in st.session_state:
        st.session_state.favorites = ["AAPL", "MSFT", "TSLA"]
        
    ticker_input = st.text_input("🔍 Search Ticker", value=st.session_state.current_ticker).upper()
    if ticker_input and ticker_input != st.session_state.current_ticker:
        st.session_state.current_ticker = ticker_input
        st.rerun()
        
    ticker = st.session_state.current_ticker
    
    st.markdown("### ⭐ Favorites")
    col_add, col_rem = st.columns([3, 1])
    with col_add:
        if st.button("Add to Fav", use_container_width=True):
            if ticker not in st.session_state.favorites:
                st.session_state.favorites.append(ticker)
                st.rerun()
    with col_rem:
        if st.button("🗑️", help="Clear", use_container_width=True):
            st.session_state.favorites = []
            st.rerun()
            
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            if st.button(fav, key=f"fav_{fav}", use_container_width=True):
                st.session_state.current_ticker = fav
                st.rerun()
    
# Main content area

# Top Header Banner with Market Status
market_open = is_market_open()
status_class = "market-status-open" if market_open else "market-status-closed"
dot_class = "dot-open" if market_open else "dot-closed"
status_text = "Market Open" if market_open else "Market Closed"

st.markdown(f"""
<div class="top-banner">
    <div>
        <h3 style="margin: 0;" class="gradient-header">US Equities Market</h3>
    </div>
    <div class="{status_class}">
        <span class="dot {dot_class}"></span>
        {status_text}
    </div>
</div>
""", unsafe_allow_html=True)

if nav_selection == "Dashboard":
    # Fetch data
    try:
        if ticker:
            with st.spinner(f"Loading Dashboard for {ticker}..."):
                stock = yf.Ticker(ticker)
                info = stock.info
            
            st.markdown(f"<h2 class='gradient-header'>{info.get('shortName', info.get('longName', ticker))} ({ticker})</h2>", unsafe_allow_html=True)
            
            # Create 4 metric cards
            col1, col2, col3, col4 = st.columns(4)
            
            market_cap = info.get('marketCap')
            volume = info.get('regularMarketVolume', info.get('volume'))
            pe_ratio = info.get('trailingPE')
            high_52 = info.get('fiftyTwoWeekHigh')
            low_52 = info.get('fiftyTwoWeekLow')
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Market Cap</div>
                    <div class="metric-value">{format_number(market_cap)}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Volume</div>
                    <div class="metric-value">{format_volume(volume)}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                pe_str = f"{pe_ratio:.2f}" if pe_ratio is not None and not pd.isna(pe_ratio) else "N/A"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">P/E Ratio</div>
                    <div class="metric-value">{pe_str}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col4:
                high_str = f"${high_52:.2f}" if high_52 is not None and not pd.isna(high_52) else "N/A"
                low_str = f"${low_52:.2f}" if low_52 is not None and not pd.isna(low_52) else "N/A"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">52W High / Low</div>
                    <div class="metric-value">{high_str} / {low_str}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.info("Navigate to 'Stock Analysis' in the sidebar for detailed charts, or try searching another ticker!")
            
    except Exception as e:
        st.error(f"Error fetching data for ticker {ticker}: {e}")

elif nav_selection == "Stock Analysis":
    st.markdown(f"<h2 class='gradient-header'>{ticker} - Technical Analysis</h2>", unsafe_allow_html=True)
    
    if not ticker:
        st.warning("Please enter a ticker in the sidebar.")
    else:
        try:
            # 1. Period Selector
            period_options = {
                "1D": "1d", "1W": "5d", "1M": "1mo", "3M": "3mo",
                "6M": "6mo", "1Y": "1y", "5Y": "5y"
            }
            
            selected_period = st.radio("Select Date Range", list(period_options.keys()), index=5, horizontal=True)
            
            period_val = period_options[selected_period]
            interval = "1d"
            if selected_period == "1D":
                interval = "5m"
            elif selected_period == "1W":
                interval = "15m"
            elif selected_period == "1M":
                interval = "1h"
            
            # Fetch data
            with st.spinner(f"Loading Technical Data for {ticker}..."):
                stock = yf.Ticker(ticker)
                df = stock.history(period=period_val, interval=interval)
                info = stock.info
            
            if df.empty:
                st.error("No data found for this ticker and date range.")
            else:
                # ----------------- INDICATOR CALCULATIONS -----------------
                # MAs
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['MA50'] = df['Close'].rolling(window=50).mean()
                df['MA200'] = df['Close'].rolling(window=200).mean()
                
                # Bollinger Bands
                df['BB_middle'] = df['Close'].rolling(window=20).mean()
                df['BB_std'] = df['Close'].rolling(window=20).std()
                df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
                df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
                
                # RSI (14)
                delta = df['Close'].diff()
                gain = delta.clip(lower=0)
                loss = -delta.clip(upper=0)
                avg_gain = gain.ewm(com=13, adjust=False).mean()
                avg_loss = loss.ewm(com=13, adjust=False).mean()
                rs = avg_gain / avg_loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                # MACD
                exp1 = df['Close'].ewm(span=12, adjust=False).mean()
                exp2 = df['Close'].ewm(span=26, adjust=False).mean()
                df['MACD'] = exp1 - exp2
                df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
                df['MACD_Hist'] = df['MACD'] - df['Signal_Line']
                
                # Stochastic Oscillator (14, 3)
                low_14 = df['Low'].rolling(14).min()
                high_14 = df['High'].rolling(14).max()
                df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
                df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()
                
                # ATR (14)
                high_low = df['High'] - df['Low']
                high_close = (df['High'] - df['Close'].shift()).abs()
                low_close = (df['Low'] - df['Close'].shift()).abs()
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = ranges.max(axis=1)
                df['ATR'] = true_range.rolling(14).mean()

                # ----------------- SIGNAL LOGIC -----------------
                latest = df.iloc[-1]
                
                rsi_val = latest['RSI']
                if pd.isna(rsi_val): rsi_sig, rsi_str = "Hold", "Neutral"
                elif rsi_val < 30: rsi_sig, rsi_str = "Buy", "Oversold"
                elif rsi_val > 70: rsi_sig, rsi_str = "Sell", "Overbought"
                else: rsi_sig, rsi_str = "Hold", "Neutral"
                
                macd_val = latest['MACD']
                macd_hist = latest['MACD_Hist']
                if pd.isna(macd_hist): macd_sig, macd_str = "Hold", "Neutral"
                elif macd_hist > 0 and latest['MACD'] > df['MACD'].iloc[-2]: macd_sig, macd_str = "Buy", "Bullish Trend"
                elif macd_hist < 0 and latest['MACD'] < df['MACD'].iloc[-2]: macd_sig, macd_str = "Sell", "Bearish Trend"
                else: macd_sig, macd_str = "Hold", "Neutral"
                
                stoch_val = latest['Stoch_K']
                if pd.isna(stoch_val): stoch_sig, stoch_str = "Hold", "Neutral"
                elif stoch_val < 20: stoch_sig, stoch_str = "Buy", "Oversold"
                elif stoch_val > 80: stoch_sig, stoch_str = "Sell", "Overbought"
                else: stoch_sig, stoch_str = "Hold", "Neutral"
                
                ma20_val = latest['MA20']
                ma50_val = latest['MA50']
                if pd.isna(ma20_val) or pd.isna(ma50_val): ma_sig, ma_str = "Hold", "Neutral"
                elif ma20_val > ma50_val: ma_sig, ma_str = "Buy", "Uptrend"
                elif ma20_val < ma50_val: ma_sig, ma_str = "Sell", "Downtrend"
                else: ma_sig, ma_str = "Hold", "Neutral"
                
                atr_val = latest['ATR']
                
                sig_map = {"Buy": 100, "Hold": 50, "Sell": 0}
                score = (sig_map[rsi_sig] + sig_map[macd_sig] + sig_map[stoch_sig] + sig_map[ma_sig]) / 4
                
                # ----------------- LAYOUT -----------------
                chart_col, stats_col = st.columns([3, 1])
                
                with chart_col:
                    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
                    show_ma20 = t_col1.checkbox("MA20", value=False)
                    show_ma50 = t_col2.checkbox("MA50", value=False)
                    show_ma200 = t_col3.checkbox("MA200", value=False)
                    show_bb = t_col4.checkbox("Bollinger Bands", value=False)
                    
                    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.04, 
                                        subplot_titles=(f'{ticker} Price', 'Volume', 'MACD', 'RSI (14)'),
                                        row_heights=[0.5, 0.15, 0.15, 0.2])
                    
                    # 1. Price
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
                    if show_ma20: fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#3b82f6', width=1.5), name='MA20'), row=1, col=1)
                    if show_ma50: fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='#f59e0b', width=1.5), name='MA50'), row=1, col=1)
                    if show_ma200: fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], line=dict(color='#ef4444', width=1.5), name='MA200'), row=1, col=1)
                    if show_bb:
                        fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='gray', width=1, dash='dash'), name='Upper BB'), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='gray', width=1, dash='dash'), fill='tonexty', fillcolor='rgba(128, 128, 128, 0.1)', name='Lower BB'), row=1, col=1)
                        
                    # 2. Volume
                    colors = ['#ff4b4b' if row['Open'] > row['Close'] else '#00d4aa' for index, row in df.iterrows()]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
                    
                    # 3. MACD
                    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#3b82f6', width=1.5), name='MACD'), row=3, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], line=dict(color='#f59e0b', width=1.5), name='Signal'), row=3, col=1)
                    macd_colors = ['#00d4aa' if val >= 0 else '#ff4b4b' for val in df['MACD_Hist']]
                    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=macd_colors, name='Histogram'), row=3, col=1)
                    
                    # 4. RSI
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#a855f7', width=1.5), name='RSI'), row=4, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="#ff4b4b", row=4, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="#00d4aa", row=4, col=1)
                    
                    fig.update_layout(
                        height=900, margin=dict(l=0, r=0, t=30, b=0),
                        paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font=dict(color='white'),
                        xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False,
                        xaxis3_rangeslider_visible=False, xaxis4_rangeslider_visible=True,
                        showlegend=False
                    )
                    fig.update_xaxes(gridcolor='#1f2937', zerolinecolor='#1f2937')
                    fig.update_yaxes(gridcolor='#1f2937', zerolinecolor='#1f2937')
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with stats_col:
                    st.markdown("### Key Stats")
                    current_price = df['Close'].iloc[-1]
                    prev_close = info.get('previousClose', df['Close'].iloc[-2] if len(df) > 1 else current_price)
                    change = current_price - prev_close
                    pct_change = (change / prev_close) * 100 if prev_close else 0
                    
                    color = "#00d4aa" if change >= 0 else "#ff4b4b"
                    sign = "+" if change >= 0 else ""
                    
                    st.markdown(f"""
                    <div style="background-color: #1e2430; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                        <div style="color: #a0aab5; font-size: 14px;">Current Price</div>
                        <div style="font-size: 28px; font-weight: bold;">${current_price:.2f}</div>
                        <div style="color: {color}; font-weight: bold; font-size: 16px;">
                            {sign}{change:.2f} ({sign}{pct_change:.2f}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # OHLC grid
                    st.markdown("#### Today's OHLC")
                    col_o, col_h = st.columns(2)
                    col_l, col_c = st.columns(2)
                    
                    day_open = info.get('regularMarketOpen', info.get('open', df['Open'].iloc[-1]))
                    day_high = info.get('regularMarketDayHigh', info.get('dayHigh', df['High'].max()))
                    day_low = info.get('regularMarketDayLow', info.get('dayLow', df['Low'].min()))
                    
                    def fmt_price(val):
                        if val is None or pd.isna(val): return "N/A"
                        return f"${float(val):.2f}"
                        
                    col_o.metric("Open", fmt_price(day_open))
                    col_h.metric("High", fmt_price(day_high))
                    col_l.metric("Low", fmt_price(day_low))
                    col_c.metric("Close", fmt_price(current_price))
                    
                    st.markdown("---")
                    
                    # Fundamentals
                    market_cap = format_number(info.get('marketCap'))
                    pe_ratio = info.get('trailingPE')
                    pe_str = f"{pe_ratio:.2f}" if pe_ratio is not None and not pd.isna(pe_ratio) else "N/A"
                    div_yield = info.get('dividendYield')
                    div_str = f"{div_yield*100:.2f}%" if div_yield is not None and not pd.isna(div_yield) else "N/A"
                    beta = info.get('beta')
                    beta_str = f"{beta:.2f}" if beta is not None and not pd.isna(beta) else "N/A"
                    
                    st.markdown(f"**Market Cap:** {market_cap}")
                    st.markdown(f"**P/E Ratio:** {pe_str}")
                    st.markdown(f"**Dividend Yield:** {div_str}")
                    st.markdown(f"**Beta:** {beta_str}")
                    
                    st.markdown("---")
                    
                    # Gauge Chart for AI Sentiment
                    st.markdown("### AI Sentiment Score")
                    gauge_color = "#ff4b4b" if score < 34 else "#f59e0b" if score < 67 else "#00d4aa"
                    gauge_fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score,
                        title = {'text': "Market Sentiment", 'font': {'color': 'white', 'size': 14}},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickcolor': "white"},
                            'bar': {'color': gauge_color},
                            'bgcolor': "#1e2430",
                            'steps': [
                                {'range': [0, 33], 'color': "rgba(255, 75, 75, 0.2)"},
                                {'range': [33, 66], 'color': "rgba(245, 158, 11, 0.2)"},
                                {'range': [66, 100], 'color': "rgba(0, 212, 170, 0.2)"}
                            ],
                        }
                    ))
                    gauge_fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="#0e1117", font=dict(color="white"))
                    st.plotly_chart(gauge_fig, use_container_width=True)
                    
                    sentiment_text = "Bearish" if score < 34 else "Neutral" if score < 67 else "Bullish"
                    st.markdown(f"<div style='text-align: center; font-size: 18px; font-weight: bold; color: {gauge_color};'>{sentiment_text}</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("### Signal Dashboard")
                    
                    def color_sig(sig):
                        if sig == "Buy": return "color: #00d4aa; font-weight: bold;"
                        if sig == "Sell": return "color: #ff4b4b; font-weight: bold;"
                        return "color: #f59e0b; font-weight: bold;"
                    
                    signals_data = [
                        {"Indicator": "RSI (14)", "Value": f"{rsi_val:.2f}" if not pd.isna(rsi_val) else "N/A", "Signal": rsi_sig, "Strength": rsi_str},
                        {"Indicator": "MACD", "Value": f"{macd_hist:.2f}" if not pd.isna(macd_hist) else "N/A", "Signal": macd_sig, "Strength": macd_str},
                        {"Indicator": "Stochastic", "Value": f"{stoch_val:.2f}" if not pd.isna(stoch_val) else "N/A", "Signal": stoch_sig, "Strength": stoch_str},
                        {"Indicator": "MA Cross", "Value": f"{ma20_val:.2f}/{ma50_val:.2f}" if not pd.isna(ma20_val) else "N/A", "Signal": ma_sig, "Strength": ma_str},
                        {"Indicator": "ATR (14)", "Value": f"{atr_val:.2f}" if not pd.isna(atr_val) else "N/A", "Signal": "-", "Strength": "Volatility"}
                    ]
                    
                    # Custom HTML table
                    table_html = """
                    <table style="width: 100%; text-align: left; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #2e3646; color: #a0aab5;">
                            <th style="padding: 8px 0;">Indicator</th>
                            <th style="padding: 8px 0;">Value</th>
                            <th style="padding: 8px 0;">Signal</th>
                        </tr>
                    """
                    for row in signals_data:
                        table_html += f"""
                        <tr style="border-bottom: 1px solid #1e2430;">
                            <td style="padding: 8px 0; font-size: 14px;">{row['Indicator']}</td>
                            <td style="padding: 8px 0; font-size: 14px;">{row['Value']}</td>
                            <td style="padding: 8px 0; font-size: 14px; {color_sig(row['Signal'])}">{row['Signal']}</td>
                        </tr>
                        """
                    table_html += "</table>"
                    st.markdown(table_html, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Price Alerts
                    st.markdown("### Price Alerts")
                    target_price = st.number_input("Set Target Price ($)", min_value=0.0, value=float(current_price*1.05), step=1.0)
                    
                    if 'alert_set' not in st.session_state:
                        st.session_state.alert_set = False
                    if 'alert_price' not in st.session_state:
                        st.session_state.alert_price = 0.0
                        
                    if st.button("Set Alert"):
                        st.session_state.alert_set = True
                        st.session_state.alert_price = target_price
                        
                    if st.session_state.alert_set:
                        st.info(f"Active Alert: ${st.session_state.alert_price:.2f}")
                        if current_price >= st.session_state.alert_price:
                            st.success(f"🎉 Target of ${st.session_state.alert_price:.2f} reached!")
                        
        except Exception as e:
            st.error(f"Error fetching data: {e}")

elif nav_selection == "Comparison":
    st.markdown("<h2 class='gradient-header'>Stock Comparison</h2>", unsafe_allow_html=True)
    
    # Input up to 5 tickers
    tickers_input = st.text_input("Enter up to 5 tickers separated by commas (e.g. AAPL, MSFT, GOOGL, AMZN, META)", "AAPL, MSFT, GOOGL")
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()][:5]
    
    if len(tickers) < 2:
        st.warning("Please enter at least 2 tickers to compare.")
    else:
        period_options = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y", "5Y": "5y"}
        selected_period = st.radio("Select Date Range", list(period_options.keys()), index=3, horizontal=True)
        
        try:
            with st.spinner("Fetching data..."):
                data = {}
                stats = []
                for t in tickers:
                    stock = yf.Ticker(t)
                    hist = stock.history(period=period_options[selected_period])
                    if not hist.empty:
                        data[t] = hist['Close']
                        info = stock.info
                        
                        # Default to last close if real-time price unavailable
                        current_price = info.get('currentPrice', info.get('regularMarketPrice', hist['Close'].iloc[-1]))
                        
                        stats.append({
                            "Ticker": t,
                            "Current Price": f"${current_price:.2f}" if current_price else "N/A",
                            "Market Cap": format_number(info.get('marketCap')),
                            "P/E Ratio": round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A",
                            "Div Yield": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",
                            "Beta": round(info.get('beta', 0), 2) if info.get('beta') else "N/A"
                        })
                
                if data:
                    df = pd.DataFrame(data).dropna(how='all')
                    # Forward fill and backward fill for missing data points
                    df = df.ffill().bfill()
                    
                    # Normalize prices to base 100
                    normalized_df = (df / df.iloc[0]) * 100
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### Performance Comparison (Base 100)")
                        fig_line = px.line(normalized_df, x=normalized_df.index, y=normalized_df.columns,
                                          labels={'value': 'Normalized Price', 'variable': 'Ticker'},
                                          color_discrete_sequence=px.colors.qualitative.Set1)
                        fig_line.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font=dict(color='white'),
                                               height=500, margin=dict(l=0, r=0, t=30, b=0))
                        fig_line.update_xaxes(gridcolor='#1f2937')
                        fig_line.update_yaxes(gridcolor='#1f2937')
                        st.plotly_chart(fig_line, use_container_width=True)
                        
                    with col2:
                        st.markdown("### Correlation Heatmap")
                        corr = df.corr()
                        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
                        fig_corr.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font=dict(color='white'),
                                               height=500, margin=dict(l=0, r=0, t=30, b=0))
                        st.plotly_chart(fig_corr, use_container_width=True)
                        
                    st.markdown("### Fundamental Comparison")
                    stats_df = pd.DataFrame(stats)
                    st.dataframe(stats_df, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error during comparison: {e}")

elif nav_selection == "Portfolio Tracker":
    st.markdown("<h2 class='gradient-header'>Portfolio Tracker</h2>", unsafe_allow_html=True)
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Shares', 'Buy Price', 'Buy Date'])
        
    with st.form("add_to_portfolio"):
        col1, col2, col3, col4 = st.columns(4)
        p_ticker = col1.text_input("Ticker").upper()
        p_shares = col2.number_input("Shares", min_value=0.01, step=1.0)
        p_price = col3.number_input("Buy Price ($)", min_value=0.01, step=1.0)
        p_date = col4.date_input("Buy Date")
        
        submitted = st.form_submit_button("Add to Portfolio")
        if submitted and p_ticker:
            new_row = pd.DataFrame({'Ticker': [p_ticker], 'Shares': [p_shares], 'Buy Price': [p_price], 'Buy Date': [p_date]})
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_row], ignore_index=True)
            st.success(f"Added {p_shares} shares of {p_ticker} to portfolio!")
            st.rerun()
            
    if not st.session_state.portfolio.empty:
        df_port = st.session_state.portfolio.copy()
        
        current_prices = {}
        with st.spinner("Updating prices..."):
            for t in df_port['Ticker'].unique():
                try:
                    hist = yf.Ticker(t).history(period='1d')
                    if not hist.empty:
                        current_prices[t] = hist['Close'].iloc[-1]
                    else:
                        current_prices[t] = yf.Ticker(t).info.get('regularMarketPrice', 0.0)
                except:
                    current_prices[t] = 0.0
                    
        df_port['Current Price'] = df_port['Ticker'].map(current_prices)
        df_port['Total Cost'] = df_port['Shares'] * df_port['Buy Price']
        df_port['Current Value'] = df_port['Shares'] * df_port['Current Price']
        df_port['Gain/Loss ($)'] = df_port['Current Value'] - df_port['Total Cost']
        df_port['Gain/Loss (%)'] = (df_port['Gain/Loss ($)'] / df_port['Total Cost']) * 100
        
        total_cost = df_port['Total Cost'].sum()
        total_value = df_port['Current Value'].sum()
        total_gain_dollar = total_value - total_cost
        total_gain_pct = (total_gain_dollar / total_cost) * 100 if total_cost > 0 else 0
        
        color = "#00d4aa" if total_gain_dollar >= 0 else "#ff4b4b"
        sign = "+" if total_gain_dollar >= 0 else ""
        
        st.markdown(f"""
        <div style="background-color: #1e2430; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid {color};">
            <h3 style="margin-top: 0; color: #a0aab5;">Total Portfolio Value</h3>
            <div style="font-size: 36px; font-weight: bold;">${total_value:,.2f}</div>
            <div style="color: {color}; font-weight: bold; font-size: 20px;">
                {sign}${total_gain_dollar:,.2f} ({sign}{total_gain_pct:.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Holdings")
            display_df = df_port.copy()
            for col in ['Buy Price', 'Current Price', 'Total Cost', 'Current Value', 'Gain/Loss ($)']:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
            display_df['Gain/Loss (%)'] = display_df['Gain/Loss (%)'].apply(lambda x: f"{x:,.2f}%")
            
            st.dataframe(display_df, use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                csv = df_port.to_csv(index=False).encode('utf-8')
                st.download_button("Download Portfolio CSV", data=csv, file_name="portfolio.csv", mime="text/csv")
            with c2:
                if st.button("Clear Portfolio"):
                    st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Shares', 'Buy Price', 'Buy Date'])
                    st.rerun()
                
        with col2:
            st.markdown("### Allocation")
            allocation_df = df_port.groupby('Ticker')['Current Value'].sum().reset_index()
            allocation_df = allocation_df[allocation_df['Current Value'] > 0]
            if not allocation_df.empty:
                fig_pie = px.pie(allocation_df, values='Current Value', names='Ticker', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font=dict(color='white'),
                                      height=400, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No value in portfolio to allocate.")
    else:
        st.info("Your portfolio is empty. Add a stock to get started!")

elif nav_selection == "Screener":
    st.markdown("<h2 class='gradient-header'>Stock Screener</h2>", unsafe_allow_html=True)
    st.markdown("Filter popular S&P 500 stocks based on fundamental metrics.")
    
    sp500_tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "LLY", "V",
        "JNJ", "XOM", "WMT", "JPM", "MA", "PG", "UNH", "HD", "CVX", "ABBV",
        "MRK", "KO", "PEP", "AVGO", "COST", "MCD", "TMO", "CSCO", "CRM", "BAC",
        "PFE", "ADBE", "ABT", "LIN", "NFLX", "AMD", "CMCSA", "DHR", "TXN", "NKE",
        "INTC", "QCOM", "VZ", "NEE", "INTU", "AMGN", "IBM", "PM", "COP", "CAT"
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    min_pe = col1.number_input("Min P/E", value=0)
    max_pe = col2.number_input("Max P/E", value=100)
    min_mcap = col3.selectbox("Min Market Cap", ["0", "10B", "50B", "100B", "500B", "1T"], index=2)
    min_vol = col4.selectbox("Min Volume", ["0", "1M", "5M", "10M"], index=1)
    
    mcap_map = {"0": 0, "10B": 10e9, "50B": 50e9, "100B": 100e9, "500B": 500e9, "1T": 1e12}
    vol_map = {"0": 0, "1M": 1e6, "5M": 5e6, "10M": 10e6}
    
    if st.button("Run Screener"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        for i, t in enumerate(sp500_tickers):
            progress_bar.progress((i + 1) / len(sp500_tickers))
            status_text.text(f"Scanning {t}...")
            try:
                info = yf.Ticker(t).info
                pe = info.get('trailingPE', 0)
                mcap = info.get('marketCap', 0)
                vol = info.get('averageVolume', 0)
                sector = info.get('sector', 'Unknown')
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                
                if pe is None: pe = 0
                if mcap is None: mcap = 0
                if vol is None: vol = 0
                
                if (min_pe <= pe <= max_pe) and (mcap >= mcap_map[min_mcap]) and (vol >= vol_map[min_vol]):
                    results.append({
                        "Ticker": t,
                        "Sector": sector,
                        "Price": f"${price:.2f}",
                        "P/E Ratio": round(pe, 2),
                        "Market Cap": mcap,
                        "Volume": vol
                    })
            except:
                continue
                
        status_text.empty()
        progress_bar.empty()
        
        if results:
            st.success(f"Found {len(results)} matching stocks.")
            df_res = pd.DataFrame(results)
            df_res = df_res.sort_values("Market Cap", ascending=False)
            df_res['Market Cap'] = df_res['Market Cap'].apply(format_number)
            df_res['Volume'] = df_res['Volume'].apply(format_volume)
            st.dataframe(df_res, use_container_width=True)
        else:
            st.warning("No stocks matched your criteria.")

elif nav_selection == "Market News":
    st.markdown(f"<h2 class='gradient-header'>{ticker} - Market News</h2>", unsafe_allow_html=True)
    if not ticker:
        st.warning("Please enter a ticker in the sidebar.")
    else:
        with st.spinner("Fetching latest news..."):
            try:
                stock = yf.Ticker(ticker)
                news = stock.news
                if not news:
                    st.info("No recent news found for this ticker.")
                else:
                    for article in news[:10]:
                        title = article.get('title', 'No Title')
                        publisher = article.get('publisher', 'Unknown Source')
                        link = article.get('link', '#')
                        
                        # Sentiment heuristic
                        lower_title = title.lower()
                        pos_words = ['surge', 'jump', 'gain', 'up', 'beat', 'growth', 'bullish', 'high', 'profit', 'soar']
                        neg_words = ['plunge', 'drop', 'fall', 'down', 'miss', 'loss', 'bearish', 'low', 'lawsuit', 'cut']
                        
                        pos_count = sum(1 for w in pos_words if w in lower_title)
                        neg_count = sum(1 for w in neg_words if w in lower_title)
                        
                        if pos_count > neg_count:
                            sentiment = "🟢 Positive"
                        elif neg_count > pos_count:
                            sentiment = "🔴 Negative"
                        else:
                            sentiment = "🟡 Neutral"
                            
                        # Format timestamp if available
                        pub_time = article.get('providerPublishTime')
                        time_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M') if pub_time else ""
                        
                        st.markdown(f"""
                        <div class="news-card">
                            <h4><a href="{link}" target="_blank" style="color: #00d4aa; text-decoration: none;">{title}</a></h4>
                            <div style="color: #a0aab5; font-size: 14px;">
                                <span>{publisher}</span> | <span>{time_str}</span> | <span style="font-weight:bold;">{sentiment}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error fetching news: {e}")

# Footer
st.markdown("""
<div class="footer">
    Data powered by <b>Yahoo Finance</b> | StockVision Pro &copy; 2026
</div>
""", unsafe_allow_html=True)
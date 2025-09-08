import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from PIL import Image
from io import BytesIO

# Nastavenie stránky
st.set_page_config(
    page_title="Stock Predictor",
    page_icon="📈",
    layout="wide"
)

@st.cache_data(ttl=3600)  # Cache na 1 hodinu
def get_stock_data(symbol, period="2y"):
    """Získanie dát o akciách s cache"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None, None
            
        # Technické indikátory
        hist['SMA_5'] = hist['Close'].rolling(5).mean()
        hist['SMA_10'] = hist['Close'].rolling(10).mean()
        hist['SMA_20'] = hist['Close'].rolling(20).mean()
        hist['SMA_50'] = hist['Close'].rolling(50).mean()
        hist['SMA_100'] = hist['Close'].rolling(100).mean()
        hist['SMA_200'] = hist['Close'].rolling(200).mean()
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # Volatilita
        hist['Volatility'] = hist['Close'].rolling(20).std()
        
        # MACD
        hist['EMA_12'] = hist['Close'].ewm(span=12).mean()
        hist['EMA_26'] = hist['Close'].ewm(span=26).mean()
        hist['MACD'] = hist['EMA_12'] - hist['EMA_26']
        hist['MACD_Signal'] = hist['MACD'].ewm(span=9).mean()
        
        # Target premenná
        hist['Next_Day_Return'] = hist['Close'].shift(-1) / hist['Close'] - 1
        hist['Target'] = (hist['Next_Day_Return'] > 0.005).astype(int)  # 0.5% prah
        
        # Info o firme
        info = ticker.info
        
        return hist, info
        
    except Exception as e:
        st.error(f"Chyba pri získavaní dát: {e}")
        return None, None

@st.cache_data
def get_company_logo(symbol, info):
    """Získanie loga firmy"""
    try:
        # Pokus o logo z rôznych zdrojov
        logo_url = info.get('logo_url')
        if not logo_url:
            website = info.get('website', '')
            if website:
                domain = website.replace('https://', '').replace('http://', '').replace('www.', '')
                logo_url = f"https://logo.clearbit.com/{domain}"
            else:
                logo_url = f"https://img.logo.dev/ticker/{symbol.upper()}?token=pk_X-1ZO13ESVSbpp_oMRFXvQ&format=png&size=200"
        
        response = requests.get(logo_url, timeout=5)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        pass
    return None

def create_price_chart(data, symbol):
    """Vytvorenie grafu s cenami a indikátormi"""
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'], 
        low=data['Low'],
        close=data['Close'],
        name=symbol,
        increasing_line_color='green',
        decreasing_line_color='red'
    ))
    
    # Klzavé priemery
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], name='SMA 20', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_100'], name='SMA 100', line=dict(color='red')))
    
    fig.update_layout(
        title=f"{symbol} - Cenový graf s klzavými priemermi",
        xaxis_title="Dátum",
        yaxis_title="Cena ($)",
        height=600,
        showlegend=True
    )
    
    return fig

def create_technical_indicators_chart(data):
    """Graf technických indikátorov"""
    fig = go.Figure()
    
    # RSI subplot
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['RSI'], 
        name='RSI',
        line=dict(color='purple')
    ))
    
    # RSI horizontálne čiary
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
    
    fig.update_layout(
        title="RSI (Relative Strength Index)",
        xaxis_title="Dátum",
        yaxis_title="RSI",
        height=400,
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_macd_chart(data):
    """MACD graf"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD_Signal'], name='Signal', line=dict(color='red')))
    
    # MACD histogram
    fig.add_trace(go.Bar(
        x=data.index, 
        y=data['MACD'] - data['MACD_Signal'], 
        name='Histogram',
        marker_color='gray',
        opacity=0.3
    ))
    
    fig.update_layout(
        title="MACD",
        xaxis_title="Dátum",
        yaxis_title="MACD",
        height=400
    )
    
    return fig

# HLAVNÁ APLIKÁCIA
def main():
    st.title("📈 Stock Market Predictor")
    st.markdown("---")
    
    # Sidebar pre nastavenia
    with st.sidebar:
        st.header("⚙️ Nastavenia")
        
        # Výber akcie
        symbol = st.text_input("Ticker Symbol", value="GOOGL", help="Napr. GOOGL, AAPL, TSLA")
        
        # Obdobie dát
        period_options = {
            "1 rok": "1y",
            "2 roky": "2y", 
            "3 roky": "3y",
            "5 rokov": "5y"
        }
        period_selected = st.selectbox("Obdobie dát", list(period_options.keys()), index=1)
        period = period_options[period_selected]
        
        # Tlačidlo na načítanie
        load_data = st.button("📊 Načítať dáta", type="primary")
    
    # Hlavný obsah
    if load_data or 'data_loaded' not in st.session_state:
        if symbol:
            with st.spinner("Načítavam dáta..."):
                data, info = get_stock_data(symbol.upper(), period)
                
                if data is not None and info is not None:
                    st.session_state['data'] = data
                    st.session_state['info'] = info
                    st.session_state['symbol'] = symbol.upper()
                    st.session_state['data_loaded'] = True
                    st.success("✅ Dáta úspešne načítané!")
                else:
                    st.error("❌ Nepodarilo sa načítať dáta. Skontrolujte ticker symbol.")
                    return
        else:
            st.warning("⚠️ Zadajte ticker symbol")
            return
    
    # Zobrazenie dát ak sú načítané
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        data = st.session_state['data']
        info = st.session_state['info']
        symbol = st.session_state['symbol']
        
        # Header s logom a info
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            # Pokus o zobrazenie loga
            logo = get_company_logo(symbol, info)
            if logo:
                st.image(logo, width=100)
        
        with col2:
            st.subheader(f"{info.get('longName', symbol)} ({symbol})")
            
            # Základné metriky
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-2]
            price_change = current_price - previous_price
            price_change_pct = (price_change / previous_price) * 100
            
            col_price1, col_price2, col_price3 = st.columns(3)
            
            with col_price1:
                st.metric("💰 Aktuálna cena", f"${current_price:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
            
            with col_price2:
                market_cap = info.get('marketCap', 0)
                if market_cap:
                    st.metric("🏢 Trhová kap.", f"${market_cap/1e9:.1f}B")
                else:
                    st.metric("🏢 Trhová kap.", "N/A")
            
            with col_price3:
                pe_ratio = info.get('trailingPE', 0)
                if pe_ratio:
                    st.metric("📊 P/E Ratio", f"{pe_ratio:.2f}")
                else:
                    st.metric("📊 P/E Ratio", "N/A")
        
        # Taby pre rôzne zobrazenia
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Cenový graf", "🔧 Technické indikátory", "📋 Dáta", "🏢 Info o firme"])
        
        with tab1:
            st.plotly_chart(create_price_chart(data, symbol), use_container_width=True)
            
            # Volatilita graf
            st.subheader("📊 Volatilita (20-dňová)")
            fig_vol = px.line(data, y='Volatility', title="Volatilita")
            st.plotly_chart(fig_vol, use_container_width=True)
        
        with tab2:
            # RSI
            st.plotly_chart(create_technical_indicators_chart(data), use_container_width=True)
            
            # MACD
            st.plotly_chart(create_macd_chart(data), use_container_width=True)
            
            # Aktuálne hodnoty indikátorov
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_rsi = data['RSI'].iloc[-1]
                rsi_color = "🔴" if current_rsi > 70 else "🟢" if current_rsi < 30 else "🟡"
                st.metric(f"{rsi_color} RSI", f"{current_rsi:.1f}")
            
            with col2:
                current_macd = data['MACD'].iloc[-1]
                st.metric("📈 MACD", f"{current_macd:.3f}")
            
            with col3:
                current_vol = data['Volatility'].iloc[-1]
                st.metric("🌊 Volatilita", f"{current_vol:.2f}")
            
            with col4:
                # Signál pre zajtra
                features_count = len([col for col in data.columns if not pd.isna(data[col].iloc[-1]) and col not in ['Target', 'Next_Day_Return']])
                signal = "📈 BUY" if current_rsi < 30 and current_macd > 0 else "📉 SELL" if current_rsi > 70 and current_macd < 0 else "⏸️ HOLD"
                st.metric("🔮 Signál", signal)
        
        with tab3:
            st.subheader("📋 Posledných 10 dní")
            
            # Výber stĺpcov na zobrazenie
            columns_to_show = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 'RSI', 'MACD']
            display_data = data[columns_to_show].tail(10).round(2)
            st.dataframe(display_data, use_container_width=True)
            
            # Download tlačidlo
            csv = data.to_csv()
            st.download_button(
                label="💾 Stiahnuť všetky dáta (CSV)",
                data=csv,
                file_name=f"{symbol}_stock_data.csv",
                mime='text/csv'
            )
        
        with tab4:
            st.subheader(f"🏢 {info.get('longName', symbol)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Základné informácie:**")
                st.write(f"• **Sektor:** {info.get('sector', 'N/A')}")
                st.write(f"• **Odvetvie:** {info.get('industry', 'N/A')}")
                st.write(f"• **Krajina:** {info.get('country', 'N/A')}")
                st.write(f"• **Zamestnanci:** {info.get('fullTimeEmployees', 'N/A'):,}" if info.get('fullTimeEmployees') else "• **Zamestnanci:** N/A")
                st.write(f"• **Webstránka:** {info.get('website', 'N/A')}")
            
            with col2:
                st.write("**Finančné metriky:**")
                st.write(f"• **P/E Ratio:** {info.get('trailingPE', 'N/A')}")
                st.write(f"• **P/B Ratio:** {info.get('priceToBook', 'N/A')}")
                st.write(f"• **Profit Margin:** {info.get('profitMargins', 'N/A')}")
                st.write(f"• **ROE:** {info.get('returnOnEquity', 'N/A')}")
                st.write(f"• **Dividend Yield:** {info.get('dividendYield', 'N/A')}")
            
            # Popis firmy
            description = info.get('longBusinessSummary', 'Popis nie je dostupný')
            if description and description != 'Popis nie je dostupný':
                st.write("**Popis firmy:**")
                st.write(description)

if __name__ == "__main__":
    main()

import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np

# Nastavenie titulku a popisu aplikácie
st.set_page_config(page_title="Stock Info App", layout="wide")

st.title("📈 Moja prvá burzová aplikácia")
st.markdown("Zadaj **ticker** firmy (napr. `AAPL`, `GOOGL`, `MSFT`) a získaj informácie + graf.")

# Vstup od používateľa
ticker = st.text_input("Ticker firmy:")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Rozdelenie obrazovky do dvoch stĺpcov
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("ℹ️ Základné informácie")
            st.write(f"**Názov:** {info.get('longName', 'N/A')}")
            st.write(f"**Odvetvie:** {info.get('sector', 'N/A')}")
            st.write(f"**Trhová kapitalizácia:** {info.get('marketCap', 'N/A')}")
            st.write(f"**Zamestnanci:** {info.get('fullTimeEmployees', 'N/A')}")

        with col2:
            st.subheader("📜 Popis firmy")
            st.write(info.get("longBusinessSummary", "N/A"))

        # Historické dáta
        st.subheader("💵 Historický vývoj ceny")
        hist = stock.history(period="6mo")
        st.line_chart(hist["Close"])

        # Aktuálna cena
        st.metric("Aktuálna cena", f"{hist['Close'][-1]:.2f} USD")

    except Exception as e:
        st.error(f"Chyba pri načítaní dát pre ticker '{ticker}': {e}")
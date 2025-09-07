import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np

st.title("My Streamlit Frontend")
st.write("Hello, Streamlit!")

# Vstup od používateľa
ticker = input("Zadaj ticker firmy (napr. AAPL, GOOGL, MSFT): ")

try:
    stock = yf.Ticker(ticker)
    info = stock.info

    print(f"\nℹ️ Informácie o {ticker}")
    print(f"Názov: {info.get('longName', 'N/A')}")
    print(f"Odvetvie: {info.get('sector', 'N/A')}")
    print(f"Popis: {info.get('longBusinessSummary', 'N/A')}")
    print(f"Trhová kapitalizácia: {info.get('marketCap', 'N/A')}")
    print(f"Zamestnanci: {info.get('fullTimeEmployees', 'N/A')}")

    hist = stock.history(period="1d")
    print("\n💵 Aktuálna cena akcie:")
    print(hist["Close"])

except Exception as e:
    print(f"Chyba pri načítaní dát pre ticker '{ticker}': {e}")


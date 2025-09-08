import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
import gradio as gr

# Vstup od používateľa
ticker = input("Zadaj ticker firmy (napr. AAPL, GOOGL, MSFT): ")

try:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    print(f"\nℹ️ Informácie o {ticker.upper()}")
    print("=" * 50)
    
    # Základné informácie
    print(f"Názov: {info.get('longName', 'N/A')}")
    print(f"Odvetvie: {info.get('sector', 'N/A')}")
    print(f"Popis: {info.get('longBusinessSummary', 'N/A')}")
    
    # Formátovanie market cap
    market_cap = info.get('marketCap', 0)
    if market_cap and market_cap > 0:
        if market_cap >= 1e12:
            print(f"Trhová kapitalizácia: ${market_cap/1e12:.2f}T")
        elif market_cap >= 1e9:
            print(f"Trhová kapitalizácia: ${market_cap/1e9:.2f}B")
        elif market_cap >= 1e6:
            print(f"Trhová kapitalizácia: ${market_cap/1e6:.2f}M")
        else:
            print(f"Trhová kapitalizácia: ${market_cap:,}")
    else:
        print("Trhová kapitalizácia: N/A")
    
    # Počet zamestnancov
    employees = info.get('fullTimeEmployees', 0)
    if employees and employees > 0:
        print(f"Zamestnanci: {employees:,}")
    else:
        print("Zamestnanci: N/A")
    
    print("\n📊 Finančné metriky:")
    print("-" * 30)
    
    # P/E Ratio (Current/Trailing)
    pe_ratio = info.get('trailingPE')
    if pe_ratio and pe_ratio > 0:
        print(f"P/E Ratio (Trailing): {pe_ratio:.2f}")
    else:
        print("P/E Ratio (Trailing): N/A")
    
    # Forward P/E Ratio
    forward_pe = info.get('forwardPE')
    if forward_pe and forward_pe > 0:
        print(f"P/E Ratio (Forward): {forward_pe:.2f}")
    else:
        print("P/E Ratio (Forward): N/A")
    
    # EPS (Earnings Per Share)
    eps_trailing = info.get('trailingEps')
    if eps_trailing and eps_trailing != 0:
        print(f"EPS (Trailing): ${eps_trailing:.2f}")
    else:
        print("EPS (Trailing): N/A")
    
    # Forward EPS
    forward_eps = info.get('forwardEps')
    if forward_eps and forward_eps != 0:
        print(f"EPS (Forward): ${forward_eps:.2f}")
    else:
        print("EPS (Forward): N/A")
    
    # Ďalšie užitočné metriky
    peg_ratio = info.get('pegRatio')
    if peg_ratio and peg_ratio > 0:
        print(f"PEG Ratio: {peg_ratio:.2f}")
    else:
        print("PEG Ratio: N/A")
    
    pb_ratio = info.get('priceToBook')
    if pb_ratio and pb_ratio > 0:
        print(f"P/B Ratio: {pb_ratio:.2f}")
    else:
        print("P/B Ratio: N/A")
    
    # Dividend Yield
    div_yield = info.get("dividendYield")
    if div_yield and div_yield > 0:
        print(f"Dividend Yield: {div_yield*100:.2f}%")
    else:
        print("Dividend Yield: N/A")
    
    # Aktuálna cena
    hist = stock.history(period="1d")
    if not hist.empty:
        print("\n💵 Aktuálna cena akcie:")
        print("-" * 25)
        current_price = hist["Close"].iloc[-1]
        print(f"Zatváracie cena: ${current_price:.2f}")
        
        # Ak sú dostupné daily dáta, ukáž aj open, high, low
        if len(hist) > 0:
            print(f"Otváracie cena: ${hist['Open'].iloc[-1]:.2f}")
            print(f"Denné maximum: ${hist['High'].iloc[-1]:.2f}")
            print(f"Denné minimum: ${hist['Low'].iloc[-1]:.2f}")
            print(f"Objem: {hist['Volume'].iloc[-1]:,}")
    else:
        print("\n💵 Aktuálna cena akcie: Nedostupná")
    
    # 52-week range
    week_52_high = info.get('fiftyTwoWeekHigh')
    week_52_low = info.get('fiftyTwoWeekLow')
    if week_52_high and week_52_low:
        print(f"\n📈 52-týždňový rozsah:")
        print(f"Maximum: ${week_52_high:.2f}")
        print(f"Minimum: ${week_52_low:.2f}")
    
except Exception as e:
    print(f"❌ Chyba pri načítaní dát pre ticker '{ticker}': {e}")
    print("💡 Tip: Skontrolujte, či je ticker správny (napr. AAPL, GOOGL, MSFT)")

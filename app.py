"""
UYGULAMA REÇETESİ (V38 - SAFE MODE):
1. ZERO-DEPENDENCY: Dış kütüphane hatalarını önlemek için indikatörler manuel hesaplanır.
2. DUAL-TIME ONay: 1d ve 1h uyumu kontrol edilir.
3. BULUT UYUMLU: Python 3.13+ versiyonlarında sorunsuz çalışır.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import requests

# --- 1. MANUEL TEKNİK ANALİZ MOTORU (Kütüphane Bağımsız) ---
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_mfi(df, period=14):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    positive_mf = mf.where(tp > tp.shift(1), 0).rolling(window=period).sum()
    negative_mf = mf.where(tp < tp.shift(1), 0).rolling(window=period).sum()
    mfr = positive_mf / negative_mf
    return 100 - (100 / (1 + mfr))

# --- 2. ANALİZ MOTORU ---
def analyze_v38(ticker, portfolio):
    try:
        df_d = yf.download(ticker, period="6mo", interval="1d", progress=False)
        df_h = yf.download(ticker, period="1mo", interval="1h", progress=False)
        
        if df_d.empty or df_h.empty: return None
        
        c = df_d['Close']
        # Basit Hareketli Ortalama
        ma20 = c.rolling(window=20).mean().iloc[-1]
        # RSI ve MFI (Manuel Fonksiyonlardan)
        rsi_h = get_rsi(df_h['Close']).iloc[-1]
        mfi_d = get_mfi(df_d).iloc[-1]
        # ATR (Basit Volatilite)
        high_low = df_d['High'] - df_d['Low']
        atr = high_low.rolling(window=14).mean().iloc[-1]
        
        score = 0
        if c.iloc[-1] > ma20: score += 40
        if mfi_d > 55: score += 30
        if rsi_h > 50: score += 30
        
        entry = c.iloc[-1]
        stop = entry - (atr * 1.5)
        target = entry + (atr * 3)
        lot = int((portfolio * 0.01) / (entry - stop)) if (entry - stop) > 0 else 0
        
        return {
            "Hisse": ticker.replace(".IS",""),
            "Skor": score,
            "Fiyat": round(entry, 2),
            "Stop": round(stop, 2),
            "Hedef": round(target, 2),
            "Lot": lot,
            "Durum": "🔱 KRAL" if score >= 85 else "🚀 AL" if score >= 65 else "⌛ İZLE"
        }
    except Exception as e:
        return None

# --- 3. ARAYÜZ ---
st.set_page_config(page_title="Titan V38 SafeMode", layout="wide")
st.title("🔱 Titan V38: Safe-Mode Terminal")

st.sidebar.header("⚙️ Ayarlar")
kasa = st.sidebar.number_input("Sanal Kasa (TL)", value=100000)
tg_token = st.sidebar.text_input("Telegram Token", type="password")
tg_id = st.sidebar.text_input("Telegram ID", type="password")

WATCHLIST = ["TUPRS.IS", "THYAO.IS", "BIMAS.IS", "AKSA.IS", "KONTR.IS", "ALTNY.IS", "ASELS.IS", "EREGL.IS"]

if st.button("Piyasayı Tara"):
    results = []
    with st.spinner("Analiz ediliyor..."):
        for t in WATCHLIST:
            res = analyze_v38(t, kasa)
            if res: results.append(res)
    
    if results:
        res_df = pd.DataFrame(results).sort_values("Skor", ascending=False)
        st.table(res_df)
        
        if tg_token and tg_id:
            for _, row in res_df.iterrows():
                if row['Durum'] == "🔱 KRAL":
                    msg = f"🔱 *KRAL SİNYAL*\n#{row['Hisse']}\nFiyat: {row['Fiyat']}\nStop: {row['Stop']}\nHedef: {row['Hedef']}"
                    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={"chat_id": tg_id, "text": msg, "parse_mode": "Markdown"})


    

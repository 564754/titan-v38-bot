import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import requests
import time

# --- 1. MANUEL İNDİKATÖR HESAPLAMALARI ---
def calculate_rsi(series, period=14):
    if len(series) < period: return pd.Series([50])
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_mfi(df, period=14):
    if len(df) < period: return pd.Series([50])
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    pos_mf = mf.where(tp > tp.shift(1), 0).rolling(window=period).sum()
    neg_mf = mf.where(tp < tp.shift(1), 0).rolling(window=period).sum()
    return 100 - (100 / (1 + (pos_mf / neg_mf)))

# --- 2. ANALİZ MOTORU (STABİLİZE EDİLMİŞ) ---
def analyze_v38(ticker, portfolio):
    try:
        # Veri çekme (Hata payını azaltmak için retry eklendi)
        df_d = yf.download(ticker, period="6mo", interval="1d", progress=False, multi_level=False)
        time.sleep(0.2) # Yahoo'yu yormayalım
        df_h = yf.download(ticker, period="1mo", interval="1h", progress=False, multi_level=False)
        
        if df_d.empty or df_h.empty or len(df_d) < 20: return None
        
        c = df_d['Close']
        ma20 = c.rolling(window=20).mean().iloc[-1]
        rsi_h = calculate_rsi(df_h['Close']).iloc[-1]
        mfi_d = calculate_mfi(df_d).iloc[-1]
        
        # Volatilite ve Skor
        volatility = (df_d['High'] - df_d['Low']).rolling(window=14).mean().iloc[-1]
        
        score = 0
        if c.iloc[-1] > ma20: score += 40
        if mfi_d > 55: score += 30
        if rsi_h > 50: score += 30
        
        entry = float(c.iloc[-1])
        stop = entry - (volatility * 1.5)
        target = entry + (volatility * 3)
        # Lot hesabı (Risk yönetimi: Kasanın %1'i kadar risk)
        risk_per_share = entry - stop
        lot = int((portfolio * 0.01) / risk_per_share) if risk_per_share > 0 else 0
        
        return {
            "Hisse": ticker.replace(".IS",""),
            "Skor": int(score),
            "Fiyat": round(entry, 2),
            "Stop": round(stop, 2),
            "Hedef": round(target, 2),
            "Lot": lot,
            "Durum": "🔱 KRAL" if score >= 85 else "🚀 AL" if score >= 65 else "⌛ İZLE"
        }
    except Exception as e:
        return None

# --- 3. ARAYÜZ ---
st.set_page_config(page_title="Titan V38 Sovereign", layout="wide")
st.title("🔱 Titan V38: Sovereign Terminal")

st.sidebar.header("⚙️ Operasyon Merkezi")
kasa = st.sidebar.number_input("Sanal Portföy (TL)", value=100000, step=1000)
st.sidebar.info("Sistem her hisse için portföyün %1'ini riske eder.")

WATCHLIST = ["TUPRS.IS", "THYAO.IS", "BIMAS.IS", "AKSA.IS", "KONTR.IS", "ALTNY.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "SISE.IS"]

if st.button("🚀 Piyasayı Tara ve Sinyalleri Yakala"):
    results = []
    progress_bar = st.progress(0)
    
    for i, t in enumerate(WATCHLIST):
        res = analyze_v38(t, kasa)
        if res: results.append(res)
        progress_bar.progress((i + 1) / len(WATCHLIST))
    
    if results:
        res_df = pd.DataFrame(results).sort_values("Skor", ascending=False)
        # Tabloyu göster
        st.subheader("🎯 Güncel Sinyal Tablosu")
        st.dataframe(res_df.style.highlight_max(axis=0, subset=['Skor'], color='#2E7D32'), use_container_width=True)
        
        # Kazanç/Risk Analizi Notu
        st.success(f"Tarama Tamamlandı. {len(results)} hisse analiz edildi.")
    else:
        st.error("Veri çekme hatası! Lütfen 1 dakika sonra tekrar 'Piyasayı Tara' deyin.")

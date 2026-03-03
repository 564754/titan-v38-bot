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

# --- 2. ANALİZ MOTORU (İNANTÇI VERİ ÇEKME) ---
def analyze_v38(ticker, portfolio):
    # 3 Kez tekrar deneme mekanizması
    for attempt in range(3):
        try:
            # multi_level=False ve auto_adjust eklenerek veri formatı sabitlendi
            df_d = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
            time.sleep(0.5) # Yahoo'yu yormayalım
            df_h = yf.download(ticker, period="1mo", interval="1h", progress=False, auto_adjust=True)
            
            if not df_d.empty and not df_h.empty and len(df_d) >= 20:
                c = df_d['Close']
                ma20 = c.rolling(window=20).mean().iloc[-1]
                rsi_h = calculate_rsi(df_h['Close']).iloc[-1]
                mfi_d = calculate_mfi(df_d).iloc[-1]
                volatility = (df_d['High'] - df_d['Low']).rolling(window=14).mean().iloc[-1]
                
                score = 0
                if c.iloc[-1] > ma20: score += 40
                if mfi_d > 55: score += 30
                if rsi_h > 50: score += 30
                
                entry = float(c.iloc[-1])
                stop = entry - (volatility * 1.5)
                target = entry + (volatility * 3)
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
        except:
            time.sleep(1) # Hata olursa 1 saniye bekle ve tekrar dene
            continue
    return None

# --- 3. ARAYÜZ ---
st.set_page_config(page_title="Titan V38 Sovereign", layout="wide")
st.title("🔱 Titan V38: Sovereign Terminal")

st.sidebar.header("⚙️ Operasyon Merkezi")
kasa = st.sidebar.number_input("Sanal Portföy (TL)", value=100000, step=1000)

WATCHLIST = ["TUPRS.IS", "THYAO.IS", "BIMAS.IS", "AKSA.IS", "KONTR.IS", "ALTNY.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "SISE.IS"]

if st.button("🚀 Piyasayı Tara ve Sinyalleri Yakala"):
    results = []
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    for i, t in enumerate(WATCHLIST):
        progress_text.text(f"Analiz ediliyor: {t}")
        res = analyze_v38(t, kasa)
        if res: results.append(res)
        progress_bar.progress((i + 1) / len(WATCHLIST))
    
    progress_text.text("Analiz Tamamlandı!")
    
    if results:
        res_df = pd.DataFrame(results).sort_values("Skor", ascending=False)
        st.subheader("🎯 Güncel Sinyal Tablosu")
        st.dataframe(res_df, use_container_width=True)
    else:
        st.error("Şu an Yahoo Finance yoğunluğu nedeniyle veri alınamadı. Lütfen 30 saniye sonra tekrar deneyin.")

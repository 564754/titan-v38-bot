import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import requests

# --- 1. MANUEL İNDİKATÖR HESAPLAMALARI ---
def calculate_rsi(series, period=14):
    if len(series) < period: return pd.Series([50] * len(series))
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_mfi(df, period=14):
    if len(df) < period: return pd.Series([50] * len(df))
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    pos_mf = mf.where(tp > tp.shift(1), 0).rolling(window=period).sum()
    neg_mf = mf.where(tp < tp.shift(1), 0).rolling(window=period).sum()
    return 100 - (100 / (1 + (pos_mf / neg_mf)))

# --- 2. ANA ARAYÜZ ---
st.set_page_config(page_title="Titan V38 Sovereign", layout="wide")
st.title("🔱 Titan V38: Sovereign Terminal")

st.sidebar.header("⚙️ Operasyon Merkezi")
kasa = st.sidebar.number_input("Sanal Portföy (TL)", value=100000, step=1000)

WATCHLIST = ["TUPRS.IS", "THYAO.IS", "BIMAS.IS", "AKSA.IS", "KONTR.IS", "ALTNY.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "SISE.IS"]

if st.button("🚀 Piyasayı Tek Seferde Tara"):
    with st.spinner("Toplu veri paketi indiriliyor..."):
        try:
            # TÜM VERİYİ TEK SEFERDE İNDİRİYORUZ (Yahoo'yu yormayan yöntem)
            data_d = yf.download(WATCHLIST, period="6mo", interval="1d", group_by='ticker', progress=False, auto_adjust=True)
            data_h = yf.download(WATCHLIST, period="1mo", interval="1h", group_by='ticker', progress=False, auto_adjust=True)
            
            results = []
            for ticker in WATCHLIST:
                try:
                    # Günlük ve Saatlik Verileri Ayıkla
                    df_d = data_d[ticker].dropna()
                    df_h = data_h[ticker].dropna()
                    
                    if len(df_d) < 20: continue
                    
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
                    lot = int((kasa * 0.01) / risk_per_share) if risk_per_share > 0 else 0
                    
                    results.append({
                        "Hisse": ticker.replace(".IS",""),
                        "Skor": int(score),
                        "Fiyat": round(entry, 2),
                        "Stop": round(stop, 2),
                        "Hedef": round(target, 2),
                        "Lot": lot,
                        "Durum": "🔱 KRAL" if score >= 85 else "🚀 AL" if score >= 65 else "⌛ İZLE"
                    })
                except: continue
            
            if results:
                res_df = pd.DataFrame(results).sort_values("Skor", ascending=False)
                st.subheader("🎯 Güncel Sinyal Tablosu")
                st.dataframe(res_df, use_container_width=True)
            else:
                st.warning("Veri işlenemedi. Piyasalar kapalı olabilir veya Yahoo geçici olarak kapalıdır.")
                
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")

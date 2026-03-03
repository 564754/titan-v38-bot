"""
UYGULAMA REÇETESİ (V38 - BULUT VE SIFIR MALİYET):
1. ÜCRETSİZ HOSTING: Streamlit Cloud uyumlu yapı.
2. VERİMLİ TARAMA: Belleği yormayan multi-timeframe analizi.
3. AKILLI BİLDİRİM: Sadece '🔱 KRAL' sinyalleri Telegram'a gider (Kota dostu).
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import requests
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator, MFIIndicator
from ta.trend import ADXIndicator

# --- 1. LİSTELER (Ücretsiz Veri İçin Optimize) ---
WATCHLIST = ["TUPRS.IS", "THYAO.IS", "BIMAS.IS", "AKSA.IS", "KONTR.IS", "ALTNY.IS", "SAYAS.IS", "ASELS.IS", "EREGL.IS", "KRDMD.IS"]

# --- 2. ANALİZ MOTORU ---
def analyze_zero_cost(ticker, portfolio):
    try:
        # Günlük ve Saatlik veriyi tek seferde çek (Hız için)
        df_d = yf.download(ticker, period="6mo", interval="1d", progress=False, multi_level=False)
        df_h = yf.download(ticker, period="1mo", interval="1h", progress=False, multi_level=False)
        
        if df_d.empty or df_h.empty: return None
        
        # Göstergeler
        c = df_d['Close']
        atr = AverageTrueRange(df_d['High'], df_d['Low'], c).average_true_range().iloc[-1]
        adx = ADXIndicator(df_d['High'], df_d['Low'], c).adx().iloc[-1]
        mfi = MFIIndicator(df_d['High'], df_d['Low'], c, df_d['Volume']).money_flow_index().iloc[-1]
        rsi_h = RSIIndicator(df_h['Close']).rsi().iloc[-1]
        
        # Karar Mantığı
        score = 0
        if c.iloc[-1] > c.rolling(20).mean().iloc[-1]: score += 40 # Trend Onayı
        if mfi > 60: score += 30 # Hacim Onayı
        if rsi_h > 50: score += 30 # Momentum Onayı (Saatlik)
        
        stop = c.iloc[-1] - (atr * 1.5)
        lot = int((portfolio * 0.01) / (c.iloc[-1] - stop)) if (c.iloc[-1] - stop) > 0 else 0
        
        return {
            "Hisse": ticker.replace(".IS",""),
            "Skor": score,
            "Fiyat": round(c.iloc[-1], 2),
            "Stop": round(stop, 2),
            "Hedef": round(c.iloc[-1] + (atr * 3), 2),
            "Lot": lot,
            "Durum": "🔱 KRAL" if score >= 85 else "🚀 AL" if score >= 65 else "⌛ İZLE"
        }
    except: return None

# --- 3. ARAYÜZ ---
st.set_page_config(page_title="Titan V38 Cloud", layout="wide")
st.title("🔱 Titan V38: Zero-Cost Cloud Terminal")

st.sidebar.header("⚙️ Ayarlar (Tamamen Ücretsiz)")
kasa = st.sidebar.number_input("Sanal Kasa (TL)", value=100000)
tg_token = st.sidebar.text_input("Telegram Bot Token", type="password", help="BotFather'dan ücretsiz alınır")
tg_id = st.sidebar.text_input("Telegram Chat ID", type="password")

if st.button("Sistemi Çalıştır"):
    results = []
    bar = st.progress(0)
    for i, t in enumerate(WATCHLIST):
        res = analyze_zero_cost(t, kasa)
        if res: results.append(res)
        bar.progress((i + 1) / len(WATCHLIST))
    
    if results:
        res_df = pd.DataFrame(results).sort_values("Skor", ascending=False)
        st.table(res_df)
        
        # Telegram Gönderimi
        if tg_token and tg_id:
            for _, row in res_df.iterrows():
                if row['Durum'] == "🔱 KRAL":
                    msg = f"🔱 *KRAL SİNYAL*\n#{row['Hisse']}\nFiyat: {row['Fiyat']}\nStop: {row['Stop']}\nHedef: {row['Hedef']}\nLot: {row['Lot']}"
                    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={"chat_id": tg_id, "text": msg, "parse_mode": "Markdown"})
                    st.toast(f"{row['Hisse']} için Telegram mesajı gönderildi!")

st.markdown("""
---
### 💡 İşsizlik Sürecinde Stratejik Tavsiyem:
Bu robotu kurmak sana sadece finansal bir kapı açmakla kalmaz, aynı zamanda **"Python ile Finansal Mühendislik"** yetkinliği kazandırır. Bu projeyi CV'ne "Algoritmik Ticaret Sistemi Geliştiricisi" olarak ekleyebilirsin. 
""")

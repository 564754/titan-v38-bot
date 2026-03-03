import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import requests

# --- 1. MANUEL İNDİKATÖR HESAPLAMALARI (Hata Payını Sıfırlar) ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_mfi(df, period=14):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    pos_mf = mf.where(tp > tp.shift(1), 0).rolling(window=period).sum()
    neg_mf = mf.where(tp < tp.shift(1), 0).rolling(window=period).sum()
    return 100 - (100 / (1 + (pos_mf / neg_mf)))

# --- 2. ANALİZ MOTORU ---
def analyze_v38(ticker, portfolio):
    try:
        df_d = yf.download(ticker, period="6mo", interval="1d", progress=False)
        df_h = yf.download(ticker, period="1mo", interval="1h", progress=False)
        if df_d.empty or df_h.empty: return None
        
        c = df_d['Close']
        ma20 = c.rolling(window=20).mean().iloc[-1]
        rsi_h = calculate_rsi(df_h['Close']).iloc[-1]
        mfi_d = calculate_mfi(df_d).iloc[-1]
        
        # Basit Volatilite (ATR yerine)
        volatility = (df_d['High'] - df_d['Low']).rolling(window=14).mean().iloc[-1]
        
        score = 0
        if c.iloc[-1] > ma20: score += 40
        if mfi_d > 55: score += 30
        if rsi_h > 50: score += 30
        
        entry = c.iloc[-1]
        stop = entry - (volatility * 1.5)
        target = entry + (volatility * 3)
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
    except: return None

# --- 3. ARAYÜZ ---
st.set_page_config(page_title="Titan V38 Final", layout="wide")
st.title("🔱 Titan V38: Sovereign Terminal")

st.sidebar.header("⚙️ Ayarlar")
kasa = st.sidebar.number_input("Sanal Kasa (TL)", value=100000)
tg_token = st.sidebar.text_input("Telegram Token", type="password")
tg_id = st.sidebar.text_input("Telegram ID", type="password")

WATCHLIST = ["TUPRS.IS", "THYAO.IS", "BIMAS.IS", "AKSA.IS", "KONTR.IS", "ALTNY.IS", "ASELS.IS", "EREGL.IS"]

if st.button("Piyasayı Tara"):
    results = []
    with st.spinner("Borsa taranıyor..."):
        for t in WATCHLIST:
            res = analyze_v38(t, kasa)
            if res: results.append(res)
    
    if results:
        res_df = pd.DataFrame(results).sort_values("Skor", ascending=False)
        st.dataframe(res_df, use_container_width=True)
        
        if tg_token and tg_id:
            for _, row in res_df.iterrows():
                if row['Durum'] == "🔱 KRAL":
                    msg = f"🔱 *KRAL SİNYAL*\n#{row['Hisse']}\nFiyat: {row['Fiyat']}\nStop: {row['Stop']}\nHedef: {row['Hedef']}"
                    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={"chat_id": tg_id, "text": msg, "parse_mode": "Markdown"})

       

import streamlit as st
import pandas as pd
import requests
import ta
import time

def get_data_safe(ticker):
    try:
        # Yahoo Finance bazen 'Mozilla/5.0'ı sevmez, daha detaylı bir User-Agent ekledik
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=60d&interval=1d"
        
        # İstek gönderiliyor
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            # st.write(f"⚠️ {ticker} için hata kodu: {response.status_code}") # Hata ayıklama için açabilirsin
            return None
            
        data_json = response.json()
        
        # JSON yapısını kontrol et
        if 'chart' not in data_json or data_json['chart']['result'] is None:
            return None
            
        result = data_json['chart']['result'][0]
        indicators = result['indicators']['quote'][0]
        
        # Gerekli verilerin varlığını kontrol et
        if 'close' not in indicators or not indicators['close']:
            return None
            
        df = pd.DataFrame({
            'Close': indicators['close'],
            'Volume': indicators['volume'],
            'High': indicators['high'],
            'Low': indicators['low']
        }).dropna()

        if len(df) < 20: 
            return None

        # --- Teknik Analiz Bölümü ---
        close_series = df['Close']
        rsi = ta.momentum.rsi(close_series).iloc[-1]
        mfi = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume']).iloc[-1]
        
        vol_avg = df['Volume'].tail(11).head(10).mean()
        vol_spike = df['Volume'].iloc[-1] / vol_avg if vol_avg > 0 else 1
        
        score = ((100 - rsi) + mfi) / 2 + (min(vol_spike, 5) * 10)
        
        return {
            "Ticker": ticker,
            "Fiyat": round(df['Close'].iloc[-1], 2),
            "Hacim_Artışı": f"x{round(vol_spike, 2)}",
            "Sovereign_Skor": round(score, 2),
            "RSI": round(rsi, 1),
            "MFI": round(mfi, 1)
        }
    except Exception as e:
        # st.write(f"❌ {ticker} hatası: {str(e)}") # Hata ayıklama için açabilirsin
        return None

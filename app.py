import streamlit as st
import pandas as pd
import numpy as np
import requests  # <--- BURAYA EKLE
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import time
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# 🔥 230 BİST KATILIM LİSTESİ
MUHURLU_KATILIM_230 = [
    "ACSEL.IS", "AHSGY.IS", "AKFYE.IS", "AKHAN.IS", "AKSA.IS", "AKYHO.IS",
    "ALBRK.IS", "ALCTL.IS", "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ALTNY.IS",
    "ALVES.IS", "ANGEN.IS", "ARASE.IS", "ARDYZ.IS", "ARFYE.IS", "ASELS.IS",
    "ATAKP.IS", "ATATP.IS", "AVPGY.IS", "AYEN.IS", "BAHKM.IS", "BAKAB.IS",
    "BANVT.IS", "BASGZ.IS", "BEGYO.IS", "BERA.IS", "BESTE.IS", "BIENY.IS",
    "BIMAS.IS", "BINBN.IS", "BINHO.IS", "BMSTL.IS", "BNTAS.IS", "BORSK.IS",
    "BOSSA.IS", "BRISA.IS", "BRKSN.IS", "BRLSM.IS", "BSOKE.IS", "BURCE.IS",
    "BURVA.IS", "CANTE.IS", "CATES.IS", "CELHA.IS", "CEMTS.IS", "CEMZY.IS",
    "CIMSA.IS", "CMBTN.IS", "COSMO.IS", "CVKMD.IS", "CWENE.IS", "DAPGM.IS",
    "DARDL.IS", "DCTTR.IS", "DENGE.IS", "DESPC.IS", "DGATE.IS", "DGNMO.IS",
    "DMSAS.IS", "DOFER.IS", "DOFRB.IS", "DOGUB.IS", "DYOBY.IS", "EBEBK.IS",
    "EDATA.IS", "EDIP.IS", "EFOR.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS",
    "EKGYO.IS", "EKSUN.IS", "ELITE.IS", "EMPAE.IS", "ENJSA.IS", "EREGL.IS",
    "ESCOM.IS", "EUPWR.IS", "EYGYO.IS", "FADE.IS", "FONET.IS", "FORMT.IS",
    "FORTE.IS", "FRMPL.IS", "FZLGY.IS", "GEDZA.IS", "GENIL.IS", "GENTS.IS",
    "GEREL.IS", "GESAN.IS", "GLRMK.IS", "GOKNR.IS", "GOLTS.IS", "GOODY.IS",
    "GRSEL.IS", "GRTHO.IS", "GUBRF.IS", "GUNDG.IS", "HATSN.IS", "HKTM.IS",
    "HOROZ.IS", "HRKET.IS", "IDGYO.IS", "IHEVA.IS", "IHLAS.IS", "IHLGM.IS",
    "IHYAY.IS", "IMASM.IS", "INTEM.IS", "ISDMR.IS", "ISSEN.IS", "IZFAS.IS",
    "IZINV.IS", "JANTS.IS", "KARSN.IS", "KATMR.IS", "KBORU.IS", "KCAER.IS",
    "KIMMR.IS", "KLSYN.IS", "KNFRT.IS", "KOCMT.IS", "KONKA.IS", "KONTR.IS",
    "KONYA.IS", "KOPOL.IS", "KOTON.IS", "KRDMA.IS", "KRDMB.IS", "KRDMD.IS",
    "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRVGD.IS", "KTLEV.IS",
    "KUTPO.IS", "KUYAS.IS", "KZBGY.IS", "LKMNH.IS", "LMKDC.IS", "LOGO.IS",
    "MAGEN.IS", "MAKIM.IS", "MARBL.IS", "MAVI.IS", "MEDTR.IS", "MEKAG.IS",
    "MERCN.IS", "MEYSU.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS",
    "NETAS.IS", "NTGAZ.IS", "OBAMS.IS", "OBASE.IS", "OFSYM.IS", "ONCSM.IS",
    "ORGE.IS", "OSTIM.IS", "OZRDN.IS", "OZYSR.IS", "PAGYO.IS", "PARSN.IS",
    "PASEU.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PKART.IS",
    "PLTUR.IS", "PNLSN.IS", "POLHO.IS", "QUAGR.IS", "RGYAS.IS", "RNPOL.IS",
    "RODRG.IS", "RUBNS.IS", "SAFKR.IS", "SAMAT.IS", "SANEL.IS", "SANKO.IS",
    "SARKY.IS", "SAYAS.IS", "SEKUR.IS", "SELEC.IS", "SELVA.IS", "SILVR.IS",
    "SMART.IS", "SMRTG.IS", "SNGYO.IS", "SNICA.IS", "SOKE.IS", "SRVGY.IS",
    "SUNTK.IS", "SURGY.IS", "SUWEN.IS", "TARKM.IS", "TDGYO.IS", "TEZOL.IS",
    "TKNSA.IS", "TMSN.IS", "TNZTP.IS", "TUCLK.IS", "TUKAS.IS", "TUPRS.IS",
    "TUREX.IS", "UCAYM.IS", "ULAS.IS", "ULUSE.IS", "USAK.IS", "VAKKO.IS",
    "VANGD.IS", "VESBE.IS", "VRGYO.IS", "YATAS.IS", "YEOTK.IS", "YUNSA.IS",
    "ZEDUR.IS", "ZERGY.IS", "AGROT.IS", "ALFAS.IS", "ENERY.IS", "KMPUR.IS",
]

SEKTOR_MAP = {
    "XSIN": ["ASELS.IS", "EREGL.IS", "KONTR.IS", "CEMTS.IS", "KNFRT.IS", "GUBRF.IS"],
    "XELAS": ["TUPRS.IS", "ENJSA.IS", "AYEN.IS", "CWENE.IS", "ENERY.IS"],
    "XUMAL": ["BIMAS.IS", "KIMMR.IS", "KOTON.IS"],
    "XBANK": ["ALBRK.IS", "EBEBK.IS", "AKFGY.IS"],
    "XHOLD": ["KCHOL.IS", "SAHOL.IS"],
}

SEKTOR_PARAMS = {
    "XSIN": {"RSI_BAND": (32, 58), "RVOL_MULT": 1.4, "ATR_MULT": 2.2},
    "XELAS": {"RSI_BAND": (38, 52), "RVOL_MULT": 1.6, "ATR_MULT": 1.8},
    "XUMAL": {"RSI_BAND": (35, 55), "RVOL_MULT": 1.3, "ATR_MULT": 2.0},
    "XBANK": {"RSI_BAND": (40, 50), "RVOL_MULT": 1.8, "ATR_MULT": 1.5},
    "XHOLD": {"RSI_BAND": (33, 57), "RVOL_MULT": 1.5, "ATR_MULT": 2.1},
}

def robust_yf_download(
    tickers: List[str], period: str = "2y", interval: str = "1d",
    chunk_size: int = 20, wait_seconds: float = 15, max_retries: int = 5
) -> Dict[str, pd.DataFrame]:
    import requests
    session = requests.Session() # Session hatası burada çözüldü
    results = {}
    downloaded = 0

    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i : i + chunk_size]
        failed_tickers = []
        
        for attempt in range(max_retries):
            try:
                # ... indirme kodları ...
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    failed_tickers.extend(chunk)
                time.sleep(wait_seconds)

        # BU SATIRIN HİZASINA DİKKAT: 'for attempt' ile AYNI HİZADA OLMALI
        for t in chunk:
                    try:
                        if isinstance(raw.columns, pd.MultiIndex):
                            df = raw[t].dropna(how="all")
                        else:
                            df = raw.dropna(how="all")
                        
                        if not df.empty:
                            results[t] = df
                            downloaded += 1
                    except: # <--- Bu satır tam olarak 'try' ile aynı hizada olmalı
                        failed_tickers.append(t)
                        break  # Başarılıysa retry'dan çık
                    except Exception as e:
                        if attempt == max_retries - 1:
                            failed_tickers.extend(chunk)  # <-- Bu satır 'if'den tam 4 boşluk içeride olmalı
                        time.sleep(wait_seconds)         # <-- Bu satır 'if' ile aynı hizada olmalı
                
    st.sidebar.write(f"✅ Toplam {downloaded} hisse verisi işlendi.")
    return results

    for t in list(set(failed_tickers)):
            try:
                tkr = yf.Ticker(t, session=session)
                df = tkr.history(period=period, interval=interval, auto_adjust=True)
                if not df.empty:
                    results[t] = df
                    downloaded += 1
            except:
                continue
                
    st.write(f"BİST indirme bitti: {downloaded}/{len(tickers)}")
    return results

class Portfolio:
    def __init__(self, initial_cash: float = 1_000_000):
        self.cash = initial_cash
        self.positions = {}
        self.trades = []
        self.equity = []

    def add_trade(self, ticker: str, qty: int, price: float, side: str, timestamp):
        sign = 1 if side == "buy" else -1
        cost = sign * qty * price * 1.001
        self.cash -= cost

        if side == "buy":
            if ticker not in self.positions:
                self.positions[ticker] = {"qty": 0, "avg_price": 0.0}
            old_qty = self.positions[ticker]["qty"]
            old_avg = self.positions[ticker]["avg_price"]
            new_qty = old_qty + qty
            if new_qty > 0:
                self.positions[ticker] = {"qty": new_qty, "avg_price": (old_qty * old_avg + qty * price) / new_qty}
        else:
            if ticker in self.positions:
                if qty >= self.positions[ticker]["qty"]:
                    self.positions.pop(ticker, None)
                else:
                    self.positions[ticker]["qty"] -= qty

        self.trades.append({"ticker": ticker, "qty": qty, "price": price, "side": side, "timestamp": timestamp, "cost": cost})

    def update_equity(self, timestamp: Any, prices: pd.Series):
        long_value = sum(info["qty"] * prices.get(t, 0.0) for t, info in self.positions.items())
        self.equity.append({"date": timestamp, "value": self.cash + long_value})

class TitanV49Pro:
    def __init__(self):
        self.risk_rules = {
            "MAX_PORTFOLIO_RISK": 0.10,
            "MAX_POSITION_RISK": 0.02,
            "MAX_SECTOR_RISK": 0.03,
            "MAX_POSITIONS": 12,
            "CORRELATION_LIMIT": 0.7,
            "DRAWDOWN_LIMIT": -0.08,
            "COMMISSION": 0.001,
        }
        self.portfolio = Portfolio()

    def calculate_rsi(self, series: pd.Series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, 1e-6)
        return 100 - (100 / (1 + rs))

    def calculate_atr(self, df: pd.DataFrame, period=14):
        tr = pd.concat([
            df["High"] - df["Low"],
            (df["High"] - df["Close"].shift()).abs(),
            (df["Low"] - df["Close"].shift()).abs()
        ], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]

    def order_flow_analysis(self, df: pd.DataFrame) -> Dict:
        window = 14
        vwap = ((df["Close"] * df["Volume"]).rolling(window).sum() / df["Volume"].rolling(window).sum()).shift(1)
        net_delta = pd.Series(np.where(df["Close"] > vwap, df["Volume"], -df["Volume"])).tail(10).sum()
        body_size = (df["Close"] - df["Open"]).abs().rolling(5).mean()
        absorption = (df["Volume"].rolling(5).mean() / (body_size * 1000 + 1e-6)).iloc[-1]
        vol_trend = df["Volume"].tail(10).mean() / max(df["Volume"].tail(20).mean(), 1e-6)
        vol_div = vol_trend > 1.2 and (df["Close"].iloc[-1] > df["Close"].iloc[-10])
        
        score = 30 if vol_div and absorption > 1.5 else 15
        return {"net_delta": net_delta, "absorption": absorption > 1.5, "volume_divergence": vol_div, "order_flow_score": score, "signal": "🟢 BULLISH" if net_delta > 0 else "🔴 BEARISH"}

    def sector_optimized_scoring(self, df: pd.DataFrame, ticker: str) -> Dict:
        sektor = next((k for k, v in SEKTOR_MAP.items() if ticker in v), "XSIN")
        params = SEKTOR_PARAMS.get(sektor, SEKTOR_PARAMS["XSIN"])
        rsi_series = self.calculate_rsi(df["Close"])
        rsi_l = rsi_series.iloc[-1]
        of = self.order_flow_analysis(df)
        
        al_score = 0
        if params["RSI_BAND"][0] <= rsi_l <= params["RSI_BAND"][1]: al_score += 25
        al_score += of["order_flow_score"]
        if of["net_delta"] > 0: al_score += 15
        if of["volume_divergence"] and of["absorption"]: al_score += 15

        return {"sektor": sektor, "rsi": rsi_l, "al_score": al_score, "order_flow": of["signal"], "atr": self.calculate_atr(df), "price": df["Close"].iloc[-1]}
# ============================ STREAMLIT ARAYÜZÜ (MARŞA BASAN KISIM) =========================

# --- BURADAN İTİBAREN KODUN EN SONUNA YAPIŞTIRIN (EN SOLA YASLI) ---
def run_app():
    st.set_page_config(layout="wide", page_title="Titan V49 Pro")
    st.title("🔱 Titan V49 Pro: Sektörel Tarama")
    
    titan = TitanV49Pro()
    
    if st.sidebar.button("🚀 230 HİSSEYİ TARAMAYA BAŞLAT"):
        with st.spinner("Veriler çekiliyor..."):
            all_data = robust_yf_download(MUHURLU_KATILIM_230)
            
        if all_data:
            results = []
            p_bar = st.progress(0)
            for idx, (ticker, df) in enumerate(all_data.items()):
                try:
                    res = titan.sector_optimized_scoring(df, ticker)
                    res["Ticker"] = ticker
                    results.append(res)
                except:
                    continue
                p_bar.progress((idx + 1) / len(all_data))
            
            if results:
                st.subheader("📊 Analiz Sonuçları")
                st.dataframe(pd.DataFrame(results).sort_values("al_score", ascending=False), use_container_width=True)
            else:
                st.warning("Uygun sonuç bulunamadı.")

if __name__ == "__main__":
    run_app()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import time
from typing import Dict, List, Tuple, Any  # Any’i import edin
import warnings

warnings.filterwarnings('ignore')

# 🔥 230 BİST KATILIM LİSTESİ (senin XKTUM 230 listesini buraya koy,
# şu an ilk 60–70 örnek; 230’den 200’lü bileşenlere genişlet)
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

# SEKTÖREL HARİTA (XKTUM’da ki bileşenleri ile senin güncel listene göre)
SEKTOR_MAP = {
    "XSIN": ["ASELS.IS", "EREGL.IS", "KONTR.IS", "CEMTS.IS", "KNFRT.IS", "GUBRF.IS"],
    "XELAS": ["TUPRS.IS", "ENJSA.IS", "AYEN.IS", "CWENE.IS", "ENERY.IS"],
    "XUMAL": ["BIMAS.IS", "KIMMR.IS", "KOTON.IS"],
    "XBANK": ["ALBRK.IS", "EBEBK.IS", "AKFGY.IS"],
    "XHOLD": ["KCHOL.IS", "SAHOL.IS"],
}

# SEKTÖREL PARAMETRELER (ileride grid search ile kalibre edilebilir)
SEKTOR_PARAMS = {
    "XSIN": {"RSI_BAND": (32, 58), "RVOL_MULT": 1.4, "ATR_MULT": 2.2},
    "XELAS": {"RSI_BAND": (38, 52), "RVOL_MULT": 1.6, "ATR_MULT": 1.8},
    "XUMAL": {"RSI_BAND": (35, 55), "RVOL_MULT": 1.3, "ATR_MULT": 2.0},
    "XBANK": {"RSI_BAND": (40, 50), "RVOL_MULT": 1.8, "ATR_MULT": 1.5},
    "XHOLD": {"RSI_BAND": (33, 57), "RVOL_MULT": 1.5, "ATR_MULT": 2.1},
}

# ============================ YFINANCE RATE LIMITLI BATCH DOWNLOAD (GENEL EXCEPT) =========================

def robust_yf_download(
    tickers: List[str], period: str = "2y", interval: str = "1d",
    chunk_size: int = 20, wait_seconds: float = 15, max_retries: int = 5
) -> Dict[str, pd.DataFrame]:
    session = yf.session.Session()
    results = {}

    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i : i + chunk_size]
        downloaded = 0

        for attempt in range(max_retries):
            failed_tickers = []
            try:
                raw = yf.download(
                    tickers=chunk,
                    period=period,
                    interval=interval,
                    group_by="ticker",
                    threads=True,
                    auto_adjust=True,
                    session=session,
                    progress=False,
                )
                cols = ["Open", "High", "Low", "Close", "Volume"]
                # Yahoo çoklu ticker formatı: MultiIndex
                for t in chunk:
                    if isinstance(raw.columns, pd.MultiIndex):
                        df = raw[t].dropna(how="all")
                    else:
                        df = raw[[t]].dropna(how="all")
                        if 0 < len(df.columns) < 2:
                            df = df.rename(columns={df.columns[0]: t})
                    df = df.iloc[:, :5] if 5 <= len(df.columns) else df
                    df = df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
                    results[t] = df
                    downloaded += 1
                break  # başarılıysa retry’i kır

            except Exception as e:
                st.write(f"Chunk için indirme hatası: {e}")
                time.sleep(wait_seconds)
                failed_tickers.extend(chunk)
                continue

        # Hata almış ticker’ları bireysel deneme (Ticker bazında)
        for t in failed_tickers:
            for _ in range(2):
                try:
                    tkr = yf.Ticker(t, session=session)
                    df = tkr.history(period=period, interval=interval, auto_adjust=True)
                    df = df.dropna(how="all")
                    df = df[["Open", "High", "Low", "Close", "Volume"]]
                    results[t] = df
                    downloaded += 1
                    break
                except Exception as e:
                    st.write(f"Ticker için indirme hatası: {t} → {e}")
                    time.sleep(2)
    st.write(f"230 BİST indirme bitti: {downloaded}/{len(tickers)}")
    return results

# ============================= PORTFÖY VE BACKTEST ENGINE ===============================
class Portfolio:
    def __init__(self, initial_cash: float = 1_000_000):
        self.cash = initial_cash
        self.positions = {}  # ticker: {"qty": int, "avg_price": float}
        self.trades = []
        self.equity = []     # [{"date", "value", "drawdown"}]

    def add_trade(self, ticker: str, qty: int, price: float, side: str, timestamp):
        if side == "buy":
            sign = 1
        elif side == "sell":
            sign = -1
        else:
            return

        cost = sign * qty * price * 1.001  # 0.1% komisyon
        self.cash -= cost

        if side == "buy":
            if ticker not in self.positions:
                self.positions[ticker] = {"qty": 0, "avg_price": 0.0}
            old_qty = self.positions[ticker]["qty"]
            old_avg = self.positions[ticker]["avg_price"]
            new_qty = old_qty + qty
            if new_qty == 0:
                self.positions.pop(ticker, None)
            else:
                new_avg = (old_qty * old_avg + qty * price) / new_qty
                self.positions[ticker] = {"qty": new_qty, "avg_price": new_avg}
        else:
            if ticker in self.positions:
                if qty >= self.positions[ticker]["qty"]:
                    qty = self.positions[ticker]["qty"]
                    self.positions.pop(ticker, None)
                else:
                    self.positions[ticker]["qty"] -= qty

        self.trades.append({
            "ticker": ticker,
            "qty": qty,
            "price": price,
            "side": side,
            "timestamp": timestamp,
            "cost": cost,
        })

    def update_equity(self, timestamp: Any, prices: pd.Series):
        long_value = 0.0
        for t, info in self.positions.items():
            qty = info["qty"]
            price = prices.get(t, 0.0)
            long_value += qty * price
        equity = self.cash + long_value
        self.equity.append({"date": timestamp, "value": equity})

# =============================== TİTAN V49 PRO FONKSİYONLAR ============================
class TitanV49Pro:
    def __init__(self):
        self.risk_rules = self.init_risk_rules()
        self.portfolio = Portfolio()

    def init_risk_rules(self):
        return {
            "MAX_PORTFOLIO_RISK": 0.10,
            "MAX_POSITION_RISK": 0.02,
            "MAX_SECTOR_RISK": 0.03,
            "MAX_POSITIONS": 12,
            "CORRELATION_LIMIT": 0.7,
            "DRAWDOWN_LIMIT": -0.08,
            "COMMISSION": 0.001,
        }

    def order_flow_analysis(self, df: pd.DataFrame) -> Dict:
        window = 14
        # Rolling VWAP (14 gün)
        rolling_vwap = (
            (df["Close"] * df["Volume"]).rolling(window=window).sum() /
            df["Volume"].rolling(window=window).sum()
        )
        vwap = rolling_vwap.shift(1)
        # Delta (sadece son 10 bar)
        vwap_delta = np.where(df["Close"] > vwap, df["Volume"], -df["Volume"])
        net_delta = pd.Series(vwap_delta).tail(10).sum()

        # Absorption: 5 bar
        body_size = (df["Close"] - df["Open"]).abs().rolling(5).mean()
        avg_volume = df["Volume"].rolling(5).mean()
        absorption_ratio = avg_volume / (body_size * 1000 + 1e-6)

        # Volume divergence: 10 bar vs 20 bar
        price_trend = (df["Close"].iloc[-1] / df["Close"].iloc[-10] - 1)
        vol_trend = df["Volume"].tail(10).mean() / max(df["Volume"].tail(20).mean(), 1e-6)
        vol_divergence = vol_trend > 1.2 and price_trend > 0

        # Order flow score
        base_score = 15
        if vol_divergence and absorption_ratio.iloc[-1] > 1.5:
            base_score = 30

        return {
            "net_delta": net_delta,
            "absorption": absorption_ratio.iloc[-1] > 1.5,
            "volume_divergence": vol_divergence,
            "order_flow_score": base_score,
            "signal": "🟢 BULLISH" if net_delta > 0 else "🔴 BEARISH",
        }

    def calculate_rsi(self, series: pd.Series, period=14):
        delta = series.diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(period).mean()
        avg_loss = pd.Series(loss).rolling(period).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-6)
        return 100 - 100 / (1 + rs)

    def calculate_atr(self, df: pd.DataFrame, period=14):
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - df["Close"].shift()).abs()
        tr3 = (df["Low"] - df["Close"].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]

    def sector_optimized_scoring(self, df: pd.DataFrame, ticker: str) -> Dict:
        sektor = next((k for k, v in SEKTOR_MAP.items() if ticker in v), "XSIN")
        params = SEKTOR_PARAMS.get(sektor, SEKTOR_PARAMS["XSIN"])
        rsi_band = params["RSI_BAND"]
        rsi_data = self

    def calculate_atr(self, df: pd.DataFrame, period=14):
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - df["Close"].shift()).abs()
        tr3 = (df["Low"] - df["Close"].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]

    def sector_optimized_scoring(self, df: pd.DataFrame, ticker: str) -> Dict:
        sektor = next((k for k, v in SEKTOR_MAP.items() if ticker in v), "XSIN")
        params = SEKTOR_PARAMS.get(sektor, SEKTOR_PARAMS["XSIN"])
        rsi_band = params["RSI_BAND"]
        rsi = self.calculate_rsi(df["Close"])
        rsi_l = rsi.iloc[-1]

        of = self.order_flow_analysis(df)
        atr = self.calculate_atr(df)
        price = df["Close"].iloc[-1]

        al_score = 0
        if rsi_band[0] <= rsi_l <= rsi_band[1]:
            al_score += 25
        al_score += of["order_flow_score"]
        if of["net_delta"] > 0:
            al_score += 15
        if of["volume_divergence"] and of["absorption"]:
            al_score += 15

        return {
            "sektor": sektor,
            "rsi": rsi_l,
            "al_score": al_score,
            "order_flow": of["signal"],
            "atr": atr,
            "price": price,
            }
            

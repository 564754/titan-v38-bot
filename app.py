import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import requests

# --- 1. MANUEL İNDİKATÖR MOTORU ---
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

# --- 2. ANA ARAYÜZ VE SİDEBAR ---
st.set_page_config(page_title="Titan V38 Sovereign", layout="wide")
st.title("🔱 Titan V38: Sovereign Terminal")

# TELEGRAM KUTUCUKLARI BURADA OLMALI
st.sidebar.header("⚙️ Operasyon Merkezi")
kasa = st.sidebar.number_input("Sanal Portföy (TL)", value=100000, step=1000)

st.sidebar.subheader("📱 Telegram Bağlantısı")
tg_token = st.sidebar.text_input("Telegram Token", type="password", help="BotFather'dan aldığınız kod")
tg_id = st.sidebar.text_input("Telegram ID", type="password", help="UserinfoBot'tan aldığınız ID")

# --- 3. WATCHLIST ---
WATCHLIST = [
    "ACSEL.IS", "AHSGY.IS", "AKFYE.IS", "AKHAN.IS", "AKSA.IS", "AKYHO.IS", "ALBRK.IS", "ALCTL.IS", "ALKA.IS", "ALKIM.IS",
    "ALKLC.IS", "ALTNY.IS", "ALVES.IS", "ANGEN.IS", "ARASE.IS", "ARDYZ.IS", "ARFYE.IS", "ASELS.IS", "ATAKP.IS", "ATATP.IS",
    "AVPGY.IS", "AYEN.IS", "BAHKM.IS", "BAKAB.IS", "BANVT.IS", "BASGZ.IS", "BEGYO.IS", "BERA.IS", "BIENY.IS", "BIMAS.IS",
    "BINBN.IS", "BINHO.IS", "BMSTL.IS", "BNTAS.IS", "BORSK.IS", "BOSSA.IS", "BRISA.IS", "BRKSN.IS", "BRLSM.IS", "BSOKE.IS",
    "BURCE.IS", "BURVA.IS", "CANTE.IS", "CATES.IS", "CEMTS.IS", "CEMZY.IS", "CIMSA.IS", "CMBTN.IS", "CVKMD.IS", "CWENE.IS",
    "DAPGM.IS", "DARDL.IS", "DCTTR.IS", "DENGE.IS", "DESPC.IS", "DGATE.IS", "DGNMO.IS", "DMSAS.IS", "DOFER.IS", "DOFRB.IS",
    "DOGUB.IS", "DYOBY.IS", "EBEBK.IS", "EDATA.IS", "EDIP.IS", "EFOR.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EKGYO.IS",
    "EKSUN.IS", "ELITE.IS", "ENJSA.IS", "EREGL.IS", "ESCOM.IS", "EUPWR.IS", "EYGYO.IS", "FONET.IS", "FORMT.IS", "FORTE.IS",
    "FRMPL.IS", "FZLGY.IS", "GEDZA.IS", "GENIL.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS", "GLRMK.IS", "GOKNR.IS", "GOLTS.IS",
    "GOODY.IS", "GRSEL.IS", "GRTHO.IS", "GUBRF.IS", "GUNDG.IS", "HATSN.IS", "HKTM.IS", "HOROZ.IS", "HRKET.IS", "IDGYO.IS",
    "IHEVA.IS", "IHLAS.IS", "IHLGM.IS", "IHYAY.IS", "INTEM.IS", "ISDMR.IS", "ISSEN.IS", "IZFAS.IS", "IZINV.IS", "JANTS.IS",
    "KARSN.IS", "KATMR.IS", "KBORU.IS", "KCAER.IS", "KIMMR.IS", "KLSYN.IS", "KNFRT.IS", "KOCMT.IS", "KONKA.IS", "KONTR.IS",
    "KONYA.IS", "KOPOL.IS", "KOTON.IS", "KRDMA.IS", "KRDMB.IS", "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS",
    "KRVGD.IS", "KTLEV.IS", "KUTPO.IS", "KUYAS.IS", "KZBGY.IS", "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "MAGEN.IS", "MAKIM.IS",
    "MARBL.IS", "MAVI.IS", "MEDTR.IS", "MEKAG.IS", "MERCN.IS", "MEYSU.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS",
    "NETAS.IS", "NTGAZ.IS", "OBAMS.IS", "OBASE.IS", "OFSYM.IS", "ONCSM.IS", "ORGE.IS", "OSTIM.IS", "OZRDN.IS", "OZYSR.IS",
    "PAGYO.IS", "PARSN.IS", "PASEU.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PKART.IS", "PLTUR.IS", "PNLSN.IS", "POLHO.IS",
    "QUAGR.IS", "RGYAS.IS", "RODRG.IS", "RUBNS.IS", "SAFKR.IS", "SAMAT.IS", "SANEL.IS", "SANKO.IS", "SARKY.IS", "SAYAS.IS",
    "SEKUR.IS", "SELEC.IS", "SELVA.IS", "SILVR.IS", "SMART.IS", "SMRTG.IS", "SNGYO.IS", "SNICA.IS", "SOKE.IS", "SRVGY.IS",
    "SUNTK.IS", "SURGY.IS", "SUWEN.IS", "TARKM.IS", "TDGYO.IS", "TEZOL.IS", "TKNSA.IS", "TMSN.IS", "TNZTP.IS", "TUCLK.IS",
    "TUKAS.IS", "TUPRS.IS", "TUREX.IS", "UCAYM.IS", "ULAS.IS", "ULUSE.IS", "USAK.IS", "VAKKO.IS", "VANGD.IS", "VESBE.IS",
    "VRGYO.IS", "YATAS.IS", "YEOTK.IS", "YUNSA.IS", "ZEDUR.IS", "ZERGY.IS", "AGROT.IS", "ALFAS.IS", "ENERY.IS", "KMPUR.IS"
]

# --- 4. ÇALIŞTIRMA VE ANALİZ ---
if st.button("🚀 Piyasayı Tara ve Sinyal Gönder"):
    with st.spinner("Toplu veri analiz ediliyor..."):
        try:
            data_d = yf.download(WATCHLIST, period="6mo", interval="1d", group_by='ticker', progress=False, auto_adjust=True)
            data_h = yf.download(WATCHLIST, period="1mo", interval="1h", group_by='ticker', progress=False, auto_adjust=True)
            
            results = []
            kral_sinyaller = []
            
            for ticker in WATCHLIST:
                try:
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
                    risk_per_share = entry - stop
                    lot = int((kasa * 0.01) / risk_per_share) if risk_per_share > 0 else 0
                    
                    res = {
                        "Hisse": ticker.replace(".IS",""),
                        "Skor": int(score),
                        "Fiyat": round(entry, 2),
                        "Stop": round(stop, 2),
                        "Lot": lot,
                        "Durum": "🔱 KRAL" if score >= 85 else "🚀 AL" if score >= 65 else "⌛ İZLE"
                    }
                    results.append(res)
                    if res["Durum"] == "🔱 KRAL":
                        kral_sinyaller.append(res)
                except: continue
            
            if results:
                res_df = pd.DataFrame(results).sort_values("Skor", ascending=False)
                st.dataframe(res_df, use_container_width=True)
                
                # TELEGRAM GÖNDERİMİ
                if tg_token and tg_id and kral_sinyaller:
                    st.info(f"📱 {len(kral_sinyaller)} adet KRAL sinyali Telegram'a gönderiliyor...")
                    for s in kral_sinyaller:
                        msg = f"🔱 *KRAL SİNYAL*\n#{s['Hisse']}\nFiyat: {s['Fiyat']}\nStop: {s['Stop']}\nLot: {s['Lot']}"
                        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={"chat_id": tg_id, "text": msg, "parse_mode": "Markdown"})
                    st.success("✅ Telegram mesajları başarıyla gönderildi!")
            else:
                st.warning("Veri çekilemedi.")
                
        except Exception as e:
            st.error(f"Hata: {e}")

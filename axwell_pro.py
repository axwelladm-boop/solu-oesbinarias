import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuração Visual Axwell
st.set_page_config(page_title="AXWELL SNIPER v4.0", layout="wide")

st.markdown("<h1 style='text-align: center; color: #00ffcc;'>AXWELL SOLUÇÕES BINÁRIAS</h1>", unsafe_allow_html=True)

# Gestão de Banca
if 'banca' not in st.session_state: st.session_state.banca = 70.0

st.sidebar.title("🛡️ Gestão de Risco")
st.sidebar.metric("Saldo Real", f"${st.session_state.banca:.2f}")
val_entrada = st.sidebar.number_input("Entrada ($)", 1.0, 10.0, 2.0)

# Seleção de Ativos
ativos = st.multiselect("Ativos Sniper", ["EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD"], default=["EURUSD=X", "BTC-USD"])

placeholder = st.empty()

while True:
    with placeholder.container():
        cols = st.columns(len(ativos) if ativos else 1)
        for i, ativo in enumerate(ativos):
            # Coleta de dados rápida
            df = yf.download(ativo, period="1d", interval="1m", progress=False)
            if not df.empty:
                df['RSI'] = ta.rsi(df['Close'], length=14)
                last_rsi = df['RSI'].iloc[-1]
                last_price = df['Close'].iloc[-1]
                
                with cols[i]:
                    st.metric(f"🏷️ {ativo}", f"{last_price:.4f}")
                    # Lógica Sniper de 90%
                    if last_rsi < 22:
                        st.success("🎯 COMPRA (CALL)")
                        st.write("Expiração: 2-3 min")
                    elif last_rsi > 78:
                        st.error("🎯 VENDA (PUT)")
                        st.write("Expiração: 2-3 min")
                    else:
                        st.info("🔎 Analisando...")
        
        time.sleep(10)

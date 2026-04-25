import os
import subprocess
import sys

# FUNÇÃO PARA FORÇAR INSTALAÇÃO (Resolve o erro ModuleNotFoundError)
def install_package(package):
    try:
        _import(package.replace("-", ""))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Instala as ferramentas antes de começar
install_package("pandas-ta")
install_package("yfinance")
install_package("plotly")

import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import time

# --- O RESTO DO CÓDIGO AXWELL SNIPER v4.0 CONTINUA ABAIXO ---
st.set_page_config(page_title="AXWELL PRO v4.0", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #080b14; }
    h1 { color: #00ffcc; text-align: center; border-bottom: 2px solid #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

if 'banca' not in st.session_state: st.session_state.banca = 70.0
if 'trades' not in st.session_state: 
    st.session_state.trades = pd.DataFrame(columns=['Hora', 'Ativo', 'Tipo', 'Result', 'Lucro', 'Saldo'])

st.markdown("<h1>AXWELL SNIPER v4.0</h1>", unsafe_allow_html=True)

# SIDEBAR GESTÃO
st.sidebar.title("🛡️ Gestão Axwell")
st.sidebar.metric("Banca Atual", f"${st.session_state.banca:.2f}")
val_entrada = st.sidebar.number_input("Entrada ($)", 1.0, 50.0, 2.0)
payout = st.sidebar.slider("Payout %", 70, 95, 89)

# MONITOR SNIPER
ativos = st.multiselect("Ativos Sniper", ["EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD"], default=["EURUSD=X", "BTC-USD"])
placeholder = st.empty()

while True:
    with placeholder.container():
        cols = st.columns(len(ativos) if ativos else 1)
        for i, ativo in enumerate(ativos):
            df = yf.download(ativo, period="1d", interval="1m", progress=False)
            if not df.empty:
                df['RSI'] = ta.rsi(df['Close'], length=14)
                last_rsi = df['RSI'].iloc[-1]
                last_price = df['Close'].iloc[-1]
                
                with cols[i]:
                    st.metric(f"{ativo}", f"{last_price:.4f}")
                    if last_rsi < 22: st.success("🎯 COMPRA (CALL)")
                    elif last_rsi > 78: st.error("🎯 VENDA (PUT)")
                    else: st.info("Aguardando...")
        time.sleep(10)

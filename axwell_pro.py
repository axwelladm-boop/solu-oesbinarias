import subprocess
import sys
import os

# --- BLOCO DE INSTALAÇÃO FORÇADA (NÃO APAGUE) ---
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import pandas_ta as ta
except ImportError:
    install('pandas-ta')
    import pandas_ta as ta

try:
    import yfinance as yf
except ImportError:
    install('yfinance')
    import yfinance as yf

try:
    import plotly.graph_objects as go
except ImportError:
    install('plotly')
    import plotly.graph_objects as go

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURAÇÃO AXWELL PRO v4.0 ---
st.set_page_config(page_title="AXWELL PRO v4.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #080b14; }
    h1 { color: #00ffcc; text-align: center; font-family: 'Courier New'; border-bottom: 2px solid #00ffcc; }
    .stMetric { background-color: #0d1520; border: 1px solid #00ffcc; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'banca' not in st.session_state: st.session_state.banca = 70.0
if 'trades' not in st.session_state: 
    st.session_state.trades = pd.DataFrame(columns=['Hora', 'Ativo', 'Result', 'Lucro', 'Saldo'])

st.markdown("<h1>AXWELL SOLUÇÕES BINÁRIAS</h1>", unsafe_allow_html=True)
st.sidebar.title("🛡️ Gestão Sniper")
st.sidebar.metric("Saldo Real", f"${st.session_state.banca:.2f}")

# MONITOR REAL-TIME
ativos = st.multiselect("Ativos sniper", ["EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD"], default=["EURUSD=X", "BTC-USD"])
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
                    st.metric(f"🏷️ {ativo}", f"{last_price:.4f}", f"RSI: {last_rsi:.1f}")
                    if last_rsi < 22:
                        st.success("🎯 COMPRA (CALL)")
                    elif last_rsi > 78:
                        st.error("🎯 VENDA (PUT)")
                    else:
                        st.info("Aguardando...")
        
        # Histórico Simples
        if not st.session_state.trades.empty:
            st.divider()
            st.subheader("📈 Minha Rentabilidade")
            st.line_chart(st.session_state.trades['Saldo'])
            
        time.sleep(10)

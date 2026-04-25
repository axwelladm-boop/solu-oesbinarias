import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import time

# Configurações de Elite Axwell
st.set_page_config(page_title="AXWELL PRO v4.0", layout="wide")

# Inicialização de Variáveis de Gestão
if 'banca' not in st.session_state: st.session_state.banca = 70.0
if 'trades' not in st.session_state: 
    st.session_state.trades = pd.DataFrame(columns=['Hora', 'Ativo', 'Tipo', 'Result', 'Lucro', 'Saldo'])

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #080b14; }
    .metric-card { background-color: #0d1520; border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; text-align: center; }
    h1 { color: #00ffcc; font-family: 'Monospace'; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>AXWELL SNIPER v4.0</h1>", unsafe_allow_html=True)

# --- SIDEBAR: GESTÃO DE RISCO (CRITÉRIO DE KELLY) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2533/2533515.png", width=100)
st.sidebar.title("🛡️ Gestão Axwell")
st.sidebar.metric("Banca Atual", f"${st.session_state.banca:.2f}")

# Sugestão Kelly Criterion (Para banca de $70, sugere entradas seguras)
sugestao_kelly = st.session_state.banca * 0.03 
st.sidebar.info(f"Sugestão Sniper: ${sugestao_kelly:.2f} (3% da banca)")

val_entrada = st.sidebar.number_input("Entrada ($)", 1.0, 50.0, 2.0)
payout = st.sidebar.slider("Payout %", 70, 95, 89)

# Registro de Trades
st.sidebar.subheader("Lançar Ordem")
col1, col2 = st.sidebar.columns(2)
if col1.button("🎯 WIN"):
    lucro = val_entrada * (payout/100)
    st.session_state.banca += lucro
    new_data = pd.DataFrame([{'Hora': datetime.now().strftime("%H:%M"), 'Ativo': "Análise", 'Tipo': "CALL", 'Result': "WIN", 'Lucro': lucro, 'Saldo': st.session_state.banca}])
    st.session_state.trades = pd.concat([st.session_state.trades, new_data], ignore_index=True)
if col2.button("💀 LOSS"):
    st.session_state.banca -= val_entrada
    new_data = pd.DataFrame([{'Hora': datetime.now().strftime("%H:%M"), 'Ativo': "Análise", 'Tipo': "PUT", 'Result': "LOSS", 'Lucro': -val_entrada, 'Saldo': st.session_state.banca}])
    st.session_state.trades = pd.concat([st.session_state.trades, new_data], ignore_index=True)

# --- MONITOR MULTI-INDICADORES ---
ativos = st.multiselect("Ativos Sniper", ["EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD", "ADA-USD"], default=["EURUSD=X", "BTC-USD"])

placeholder = st.empty()

while True:
    with placeholder.container():
        c_ativos = st.columns(len(ativos) if ativos else 1)
        
        for i, ativo in enumerate(ativos):
            df = yf.download(ativo, period="1d", interval="1m", progress=False)
            if not df.empty:
                # Calculando Indicadores do README v4.0
                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['MACD'], df['MACDs'], df['MACDh'] = ta.macd(df['Close']).iloc[:,0], ta.macd(df['Close']).iloc[:,1], ta.macd(df['Close']).iloc[:,2]
                bb = ta.bbands(df['Close'], length=20, std=2)
                df['BBU'] = bb.iloc[:, 2] # Upper Band
                df['BBL'] = bb.iloc[:, 0] # Lower Band
                
                last_close = df['Close'].iloc[-1]
                last_rsi = df['RSI'].iloc[-1]
                
                # SCORE DE CONFLUÊNCIA AXWELL (0-100)
                score = 50
                if last_rsi < 30: score += 15
                if last_rsi > 70: score -= 15
                if last_close < df['BBL'].iloc[-1]: score += 20
                if last_close > df['BBU'].iloc[-1]: score -= 20
                if df['MACDh'].iloc[-1] > 0: score += 15
                else: score -= 15
                
                with c_ativos[i]:
                    st.markdown(f"<div class='metric-card'><b>{ativo}</b><br><span style='font-size:20px;'>{last_close:.4f}</span><br>Score: {score}%</div>", unsafe_allow_html=True)
                    
                    if score >= 85:
                        st.success("🔥 CALL CONFIRMADO")
                        st.toast(f"ALERTA SNIPER: {ativo} em COMPRA!", icon="🚀")
                    elif score <= 15:
                        st.error("❄️ PUT CONFIRMADO")
                        st.toast(f"ALERTA SNIPER: {ativo} em VENDA!", icon="⚠️")
        
        # Gráfico de Rentabilidade Real Axwell
        if not st.session_state.trades.empty:
            st.divider()
            st.subheader("📈 Curva de Patrimônio Axwell")
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=st.session_state.trades['Saldo'], mode='lines+markers', line=dict(color='#00ffcc', width=3), fill='tozeroy'))
            fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(st.session_state.trades.tail(5), use_container_width=True)

        time.sleep(10)

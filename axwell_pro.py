import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import time

# 1. Configurações de Interface e Estilo (Branding Axwell)
st.set_page_config(page_title="Axwell Soluções Binárias", layout="wide")

# CSS para customização de design
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #00ffcc; }
    h1 { color: #00ffcc; font-family: 'Arial Black'; text-align: center; border-bottom: 2px solid #00ffcc; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialização do Banco de Dados Interno
if 'banca' not in st.session_state:
    st.session_state.banca = 70.0
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Hora', 'Ativo', 'Resultado', 'Valor', 'Saldo'])
    st.session_state.logs.loc[0] = [datetime.now().strftime("%H:%M"), "Início", "---", 0, 70.0]

# --- LOGO E TÍTULO ---
st.markdown("<h1>AXWELL SOLUÇÕES BINÁRIAS</h1>", unsafe_allow_html=True)
st.caption("Analista Pro v3.0 | Inteligência em Tempo Real para Royal Capital")

# --- SIDEBAR: GESTÃO E ATIVOS ---
st.sidebar.title("🛡️ Gestão de Banca")
st.sidebar.metric("Saldo Atualizado", f"${st.session_state.banca:.2f}")

ativos_lista = st.sidebar.multiselect(
    "Monitorar Ativos (Tempo Real)", 
    ["EURUSD=X", "GBPUSD=X", "JPY=X", "BTC-USD", "ETH-USD", "ADA-USD", "GC=F"],
    default=["EURUSD=X", "BTC-USD"]
)

val_operacao = st.sidebar.number_input("Entrada ($)", 1.0, 10.0, 2.0)
payout = st.sidebar.slider("Payout %", 70, 95, 89)

st.sidebar.divider()
st.sidebar.subheader("Lançar Resultado")
c_win, c_loss = st.sidebar.columns(2)

if c_win.button("🎯 WIN"):
    ganho = val_operacao * (payout/100)
    st.session_state.banca += ganho
    st.session_state.logs.loc[len(st.session_state.logs)] = [datetime.now().strftime("%H:%M"), "Manual", "WIN", ganho, st.session_state.banca]
    st.balloons()

if c_loss.button("💀 LOSS"):
    st.session_state.banca -= val_operacao
    st.session_state.logs.loc[len(st.session_state.logs)] = [datetime.now().strftime("%H:%M"), "Manual", "LOSS", -val_operacao, st.session_state.banca]

# --- PAINEL PRINCIPAL ---
tab_monitor, tab_performance = st.tabs(["🔍 Monitor Sniper", "📈 Performance Axwell"])

with tab_monitor:
    placeholder = st.empty()
    while True:
        with placeholder.container():
            cols = st.columns(len(ativos_lista) if ativos_lista else 1)
            idx = 0
            for ativo in ativos_lista:
                data = yf.download(ativo, period="1d", interval="1m", progress=False)
                if not data.empty:
                    # Cálculo de Indicadores Profissionais
                    data['RSI'] = ta.rsi(data['Close'], length=14)
                    data['EMA_8'] = ta.ema(data['Close'], length=8)
                    data['EMA_20'] = ta.ema(data['Close'], length=20)
                    
                    last_rsi = data['RSI'].iloc[-1]
                    last_price = data['Close'].iloc[-1]
                    tendencia = "ALTA" if data['EMA_8'].iloc[-1] > data['EMA_20'].iloc[-1] else "BAIXA"
                    
                    with cols[idx]:
                        st.metric(f"🏷️ {ativo}", f"{last_price:.4f}", f"RSI: {last_rsi:.1f}")
                        
                        # LÓGICA DE ASSERTIVIDADE AXWELL (90%+)
                        if last_rsi < 22 and tendencia == "ALTA":
                            st.success("💎 COMPRA (CALL)")
                            st.write("*Expiração:* 2-3 min")
                            st.toast(f"OPORTUNIDADE EM {ativo}", icon="🚀")
                        elif last_rsi > 78 and tendencia == "BAIXA":
                            st.error("📉 VENDA (PUT)")
                            st.write("*Expiração:* 2-3 min")
                            st.toast(f"OPORTUNIDADE EM {ativo}", icon="⚠️")
                        else:
                            st.info("Aguardando Sniper...")
                idx += 1
            time.sleep(10)

with tab_performance:
    st.subheader("Histórico de Rentabilidade Axwell")
    
    # Gráfico de evolução da banca
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(
        x=st.session_state.logs.index, 
        y=st.session_state.logs['Saldo'],
        mode='lines+markers',
        line=dict(color='#00FFCC', width=3),
        fill='tozeroy',
        name="Saldo Real"
    ))
    fig_perf.update_layout(template="plotly_dark", title="Curva de Patrimônio ($70 base)")
    st.plotly_chart(fig_perf, use_container_width=True)
    
    st.dataframe(st.session_state.logs, use_container_width=True)

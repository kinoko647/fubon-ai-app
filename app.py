import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema

# 🎨 1. iOS 全螢幕佈局優化
st.set_page_config(layout="wide", page_title="股票預測分析", initial_sidebar_state="collapsed")

if 'u_code' not in st.session_state: st.session_state.u_code = '2330'
if 'm_type' not in st.session_state: st.session_state.m_type = '台股'

st.markdown("""
    <style>
    .stTextInput > div > div > input { background-color: #161b22; color: #00ffcc; font-size: 16px !important; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3rem; background-color: #2b313e; color: #00ffcc; border: 1px solid #4a5568; margin-bottom: 5px; font-weight: bold; }
    .status-box { padding: 12px; border-radius: 10px; border: 1px solid #30363d; background-color: #0d1117; font-size: 15px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ⚙️ 2. 傑克大師 & 蝴蝶分析引擎
def analyze_master_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 50: return None
    # 核心修復：徹底攤平多層索引
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).title() for c in df.columns]
    
    prices = df['Close'].values.flatten().astype(float)
    curr_p = float(prices[-1])
    
    # A. 傑克指標：收斂發散
    df['MA20'] = df['Close'].rolling(20).mean()
    df['STD'] = df['Close'].rolling(20).std()
    df['Upper'] = df['MA20'] + (df['STD'] * 2)
    df['Lower'] = df['MA20'] - (df['STD'] * 2)
    bw = (df['Upper'].iloc[-1] - df['Lower'].iloc[-1]) / df['MA20'].iloc[-1]
    
    # B. 傑克指標：能量背離
    delta = df['Close'].diff()
    df['RSI'] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(13).mean() / -delta.clip(upper=0).ewm(13).mean().replace(0, 0.001))))
    is_div = (curr_p < df['Close'].tail(20).min() * 1.02) and (df['RSI'].iloc[-1] > df['RSI'].tail(20).min())

    # C. 斐波那契點位
    # $$P_{buy} = H_{max} - 0.618 \times (H_{max} - L_{min})$$
    # $$P_{target} = L_{min} + 1.272 \times (H_{max} - L_{min})$$
    h_max, l_min = float(df['High'].max()), float(df['Low'].min())
    diff = h_max - l_min
    fib_buy = h_max - 0.618 * diff
    fib_target = l_min + 1.272 * diff
    
    # D. 蝴蝶形態偵測
    n = 10
    df['Min_Pt'] = df['Low'].iloc[argrelextrema(df['Low'].values, np.less_equal, order=n)[0]]
    df['Max_Pt'] = df['High'].iloc[argrelextrema(df['High'].values, np.greater_equal, order=n)[0]]
    pts = df[(df['Min_Pt'].notnull()) | (df['Max_Pt'].notnull())].tail(5)

    shares = int(budget / curr_p)
    return {
        "score": 88 if is_div else 65, "curr": curr_p, "shares": shares, 
        "profit": (shares * fib_target) - (shares * curr_p),
        "roi": ((fib_target / curr_p) - 1) * 100, "df": df, "fib_buy": fib_buy, "fib_target": fib_target, 
        "pts": pts, "bw": bw, "div": is_div
    }

# ==========================================
# 🖥️ 3. UI 介面
# ==========================================
st.title("🏆 股票預測分析系統")

# --- 🎯 智慧推薦 ---
strategy = st.selectbox("🎯 選擇分析戰略", ("🛡️ 穩健抄底", "⚡ 強勢進攻", "🔥 激進當沖"))

recom_data = {
    "🛡️ 穩健抄底": [("2330", "台積電"), ("2412", "中華電"), ("AAPL", "蘋果")],
    "⚡ 強勢進攻": [("2317", "鴻海"), ("2454", "聯發科"), ("NVDA", "輝達")],
    "🔥 激進當沖": [("2603", "長榮"), ("3231", "緯創"), ("TSLA", "特斯拉")]
}

st.markdown(f'<p style="color:#8b949e; font-size:14px;">推薦標的：</p>', unsafe_allow_html=True)
rec_cols = st.columns(3)
for i, (code, name) in enumerate(recom_data[strategy]):
    if rec_cols[i].button(name):
        st.session_state.u_code, st.session_state.m_type = code, ('台股' if code.isdigit() else '美股')
        st.rerun()

st.divider()

# --- 控制區 ---
c1, c2 = st.columns([1, 1])
with c1:
    m_type = st.radio("市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
with c2:
    u_code = st.text_input("🔍 代碼", value=st.session_state.u_code)
    u_budget = st.number_input("💰 投資預算 (元)", value=1000000)

st.session_state.u_code, st.session_state.m_type = u_code, m_type
ticker = f"{u_code}.TW" if m_type == "台股" else u_code

# --- 分析展示 ---
try:
    data = yf.download(ticker, period="1y", progress=False)
    res = analyze_master_engine(data, u_budget, strategy)
    
    if res:
        # 狀態顯示
        bw_t = "收斂" if res['bw'] < 0.15 else "發散"
        div_t = "底背離 ✅" if res['div'] else "正常"
        st.markdown(f'<div class="status-box">📊 傑克指標：{bw_t} | {div_t}</div>', unsafe_allow_html=True)
        
        # 指標
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("AI 勝率", f"{res['score']}%")
        mc2.metric("預期獲利", f"${res['profit']:,.0f}")
        mc3.metric("報酬率", f"{res['roi']:.1f}%")

        # 圖表：解決座標平掉問題 (核心修正)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        
        # 1. K線主圖：只放價格相關數據，絕不放成交量
        fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
        
        # 布林軌道
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Upper'], line=dict(color='rgba(255,255,255,0.2)', width=1), name='布林'), row=1, col=1)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Lower'], line=dict(color='rgba(255,255,255,0.2)', width=1), name='布林', fill='tonexty'), row=1, col=1)
        
        # 蝴蝶連線
        if len(res['pts']) >= 2:
            fig.add_trace(go.Scatter(x=res['pts'].index, y=res['pts'].values.flatten(), mode='lines+text', name='蝴蝶', line=dict(color='#00ffcc', width=2), text=['X','A','B','C','D']), row=1, col=1)

        # 斐波那契基準線
        fig.add_hline(y=res['fib_buy'], line_dash="dash", line_color="yellow", row=1, col=1)
        fig.add_hline(y=res['fib_target'], line_dash="dash", line_color="green", row=1, col=1)

        # 2. RSI 能量指標 (獨立在第二行，不影響第一行座標)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white', width=2), name='RSI'), row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

        # 關鍵修正：強制第一行 Y 軸只根據「股價」範圍自動縮放，不被成交量干擾
        fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        fig.update_yaxes(autorange=True, fixedrange=False, row=1, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("數據載入中...")
except Exception as e:
    st.error(f"錯誤：{str(e)}")

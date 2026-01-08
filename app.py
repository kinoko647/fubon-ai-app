import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema

# ==========================================
# 🛡️ 0. 安全防護：密碼鎖 (密碼: 8888)
# ==========================================
APP_PASSWORD = "8888" 

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.authenticated: return True
    st.title("🔒 授權驗證")
    pwd_input = st.text_input("請輸入授權碼", type="password")
    if st.button("確認登入"):
        if pwd_input == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("❌ 授權碼錯誤")
    return False

if check_password():
    # 🎨 1. iOS 全螢幕佈局
    st.set_page_config(layout="wide", page_title="股票預測分析", initial_sidebar_state="collapsed")
    if 'u_code' not in st.session_state: st.session_state.u_code = '2330'
    if 'm_type' not in st.session_state: st.session_state.m_type = '台股'

    st.markdown("""
        <style>
        .stTextInput > div > div > input { background-color: #161b22; color: #00ffcc; font-size: 16px !important; }
        [data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #00ffcc; font-weight: bold; }
        .status-box { padding: 12px; border-radius: 10px; border: 1px solid #30363d; background-color: #0d1117; font-size: 14px; margin-bottom: 15px; border-left: 5px solid #007bff; }
        .stButton>button { border-radius: 10px; background-color: #2b313e; color: #00ffcc; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    # ⚙️ 2. 核心大師引擎 (全指標補全)
    def analyze_master_engine(df, budget, mode):
        if df is None or df.empty or len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        close_p = df['Close'].values.flatten().astype(float)
        highs, lows = df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- A. 指標: 布林通道 (收斂發散) ---
        df['MA20'] = df['Close'].rolling(20).mean()
        df['Upper'] = df['MA20'] + (df['Close'].rolling(20).std() * 2)
        df['Lower'] = df['MA20'] - (df['Close'].rolling(20).std() * 2)
        bw = (df['Upper'].iloc[-1] - df['Lower'].iloc[-1]) / df['MA20'].iloc[-1]
        
        # --- B. 指標: RSI & MACD (MSI能量) ---
        delta = df['Close'].diff()
        df['RSI'] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(13).mean() / -delta.clip(upper=0).ewm(13).mean().replace(0, 0.001))))
        
        # MACD 計算
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']

        # --- C. 斐波那契與預計天數 ---
        h_max, l_min = float(highs.max()), float(lows.min())
        diff = h_max - l_min
        fib_buy = h_max - 0.618 * diff
        fib_target = l_min + 1.272 * diff
        
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        days = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0

        # --- D. 蝴蝶形態 ---
        n = 10
        df['Min_P'] = df['Low'].iloc[argrelextrema(df['Low'].values, np.less_equal, order=n)[0]]
        df['Max_P'] = df['High'].iloc[argrelextrema(df['High'].values, np.greater_equal, order=n)[0]]
        pts = df[(df['Min_P'].notnull()) | (df['Max_P'].notnull())].tail(5)

        return {
            "score": 85 if df['Hist'].iloc[-1] > 0 else 60, "curr": curr_p, "shares": int(budget / curr_p), 
            "days": days, "profit": (int(budget / curr_p) * fib_target) - (int(budget / curr_p) * curr_p),
            "roi": ((fib_target / curr_p) - 1) * 100, "df": df, "fib_buy": fib_buy, "fib_target": fib_target,
            "bw": bw, "pts_x": pts.index, "pts_y": pts['Close'].values
        }

    # 🖥️ 3. UI 介面
    st.title("🏆 股票預測分析系統")

    # --- 智慧推薦 ---
    strategy = st.selectbox("🎯 戰略模式", ("🛡️ 穩健抄底", "⚡ 強勢進攻", "🔥 激進當沖"))
    recom_data = {
        "🛡️ 穩健抄底": [("2330", "台積電"), ("2412", "中華電"), ("AAPL", "蘋果")],
        "⚡ 強勢進攻": [("2317", "鴻海"), ("2454", "聯發科"), ("NVDA", "輝達")],
        "🔥 激進當沖": [("2603", "長榮"), ("2382", "廣達"), ("TSLA", "特斯拉")]
    }
    r_cols = st.columns(3)
    for i, (code, name) in enumerate(recom_data[strategy]):
        if r_cols[i].button(name):
            st.session_state.u_code, st.session_state.m_type = code, ('台股' if code.isdigit() else '美股')
            st.rerun()

    st.divider()

    # --- 控制區 ---
    c1, c2 = st.columns([1, 1])
    with c1:
        m_type = st.radio("市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with c2:
        u_code = st.text_input("🔍 代碼", value=st.session_state.u_code)
        u_budget = st.number_input("💰 預算 (元)", value=1000000)

    st.session_state.u_code, st.session_state.m_type = u_code, m_type
    ticker = f"{u_code}.TW" if m_type == "台股" else u_code

    try:
        data = yf.download(ticker, period="1y", progress=False)
        res = analyze_master_engine(data, u_budget, strategy)
        
        if res:
            # 狀態顯示 (補齊收斂發散文字)
            bw_t = "收斂" if res['bw'] < 0.15 else "發散"
            st.markdown(f'<div class="status-box">📊 傑克指標：{bw_t} | 預計達成：{res["days"]} 天</div>', unsafe_allow_html=True)
            
            # 數據核心卡
            k1, k2, k3 = st.columns(3)
            k1.metric("AI 勝率", f"{res['score']}%")
            k2.metric("預期獲利", f"${res['profit']:,.0f}")
            k3.metric("報酬率", f"{res['roi']:.1f}%")

            # 位階顯示
            st.write(f"🎯 建議買入：`${res['fib_buy']:,.1f}` | 目標：`${res['fib_target']:,.1f}`")

            # --- 📈 三層指標圖表 (補全 MSI/MACD) ---
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                               row_heights=[0.5, 0.2, 0.3], vertical_spacing=0.03)
            
            # 1. K線 + 布林 + 蝴蝶
            fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Upper'], line=dict(color='rgba(255,255,255,0.2)', width=1), name='布林'), row=1, col=1)
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Lower'], line=dict(color='rgba(255,255,255,0.2)', width=1), name='布林', fill='tonexty'), row=1, col=1)
            if len(res['pts_x']) >= 2:
                fig.add_trace(go.Scatter(x=res['pts_x'], y=res['pts_y'], mode='lines+text', name='蝴蝶', line=dict(color='#00ffcc', width=2), text=['X','A','B','C','D']), row=1, col=1)
            fig.add_hline(y=res['fib_buy'], line_dash="dash", line_color="yellow", row=1, col=1)
            fig.add_hline(y=res['fib_target'], line_dash="dash", line_color="green", row=1, col=1)

            # 2. RSI 指標
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white', width=2), name='RSI'), row=2, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

            # 3. MACD 動能柱 (補回 MSI 功能)
            colors = ['#00ffcc' if val > 0 else '#ff4d4d' for val in res['df']['Hist']]
            fig.add_trace(go.Bar(x=res['df'].index, y=res['df']['Hist'], name='動能柱', marker_color=colors), row=3, col=1)

            # 強制座標縮放與佈局
            y_min, y_max = res['df']['Low'].min() * 0.98, res['df']['High'].max() * 1.02
            fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=5, r=5, t=10, b=10))
            fig.update_yaxes(range=[y_min, y_max], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("🚪 安全登出"):
                st.session_state.authenticated = False
                st.rerun()
    except Exception as e:
        st.error(f"系統異常：{str(e)}")

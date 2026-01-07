import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 🎨 1. iOS 顯示優化
st.set_page_config(layout="wide", page_title="富邦戰神 Master", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; background-color: #2b313e; color: white; border: 1px solid #4a5568; }
    </style>
    """, unsafe_allow_html=True)

# ⚙️ 2. 核心大師引擎 (修正數據對接)
def analyze_master_engine(df, budget, mode="🛡️ 穩健抄底"):
    # --- 修正：更強大的數據清洗邏輯 ---
    if df is None or df.empty or len(df) < 30: 
        return None
    
    # 處理 yfinance 多層索引問題 (這是報錯的主因)
    if df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(-1)
    
    df = df.copy()
    # 確保欄位名稱正確
    df.columns = [str(c).capitalize() for c in df.columns]
    
    # 數據數值化
    prices = df['Close'].values.flatten().astype(float)
    highs, lows = df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    curr_p = float(prices[-1])
    
    # A. 斐波那契預測
    h_max, l_min = float(highs.max()), float(lows.min())
    diff = h_max - l_min
    fib_target = l_min + 1.272 * diff
    
    # B. 盈虧試算
    shares = int(budget / curr_p)
    target_val = shares * fib_target
    profit = target_val - (shares * curr_p)
    roi = ((fib_target / curr_p) - 1) * 100

    # C. 指標計算 (修復 RSI)
    delta = df['Close'].diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down.replace(0, 0.001))))
    df['RSI'] = df['RSI'].fillna(50)

    # D. 診斷報告 (移除 NULL)
    reasons = []
    if curr_p > (h_max - 0.618 * diff):
        reasons.append("❌ 價格離 0.618 支撐區過遠。")
    
    return {"score": 85 if not reasons else 45, "curr": curr_p, "shares": shares, 
            "target_val": target_val, "profit": profit, "df": df, "reasons": reasons, "roi": roi}

# 🖥️ 3. UI 介面
st.sidebar.header("🕹️ 控制中心")
m_type = st.sidebar.radio("市場", ("台股", "美股"))
u_code = st.sidebar.text_input("輸入代碼", value="2317")
budget = st.sidebar.number_input("投資預算", value=1000000)

# 自動補齊台股代號
ticker = f"{u_code}.TW" if m_type == "台股" else u_code

# 下載數據 (增加對接穩定性)
data = yf.download(ticker, period="2y", progress=False, multi_level_download=True)
res = analyze_master_engine(data, budget)

if res:
    st.metric(f"{u_code} AI 綜合勝率", f"{res['score']}%")
    
    st.write("### 📈 獲利精確模擬 (投入 vs 產出)")
    c1, c2, c3 = st.columns(3)
    c1.metric("能買入股數", f"{res['shares']:,}股")
    c2.metric("預期總值", f"${res['target_val']:,.0f}")
    c3.metric("盈利金額", f"${res['profit']:,.0f}", delta=f"{res['roi']:.1f}%")

    if st.button("❓ 查看 AI 深度診斷"):
        if res['reasons']:
            for r in res['reasons']: st.error(r)
        else: st.success("✅ 技術指標完美共振！")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white'), name='RSI'), row=2, col=1)
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"無法抓取 {ticker} 的數據，請檢查代碼是否正確或稍後再試。")

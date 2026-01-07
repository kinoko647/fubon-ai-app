import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from scipy.stats import linregress

# ==========================================
# 🎨 1. iOS 全螢幕顯示與 UI 優化
# ==========================================
st.set_page_config(layout="wide", page_title="富邦戰神 Master", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; background-color: #2b313e; color: white; border: 1px solid #4a5568; }
    .stMetric { background-color: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ⚙️ 2. 核心大師引擎 (徹底修復版)
# ==========================================
def analyze_master_engine(df, budget, mode="🛡️ 穩健抄底"):
    # A. 數據清洗與嚴謹性檢查
    if df is None or len(df) < 50: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # 數值純量化，解決判斷報錯
    prices = df['Close'].values.flatten().astype(float)
    highs, lows = df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    curr_p = float(prices[-1])
    
    # B. 斐波那契與獲利分析
    h_max, l_min = float(highs.max()), float(lows.min())
    diff = h_max - l_min
    fib_target = l_min + 1.272 * diff
    
    # 投入產出模擬 (核心新增)
    shares = int(budget / curr_p)
    target_val = shares * fib_target
    profit = target_val - (shares * curr_p)
    roi_pct = ((fib_target / curr_p) - 1) * 100

    # C. 技術指標計算 (【重要】修復 NameError: delta)
    delta = df['Close'].diff() # 確保在計算前先定義變數
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    
    # 修復 RSI 顯示 (確保畫出曲線)
    df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
    df['RSI'] = df['RSI'].fillna(50) 
    
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['Hist'] = df['MACD'] - df['MACD'].ewm(span=9).mean()

    # D. 診斷邏輯 (【重要】徹底移除 NULL 顯示)
    reasons = [] # 初始化空清單，避免輸出 NULL
    score = 35 
    if "穩健" in mode:
        if curr_p > (h_max - 0.618 * diff): reasons.append("❌ 價格離 0.618 支撐區過遠")
    elif "激進" in mode:
        if curr_p < df['VWAP'].iloc[-1]: reasons.append("❌ 跌破 VWAP 短線趨勢偏空")

    atr = (df['High']-df['Low']).rolling(20).mean().iloc[-1]
    days = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0

    return {"fib": fib_target, "score": min(score + (40 if not reasons else 0), 100), "curr": curr_p, 
            "shares": shares, "target_val": target_val, "profit": profit, 
            "df": df, "reasons": reasons, "roi": roi_pct, "days": days}

# ==========================================
# 🖥️ 3. UI 介面佈局
# ==========================================
st.sidebar.header("🕹️ 控制中心")
strategy = st.sidebar.selectbox("🎯 模式選擇", ("🛡️ 穩健抄底", "⚡ 強勢進攻", "🔥 激進當沖"))
market = st.sidebar.radio("市場", ("台股", "美股"))
u_code = st.sidebar.text_input("代碼分析", value="2317")
total_budget = st.sidebar.number_input("總預算 (模擬)", value=1000000)

data = yf.download(f"{u_code}{'.TW' if market=='台股' else ''}", period="2y", progress=False)
res = analyze_master_engine(data, total_budget, strategy)

if res:
    # 頂部：勝率與天數
    st.metric(f"{u_code} AI 勝率", f"{res['score']}%")
    st.info(f"⏱️ 預計達成時間：約 **{res['days']}** 個交易日")
    
    # 獲利精確模擬 (核心輸出)
    st.write("### 📈 獲利精確模擬 (投入 vs 產出)")
    c1, c2, c3 = st.columns(3)
    c1.metric("可買股數", f"{res['shares']:,} 股")
    c2.metric("預期總值", f"${res['target_val']:,.0f}")
    c3.metric("盈利金額", f"${res['profit']:,.0f}", delta=f"{res['roi']:.1f}%")

    # 診斷區域：解決 NULL 問題
    if st.button("❓ 查看 AI 深度診斷"):
        st.write("#### 💡 診斷報告：")
        if res['reasons']:
            for r in res['reasons']: st.error(r)
        else: st.success("✅ 指標達成完美共振！")

    # 三層指標圖表
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white'), name='RSI'), row=2, col=1)
    fig.add_trace(go.Bar(x=res['df'].index, y=res['df']['Hist'], name='MACD'), row=3, col=1)
    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("分析異常，請確認代碼...")

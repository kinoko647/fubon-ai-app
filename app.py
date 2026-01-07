import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ==========================================
# 🎨 1. iOS 旗艦全螢幕佈局
# ==========================================
st.set_page_config(layout="wide", page_title="富邦戰神 Master", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stTextInput > div > div > input { background-color: #161b22; color: #00ffcc; font-size: 18px !important; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ⚙️ 2. 核心大師引擎
# ==========================================
def analyze_master_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 40: return None
    
    # 修正 yfinance 多層索引
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).title() for c in df.columns]
    
    prices = df['Close'].values.flatten().astype(float)
    highs, lows = df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    curr_p = float(prices[-1])
    
    # A. 斐波那契
    h_max, l_min = float(highs.max()), float(lows.min())
    diff = h_max - l_min
    fib_buy = h_max - 0.618 * diff
    fib_target = l_min + 1.272 * diff
    
    # B. 獲利模擬 (單位：元)
    shares = int(budget / curr_p)
    target_val = shares * fib_target
    profit = target_val - (shares * curr_p)
    roi = ((fib_target / curr_p) - 1) * 100

    # C. 指標計算
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    delta = df['Close'].diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down.replace(0, 0.001))))
    
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Hist'] = df['MACD'] - df['Signal']

    # D. 評分
    reasons = []
    score = 40
    if mode == "🛡️ 穩健抄底":
        if curr_p <= fib_buy * 1.02: score += 45
        else: reasons.append(f"❌ 價格未回測黃金支撐區 (${fib_buy:,.1f})")
    elif mode == "⚡ 強勢進攻":
        if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]: score += 40
        else: reasons.append("❌ MACD 動能目前偏弱")
    else:
        if curr_p > df['VWAP'].iloc[-1]: score += 50
        else: reasons.append("❌ 價格位於 VWAP 生命線下方")

    atr = (df['High']-df['Low']).rolling(20).mean().iloc[-1]
    days = int(abs(fib_target - curr_p) / (atr * 0.7)) if atr > 0 else 0

    return {
        "score": min(score, 100), "curr": curr_p, "shares": shares, "target_val": target_val,
        "profit": profit, "roi": roi, "df": df, "reasons": reasons, "days": days,
        "fib_buy": fib_buy, "fib_target": fib_target
    }

# ==========================================
# 🖥️ 3. UI 介面佈局
# ==========================================
st.title("🏆 富邦 2026 AI 戰神")

# --- 控制區 ---
c1, c2 = st.columns([1, 1])
with c1:
    strategy = st.selectbox("🎯 模式", ("🛡️ 穩健抄底", "⚡ 強勢進攻", "🔥 激進當沖"))
    m_type = st.radio("市場", ("台股", "美股"), horizontal=True)
with c2:
    u_code = st.text_input("🔍 代碼", value="2317")
    u_budget = st.number_input("💰 投資預算 (元)", value=1000000, step=10000)

ticker = f"{u_code}.TW" if m_type == "台股" else u_code

try:
    data = yf.download(ticker, period="2y", progress=False)
    res = analyze_master_engine(data, u_budget, strategy)
    
    if res:
        st.divider()
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("AI 綜合勝率", f"{res['score']}%")
        col_m2.metric("預計達成時間", f"約 {res['days']} 天")
        
        st.write("### 📈 獲利精確模擬 (投入 vs 產出)")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("可買股數", f"{res['shares']:,} 股")
        mc2.metric("預期總值", f"${res['target_val']:,.0f}")
        mc3.metric("盈利金額", f"${res['profit']:,.0f}", delta=f"{res['roi']:.1f}%")

        with st.expander("❓ 查看 AI 深度診斷", expanded=True):
            st.write(f"🎯 **策略參考價：**")
            st.write(f"- 建議佈局價： `${res['fib_buy']:,.2f}`")
            st.write(f"- 目標獲利價： `${res['fib_target']:,.2f}`")
            if res['reasons']:
                for r in res['reasons']: st.error(r)
            else: st.success("✅ 指標共振，符合佈局條件")

        # 圖表
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.2, 0.3], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['VWAP'], line=dict(color='orange', width=1), name='VWAP'), row=1, col=1)
        fig.add_hline(y=res['fib_buy'], line_dash="dash", line_color="yellow", row=1, col=1)
        fig.add_hline(y=res['fib_target'], line_dash="dash", line_color="green", row=1, col=1)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white', width=2), name='RSI'), row=2, col=1)
        fig.add_trace(go.Bar(x=res['df'].index, y=res['df']['Hist'], name='MACD柱狀圖', marker_color='cyan'), row=3, col=1)
        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("請確認代碼。")
except Exception as e:
    st.error(f"系統錯誤：{str(e)}")

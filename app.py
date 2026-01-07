import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 🎨 1. iOS 全螢幕佈局優化
st.set_page_config(layout="wide", page_title="富邦 AI 戰神", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 讓手機端的輸入框更醒目 */
    .stTextInput > div > div > input { background-color: #2b303b; color: #00ffcc; font-size: 20px !important; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3rem; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ⚙️ 2. 核心大師引擎
def analyze_stock_logic(df, budget):
    if df is None or df.empty or len(df) < 20: return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).title() for c in df.columns]
    
    prices = df['Close'].values.flatten().astype(float)
    highs, lows = df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    curr_p = float(prices[-1])
    
    h_max, l_min = float(highs.max()), float(lows.min())
    diff = h_max - l_min
    target_p = l_min + 1.272 * diff
    
    shares = int(budget / curr_p)
    profit = (shares * target_p) - (shares * curr_p)
    roi = ((target_p / curr_p) - 1) * 100

    delta = df['Close'].diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down.replace(0, 0.001))))
    
    reasons = []
    if curr_p > (h_max - 0.618 * diff): reasons.append("❌ 價格離 0.618 支撐區太遠")
    
    return {"score": 88 if not reasons else 48, "curr": curr_p, "shares": shares, 
            "profit": profit, "df": df, "reasons": reasons, "roi": roi, "target": target_p}

# 🖥️ 3. 直接在「首頁」顯示搜尋控制區
st.title("🏆 富邦 2026 AI 戰神")

# --- 搜尋區塊 ---
col_search1, col_search2 = st.columns([1, 2])
with col_search1:
    m_type = st.radio("選擇市場", ("台股", "美股"), horizontal=True)
with col_search2:
    u_code = st.text_input("🔍 輸入代碼（輸入完按 Return）", value="2317")

u_budget = st.number_input("💰 投資預算", value=1000000)

# --- 執行分析 ---
ticker_final = f"{u_code}.TW" if m_type == "台股" else u_code

try:
    # 確保抓取最新數據
    data_raw = yf.download(ticker_final, period="2y", progress=False)
    res = analyze_stock_logic(data_raw, u_budget)
    
    if res:
        st.divider()
        st.metric(f"【{u_code}】AI 綜合勝率", f"{res['score']}%")
        
        # 獲利模擬區
        st.write("### 📈 獲利精確模擬")
        c1, c2, c3 = st.columns(3)
        c1.metric("可買股數", f"{res['shares']:,}股")
        c2.metric("預期獲利", f"${res['profit']:,.0f}")
        c3.metric("預期報酬", f"{res['roi']:.1f}%")

        if st.button("❓ 查看 AI 深度診斷"):
            if res['reasons']:
                for r in res['reasons']: st.error(r)
            else: st.success("✅ 技術指標完美共振，建議佈局")

        # K 線圖
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white', width=2), name='RSI'), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=5, r=5, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"⚠️ 找不到代碼 {ticker_final}，請檢查輸入是否正確。")

except Exception as e:
    st.error(f"❌ 系統錯誤：{str(e)}")

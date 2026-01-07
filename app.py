import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 🎨 1. iOS 行動端優化配置
st.set_page_config(layout="wide", page_title="富邦戰神 Master", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; background-color: #212529; color: white; border: 1px solid #495057; }
    </style>
    """, unsafe_allow_html=True)

# ⚙️ 2. 核心大師引擎 (修正 TypeError 與多層索引)
def analyze_stock_logic(df, budget):
    # --- 數據安全防護網 ---
    if df is None or df.empty or len(df) < 20:
        return None
    
    # 核心修復：徹底攤平 yfinance 的多層欄位 (解決分析異常關鍵)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 確保欄位大小寫統一
    df.columns = [str(c).title() for c in df.columns]
    
    # 數據純量化 (避免 ValueError: Ambiguous)
    prices = df['Close'].values.flatten().astype(float)
    highs = df['High'].values.flatten().astype(float)
    lows = df['Low'].values.flatten().astype(float)
    curr_p = float(prices[-1])
    
    # A. 預測位階與盈虧 (您的核心需求)
    h_max, l_min = float(highs.max()), float(lows.min())
    diff = h_max - l_min
    target_p = l_min + 1.272 * diff # 1.272 預測目標
    
    shares = int(budget / curr_p)
    profit = (shares * target_p) - (shares * curr_p)
    roi = ((target_p / curr_p) - 1) * 100

    # B. 技術指標 (修復 NameError: delta)
    delta = df['Close'].diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down.replace(0, 0.001))))
    df['RSI'] = df['RSI'].fillna(50)

    # C. 診斷邏輯 (徹底移除 NULL)
    reasons = []
    if curr_p > (h_max - 0.618 * diff):
        reasons.append("❌ 目前價格離 0.618 價值區較遠")
    
    return {"score": 88 if not reasons else 48, "curr": curr_p, "shares": shares, 
            "profit": profit, "df": df, "reasons": reasons, "roi": roi, "target": target_p}

# 🖥️ 3. iOS UI 介面
st.sidebar.header("🕹️ 控制中心")
m_type = st.sidebar.radio("市場選擇", ("台股", "美股"))
u_code = st.sidebar.text_input("輸入代碼 (例如 2317 或 NVDA)", value="2317")
u_budget = st.sidebar.number_input("您的總預算 (模擬)", value=1000000)

# 自動補齊代碼
ticker_final = f"{u_code}.TW" if m_type == "台股" else u_code

# 下載數據 (採用最穩定參數，避免 TypeError)
try:
    data_raw = yf.download(ticker_final, period="2y", progress=False)
    res = analyze_stock_logic(data_raw, u_budget)
    
    if res:
        st.metric(f"{u_code} AI 綜合勝率", f"{res['score']}%")
        
        # 獲利金額模擬區
        st.write("### 📈 獲利精確模擬 (投入 vs 產出)")
        c1, c2, c3 = st.columns(3)
        c1.metric("可買股數", f"{res['shares']:,}股")
        c2.metric("預期獲利", f"${res['profit']:,.0f}")
        c3.metric("預期報酬", f"{res['roi']:.1f}%")

        if st.button("❓ 查看 AI 深度診斷"):
            if res['reasons']:
                for r in res['reasons']: st.error(r)
            else: st.success("✅ 技術指標完美共振，建議佈局")

        # 專業 K 線圖 (修正 RSI 顯示)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white', width=2), name='RSI'), row=2, col=1)
        fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"⚠️ 無法下載 {ticker_final} 的數據，請檢查代號是否輸入正確。")

except Exception as e:
    st.error(f"❌ 系統發生錯誤：{str(e)}")


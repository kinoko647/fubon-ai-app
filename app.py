import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema

# ==========================================
# 🎨 1. iOS 佈局優化與 Session 初始化
# ==========================================
st.set_page_config(layout="wide", page_title="富邦戰神 Master", initial_sidebar_state="collapsed")

if 'u_code' not in st.session_state: st.session_state.u_code = '2317'
if 'm_type' not in st.session_state: st.session_state.m_type = '台股'

st.markdown("""
    <style>
    .stTextInput > div > div > input { background-color: #161b22; color: #00ffcc; font-size: 18px !important; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 2.5rem; background-color: #2b313e; color: #00ffcc; border: 1px solid #4a5568; font-size: 14px; }
    .status-box { padding: 10px; border-radius: 10px; border: 1px solid #30363d; background-color: #0d1117; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ⚙️ 2. 傑克大師分析引擎 (收斂、發散、背離、蝴蝶)
# ==========================================
def analyze_master_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).title() for c in df.columns]
    
    # A. 數據清洗與基礎指標
    df = df.copy()
    prices = df['Close'].values.flatten().astype(float)
    curr_p = float(prices[-1])
    
    # 布林通道 (判斷 收斂 / 發散)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['MA20'] + (df['STD'] * 2)
    df['Lower'] = df['MA20'] - (df['STD'] * 2)
    df['BW'] = (df['Upper'] - df['Lower']) / df['MA20'] # Bandwidth
    
    # 判斷狀態
    is_converging = df['BW'].iloc[-1] < df['BW'].iloc[-5] # 收斂中
    
    # B. 傑克邏輯：能量背離 (Divergence)
    delta = df['Close'].diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    df['RSI'] = 100 - (100 / (1 + (up.ewm(13).mean() / down.ewm(13).mean().replace(0, 0.001))))
    
    # 背離偵測
    last_p = df['Close'].tail(20)
    last_rsi = df['RSI'].tail(20)
    bull_div = (last_p.iloc[-1] < last_p.min()) and (last_rsi.iloc[-1] > last_rsi.min())
    
    # C. 斐波那契蝴蝶點位
    h_max, l_min = float(df['High'].max()), float(df['Low'].max())
    diff = h_max - l_min
    fib_buy = h_max - 0.618 * diff
    fib_target = l_min + 1.272 * diff
    
    # D. 蝴蝶形態轉折點 (X-A-B-C-D)
    n = 12
    df['Min'] = df['Low'].iloc[argrelextrema(df['Low'].values, np.less_equal, order=n)[0]]
    df['Max'] = df['High'].iloc[argrelextrema(df['High'].values, np.greater_equal, order=n)[0]]
    pts = df[(df['Min'].notnull()) | (df['Max'].notnull())].tail(5)

    # E. 診斷報告與評分
    reasons = []
    score = 50
    
    # 傑克分析總結
    jack_status = "📊 傑克能量分析："
    if bull_div: 
        score += 20
        jack_status += " [底背離 - 強力看漲]"
    if is_converging: 
        jack_status += " [區間收斂 - 醞釀爆發]"
    else: 
        jack_status += " [趨勢發散 - 動能釋放]"
    
    if mode == "🛡️ 穩健抄底":
        if curr_p <= fib_buy * 1.02: score += 20
        else: reasons.append(f"❌ 未回測黃金支撐位 (${fib_buy:,.1f})")

    atr = (df['High']-df['Low']).rolling(20).mean().iloc[-1]
    days = int(abs(fib_target - curr_p) / (atr * 0.7)) if atr > 0 else 0

    return {
        "score": min(score, 100), "curr": curr_p, "shares": int(budget / curr_p), 
        "profit": (int(budget / curr_p) * fib_target) - (int(budget / curr_p) * curr_p),
        "roi": ((fib_target / curr_p) - 1) * 100, "df": df, "reasons": reasons, "days": days,
        "fib_buy": fib_buy, "fib_target": fib_target, "pts": pts, "jack_status": jack_status
    }

# ==========================================
# 🖥️ 3. UI 介面佈局
# ==========================================
st.title("🏆 富邦 2026 AI 戰神 - 傑克旗艦版")

# --- 推薦跳轉 ---
tw_list = [("2330", "台積電"), ("2317", "鴻海"), ("2454", "聯發科"), ("2382", "廣達")]
t_cols = st.columns(4)
for i, (code, name) in enumerate(tw_list):
    if t_cols[i].button(f"🇹🇼 {name}"):
        st.session_state.u_code, st.session_state.m_type = code, '台股'
        st.rerun()

# --- 控制區 ---
c1, c2 = st.columns([1, 1])
with c1:
    strategy = st.selectbox("🎯 戰略模式", ("🛡️ 穩健抄底", "⚡ 強勢進攻", "🔥 激進當沖"))
    m_type = st.radio("市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
with c2:
    u_code = st.text_input("🔍 代碼", value=st.session_state.u_code)
    u_budget = st.number_input("💰 預算 (元)", value=1000000)

ticker = f"{u_code}.TW" if m_type == "台股" else u_code

try:
    data = yf.download(ticker, period="1y", progress=False)
    res = analyze_master_engine(data, u_budget, strategy)
    
    if res:
        st.divider()
        # 勝率與傑克狀態
        st.metric(f"【{u_code}】AI 綜合勝率", f"{res['score']}%")
        st.markdown(f'<div class="status-box">{res["jack_status"]}</div>', unsafe_allow_html=True)
        
        # 獲利模擬
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("可買股數", f"{res['shares']:,} 股")
        mc2.metric("預期獲利", f"${res['profit']:,.0f}")
        mc3.metric("預期報酬", f"{res['roi']:.1f}%")

        with st.expander("🦋 傑克大師診斷與蝴蝶位階", expanded=True):
            st.write(f"🎯 買入位：`${res['fib_buy']:,.2f}` | 目標位：`${res['fib_target']:,.2f}`")
            if res['reasons']:
                for r in res['reasons']: st.error(r)
            else: st.success("✅ 指標達成共振，目前處於最佳交易區間。")

        # 圖表：加回布林通道與蝴蝶連線
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.2, 0.3], vertical_spacing=0.03)
        
        # 1. 主圖：K線 + 布林通道 (收斂/發散)
        fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Upper'], line=dict(color='rgba(173, 216, 230, 0.4)', width=1), name='布林上軌'), row=1, col=1)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Lower'], line=dict(color='rgba(173, 216, 230, 0.4)', width=1), name='布林下軌', fill='tonexty'), row=1, col=1)
        
        # 蝴蝶連線
        if len(res['pts']) >= 2:
            fig.add_trace(go.Scatter(x=res['pts'].index, y=res['pts'].values.flatten(), mode='lines+text', name='蝴蝶形態', line=dict(color='#00ffcc', width=2), text=['X','A','B','C','D']), row=1, col=1)

        # 2. RSI (背離分析)
        fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='white', width=2), name='RSI'), row=2, col=1)
        
        # 3. MACD 柱狀圖
        df_hist = res['df']['Close'].ewm(span=12).mean() - res['df']['Close'].ewm(span=26).mean()
        fig.add_trace(go.Bar(x=res['df'].index, y=df_hist, name='能量柱', marker_color='cyan'), row=3, col=1)
        
        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("請確認代碼。")
except Exception as e:
    st.error(f"系統錯誤：{str(e)}")

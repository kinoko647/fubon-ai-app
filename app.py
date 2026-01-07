import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema

# ==========================================
# 🛡️ 0. 安全防護：密碼鎖設定
# ==========================================
# 您可以在這裡修改您想要的密碼
APP_PASSWORD = "910304" 

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.authenticated:
        return True
    
    st.title("🔒 股票預測分析系統 - 授權驗證")
    pwd_input = st.text_input("請輸入授權碼以開啟系統", type="password")
    if st.button("確認登入"):
        if pwd_input == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 授權碼錯誤，請重新輸入")
    return False

# 只有密碼正確才會執行後續代碼
if check_password():

    # 🎨 1. iOS 全螢幕佈局
    st.set_page_config(layout="wide", page_title="股票預測分析", initial_sidebar_state="collapsed")

    # 初始化狀態
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
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        close_prices = df['Close'].values.flatten().astype(float)
        curr_p = float(close_prices[-1])
        
        # A. 傑克指標：收斂發散
        df['MA20'] = df['Close'].rolling(20).mean()
        df['STD'] = df['Close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        bw = (df['Upper'].iloc[-1] - df['Lower'].iloc[-1]) / df['MA20'].iloc[-1]
        
        # B. 傑克指標：背離 (RSI)
        delta = df['Close'].diff()
        df['RSI'] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(13).mean() / -delta.clip(upper=0).ewm(13).mean().replace(0, 0.001))))
        is_div = (curr_p < df['Close'].tail(20).min() * 1.02) and (df['RSI'].iloc[-1] > df['RSI'].tail(20).min())

        # C. 斐波那契與預計天數
        h_max, l_min = float(df['High'].max()), float(df['Low'].min())
        diff = h_max - l_min
        fib_buy = h_max - 0.618 * diff
        fib_target = l_min + 1.272 * diff
        
        tr = np.maximum(df['High'].values[1:] - df['Low'].values[1:], np.maximum(abs(df['High'].values[1:] - close_prices[:-1]), abs(df['Low'].values[1:] - close_prices[:-1])))
        atr = pd.Series(tr).rolling(14).mean().iloc[-1]
        days = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0

        # D. 蝴蝶形態偵測
        n = 10
        df['Min_Pt'] = df['Low'].iloc[argrelextrema(df['Low'].values, np.less_equal, order=n)[0]]
        df['Max_Pt'] = df['High'].iloc[argrelextrema(df['High'].values, np.greater_equal, order=n)[0]]
        pts_df = df[(df['Min_Pt'].notnull()) | (df['Max_Pt'].notnull())].tail(5)

        shares = int(budget / curr_p)
        return {
            "score": 88 if is_div else 62, "curr": curr_p, "shares": shares, "days": days,
            "profit": (shares * fib_target) - (shares * curr_p), "roi": ((fib_target / curr_p) - 1) * 100,
            "df": df, "fib_buy": fib_buy, "fib_target": fib_target, 
            "pts_x": pts_df.index, "pts_y": pts_df['Close'].values, "bw": bw, "div": is_div
        }

    # 🖥️ 3. UI 介面
    st.title("🏆 股票預測分析系統")

    # --- 🎯 智慧推薦模式 ---
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
            div_t = "底背離 ✅" if res['div'] else "能量正常"
            st.markdown(f'<div class="status-box">📊 傑克指標：{bw_t} | {div_t}</div>', unsafe_allow_html=True)
            
            # 指標卡
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("AI 勝率", f"{res['score']}%")
            mc2.metric("預計天數", f"{res['days']} 天")
            mc3.metric("預期報酬", f"{res['roi']:.1f}%")

            st.write("### 📈 獲利試算")
            cc1, cc2 = st.columns(2)
            cc1.metric("可買股數", f"{res['shares']:,}")
            cc2.metric("預期獲利", f"${res['profit']:,.0f}")

            # 圖表：強制座標鎖定
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
            fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
            
            if len(res['pts_x']) >= 2:
                fig.add_trace(go.Scatter(x=res['pts_x'], y=res['pts_y'], mode='lines+markers+text', name='蝴蝶', line=dict(color='#00ffcc', width=2), text=['X','A','B','C','D']), row=1, col=1)

            fig.add_hline(y=res['fib_buy'], line_dash="dash", line_color="yellow", row=1, col=1)
            fig.add_hline(y=res['fib_target'], line_dash="dash", line_color="green", row=1, col=1)

            # RSI
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'].values, line=dict(color='#ffcc00', width=2), name='RSI'), row=2, col=1)

            # 強制鎖定座標範圍
            y_min, y_max = res['df']['Low'].min() * 0.98, res['df']['High'].max() * 1.02
            fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
            fig.update_yaxes(range=[y_min, y_max], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 登出按鈕
            if st.button("🚪 安全登出"):
                st.session_state.authenticated = False
                st.rerun()

        else:
            st.warning("數據載入中...")
    except Exception as e:
        st.error(f"系統異常：{str(e)}")

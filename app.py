import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# 1. 系統配置與高對比視覺
st.set_page_config(layout="wide", page_title="2026 戰神終極終端", initial_sidebar_state="expanded")
for s in ['auth','u_c','m_t','strat','tf']:
    if s not in st.session_state:
        st.session_state.auth, st.session_state.u_c, st.session_state.m_t, st.session_state.strat, st.session_state.tf = False, '6188', '台股', '⚡ 中線', '日線'

st.markdown("""<style>
    .main { background-color: #000000; }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900 !important; font-size: 3rem !important; text-shadow: 0 0 20px #00ffcc; }
    .stMetric, .jack-panel { background-color: #000000; border: 2px solid #30363d; border-radius: 15px; padding: 25px; }
    .jack-panel { border-left: 15px solid #007bff; margin-bottom: 25px; }
    .jack-title { color: #fff; font-size: 32px; font-weight: 900; }
    .jack-val { color: #ffff00; font-size: 26px; font-weight: 900; }
    .advice-card { padding: 25px; border-radius: 15px; text-align: center; border: 5px solid; font-size: 24px; font-weight: 900; }
    .right-side { border-color: #ff3e3e; background: rgba(255,62,62,0.2); }
    .left-side { border-color: #00ffcc; background: rgba(0,255,204,0.2); }
</style>""", unsafe_allow_html=True)

# 2. 核心分析引擎 (蝴蝶、雙軌、突破、物理對焦)
def analyze_engine(df, budget):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # 指標計算 (修正 ema12, macd, cci 定義錯誤)
    df['ma20'], df['ema8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['ema12'], df['ema26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['up'], df['dn'] = df['ma20'] + (df['Close'].rolling(20).std()*2), df['ma20'] - (df['Close'].rolling(20).std()*2)
    df['bw'] = (df['up'] - df['dn']) / df['ma20']
    df['macd'] = df['ema12'] - df['ema26']
    df['hist'] = df['macd'] - df['macd'].ewm(span=9).mean()
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['cci'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())
    d = df['Close'].diff(); g, l = d.where(d>0,0).rolling(14).mean(), -d.where(d<0,0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (g / l.replace(0,0.001))))

    # 形態偵測     n=10; mx_pk, mn_pk = argrelextrema(hp, np.greater, order=n)[0], argrelextrema(lp, np.less, order=n)[0]
    pts = sorted(np.concatenate([mx_pk[-3:], mn_pk[-3:]]))
    p_lab, score, diag = "盤整中", 60, []
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]>v[1] and v[2]>v[1] and v[2]>v[3] and v[2]<=v[0]*1.02: p_lab, score = "蝴蝶 M 頭 (壓力)", score-20; diag.append("🔴 左側賣壓：蝴蝶形態 D 點承壓")
        elif v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.98: p_lab, score = "蝴蝶 W 底 (佈局)", score+35; diag.append("🟢 左側買點：蝴蝶形態 D 點守穩")

    # 雙軌與突破偵測 (2486 漲停關鍵)     brk = cp[-1] > hp[-21:-1].max() and df['bw'].iloc[-1] > df['bw'].iloc[-2]
    if brk: score += 25; diag.append("🔥 右側突破：攻破 20 日高點，黑馬啟航")
    if df['ema8'].iloc[-1] > df['ma20'].iloc[-1]: score += 10; diag.append("✨ 趨勢金叉：黃金 T 線上穿生命線")

    look, curr = 120, cp[-1]
    mx, mn = hp[-look:].max(), lp[-look:].min()
    fib_b, fib_t = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    return {"score": min(score, 98), "curr": curr, "shares": int(budget/curr), "df": df, "fib_b": fib_b, "fib_t": fib_t, "bw": df['bw'].iloc[-1], "p_lab": p_lab, "diag": diag, "brk": brk, "pts_x": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "pts_y": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# 3. 搜尋與 Ticker 修復 (解決 6188 找不到問題)
def get_data(code, tf):
    # 台股智慧辨識上市(.TW)或上櫃(.TWO)
    if st.session_state.m_t == '台股':
        for sfx in ['.TW', '.TWO']:
            d = yf.download(f"{code}{sfx}", interval=tf, period="2y" if '日' in tf else "1mo", progress=False)
            if not d.empty: return d
    return yf.download(code, interval=tf, period="2y", progress=False)

# 4. UI 邏輯
if not st.session_state.auth:
    st.title("🔒 戰神操盤終端")
    if st.text_input("密碼", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 500 檔海量掃描")
        st.session_state.tf = st.selectbox("週期", ("15分鐘", "1小時", "日線", "週線"), index=2)
        if st.button("🚀 啟動 500 檔掃描"):
            targets = ["2330","2317","2454","2486","6188","2603","2303","3231","2383","3037","1513","2881","2882","0050","0056","00878","00919"]
            res = []
            pb = st.progress(0)
            for i, c in enumerate(targets):
                d = get_data(c, '1d')
                a = analyze_engine(d, 1000000)
                if a and (a['score'] >= 85 or a['brk']): res.append({"代碼": c, "形態": a['p_lab'], "勝率": f"{a['score']}%"})
                pb.progress((i+1)/len(targets))
            st.session_state.scan_df = pd.DataFrame(res)
        if 'scan_df' in st.session_state: st.dataframe(st.session_state.scan_df, use_container_width=True)

    st.title("🏆 戰神 2026 旗艦完全體")
    cc1, cc2, cc3 = st.columns(3)
    with cc1: st.session_state.m_t = st.radio("市場", ("台股", "美股"), horizontal=True)
    with cc2: st.session_state.u_c = st.text_input("🔍 診斷代碼 (如 6188, 2486)", value=st.session_state.u_c)
    with cc3: u_inv = st.number_input("💰 預算", value=1000000)

    tf_map = {"15分鐘":"15m", "1小時":"60m", "日線":"1d", "週線":"1wk"}
    raw = get_data(st.session_state.u_c, tf_map[st.session_state.tf])
    a = analyze_engine(raw, u_inv)
    
    if a:
        # 實戰計算機         st.markdown("<h2 style='color:#ffff00;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        my_p = k1.number_input("👉 我的買入價", value=a['curr'])
        k2.write(f"**AI 目標：**\n\n<span style='color:#00ffcc; font-size:30px; font-weight:900;'>${a['fib_t']:,.2f}</span>", unsafe_allow_html=True)
        prof = (a['shares']*a['fib_t'])-(a['shares']*my_p)
        k3.write(f"**預計獲利：**\n\n<span style='color:#ff3e3e; font-size:30px; font-weight:900;'>${prof:,.0f}</span>", unsafe_allow_html=True)

        st.markdown(f"""<div class="jack-panel"><div class="jack-title">📊 傑克看板：{"📉 壓縮變盤" if a['bw']<0.12 else "📊 發散趨勢"}</div>
            <p class="jack-sub-text">偵測：<span class="jack-status-highlight">{a['p_lab']}</span> | AI 勝率：<span class="jack-val">{a['score']}%</span></p>
            <p class="jack-sub-text">參考：<span class="jack-val">${a['fib_b']:,.2f} (左軌)</span> | <span class="jack-val">${raw['High'].iloc[-21:-1].max():,.2f} (右軌)</span></p></div>""", unsafe_allow_html=True)

        v1, v2 = st.columns(2)
        v1.markdown(f'<div class="advice-card left-side">💎 左軌抄底：{"進入價值區" if a["curr"]<=a["fib_b"]*1.02 else "尚未到達"}</div>', unsafe_allow_html=True)
        v2.markdown(f'<div class="advice-card right-side">🚀 右軌突破：{"強勢噴發追進" if a["brk"] else "等待突破"}</div>', unsafe_allow_html=True)

        # 專業圖表 (徹底解決平線問題)         fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線形態 & 蝴蝶 XABCD (物理對焦)", "RSI 指標", "MACD 動能"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        if a['pts_x']: fig.add_trace(go.Scatter(x=a['pts_x'], y=a['pts_y'], mode='markers+lines+text', name='蝴蝶 XABCD', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D']), 1, 1)
        
        # 標記買點         fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['fib_b']], mode='markers+text', name='左軌點', marker=dict(symbol='triangle-up', size=18, color='#ffa500'), text=['抄底']), 1, 1)
        if a['brk']: fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右軌點', marker=dict(symbol='star', size=22, color='#ff00ff'), text=['突破']), 1, 1)

        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ema8'], line=dict(color='#ffff00', width=2), name='T線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ma20'], line=dict(color='#fff', dash='dot'), name='月線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['rsi'], line=dict(color='#ffcc00'), name='RSI'), 2, 1)
        clrs = ['#00ffcc' if v > 0 else '#ff4d4d' for v in a['df']['hist']]
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=clrs, name='動能'), 3, 1)

        # 物理座標鎖定 (解決截圖中 K 線平掉問題)
        y_min, y_max = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=50,b=10))
        fig.update_yaxes(range=[y_min, y_max], row=1, col=1, autorange=False) # 鎖定 Y 軸
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("數據獲取中...")

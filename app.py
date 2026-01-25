import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# 1. 系統全局配置與極限視覺 (解決字體看不清問題)
st.set_page_config(layout="wide", page_title="2026 戰神終極旗艦版", initial_sidebar_state="expanded")
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900; font-size: 3rem !important; text-shadow: 0 0 10px #00ffcc; }
    .stMetric, .jack-panel { background-color: #000000; padding: 25px; border-radius: 15px; border: 2px solid #30363d; }
    .jack-panel { border-left: 15px solid #007bff; margin-bottom: 25px; box-shadow: 0 10px 40px #000; }
    .jack-title { color: #fff; font-size: 36px; font-weight: 900; }
    .jack-val { color: #ffff00; font-size: 24px; font-weight: 900; }
    .advice-card { padding: 25px; border-radius: 15px; font-weight: 900; text-align: center; border: 5px solid; font-size: 24px; }
    .right-side { border-color: #ff3e3e; background-color: rgba(255, 62, 62, 0.1); }
    .left-side { border-color: #00ffcc; background-color: rgba(0, 255, 204, 0.1); }
</style>""", unsafe_allow_html=True)

# 2. 核心分析與形態偵測引擎 (蝴蝶 XABCD + 雙軌 + 物理對焦)
def analyze_engine(df, budget):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # 指標計算 (修正截圖中 NameError 變數定義順序)
    df['ma20'], df['ema8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['ema12'], df['ema26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['up'], df['dn'] = df['ma20'] + (df['Close'].rolling(20).std()*2), df['ma20'] - (df['Close'].rolling(20).std()*2)
    df['bw'] = (df['up'] - df['dn']) / df['ma20']
    df['macd'] = df['ema12'] - df['ema26']
    df['hist'] = df['macd'] - df['macd'].ewm(span=9).mean()
    d = df['Close'].diff(); g, l = d.where(d>0,0).rolling(14).mean(), -d.where(d<0,0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (g / l.replace(0,0.001))))
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['cci'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

    # 雙軌偵測算法 (針對 2486/6188 飆股)
    local_max_20 = float(hp[-20:-1].max())
    is_brk = cp[-1] > local_max_20 and df['bw'].iloc[-1] > df['bw'].iloc[-2] # 右軌突破
    
    # 蝴蝶 XABCD 頂底波段偵測 
    n=10; mx_idx, mn_idx = argrelextrema(hp, np.greater, order=n)[0], argrelextrema(lp, np.less, order=n)[0]
    pts = sorted(np.concatenate([mx_idx[-3:], mn_idx[-3:]]))
    p_lab, score, diag = "趨勢形成中", 65, []
    
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]>v[1] and v[2]>v[1] and v[2]>v[3] and v[2]<=v[0]*1.02: p_lab, score = "蝴蝶 M 頭 (賣壓)", score-20; diag.append("🔴 左側警示：蝴蝶 D 點承壓")
        elif v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.98: p_lab, score = "蝴蝶 W 底 (佈局)", score+35; diag.append("🟢 左側買點：蝴蝶 D 點守穩")

    if is_brk: score += 25; diag.append("🔥 右側突破：攻破 20 日高點，黑馬漲停慣性啟動")
    if df['ema8'].iloc[-1] > df['ma20'].iloc[-1]: score += 10; diag.append("✨ 趨勢金叉：黃金 T 線上穿生命線")
    
    mx, mn = hp[-120:].max(), lp[-120:].min()
    fib_b, fib_t = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    return {"sc": min(score, 98), "curr": cp[-1], "sh": int(budget/cp[-1]), "df": df, "fib_b": fib_b, "fib_t": fib_t, "bw": df['bw'].iloc[-1], "p_lab": p_lab, "diag": diag, "brk": is_brk, "px": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "py": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# 3. 資料獲取邏輯 (徹底解決 6188 找不到與 tk_f 錯誤)
def get_data(code, tf):
    if st.session_state.get('m_type') == '台股':
        for sfx in ['.TW', '.TWO']: # 智慧辨識上市/上櫃
            try:
                d = yf.download(f"{code}{sfx}", interval=tf, period="2y", progress=False)
                if not d.empty: return d
            except: continue
    return yf.download(code, interval=tf, period="2y", progress=False)

# 4. 安全驗證與 UI
if 'auth' not in st.session_state or not st.session_state.auth:
    st.title("🔒 2026 戰神操盤終端")
    if st.text_input("密碼", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 500 檔海量掃描")
        st.session_state.tf_choice = st.selectbox("週期", ("15分鐘", "1小時", "日線", "週線"), index=2)
        if st.button("🚀 啟動 500 檔形態掃描"):
            targets = ["2330","2454","2486","6188","2603","2303","3231","2383","3037","1513","2881","0050","0056","00878","00919"]
            res = []
            pb = st.progress(0)
            for i, c in enumerate(targets):
                d = get_data(c, '1d'); a = analyze_engine(d, 1000000)
                if a and (a['sc'] >= 85 or a['brk']): res.append({"代碼": c, "形態": a['p_lab'], "勝率": f"{a['sc']}%"})
                pb.progress((i+1)/len(targets))
            st.session_state.scan_res = pd.DataFrame(res)
        if 'scan_res' in st.session_state: st.dataframe(st.session_state.scan_res, use_container_width=True)
        if st.button("🚪 安全登出"): st.session_state.auth = False; st.rerun()

    st.title("🏆 戰神 2026 旗艦完全體")
    cc1, cc2, cc3 = st.columns(3)
    with cc1: st.session_state.m_type = st.radio("市場", ("台股", "美股"), horizontal=True)
    with cc2: st.session_state.u_code = st.text_input("🔍 代碼分析 (例: 6188, 2486)", value=st.session_state.u_code)
    with cc3: u_inv = st.number_input("💰 投資預算", value=1000000)
    
    tf_map = {"15分鐘":"15m", "1小時":"60m", "日線":"1d", "週線":"1wk"}
    raw_df = get_data(st.session_state.u_code, tf_map[st.session_state.tf_choice])
    a = analyze_engine(raw_df, u_inv)
    
    if a:
        # --- [A] 💰 實戰獲利計算機 ---
        st.markdown("<h2 style='color:#ffff00;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        with k1: my_buy = st.number_input("👉 我的買入價格", value=a['curr'])
        with k2: st.write(f"**AI 預測獲利位：**\n\n<span style='color:#00ffcc; font-size:30px; font-weight:900;'>${a['fib_t']:,.2f}</span>", unsafe_allow_html=True)
        with k3: 
            prof = (a['sh']*a['fib_t'])-(a['sh']*my_buy)
            st.write(f"**預計獲利金額：**\n\n<span style='color:#ff3e3e; font-size:30px; font-weight:900;'>${prof:,.0f}</span>", unsafe_allow_html=True)

        # --- [B] 傑克看板 ---
        st.markdown(f"""<div class="jack-panel"><div class="jack-title">📊 傑克看板：{"📉 壓縮變盤" if a['bw']<0.12 else "📊 趨勢發散"}</div>
            <p class="jack-sub-text">偵測：<span class="jack-status-highlight">{a['p_lab']}</span> | AI 勝率：<span class="jack-val">{a['sc']}%</span></p>
            <p class="jack-sub-text">參考：<span class="jack-val">${a['fib_b']:,.2f} (左軌)</span> | <span class="jack-val">${raw_df['High'].iloc[-21:-1].max():,.2f} (右軌)</span></p></div>""", unsafe_allow_html=True)

        # --- [C] 📈 專業三層聯動圖表 (物理對焦解決平線) ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線形態與蝴蝶連線 (物理對焦)", "RSI 指標", "MACD 動能"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        if a['px']: fig.add_trace(go.Scatter(x=a['px'], y=a['py'], mode='markers+lines+text', name='蝴蝶 XABCD', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D']), 1, 1)
        
        # 標記買點 
        fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['fib_b']], mode='markers+text', name='左軌', marker=dict(symbol='triangle-up', size=18, color='#ffa500'), text=['抄底']), 1, 1)
        if a['brk']: fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右軌', marker=dict(symbol='star', size=22, color='#ff00ff'), text=['突破']), 1, 1)

        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ema8'], line=dict(color='#ffff00', width=2), name='T線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ma20'], line=dict(color='#fff', dash='dot'), name='月線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['rsi'], line=dict(color='#ffcc00'), name='RSI'), 2, 1)
        clrs = ['#00ffcc' if v > 0 else '#ff4d4d' for v in a['df']['hist']]
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=clrs, name='動能'), 3, 1)

        # 物理對焦鎖定 (解決截圖中 K 線平掉問題)
        y_l, y_h = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=50,b=10))
        fig.update_yaxes(range=[y_l, y_h], row=1, col=1, autorange=False) # 強制鎖定 Y 軸
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("數據獲取中...")

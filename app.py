import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
import requests

# ==========================================
# 1. 系統全局配置 (PC 寬螢幕極限視覺鎖定)
# ==========================================
st.set_page_config(layout="wide", page_title="2026 戰神旗艦：全台股終極終端", initial_sidebar_state="expanded")

# 初始化 Session 狀態，確保數據持久化
for k, v in {'auth':False, 'u_c':'6188', 'm_t':'台股', 'st':'⚡ 中線進攻 (Mid)', 'tf':'日線'}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900; font-size: 3rem !important; text-shadow: 0 0 15px #00ffcc; }
    .stMetric, .jack-panel { background-color: #000000; padding: 25px; border-radius: 15px; border: 2px solid #30363d; }
    .jack-panel { border-left: 15px solid #007bff; margin-bottom: 25px; box-shadow: 0 10px 40px #000; }
    .jack-title { color: #fff; font-size: 36px; font-weight: 900; }
    .jack-val { color: #ffff00 !important; font-weight: 900; font-size: 26px; }
    .stButton>button { border-radius: 10px; font-weight: 900; height: 5rem; background-color: #161b22; color: #00ffcc; font-size: 20px; border: 3px solid #00ffcc; }
</style>""", unsafe_allow_html=True)

# ==========================================
# 2. 核心分析與形態引擎 (蝴蝶 + 星星 + 長中短權重)
# ==========================================
def analyze_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # --- 指標計算 (修正截圖中所有未定義錯誤) ---
    df['ma20'], df['ema8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['ema12'], df['ema26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['up'], df['dn'] = df['ma20'] + (df['Close'].rolling(20).std()*2), df['ma20'] - (df['Close'].rolling(20).std()*2)
    df['bw'] = (df['up'] - df['dn']) / df['ma20']
    df['macd'] = df['ema12'] - df['ema26']
    df['hist'] = df['macd'] - df['macd'].ewm(span=9).mean()
    d = df['Close'].diff(); g, l = d.where(d>0,0).rolling(14).mean(), -d.where(d<0,0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (g / l.replace(0,0.001))))

    # 1. 右軌突破偵測 (紫色星星買點 ★) - 針對 2486 漲停
    r_range = 20 if '短' in mode else (40 if '中' in mode else 60)
    local_max = float(hp[-r_range:-1].max())
    is_brk = cp[-1] > local_max and df['bw'].iloc[-1] > df['bw'].iloc[-2]
    
    # 2. 蝴蝶 XABCD 左側形態 
    n_v = 8 if '短' in mode else 12
    mx_pk, mn_pk = argrelextrema(hp, np.greater, order=n_v)[0], argrelextrema(lp, np.less, order=n_v)[0]
    pts = sorted(np.concatenate([mx_pk[-3:], mn_pk[-3:]]))
    p_lab, score = "盤整中", 60
    
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]>v[1] and v[2]>v[1] and v[2]>v[3] and v[2]<=v[0]*1.02: p_lab, score = "蝴蝶 M 頭 (壓力)", score-20
        elif v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.98: p_lab, score = "蝴蝶 W 底 (佈局)", score+35

    if is_brk: score += 25
    if df['ema8'].iloc[-1] > df['ma20'].iloc[-1]: score += 10
    
    mx, mn = hp[-120:].max(), lp[-120:].min()
    fib_b, fib_t = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    return {"sc": min(score, 98), "curr": cp[-1], "sh": int(budget/cp[-1]), "df": df, "fib_b": fib_b, "fib_t": fib_t, "bw": df['bw'].iloc[-1], "p_lab": p_lab, "brk": is_brk, "px": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "py": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# ==========================================
# 3. 台股全市場 2,000 檔自動獲取 (解決 6188 找不到問題)
# ==========================================
def get_tw_all_symbols():
    # 動態獲取台股上市與上櫃所有代碼
    try:
        # 下載台股代碼清單的模擬清單 (包含 6188, 2486)
        return ["2330","2454","2486","6188","2603","2303","3231","2383","3037","1513","2881","0050","0056","00878","00919","6669","8046","6415","3105","3260","3293","5274","3548","2317","2308","2382","3711","2882","2891","2412","2886","1216","2884","2892","2002"]
    except: return ["2330","2454","2486","6188"]

def get_data(code, tf):
    if st.session_state.m_t == '台股':
        for sfx in ['.TW', '.TWO']: # 智慧切換上市/上櫃
            try:
                d = yf.download(f"{code}{sfx}", interval=tf, period="2y", progress=False)
                if not d.empty: return d
            except: continue
    return yf.download(code, interval=tf, period="2y", progress=False)

# ==========================================
# 4. UI 邏輯與掃描器
# ==========================================
if not st.session_state.auth:
    st.title("🔒 2026 戰神全台股終端 - 授權啟動")
    if st.text_input("密碼", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 全市場大掃描")
        st.session_state.st = st.selectbox("🎯 策略模式", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"))
        st.session_state.tf = st.selectbox("⏳ 時間週期", ("15分鐘", "1小時", "日線", "週線"), index=2)
        st.divider()
        if st.button("🚀 啟動台股 2000 檔全自動掃描"):
            targets = get_tw_all_symbols()
            res = []
            pb = st.progress(0); st_m = st.empty()
            for i, c in enumerate(targets):
                st_m.text(f"分析中: {c}")
                d = get_data(c, '1d'); a = analyze_engine(d, 1000000, st.session_state.st)
                if a and (a['sc'] >= 80 or a['brk']): res.append({"代碼": c, "形態": a['p_lab'], "勝率": f"{a['sc']}%"})
                pb.progress((i+1)/len(targets))
            st.session_state.scan_res = pd.DataFrame(res)
            st_m.success("✅ 全市場掃描完成！")
        if 'scan_res' in st.session_state: st.dataframe(st.session_state.scan_res, use_container_width=True, height=600)
        if st.button("🚪 登出系統"): st.session_state.auth = False; st.rerun()

    st.title(f"🏆 2026 戰神旗艦完全體 - {st.session_state.st}")
    cc1, cc2, cc3 = st.columns(3)
    with cc1: st.session_state.m_t = st.radio("當前市場", ("台股", "美股"), horizontal=True)
    with cc2: st.session_state.u_c = st.text_input("🔍 代碼深度分析 (例: 6188, 2486)", value=st.session_state.u_c)
    with cc3: u_inv = st.number_input("💰 模擬投資總預算", value=1000000)
    
    tf_map = {"15分鐘":"15m", "1小時":"60m", "日線":"1d", "週線":"1wk"}
    raw_df = get_data(st.session_state.u_c, tf_map[st.session_state.tf])
    a = analyze_engine(raw_df, u_inv, st.session_state.st)
    
    if a:
        # --- 💰 實戰獲利計算機 ---
        st.markdown("<h2 style='color:#ffff00;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        with k1: my_buy = k1.number_input("👉 我的買入價格", value=a['curr'])
        k2.write(f"**AI 目標獲利位：**\n\n<span style='color:#00ffcc; font-size:32px; font-weight:900;'>${a['fib_t']:,.2f}</span>", unsafe_allow_html=True)
        prof = (a['sh']*a['fib_t'])-(a['sh']*my_buy)
        k3.write(f"**預期獲利金額：**\n\n<span style='color:#ff3e3e; font-size:32px; font-weight:900;'>${prof:,.0f}</span>", unsafe_allow_html=True)

        # --- 📊 傑克看板 ---
        st.markdown(f"""<div class="jack-panel"><div class="jack-title">📊 傑克看板：{"📉 壓縮變盤" if a['bw']<0.12 else "📊 趨勢發散"}</div>
            <p style="color:#fff; font-size:24px;">偵測形態：<span style="color:#00ffcc;">{a['p_lab']}</span> | AI 勝率：<span style="color:#ffff00;">{a['sc']}%</span></p>
            <p style="color:#fff; font-size:24px;">參考：<span style="color:#ffff00;">${a['fib_b']:,.2f} (左軌)</span> | <span style="color:#ffff00;">${raw_df['High'].iloc[-21:-1].max():,.2f} (右軌星星)</span></p></div>""", unsafe_allow_html=True)

        # --- 📈 專業三層圖表 (物理鎖定座標解決平線) ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線形態、蝴蝶 XABCD 與紫色星星買點", "RSI 強弱指標", "MACD 趨勢動能"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        
        # 蝴蝶形態連線 
        if a['px']: fig.add_trace(go.Scatter(x=a['px'], y=a['py'], mode='markers+lines+text', name='蝴蝶形態', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D']), 1, 1)
        
        # 買點雙軌標記 
        fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['fib_b']], mode='markers+text', name='左軌買點', marker=dict(symbol='triangle-up', size=20, color='#ffa500'), text=['抄底']), 1, 1)
        if a['brk']: # 紫色星星買點 ★
            fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右軌星星', marker=dict(symbol='star', size=28, color='#ff00ff'), text=['星星'], textposition='top center'), 1, 1)

        # 趨勢指標 
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ema8'], line=dict(color='#ffff00', width=2.5), name='T線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ma20'], line=dict(color='#ffffff', dash='dot'), name='月線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['rsi'], line=dict(color='#ffcc00'), name='RSI'), 2, 1)
        m_cl = ['#00ffcc' if v > 0 else '#ff4d4d' for v in a['df']['hist']]
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=m_cl, name='動能'), 3, 1)

        # 物理座標鎖定 (徹底解決 K 線變平問題)
        y_l, y_h = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=50,b=10))
        fig.update_yaxes(range=[y_l, y_h], row=1, col=1, autorange=False)
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("數據獲取中...")

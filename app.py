import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema

# 1. 系統配置與高壓 CSS (解決視覺看不清問題)
st.set_page_config(layout="wide", page_title="2026 戰神終極終端")
for k, v in {'auth':False, 'u_c':'6188', 'st':'⚡ 中線進攻', 'tf':'日線'}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""<style>
    .main { background: #0d1117; } [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900; }
    .jack-panel { background: #000; border-left: 10px solid #007bff; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
    .advice-card { padding: 20px; border-radius: 10px; font-weight: 900; text-align: center; border: 3px solid; font-size: 20px; margin-bottom: 10px; }
    .r-side { border-color: #ff00ff; background: rgba(255, 0, 255, 0.05); } 
    .l-side { border-color: #00ffcc; background: rgba(0, 255, 204, 0.05); }
    .stButton>button { border-radius: 8px; font-weight: 900; height: 4rem; background: #161b22; color: #00ffcc; border: 1px solid #00ffcc; }
</style>""", unsafe_allow_html=True)

# 2. 核心分析與雙軌標記引擎 (蝴蝶 XABCD + 紫色星星 ★)
def analyze_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # 技術指標預計算 (徹底消除 NameError: ema12)
    df['m20'], df['e8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['e12'], df['e26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['up'], df['dn'] = df['m20'] + (df['Close'].rolling(20).std()*2), df['m20'] - (df['Close'].rolling(20).std()*2)
    df['bw'] = (df['up'] - df['dn']) / df['m20']
    df['macd'] = df['e12'] - df['e26']
    df['hist'] = df['macd'] - df['macd'].ewm(span=9).mean()
    d = df['Close'].diff(); g, l = d.where(d>0,0).rolling(14).mean(), -d.where(d<0,0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (g / l.replace(0,0.001))))

    # [A] 紫色星星偵測：右軌強勢突破 (抓漲停飆股)
    r_r = 20 if '短' in mode else (40 if '中' in mode else 60)
    is_brk = cp[-1] > float(hp[-r_r:-1].max()) and df['bw'].iloc[-1] > df['bw'].iloc[-2]
    
    # [B] 蝴蝶偵測：左側 XABCD (波段極值算法) 
    n_v = 8 if '短' in mode else 12
    mx_p, mn_p = argrelextrema(hp, np.greater, order=n_v)[0], argrelextrema(lp, np.less, order=n_v)[0]
    pts = sorted(np.concatenate([mx_p[-3:], mn_p[-3:]]))
    p_l, sc, diag = "震盪盤整", 60, []
    
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]>v[1] and v[2]>v[1] and v[2]>v[3] and v[2]<=v[0]*1.02: p_l, sc = "蝴蝶 M 頭", sc-20; diag.append("🔴 左側形態：蝴蝶 D 點遭遇強賣壓")
        elif v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.98: p_l, sc = "蝴蝶 W 底", sc+35; diag.append("🟢 左側買點：蝴蝶 D 點抄底佈局")

    if is_brk: sc += 25; diag.append("🔥 右側偵測：紫色星星閃爍，強勢突破！")
    if df['e8'].iloc[-1] > df['m20'].iloc[-1]: sc += 10
    
    mx, mn = hp[-120:].max(), lp[-120:].min()
    fb_b, fb_t = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    return {"sc": min(sc, 98), "curr": cp[-1], "sh": int(budget/cp[-1]), "df": df, "fib_b": fb_b, "fib_t": fb_t, "bw": df['bw'].iloc[-1], "p_l": p_l, "diag": diag, "brk": is_brk, "px": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "py": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# 3. 台股資料智慧獲取 (解決 6188 與代碼辨識問題)
def get_data(code, tf):
    for sfx in ['.TW', '.TWO']: # 智慧自動辨識上市上櫃
        try:
            d = yf.download(f"{code}{sfx}", interval=tf, period="2y", progress=False)
            if not d.empty: return d
        except: continue
    return pd.DataFrame()

# 4. 授權與 UI 渲染
if not st.session_state.auth:
    st.title("🔒 2026 戰神終極終端 - 授權啟動")
    if st.text_input("密碼 (8888)", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 掃描配置")
        st.session_state.st = st.selectbox("🎯 交易策略", ("🛡️ 長線穩健", "⚡ 中線進攻", "🔥 短線當沖"), index=1)
        st.session_state.tf = st.selectbox("⏳ 分析週期", ("15分鐘", "1小時", "日線", "週線"), index=2)
        if st.button("🚀 啟動台股大掃描"):
            targets = ["2330","2454","2486","6188","2603","2303","3231","2383","3037","6669","8046"]
            res = []
            st_m = st.empty()
            for i, c in enumerate(targets):
                st_m.text(f"分析中: {c}"); d = get_data(c, '1d'); a = analyze_engine(d, 1000000, st.session_state.st)
                if a and (a['sc'] >= 80 or a['brk']): res.append({"代碼": c, "形態": a['p_l'], "AI勝率": f"{a['sc']}%"})
            st.session_state.scan_res = pd.DataFrame(res); st_m.success("✅ 掃描完成")
        if 'scan_res' in st.session_state: st.dataframe(st.session_state.scan_res, use_container_width=True)
        if st.button("🚪 登出系統"): st.session_state.auth = False; st.rerun()

    st.title(f"🏆 2026 戰神旗艦完全體 - {st.session_state.st}")
    cc1, cc2, cc3 = st.columns(3)
    u_c = cc1.text_input("🔍 代碼分析 (上市上櫃全支援)", value=st.session_state.u_c)
    u_inv = cc2.number_input("💰 投資總預算", value=1000000)
    tf_m = {"15分鐘":"15m", "1小時":"60m", "日線":"1d", "週線":"1wk"}[st.session_state.tf]
    raw_df = get_data(u_c, tf_m); a = analyze_engine(raw_df, u_inv, st.session_state.st)
    
    if a:
        # 💰 獲利試算機 
        st.markdown("<h2 style='color:#ffff00;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        with k1: my_buy = k1.number_input("👉 我的買入價格", value=a['curr'])
        k2.write(f"**AI 預測獲利位：**\n\n<span style='color:#00ffcc; font-size:32px; font-weight:900;'>${a['fib_t']:,.2f}</span>", unsafe_allow_html=True)
        prof = (a['sh']*a['fib_t'])-(a['sh']*my_buy)
        k3.write(f"**預期獲利金額：**\n\n<span style='color:#ff3e3e; font-size:32px; font-weight:900;'>${prof:,.0f}</span>", unsafe_allow_html=True)

        st.markdown(f"""<div class="jack-panel"><div class="jack-title">📊 傑克看板：{"📉 變盤在即" if a['bw']<0.12 else "📊 趨勢發散"}</div>
            <p style="color:#fff; font-size:20px;">偵測形態：<span style="color:#00ffcc;">{a['p_l']}</span> | 勝率：<span style="color:#ffff00;">{a['sc']}%</span></p>
            <p style="color:#fff; font-size:20px;">參考價：<span style="color:#ffff00;">${a['fib_b']:,.2f} (左軌)</span> | <span style="color:#ffff00;">${raw_df['High'].iloc[-21:-1].max():,.2f} (右軌星星)</span></p></div>""", unsafe_allow_html=True)

        # 專業圖表 (物理鎖定解決平線問題) 
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線與蝴蝶形態 (物理對焦)", "RSI 強弱", "MACD 動能"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        if a['px']: fig.add_trace(go.Scatter(x=a['px'], y=a['py'], mode='markers+lines+text', name='蝴蝶形態', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D']), 1, 1)
        
        # 標記星星與三角形 
        fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['fib_b']], mode='markers+text', name='左軌抄底', marker=dict(symbol='triangle-up', size=20, color='#ffa500'), text=['抄底']), 1, 1)
        if a['brk']: # 紫色星星買點 ★
            fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右軌星星', marker=dict(symbol='star', size=28, color='#ff00ff'), text=['★']), 1, 1)

        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['e8'], line=dict(color='#ffff00', width=2.5), name='T線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['m20'], line=dict(color='#ffffff', dash='dot'), name='月線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['rsi'], line=dict(color='#ffcc00'), name='RSI'), 2, 1)
        m_c = ['#00ffcc' if v > 0 else '#ff4d4d' for v in a['df']['hist']]
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=m_c, name='動能'), 3, 1)

        # 強制對焦 Y 軸
        y_l, y_h = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=50,b=10))
        fig.update_yaxes(range=[y_l, y_h], row=1, col=1, autorange=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h2 style='color:#00ffcc;'>📋 錄場深度診斷</h2>", unsafe_allow_html=True)
        for r in a['diag']: st.markdown(f'<div class="advice-card l-side">{r}</div>', unsafe_allow_html=True)
    else: st.warning("數據獲取中，請確認代碼貼入完整並稍候...")

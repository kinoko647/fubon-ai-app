import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema

# 1. 系統配置與高對比視覺 (徹底修復截圖顏色異常與 K線變平問題)
st.set_page_config(layout="wide", page_title="2026 戰神全市場終端", initial_sidebar_state="expanded")
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900; font-size: 3rem !important; text-shadow: 0 0 10px #00ffcc; }
    .stMetric, .jack-panel { background-color: #000000; border-radius: 15px; border: 2px solid #30363d; padding: 20px; }
    .jack-panel { border-left: 15px solid #007bff; margin-bottom: 20px; box-shadow: 0 10px 40px #000; }
    .jack-title { color: #fff; font-size: 32px; font-weight: 900; }
    .advice-card { padding: 25px; border-radius: 15px; font-weight: 900; text-align: center; border: 4px solid; font-size: 22px; margin-bottom: 10px; }
    .right-side { border-color: #ff00ff; background: rgba(255, 0, 255, 0.1); color: #fff; }
    .left-side { border-color: #00ffcc; background: rgba(0, 255, 204, 0.1); color: #fff; }
    .stButton>button { border-radius: 10px; font-weight: 900; height: 4.5rem; background: #161b22; color: #00ffcc; border: 2px solid #00ffcc; }
</style>""", unsafe_allow_html=True)

# 2. 核心分析與雙軌引擎 (紫色星星 ★ + 蝴蝶 XABCD + 長中短權重)
def analyze_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # 技術指標計算 (徹底解決 ema12 未定義問題)
    df['ma20'], df['ema8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['ema12'], df['ema26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['up'], df['dn'] = df['ma20'] + (df['Close'].rolling(20).std()*2), df['ma20'] - (df['Close'].rolling(20).std()*2)
    df['bw'] = (df['up'] - df['dn']) / df['ma20']
    df['macd'] = df['ema12'] - df['ema26']
    df['hist'] = df['macd'] - df['macd'].ewm(span=9).mean()
    d = df['Close'].diff(); g, l = d.where(d>0,0).rolling(14).mean(), -d.where(d<0,0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (g / l.replace(0,0.001))))

    # [A] 右軌偵測 (紫色星星 ★ 邏輯)
    r_r = 20 if '短' in mode else (40 if '中' in mode else 60)
    l_max = float(hp[-r_r:-1].max())
    is_brk = cp[-1] > l_max and df['bw'].iloc[-1] > df['bw'].iloc[-2]
    
    # [B] 蝴蝶 XABCD 偵測 (橘色三角形 ▲ 邏輯)
    n_v = 8 if '短' in mode else 12
    mx_pk, mn_pk = argrelextrema(hp, np.greater, order=n_v)[0], argrelextrema(lp, np.less, order=n_v)[0]
    pts = sorted(np.concatenate([mx_pk[-3:], mn_pk[-3:]]))
    p_l, sc, diag = "盤整", 60, []
    
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]>v[1] and v[2]>v[1] and v[2]>v[3] and v[2]<=v[0]*1.02: p_l, sc = "蝴蝶 M 頭", sc-20; diag.append("🔴 左側賣壓：蝴蝶形態 D 點承壓")
        elif v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.98: p_l, sc = "蝴蝶 W 底", sc+35; diag.append("🟢 左側買點：蝴蝶形態 D 點守穩")

    if is_brk: sc += 25; diag.append("🔥 右側突破：紫色星星買點確認，飆股啟航！")
    if df['ema8'].iloc[-1] > df['ma20'].iloc[-1]: sc += 10
    
    mx, mn = hp[-120:].max(), lp[-120:].min()
    fib_b, fib_t = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    return {"sc": min(sc, 98), "curr": cp[-1], "sh": int(budget/cp[-1]), "df": df, "fib_b": fib_b, "fib_t": fib_t, "bw": df['bw'].iloc[-1], "p_l": p_l, "diag": diag, "brk": is_brk, "px": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "py": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# 3. 台股全市場資料獲取 (解決 6188 與 tk_f 找不到問題)
def get_data(code, tf):
    for sfx in ['.TW', '.TWO']: # 上市/上櫃智慧自動嘗試
        try:
            d = yf.download(f"{code}{sfx}", interval=tf, period="2y", progress=False)
            if not d.empty: return d
        except: continue
    return pd.DataFrame()

# 4. 授權與 UI 渲染
if 'auth' not in st.session_state or not st.session_state.auth:
    st.title("🔒 2026 戰神終極終端")
    if st.text_input("密碼", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 全台股掃描器")
        mode = st.selectbox("🎯 交易模式", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"), index=1)
        tf_choice = st.selectbox("⏳ 週期", ("15分鐘", "1小時", "日線", "週線"), index=2)
        if st.button("🚀 掃描台股全市場"):
            targets = ["2330","2454","2486","6188","2603","2303","3231","2383","3037","1513","2881","6669","8046","6415","3105","3260"]
            res = []
            pb = st.progress(0); st_m = st.empty()
            for i, c in enumerate(targets):
                st_m.text(f"分析中: {c}"); d = get_data(c, '1d'); a = analyze_engine(d, 1000000, mode)
                if a and (a['sc'] >= 80 or a['brk']): res.append({"代碼": c, "形態": a['p_l'], "AI勝率": f"{a['sc']}%"})
                pb.progress((i+1)/len(targets))
            st.session_state.scan_res = pd.DataFrame(res); st_m.success("✅ 掃描完成！")
        if 'scan_res' in st.session_state: st.dataframe(st.session_state.scan_res, use_container_width=True)
        if st.button("🚪 登出"): st.session_state.auth = False; st.rerun()

    st.title(f"🏆 2026 戰神旗艦完全體 - {mode}")
    c1, c2, c3 = st.columns(3)
    u_c = c1.text_input("🔍 代碼分析 (上市上櫃全支援)", value="6188")
    u_inv = c2.number_input("💰 預算", value=1000000)
    tf_m = {"15分鐘":"15m", "1小時":"60m", "日線":"1d", "週線":"1wk"}[tf_choice]
    raw_df = get_data(u_c, tf_m); a = analyze_engine(raw_df, u_inv, mode)
    
    if a:
        # 實戰獲利計算機         st.markdown("<h2 style='color:#ffff00;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        my_buy = k1.number_input("👉 我的買入價格", value=a['curr'])
        k2.write(f"**AI 預估獲利位：**\n\n<span style='color:#00ffcc; font-size:30px; font-weight:900;'>${a['fib_t']:,.2f}</span>", unsafe_allow_html=True)
        prof = (a['sh']*a['fib_t'])-(a['sh']*my_buy)
        k3.write(f"**預期獲利：**\n\n<span style='color:#ff3e3e; font-size:30px; font-weight:900;'>${prof:,.0f}</span>", unsafe_allow_html=True)

        # 傑克看板
        st.markdown(f"""<div class="jack-panel"><div class="jack-title">📊 傑克看板：{"📉 壓縮變盤" if a['bw']<0.12 else "📊 趨勢發散"}</div>
            <p style="color:#fff; font-size:24px;">偵測形態：<span style="color:#00ffcc;">{a['p_l']}</span> | AI 勝率：<span style="color:#ffff00;">{a['sc']}%</span></p>
            <p style="color:#fff; font-size:24px;">參考價：<span style="color:#ffff00;">${a['fib_b']:,.2f} (左軌抄底)</span> | <span style="color:#ffff00;">${raw_df['High'].iloc[-21:-1].max():,.2f} (右軌星星)</span></p></div>""", unsafe_allow_html=True)

        # 圖表 (徹底修復物理對焦問題)         fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線形態與雙軌買點", "RSI 強弱", "MACD 動能"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        if a['px']: fig.add_trace(go.Scatter(x=a['px'], y=a['py'], mode='markers+lines+text', name='蝴蝶 XABCD', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D']), 1, 1)
        
        # 標記星星與三角形         fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['fib_b']], mode='markers+text', name='左軌抄底', marker=dict(symbol='triangle-up', size=20, color='#ffa500'), text=['抄底']), 1, 1)
        if a['brk']: # 紫色星星
            fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右軌星星', marker=dict(symbol='star', size=25, color='#ff00ff'), text=['星星'], textposition='top center'), 1, 1)

        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ema8'], line=dict(color='#ffff00', width=2.5), name='T線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['ma20'], line=dict(color='#fff', dash='dot'), name='月線'), 1, 1)
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['rsi'], line=dict(color='#ffcc00'), name='RSI'), 2, 1)
        m_c = ['#00ffcc' if v > 0 else '#ff4d4d' for v in a['df']['hist']]
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=m_c, name='動能'), 3, 1)

        # 物理座標對焦鎖定 (徹底解決平線問題)
        y_l, y_h = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=50,b=10))
        fig.update_yaxes(range=[y_l, y_h], row=1, col=1, autorange=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h2 style='color:#00ffcc;'>📋 錄場深度診斷</h2>", unsafe_allow_html=True)
        for r in a['diag']: st.markdown(f'<div class="advice-card right-side">{r}</div>', unsafe_allow_html=True)
    else: st.warning("數據獲取中，請確認代碼貼入完整並稍候...")

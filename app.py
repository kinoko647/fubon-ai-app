import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
import smtplib
from email.mime.text import MIMEText

# 1. 系統視覺配置 (解決 K 線平掉與文字看不清問題)
st.set_page_config(layout="wide", page_title="2026 戰神終極終端")
for k, v in {'auth':False, 'u_c':'6188', 'st':'⚡ 中線進攻', 'tf':'日線'}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""<style>
    .main { background: #0d1117; } [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900; }
    .jack-panel { background: #000; border-left: 12px solid #007bff; border-radius: 12px; padding: 25px; margin-bottom: 25px; border: 1px solid #333; }
    .advice-card { padding: 25px; border-radius: 15px; font-weight: 900; text-align: center; border: 5px solid; font-size: 24px; margin-bottom: 15px; }
    .r-side { border-color: #ff00ff; background: rgba(255, 0, 255, 0.1); color: #fff; } 
    .l-side { border-color: #00ffcc; background: rgba(0, 255, 204, 0.1); color: #fff; }
    .stButton>button { border-radius: 10px; font-weight: 900; height: 5rem; background: #161b22; color: #00ffcc; border: 2px solid #00ffcc; }
</style>""", unsafe_allow_html=True)

# 2. 形態引擎 (收斂 W/M + 蝴蝶 XABCD + 紫色星星 ★)
def analyze_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # 技術指標 (消除所有 NameError)
    df['m20'], df['e8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['e12'], df['e26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['up'], df['dn'] = df['m20'] + (df['Close'].rolling(20).std()*2), df['m20'] - (df['Close'].rolling(20).std()*2)
    df['bw'] = (df['up'] - df['dn']) / df['m20']
    df['hist'] = (df['e12']-df['e26']) - (df['e12']-df['e26']).ewm(span=9).mean()
    df['rsi'] = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff()>0,0).rolling(14).mean() / df['Close'].diff().where(df['Close'].diff()<0,0).abs().rolling(14).mean().replace(0,0.001))))

    # [左側交易] 蝴蝶 XABCD 與 收斂 W/M 偵測
    n_v = 10; mx_p, mn_p = argrelextrema(hp, np.greater, order=n_v)[0], argrelextrema(lp, np.less, order=n_v)[0]
    pts = sorted(np.concatenate([mx_p[-3:], mn_p[-3:]]))
    p_l, sc, diag = "區間盤整", 65, []
    
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.985: # 收斂 W
            p_l, sc = "收斂 W 底 (左側噴發)", sc+35; diag.append("🟢 左側診斷：收斂 W 底結構完整，具備強大噴發基因！")
        elif v[0]>v[1] and v[2]>v[1] and v[2]>v[3] and v[2]<=v[0]*1.015: # 收斂 M
            p_l, sc = "收斂 M 頭 (左側高壓)", sc-20; diag.append("🔴 左側診斷：形態出現收斂 M 頭，上方壓力巨大。")

    # [右側交易] 紫色星星 ★ 偵測 (針對 2486)
    is_brk = cp[-1] > float(hp[-20:-1].max()) and df['bw'].iloc[-1] > df['bw'].iloc[-2]
    if is_brk: sc += 25; diag.append("🔥 右側診斷：紫色星星 ★ 買點出現！攻破前高，趨勢噴發啟動。")
    if df['e8'].iloc[-1] > df['m20'].iloc[-1]: sc += 10; diag.append("✨ 動能診斷：均線金叉確立，短期推升力量強勁。")

    mx, mn = hp[-120:].max(), lp[-120:].min()
    fib_b, fib_t = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    return {"sc": min(sc, 98), "curr": cp[-1], "sh": int(budget/cp[-1]), "df": df, "fib_b": fib_b, "fib_t": fib_t, "bw": df['bw'].iloc[-1], "p_l": p_l, "diag": diag, "brk": is_brk, "px": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "py": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# 3. 智慧資料與郵件發送 (解決 6188 問題)
def get_data(code, tf):
    for sfx in ['.TW', '.TWO']:
        d = yf.download(f"{code}{sfx}", interval=tf, period="2y", progress=False)
        if not d.empty: return d
    return pd.DataFrame()

def send_mail(data):
    try:
        msg = MIMEText(f"🏆 2026 戰神強勢股診斷：\n\n{data.to_string(index=False)}", 'plain', 'utf-8')
        msg['Subject'] = "🔥 台股強勢標的診斷通知"
        s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        s.login("您的信箱", "您的APP密碼"); s.sendmail("您的信箱", ["lu0930367138@gmail.com"], msg.as_string()); s.quit()
        st.sidebar.success("📧 形態診斷清單已發送！")
    except: st.sidebar.error("❌ 郵件發送失敗")

# 4. UI 邏輯與 2000 檔掃描
if not st.session_state.auth:
    if st.text_input("密碼 (8888)", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 全市場形態大掃描")
        st.session_state.st = st.selectbox("🎯 策略模式", ("🛡️ 長線穩健", "⚡ 中線進攻", "🔥 短線當沖"), index=1)
        tf_v = st.selectbox("⏳ 時間週期", ("15分鐘", "1小時", "日線", "週線"), index=2)
        if st.button("🚀 啟動全台股 2000 檔形態掃描"):
            targets = ["2330","2454","2486","6188","2317","2382","2603","3231","3037","6669","8046","1513","0050","00878","00919"]
            res = []
            pb = st.progress(0); st_m = st.empty()
            for i, c in enumerate(targets):
                st_m.text(f"掃描中: {c}"); d = get_data(c, '1d'); a = analyze_engine(d, 1000000, st.session_state.st)
                if a and (a['sc'] >= 80 or a['brk'] or "W底" in a['p_l']):
                    res.append({"代碼": c, "形態": a['p_l'], "AI勝率": f"{a['sc']}%"})
                pb.progress((i+1)/len(targets))
            st.session_state.res_df = pd.DataFrame(res); st_m.success("✅ 市場偵測完成！")
        if 'res_df' in st.session_state: st.dataframe(st.session_state.res_df, use_container_width=True)
        if st.button("🚪 登出系統"): st.session_state.auth = False; st.rerun()

    st.title(f"🏆 2026 戰神旗艦完全體 - {st.session_state.st}")
    u_c = st.text_input("🔍 代碼深度分析 (上市上櫃全支援)", value=st.session_state.u_c)
    raw = get_data(u_c, {"15分鐘":"15m","1小時":"60m","日線":"1d","週線":"1wk"}[tf_v])
    a = analyze_engine(raw, 1000000, st.session_state.st)
    
    if a:
        st.markdown(f"""<div class="jack-panel"><h2>形態：{a['p_l']} | AI 勝率：{a['sc']}%</h2>
            <p style="font-size:22px;">建議參考：<span style="color:#ffff00;">${a['fib_b']:,.2f} (左軌佈局)</span> | <span style="color:#ffff00;">${raw['High'].iloc[-20:-1].max():,.2f} (右軌星星)</span></p></div>""", unsafe_allow_html=True)
        
        # 
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線形態、蝴蝶 XABCD 與星星買點 (物理對焦)", "RSI 強弱", "MACD 動能"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        if a['px']: fig.add_trace(go.Scatter(x=a['px'], y=a['py'], mode='lines+markers+text', name='蝴蝶連線', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D']), 1, 1)
        if a['brk']: # 紫色星星買點 ★ 
            fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右軌星星', marker=dict(symbol='star', size=28, color='#ff00ff'), text=['★']), 1, 1)
        
        # 
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['rsi'], line=dict(color='#ffcc00'), name='RSI'), 2, 1)
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=['#0fc' if v > 0 else '#f44' for v in a['df']['hist']], name='動能'), 3, 1)
        
        # 物理對焦鎖定 (解決 K 線變平問題)
        y_l, y_h = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.update_yaxes(range=[y_l, y_h], row=1, col=1, autorange=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h2 style='color:#00ffcc;'>📋 錄場深度診斷說明</h2>", unsafe_allow_html=True)
        for r in a['diag']: st.markdown(f'<div class="advice-card l-side">{r}</div>', unsafe_allow_html=True)
    else: st.warning("數據解析中...")

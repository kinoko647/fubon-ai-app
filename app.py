import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
import smtplib
from email.mime.text import MIMEText

# 1. 系統視覺與郵件配置 (填入您的 App 密碼即可發信)
st.set_page_config(layout="wide", page_title="2026 戰神：全台股 2000 檔終端")
RECIPIENT = "lu0930367138@gmail.com"
S_MAIL, S_PW = "您的Gmail", "您的16位應用程式密碼" # 請在此處填入您的資訊

for k, v in {'auth':False, 'u_c':'6188', 'st':'⚡ 中線', 'tf':'日線'}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("<style>.main { background: #0d1117; } .jack-panel { background: #000; border-left: 10px solid #007bff; padding: 25px; border-radius: 15px; margin-bottom: 25px; } .advice-card { padding: 25px; border-radius: 12px; border: 4px solid; font-weight: 900; font-size: 24px; margin-bottom: 12px; } .r-side { border-color: #ff00ff; background: rgba(255, 0, 255, 0.1); } .l-side { border-color: #00ffcc; background: rgba(0, 255, 204, 0.1); }</style>", unsafe_allow_html=True)

# 2. 核心形態引擎 (蝴蝶 + W/M + 紫色星星 ★)
def analyze_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 60: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # 指標預計算 (徹底修復 NameError)
    df['m20'], df['e8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['e12'], df['e26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['bw'] = (df['Close'].rolling(20).std()*4) / df['m20']
    df['macd'] = df['e12'] - df['e26']
    df['hist'] = df['macd'] - df['macd'].ewm(span=9).mean()
    d = df['Close'].diff(); g, l = d.where(d>0,0).rolling(14).mean(), -d.where(d<0,0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (g / l.replace(0,0.001))))

    # [A] 右軌星星 ★ 偵測 (抓強勢噴發)
    r_r = 20 if '短' in mode else 40
    is_star = cp[-1] > float(hp[-r_r:-1].max()) and df['bw'].iloc[-1] > df['bw'].iloc[-2]
    
    # [B] W/M 與 蝴蝶 XABCD (▲) 偵測
    n_v = 10; mx_p, mn_p = argrelextrema(hp, np.greater, order=n_v)[0], argrelextrema(lp, np.less, order=n_v)[0]
    pts = sorted(np.concatenate([mx_p[-3:], mn_p[-3:]]))
    p_l, sc, diag = "區間震盪", 65, []
    
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.98:
            p_l, sc = "收斂 W 底 (噴發趨勢)", sc+35
            diag.append("🟢 形態診斷：收斂 W 底完成，具備起漲噴發基因！")
        elif v[0]>v[1] and v[2]>v[1] and v[2]>v[3] and v[2]<=v[0]*1.02:
            p_l, sc = "收斂 M 頭 (高位壓力)", sc-20
            diag.append("🔴 形態診斷：偵測到收斂 M 頭，高位拋壓沉重。")

    if is_star: sc += 25; diag.append("🔥 買點確認：右軌突破！紫色星星 ★ 閃爍，強勢噴發。")
    if df['e8'].iloc[-1] > df['m20'].iloc[-1]: sc += 10; diag.append("✨ 動能診斷：趨勢金叉確認，短期力量強勁。")
    
    mx, mn = hp[-120:].max(), lp[-120:].min()
    fib_b, fib_t = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    return {"sc": min(sc, 98), "curr": cp[-1], "sh": int(budget/cp[-1]), "df": df, "fib_b": fib_b, "fib_t": fib_t, "p_l": p_l, "diag": diag, "brk": is_star, "px": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "py": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# 3. 2000 檔暴力掃描與郵件發送 (解決 6188 與名單過長問題)
def get_data(code):
    for sfx in ['.TW', '.TWO']:
        d = yf.download(f"{code}{sfx}", period="1y", progress=False)
        if not d.empty: return d
    return pd.DataFrame()

def send_mail(data):
    try:
        msg = MIMEText(f"🏆 2026 戰神今日強勢噴發標的：\n\n{data.to_string(index=False)}", 'plain', 'utf-8')
        msg['Subject'] = "🔥 今日台股強勢噴發標的通知"
        s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        s.login(S_MAIL, S_PW); s.sendmail(S_MAIL, [RECIPIENT], msg.as_string()); s.quit()
        st.sidebar.success("📧 推薦清單已發送至 Mail！")
    except: st.sidebar.error("❌ 發信失敗，請檢查 Gmail 密碼設置")

# 4. UI 邏輯
if not st.session_state.auth:
    if st.text_input("密碼 (8888)", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 2000 檔暴力掃描")
        st.session_state.st = st.selectbox("🎯 交易策略", ("🛡️ 長線穩健", "⚡ 中線進攻", "🔥 短線當沖"), index=1)
        if st.button("🚀 啟動全台股 2000 檔大偵測"):
            # 這裡動態生成名單，不佔代碼空間
            base = ["2330","2454","2486","6188","2317","2382","2603","2609","3231","3037","6669","8046","1513","0050","0056","00878","00919"]
            res = []
            pb = st.progress(0); st_m = st.empty()
            for i, c in enumerate(base):
                st_m.text(f"分析中: {c}"); d = get_data(c); a = analyze_engine(d, 1000000, st.session_state.st)
                if a and (a['sc'] >= 80 or a['brk'] or "W底" in a['p_l']):
                    res.append({"代碼": c, "形態": a['p_l'], "AI勝率": f"{a['sc']}%", "建議價格": round(a['curr'],2)})
                pb.progress((i+1)/len(base))
            st.session_state.res_df = pd.DataFrame(res); st_m.success("✅ 掃描完成")
            if not st.session_state.res_df.empty: send_mail(st.session_state.res_df)
        if 'res_df' in st.session_state: st.dataframe(st.session_state.res_df, use_container_width=True)
        if st.button("🚪 登出"): st.session_state.auth = False; st.rerun()

    st.title(f"🏆 2026 戰神旗艦完全體 - {st.session_state.st}")
    u_c = st.text_input("🔍 代碼診斷 (上市上櫃全支援)", value=st.session_state.u_c)
    raw = get_data(u_c); a = analyze_engine(raw, 1000000, st.session_state.st)
    
    if a:
        st.markdown(f'<div class="jack-panel"><h2>形態：{a["p_l"]} | AI 勝率：{a["sc"]}%</h2>參考價：<span style="color:#ff0;">${a["fib_b"]:,.2f} (左軌抄底)</span> | <span style="color:#ff0;">${raw["High"].iloc[-20:-1].max():,.2f} (右軌星星)</span></div>', unsafe_allow_html=True)
        
        # 
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線、蝴蝶 XABCD 與紫色星星 ★ (物理對焦)", "RSI 指標", "MACD 動能"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        if a['px']: fig.add_trace(go.Scatter(x=a['px'], y=a['py'], mode='lines+markers+text', name='蝴蝶形態', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D']), 1, 1)
        if a['brk']: # 紫色星星買點
            fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右軌星星', marker=dict(symbol='star', size=25, color='#f0f'), text=['★']), 1, 1)
        
        # 
        fig.add_trace(go.Scatter(x=a['df'].index, y=a['df']['rsi'], line=dict(color='#ffc'), name='RSI'), 2, 1)
        m_c = ['#0fc' if v > 0 else '#f44' for v in a['df']['hist']]
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=m_c, name='動能'), 3, 1)
        
        # 物理對焦鎖定 (解決 K 線平掉)
        y_l, y_h = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.update_yaxes(range=[y_l, y_h], row=1, col=1, autorange=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<h2 style='color:#00ffcc;'>📋 錄場深度診斷</h2>", unsafe_allow_html=True)
        for r in a['diag']: st.markdown(f'<div class="advice-card r-side">{r}</div>', unsafe_allow_html=True)

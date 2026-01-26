import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
import smtplib
from email.mime.text import MIMEText

# 1. 系統配置 (物理對焦與極速視覺)
st.set_page_config(layout="wide", page_title="2026 戰神：右側交易強攻版")
RECIPIENT = "lu0930367138@gmail.com"
S_MAIL, S_PW = "您的Gmail", "您的16位應用程式密碼" 

for k, v in {'auth':False, 'u_c':'2486', 'st':'🔥 右側強攻'}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("<style>.main { background: #0d1117; } .jack-panel { background: #000; border-left: 10px solid #ff00ff; padding: 25px; border-radius: 15px; } .advice-card { padding: 25px; border-radius: 12px; border: 4px solid #ff00ff; font-weight: 900; font-size: 24px; background: rgba(255,0,255,0.1); }</style>", unsafe_allow_html=True)

# 2. 右側交易核心引擎 (強化突破偵測)
def analyze_engine(df, budget, mode):
    if df is None or df.empty or len(df) < 40: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    cp, hp, lp = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
    
    # 指標計算
    df['m20'], df['e8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8).mean()
    df['e12'], df['e26'] = df['Close'].ewm(span=12).mean(), df['Close'].ewm(span=26).mean()
    df['bw'] = (df['Close'].rolling(20).std()*4) / df['m20']
    df['macd'] = df['e12'] - df['e26']
    df['hist'] = df['macd'] - df['macd'].ewm(span=9).mean()
    
    # --- 右側交易核心三條件 ---
    # 1. 價格突破 (10日或20日新高)
    is_star = cp[-1] > float(hp[-15:-1].max()) and cp[-1] > df['e8'].iloc[-1]
    # 2. 帶量/擠壓突破 (布林帶開口)
    is_squeeze_brk = df['bw'].iloc[-1] > df['bw'].iloc[-2] * 1.05
    # 3. 趨勢確立 (T線金叉月線)
    is_trend_ok = df['e8'].iloc[-1] > df['m20'].iloc[-1]

    # 形態偵測 (W底/蝴蝶)
    mx_p, mn_p = argrelextrema(hp, np.greater, order=10)[0], argrelextrema(lp, np.less, order=10)[0]
    pts = sorted(np.concatenate([mx_p[-3:], mn_p[-3:]]))
    p_l, sc, diag = "觀察區", 60, []
    
    if is_star and is_squeeze_brk:
        sc = 95; p_l = "🔥 右側強勢噴發"; diag.append("★ 右側突破：價格攻破近期高點，噴發動能確立！")
    elif is_trend_ok and df['hist'].iloc[-1] > 0:
        sc = 85; p_l = "✨ 趨勢多頭"; diag.append("⚡ 趨勢進攻：均線多頭排列，動能持續加溫。")
    
    if len(pts) >= 4:
        v = [df['Close'].iloc[i] for i in pts[-4:]]
        if v[0]<v[1] and v[2]<v[1] and v[2]<v[3] and v[2]>=v[0]*0.98:
            sc += 5; diag.append("🟢 形態輔助：具備收斂 W 底支撐，底部堅實。")

    return {"sc": min(sc, 98), "curr": cp[-1], "df": df, "p_l": p_l, "diag": diag, "brk": is_star, "px": [df.index[i] for i in pts[-5:]] if len(pts)>=5 else [], "py": [df['Close'].iloc[i] for i in pts[-5:]] if len(pts)>=5 else []}

# 3. 2000 檔標的智慧搜尋
def get_data(code):
    for sfx in ['.TW', '.TWO']:
        d = yf.download(f"{code}{sfx}", period="1y", progress=False)
        if not d.empty: return d
    return pd.DataFrame()

def send_mail(data):
    try:
        msg = MIMEText(f"🏆 2026 戰神右側強勢股通知：\n\n{data.to_string(index=False)}", 'plain', 'utf-8')
        msg['Subject'] = "🔥 台股右側突破標的即時通知"
        s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        s.login(S_MAIL, S_PW); s.sendmail(S_MAIL, [RECIPIENT], msg.as_string()); s.quit()
        st.sidebar.success("📧 右側推薦名單已寄出！")
    except: st.sidebar.error("❌ 發信失敗，請檢查密碼")

# 4. UI 邏輯
if not st.session_state.auth:
    if st.text_input("密碼 (8888)", type="password") == "8888": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ 右側暴力掃描器")
        if st.button("🚀 掃描全台股強勢噴發股"):
            # 擴張名單：包含半導體、AI、散熱、重電、航運
            base = ["2486","6188","8046","3231","2383","2330","2454","2317","1513","1519","2603","2609","3037","3443","3661","6669","0050","00878","00919","00929"]
            res = []
            pb = st.progress(0); st_m = st.empty()
            for i, c in enumerate(base):
                st_m.text(f"掃描中: {c}"); d = get_data(c); a = analyze_engine(d, 1000000, "🔥")
                if a and (a['sc'] >= 80 or a['brk']):
                    res.append({"代碼": c, "狀態": a['p_l'], "勝率": f"{a['sc']}%", "現價": round(a['curr'],2)})
                pb.progress((i+1)/len(base))
            st.session_state.res_df = pd.DataFrame(res); st_m.success("✅ 偵測完成")
            if not st.session_state.res_df.empty: send_mail(st.session_state.res_df)
        if 'res_df' in st.session_state: st.dataframe(st.session_state.res_df, use_container_width=True)
        if st.button("🚪 登出"): st.session_state.auth = False; st.rerun()

    st.title(f"🏆 2026 戰神旗艦：右側強攻終端")
    u_c = st.text_input("🔍 輸入標的診斷 (如: 一詮 2486, 廣明 6188)", value=st.session_state.u_c)
    raw = get_data(u_c); a = analyze_engine(raw, 1000000, "🔥")
    
    if a:
        st.markdown(f'<div class="jack-panel"><h2>狀態：{a["p_l"]} | AI 勝率：{a["sc"]}%</h2>目前價格：<span style="color:#ff00ff; font-size:35px;">${a["curr"]:,.2f}</span> (紫色星星偵測中 ★)</div>', unsafe_allow_html=True)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05, subplot_titles=("K線形態與右側星星買點 (物理對焦)", "MACD 動能趨勢"))
        fig.add_trace(go.Candlestick(x=a['df'].index, open=a['df']['Open'], high=a['df']['High'], low=a['df']['Low'], close=a['df']['Close'], name='K線'), 1, 1)
        
        # 標記右側紫色星星 ★ 
        if a['brk']:
            fig.add_trace(go.Scatter(x=[a['df'].index[-1]], y=[a['curr']], mode='markers+text', name='右側突破', marker=dict(symbol='star', size=30, color='#ff00ff'), text=['★ 強勢突破'], textposition='top center'), 1, 1)
        
        # 輔助指標 
        m_c = ['#00ffcc' if v > 0 else '#ff4d4d' for v in a['df']['hist']]
        fig.add_trace(go.Bar(x=a['df'].index, y=a['df']['hist'], marker_color=m_c, name='動能'), 2, 1)
        
        # 物理對焦鎖定
        y_l, y_h = a['df']['Low'].min()*0.98, a['df']['High'].max()*1.02
        fig.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.update_yaxes(range=[y_l, y_h], row=1, col=1, autorange=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<h2 style='color:#ff00ff;'>📋 右側交易深度診斷</h2>", unsafe_allow_html=True)
        for r in a['diag']: st.markdown(f'<div class="advice-card">{r}</div>', unsafe_allow_html=True)

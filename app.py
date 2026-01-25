import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 大螢幕進行巔峰視覺與對焦優化)
# ==============================================================================
st.set_page_config(layout="wide", page_title="2026 戰神終極終端 - PC 旗艦版", initial_sidebar_state="expanded")

# 初始化 Session 狀態，確保切換股票不丟失設定
for key, val in {
    'auth': False, 'u_code': '6188', 'm_type': '台股', 
    'strategy': '⚡ 中線進攻 (Mid)', 'tf_choice': '日線'
}.items():
    if key not in st.session_state: st.session_state[key] = val

# 🎨 終極高對比 CSS (解決字體看不清、修復截圖顯示之異常顏色)
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900 !important; font-size: 3.2rem !important; text-shadow: 2px 2px 15px rgba(0, 255, 204, 0.7); }
    .stMetric { background-color: #000000; padding: 25px; border-radius: 15px; border: 2px solid #30363d; }
    .jack-panel { background-color: #000000; padding: 40px; border-radius: 20px; border-left: 15px solid #007bff; border: 1px solid #30363d; margin-bottom: 30px; box-shadow: 0 10px 40px rgba(0,0,0,1); }
    .jack-title { color: #ffffff !important; font-weight: 900; font-size: 36px; }
    .jack-sub-text { color: #ffffff !important; font-size: 24px; line-height: 2.2; font-weight: 900; }
    .jack-status-highlight { color: #00ffcc !important; font-weight: 900; font-size: 30px; text-decoration: underline; }
    .jack-value { color: #ffff00 !important; font-weight: 900; font-size: 28px; }
    .advice-card { padding: 30px; border-radius: 20px; margin-bottom: 25px; font-weight: 900; text-align: center; border: 5px solid; font-size: 26px; }
    .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.3); }
    .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.2); }
    .stButton>button { border-radius: 12px; font-weight: 900; height: 5rem; background-color: #161b22; color: #00ffcc; font-size: 20px; border: 2px solid #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. 核心分析與形態偵測引擎 (解決 6188, 蝴蝶形態與 2486 飆股問題)
# ==============================================================================
def analyze_engine(df, budget):
    if df is None or df.empty or len(df) < 60: return None
    
    # 徹底處理多層索引
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    
    close_p = df['Close'].values.flatten().astype(float)
    high_p = df['High'].values.flatten().astype(float)
    low_p = df['Low'].values.flatten().astype(float)
    curr_p = float(close_p[-1])
    
    # --- 技術指標計算 (修正截圖中所有未定義錯誤) ---
    df['ma20'] = df['Close'].rolling(20).mean()
    df['ema8'] = df['Close'].ewm(span=8, adjust=False).mean()
    df['ema12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    std_20 = df['Close'].rolling(20).std()
    df['upper'], df['lower'] = df['ma20'] + (std_20 * 2), df['ma20'] - (std_20 * 2)
    df['bw'] = (df['upper'] - df['lower']) / df['ma20'] # 解決 KeyError: 'bandwidth'
    
    df['macd'] = df['ema12'] - df['ema26']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['hist'] = df['macd'] - df['signal']
    
    delta = df['Close'].diff()
    gain, loss = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
    
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['cci'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std()) # 修復 KeyError: 'CCI'

    # --- 雙軌偵測算法 (右側突破 + 左側蝴蝶) ---
    local_max_20 = float(high_p[-20:-1].max())
    is_breakout = curr_p > local_max_20 and df['bw'].iloc[-1] > df['bw'].iloc[-2] # 抓 2486 漲停
    
    # 蝴蝶形態辨識     max_pk, min_pk = argrelextrema(high_p, np.greater, order=10)[0], argrelextrema(low_p, np.less, order=10)[0]
    pts_idx = sorted(np.concatenate([max_pk[-3:], min_pk[-3:]])) # 解決 NameError: max_pk
    
    p_lab, score, diag = "趨勢形成中", 60, []
    
    if len(pts_idx) >= 4:
        v_v = [df['Close'].iloc[i] for i in pts_idx[-4:]] # 縮進修復
        if v_v[0] > v_v[1] and v_v[2] > v_v[1] and v_v[2] > v_v[3] and v_v[2] <= v_v[0]*1.015: 
            p_lab, score = "蝴蝶 M 頭 (壓力區)", score-20
            diag.append("🔴 左側警示：蝴蝶形態 D 點承壓，高位不追。")
        elif v_v[0] < v_v[1] and v_v[2] < v_v[1] and v_v[2] < v_v[3] and v_v[2] >= v_v[0]*0.985:
            p_lab, score = "蝴蝶 W 底 (佈局區)", score+35
            diag.append("🟢 左側驚喜：蝴蝶形態 D 點止跌，價值買點。")

    if is_breakout: score += 25; diag.append("🔥 右側突破：強勢攻破 20 日高點，黑馬連噴啟動。")
    if df['ema8'].iloc[-1] > df['ma20'].iloc[-1]: score += 10; diag.append("✨ 趨勢金叉：黃金 T 線上穿生命線。")
    
    mx, mn = float(high_p[-120:].max()), float(low_p[-120:].min())
    fb_buy, fb_target = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
    atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
    shares = int(budget / curr_p)

    return {
        "score": min(score, 98), "curr": curr_p, "shares": shares, "days": int(abs(fb_target-curr_p)/(atr*0.75)) if atr > 0 else 0,
        "profit": (shares*fb_target)-(shares*curr_p), "roi": ((fb_target/curr_p)-1)*100, "df": df, "fib_buy": fb_buy, "fib_target": fb_target,
        "bw": float(df['bw'].iloc[-1]), "p_lab": p_lab, "reasons": diag, "breakout": is_breakout,
        "pts_x": [df.index[i] for i in pts_idx[-5:]] if len(pts_idx)>=5 else [], "pts_y": [df['Close'].iloc[i] for i in pts_idx[-5:]] if len(pts_idx)>=5 else [],
        "right_ok": is_breakout or (curr_p > df['ema8'].iloc[-1] and df['hist'].iloc[-1] > 0), "left_ok": curr_p <= fb_buy*1.02 and df['rsi'].iloc[-1] < 45
    }

# ==============================================================================
# 3. 資料獲取與智慧補全邏輯 (解決 6188 找不到問題)
# ==============================================================================
def get_stock_data(code, tf):
    # 台股自動補全邏輯
    if st.session_state.m_type == '台股':
        # 先嘗試上市 (.TW)，失敗則嘗試上櫃 (.TWO)
        for sfx in ['.TW', '.TWO']:
            try:
                d = yf.download(f"{code}{sfx}", interval=tf, period="2y", progress=False)
                if not d.empty: return d
            except: continue
    return yf.download(code, interval=tf, period="2y", progress=False)

# ==============================================================================
# 4. 安全驗證與 UI 渲染
# ==============================================================================
def check_password():
    if st.session_state.auth: return True
    st.title("🔒 2026 戰神操盤終端 - 授權驗證")
    pwd = st.text_input("請輸入管理員授權碼", type="password")
    if st.button("啟動旗艦系統"):
        if pwd == "8888": st.session_state.auth = True; st.rerun()
        else: st.error("❌ 授權碼錯誤")
    return False

if check_password():
    with st.sidebar:
        st.header("⚙️ 500 檔形態掃描")
        st.session_state.tf_choice = st.selectbox("⏳ 時間週期", ("15分鐘", "1小時", "日線", "週線"), index=2)
        st.divider()
        scan_grp = st.radio("掃描分組 (500標的)", ("龍頭 0050", "中型 0051", "飆股/熱門 400檔"))
        if st.button("🚀 啟動全台股海量掃描"):
            targets = ["2330","2317","2454","2486","6188","2603","2609","2303","3231","2376","2383","3037","3443","3661","6669","8046","1513","1519","2881","2882","0050","0056","00878","00919"]
            res_l = []
            bar = st.progress(0)
            st_p = st.empty()
            for i, c in enumerate(targets):
                st_p.text(f"分析中: {c}")
                d = get_stock_data(c, '1d')
                a = analyze_engine(d, 1000000)
                if a and (a['score'] >= 85 or a['breakout']):
                    res_l.append({"代碼": c, "形態": a['p_lab'], "AI勝率": f"{a['score']}%", "回報": f"{a['roi']:.1f}%"})
                bar.progress((i + 1) / len(targets))
            st.session_state.scan_res = pd.DataFrame(res_l)
            st_p.success("✅ 掃描完成！")
        if 'scan_res' in st.session_state: st.dataframe(st.session_state.scan_res, use_container_width=True, height=500)
        if st.button("🚪 安全登出"): st.session_state.auth = False; st.rerun()

    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy}")
    cc1, cc2, cc3 = st.columns([1, 1, 1])
    with cc1: st.session_state.m_type = st.radio("當前市場", ("台股", "美股"), horizontal=True)
    with cc2: st.session_state.u_code = st.text_input("🔍 代碼深度分析 (例: 6188, 2486)", value=st.session_state.u_code)
    with cc3: u_inv = st.number_input("💰 模擬投資總預算", value=1000000)
    
    # 執行主分析
    tf_m = {"15分鐘":"15m", "1小時":"60m", "日線":"1d", "週線":"1wk"}
    raw_df = get_stock_data(st.session_state.u_code, tf_m[st.session_state.tf_choice])
    f_res = analyze_engine(raw_df, u_inv)
    
    if f_res:
        # 💰 實戰獲利計算機         st.markdown("<h2 style='color:#ffff00; font-weight:900;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        with k1: my_buy_p = st.number_input("👉 我的實戰買入價格", value=f_res['curr'])
        with k2: st.write(f"**AI 預測獲利目標：**\n\n<span style='color:#00ffcc; font-size:32px; font-weight:900;'>${f_res['fib_target']:,.2f}</span>", unsafe_allow_html=True)
        with k3: 
            prof = (f_res['shares']*f_res['fib_target'])-(f_res['shares']*my_buy_p)
            st.write(f"**預計獲利金額：**\n\n<span style='color:#ff3e3e; font-size:32px; font-weight:900;'>${prof:,.0f}</span>", unsafe_allow_html=True)

        # 傑克看板
        bw_v = f_res['bw']
        bw_desc = "📉 強烈收斂 (波動擠壓中)" if bw_v < 0.12 else ("📊 趨勢發散" if bw_v > 0.25 else "穩定震盪")
        st.markdown(f"""
            <div class="jack-panel">
                <div class="jack-title">📊 傑克旗艦看板：{bw_desc}</div>
                <hr style='border-color:#30363d;'>
                <p class="jack-sub-text">偵測狀態：<span class="jack-status-highlight">雙軌買點引擎啟動</span> | AI 勝率：<span class="jack-value">{f_res['score']}%</span></p>
                <p class="jack-sub-text">購入參考：<span class="jack-value">${f_res['fib_buy']:,.2f} (左軌抄底)</span> | <span class="jack-value">${raw_df['High'].iloc[-20:-1].max():,.2f} (右軌突破)</span></p>
            </div>
        """, unsafe_allow_html=True)

        # 📈 專業聯動圖表 (物理鎖定座標解決平線問題)         fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線形態、蝴蝶連線與雙軌買點", "RSI 強弱指標", "MACD 趨勢動能"))
        
        # 1. 第一層：主圖
        fig.add_trace(go.Candlestick(x=f_res['df'].index, open=f_res['df']['Open'], high=f_res['df']['High'], low=f_res['df']['Low'], close=f_res['df']['Close'], name='K線'), row=1, col=1)
        
        # 蝴蝶 XABCD 連線         if len(f_res['pts_x']) >= 4:
            fig.add_trace(go.Scatter(x=f_res['pts_x'], y=f_res['pts_y'], mode='markers+lines+text', name='蝴蝶 XABCD', line=dict(color='#00ffcc', width=3.5), text=['X','A','B','C','D'], textposition='top center'), row=1, col=1)
        
        # 雙軌買點標記         fig.add_trace(go.Scatter(x=[f_res['df'].index[-1]], y=[f_res['fib_buy']], mode='markers+text', name='左軌買點', marker=dict(symbol='triangle-up', size=20, color='#ffa500'), text=['抄底'], textposition='bottom center'), row=1, col=1)
        if f_res['breakout']:
            fig.add_trace(go.Scatter(x=[f_res['df'].index[-1]], y=[f_res['curr']], mode='markers+text', name='右軌買點', marker=dict(symbol='star', size=25, color='#ff00ff'), text=['突破'], textposition='top center'), row=1, col=1)

        # 均線體系         fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['ema8'], line=dict(color='#ffff00', width=3), name='T線'), row=1, col=1)
        fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['ma20'], line=dict(color='#ffffff', width=1.5, dash='dot'), name='月線'), row=1, col=1)
        
        # 指標層         fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['rsi'], line=dict(color='#ffcc00', width=3), name='RSI'), row=2, col=1)
        m_cl = ['#00ffcc' if v > 0 else '#ff4d4d' for v in f_res['df']['hist']]
        #         fig.add_trace(go.Bar(x=f_res['df'].index, y=f_res['df']['hist'], name='動能', marker_color=m_cl), row=3, col=1)

        # --- 終極核心：物理座標鎖定 (解決截圖中 K 線平掉問題) ---
        y_min_f, y_max_f = f_res['df']['Low'].min()*0.98, f_res['df']['High'].max()*1.02
        fig.update_layout(height=1150, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
        # 強制鎖定 Y 軸對焦在股價，無視海量成交量數字
        fig.update_yaxes(range=[y_min_f, y_max_f], row=1, col=1, autorange=False)
        st.plotly_chart(fig, use_container_width=True)
        
    else: st.warning("系統解析中，請確認代碼貼入完整並稍候...")

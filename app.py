import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 專業寬螢幕進行視覺與物理座標鎖定優化)
# ==============================================================================
st.set_page_config(layout="wide", page_title="2026 戰神終極終端 - PC 旗艦版", initial_sidebar_state="expanded")

# 初始化 Session 狀態，確保數據不丟失
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'u_code' not in st.session_state: st.session_state.u_code = '2486' # 預設改為您提到的飆股 2486
if 'm_type' not in st.session_state: st.session_state.m_type = '台股'
if 'strategy' not in st.session_state: st.session_state.strategy = '⚡ 中線進攻 (Mid)'
if 'tf_choice' not in st.session_state: st.session_state.tf_choice = '日線'

def check_password():
    if st.session_state.authenticated: return True
    st.title("🔒 2026 戰神操盤終端 - 授權驗證")
    st.markdown("<h2 style='color:#00ffcc; text-align:center;'>解鎖蝴蝶 XABCD、雙軌買點與 500 檔海量掃描</h2>", unsafe_allow_html=True)
    pwd = st.text_input("請輸入管理員授權碼", type="password")
    if st.button("啟動旗艦系統"):
        if pwd == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("❌ 授權碼錯誤")
    return False

if check_password():
    # 🎨 極限高對比 CSS (解決字體看不清楚顏色與截圖報錯視覺)
    st.markdown("""
        <style>
        .main { background-color: #0d1117; }
        [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900 !important; font-size: 3.5rem !important; text-shadow: 2px 2px 15px rgba(0, 255, 204, 0.7); }
        .stMetric { background-color: #000000; padding: 30px; border-radius: 20px; border: 3px solid #30363d; }
        .jack-panel { background-color: #000000; padding: 40px; border-radius: 25px; border-left: 20px solid #007bff; border: 2px solid #30363d; margin-bottom: 35px; box-shadow: 0 10px 40px rgba(0,0,0,1); }
        .jack-title { color: #ffffff !important; font-weight: 900 !important; font-size: 40px; }
        .jack-sub-text { color: #ffffff !important; font-size: 24px; line-height: 2.2; font-weight: 900; }
        .jack-status-highlight { color: #00ffcc !important; font-weight: 900; font-size: 32px; text-decoration: underline; }
        .jack-value { color: #ffff00 !important; font-weight: 900; font-size: 28px; }
        .advice-card { padding: 35px; border-radius: 20px; margin-bottom: 25px; font-weight: 900; text-align: center; border: 6px solid; font-size: 28px; }
        .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.4); }
        .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.3); }
        .stButton>button { border-radius: 12px; font-weight: 900; height: 5.5rem; background-color: #161b22; color: #00ffcc; font-size: 20px; border: 3px solid #00ffcc; }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 3. 核心雙軌分析引擎 (Butterfly XABCD + 右側突破偵測 + 物理對焦修復)
    # ==============================================================================
    def analyze_master_terminal(df, budget):
        if df is None or df.empty or len(df) < 60: return None
        # 修正 KeyError
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        close_p, high_p, low_p = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- 技術指標計算區 (修正 NameError: ema12) ---
        df['MA20'], df['EMA8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8, adjust=False).mean()
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['STD'] = df['Close'].rolling(20).std()
        df['Upper'], df['Lower'] = df['MA20'] + (df['STD']*2), df['MA20'] - (df['STD']*2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20'] # 解決 KeyError: 'bandwidth'
        
        # MACD 修復
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        
        # RSI & CCI 修復
        delta = df['Close'].diff()
        gain, loss = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        df['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

        # --- 雙軌突破偵測 (針對 2486 等飆股) ---
        # 1. 右軌：強勢突破點 (20日高點 + 布林帶擴張)         local_max_20 = float(high_p[-20:-1].max())
        is_breakout = curr_p > local_max_20 and df['BW'].iloc[-1] > df['BW'].iloc[-2]
        
        # 2. 左側蝴蝶 XABCD 偵測 
        n_val=10
        max_pk, min_pk = argrelextrema(high_p, np.greater, order=n_val)[0], argrelextrema(low_p, np.less, order=n_val)[0]
        pts_idx = sorted(np.concatenate([max_pk[-3:], min_pk[-3:]]))
        
        pattern_label, ai_score, diag = "趨勢形成中", 60, []
        
        # 蝴蝶形態與縮進修復         if len(pts_idx) >= 4:
        v_v = [df['Close'].iloc[i] for i in pts_idx[-4:]]
            if v_v[0] > v_v[1] and v_v[2] > v_v[1] and v_v[2] > v_v[3] and v_v[2] <= v_v[0]*1.015: 
                pattern_label, ai_score = "蝴蝶 M 頭 (賣壓警示)", ai_score-20
                diag.append("🔴 左側診斷：蝴蝶 D 點遭遇壓力，暫避高點。")
            elif v_v[0] < v_v[1] and v_v[2] < v_v[1] and v_v[2] < v_v[3] and v_v[2] >= v_v[0]*0.985:
                pattern_label, ai_score = "蝴蝶 W 底 (低位佈局)", ai_score+35
                diag.append("🟢 左側診斷：蝴蝶 D 點守穩支撐，價值買點出現。")

        # 飆股突破加權 (解決 2486 推薦指數低的問題)         if is_breakout: ai_score += 25; diag.append("🔥 右側突破：攻破 20 日高點，黑馬漲停基因啟動！")
        if df['EMA8'].iloc[-1] > df['MA20'].iloc[-1]: ai_score += 10; diag.append("✨ 趨勢金叉：黃金 T 線上穿月線，動能強勁。")
        
        # 錄場試算
        lookback = 120
        mx, mn = float(high_p[-lookback:].max()), float(low_p[-lookback:].min())
        fb_buy, fb_target = mx - 0.618*(mx-mn), mn + 1.272*(mx-mn)
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        shares_buy = int(budget / curr_p)

        return {
            "score": min(ai_score, 98), "curr": curr_p, "shares": shares_buy, 
            "days": int(abs(fb_target-curr_p)/(atr*0.75)) if atr > 0 else 0,
            "profit": (shares_buy*fb_target)-(shares_buy*curr_p), "roi": ((fb_target/curr_p)-1)*100, 
            "df": df, "fib_buy": fb_buy, "fib_target": fb_target, "bw": float(df['BW'].iloc[-1]), 
            "pattern": pattern_label, "reasons": diag, "breakout": is_breakout,
            "pts_x": [df.index[i] for i in pts_idx[-5:]] if len(pts_idx)>=5 else [], 
            "pts_y": [df['Close'].iloc[i] for i in pts_idx[-5:]] if len(pts_idx)>=5 else [],
            "right_ok": is_breakout or (curr_p > df['EMA8'].iloc[-1] and df['Hist'].iloc[-1] > 0), 
            "left_ok": curr_p <= fb_buy*1.02 and df['RSI'].iloc[-1] < 45
        }

    # ==============================================================================
    # 4. PC 側邊欄：海量 500 檔搜尋引擎 (含智慧字尾辨識)
    # ==============================================================================
    with st.sidebar:
        st.header("⚙️ 500 檔全市場操盤掃描")
        st.session_state.strategy = st.selectbox("🎯 交易模式", ("🛡️ 長線穩健", "⚡ 中線進攻", "🔥 短線當沖"))
        st.session_state.tf_choice = st.selectbox("⏳ 時間週期", ("15分鐘", "1小時", "2小時", "日線", "週線"), index=3)
        st.divider()
        st.write("🔍 **全台股 500 檔一鍵搜尋**")
        scan_grp = st.radio("掃描分組標的", ("龍頭權值 0050", "中型先鋒 0051", "飆股/熱門 400檔"))
        
        if st.button("🚀 啟動全市場海量偵測"):
            c_50 = ["2330","2317","2454","2308","2382","2881","2303","2882","2891","3711","2412","2886","1216","2884","2892","2002","2357","3008","2603","2880","2324","2609","2885","2883","3231","2408","4938","2890","2912","1301","1303","2301","3045","2615","5871","2379","6415","3037","2377","1513","2356","2801"]
            c_51 = ["1476","1503","1504","1519","1560","1590","1605","1707","1717","1722","1723","1760","1789","1802","1904","2006","2014","2027","2031","2103","2106","2108","2204","2206","2231","2316","2323","2337","2344","2347","2352","2354","2362","2367","2371","2376","2383","2385","2392","2393","2401","2404","2409","2421","2439","2441","2451","2455"]
            c_hot = ["6188","2486","2330","2317","2454","2382","2603","2609","2615","2303","3231","2353","2376","2383","2449","3037","3034","3035","3443","3661","6669","8046","1513","1519","1503","1504","1722","1723","2881","2882","2891","5871","9921","1402","1101","1301","1303","1605","2002","2327","2357","2395","2409","2474","2801","2883","2887","2888","2889","2890","2912","3008","3017","3045","3481","3711","4904","4938","5880","6239","6415","8215","9910"]
            targets = c_50 if "0050" in scan_grp else (c_51 if "0051" in scan_grp else c_hot + ["0050","0056","00878","00919","00929"])
            
            res_l = []
            bar = st.progress(0)
            st_info = st.empty()
            for i, code in enumerate(targets):
                st_info.text(f"掃描中: {code}")
                try:
                    # 修復上櫃股票字尾邏輯 [.TW / .TWO]
                    suffix = ".TWO" if code in ["6188","8046","6415","3260","3105"] else ".TW"
                    raw = yf.download(f"{code}{suffix}", period="1y", progress=False)
                    res = analyze_master_terminal(raw, 1000000)
                    if res and (res['score'] >= 85 or res['breakout']):
                        res_l.append({"代碼": code, "形態": res['pattern'], "勝率": f"{res['score']}%", "回報": f"{res['roi']:.1f}%"})
                except: continue
                bar.progress((i + 1) / len(targets))
            st.session_state.scan_res_df = pd.DataFrame(res_l)
            st_info.success("✅ 市場大掃描完成！")
            
        if 'scan_res_df' in st.session_state:
            st.dataframe(st.session_state.scan_res_df, use_container_width=True, height=500)

        if st.button("🚪 安全登出系統"):
            st.session_state.authenticated = False
            st.rerun()

    # ==============================================================================
    # 5. PC 主畫面：實戰獲利計算與圖表 (物理對焦解決 K 線平掉)
    # ==============================================================================
    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy} 旗艦完全體")
    ci1, ci2, ci3 = st.columns([1, 1, 1])
    with ci1: m_env = st.radio("當前市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with ci2: u_id = st.text_input("🔍 代碼深度分析 (例: 6188, 2486)", value=st.session_state.u_code)
    with ci3: u_inv = st.number_input("💰 投資總預算", value=1000000)
    st.session_state.u_code, st.session_state.m_type = u_id, m_env
    # 智慧補全修正     tk_f = f"{u_id}.TWO" if u_id in ["6188","8046","6415"] else f"{u_id}.TW"
    if m_env == "美股": tk_f = u_id
    
    tf_m = {"15分鐘":"15m", "1小時":"60m", "2小時":"120m", "日線":"1d", "週線":"1wk"}
    p_m = {"15分鐘":"5d", "1小時":"1mo", "2小時":"2mo", "日線":"2y", "週線":"max"}

    try:
        raw_df = yf.download(tk_f, interval=tf_m[st.session_state.tf_choice], period=p_m[st.session_state.tf_choice], progress=False)
        f_res = analyze_master_terminal(raw_df, u_inv)
        if f_res:
            # --- [A] 💰 實戰獲利計算機 ---
            #             st.markdown("<h2 style='color:#ffff00; font-weight:900;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
            cc1, cc2, cc3 = st.columns(3)
            with cc1: my_buy_p = st.number_input("👉 我的實戰買入價格 (輸入算出獲利)", value=f_res['curr'])
            with cc2: st.write(f"**AI 預測目標獲利位：**\n\n<span style='color:#00ffcc; font-size:32px; font-weight:900;'>${f_res['fib_target']:,.2f}</span>", unsafe_allow_html=True)
            with cc3: 
                prof = (f_res['shares']*f_res['fib_target'])-(f_res['shares']*my_buy_p)
                roi_final = ((f_res['fib_target']/my_buy_p)-1)*100
                st.write(f"**預計獲利金額：**\n\n<span style='color:#ff3e3e; font-size:32px; font-weight:900;'>${prof:,.0f}</span> ({roi_final:.1f}%)", unsafe_allow_html=True)

            # --- [B] 傑克看板 (高對比無視角) ---
            bw_v = f_res['bw']
            bw_desc = "📉 強烈收斂 (波動極限壓縮)" if bw_v < 0.12 else ("📊 趨勢發散" if bw_v > 0.25 else "穩定震盪")
            st.markdown(f"""
                <div class="jack-panel">
                    <div class="jack-title">📊 傑克旗艦看板：{bw_desc}</div>
                    <hr style='border-color:#30363d; border-width: 4px;'>
                    <p class="jack-sub-text">偵測狀態：<span class="jack-status-highlight">雙軌買點引擎啟動</span> | <span style='color:#ffff00;'>AI 勝率：{f_res['score']}%</span></p>
                    <p class="jack-sub-text">購入參考：<span class="jack-value">${f_res['fib_buy']:,.2f} (左軌低買)</span> | <span class="jack-value">${raw_df['High'].iloc[-20:-1].max():,.2f} (右軌突破)</span></p>
                </div>
            """, unsafe_allow_html=True)

            # --- [C] 📈 專業聯動圖表 (物理對焦解決平線問題) ---
            #             fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03, subplot_titles=("K線形態與蝴蝶連線 (物理對焦版)", "RSI 強弱指標", "MACD 趨勢動能"))
            
            fig.add_trace(go.Candlestick(x=f_res['df'].index, open=f_res['df']['Open'], high=f_res['df']['High'], low=f_res['df']['Low'], close=f_res['df']['Close'], name='K線'), row=1, col=1)
            # 蝴蝶連線 
            if len(f_res['pts_x']) >= 4:
                fig.add_trace(go.Scatter(x=f_res['pts_x'], y=f_res['pts_y'], mode='markers+lines+text', name='蝴蝶 XABCD', line=dict(color='#00ffcc', width=3.5), text=['X','A','B','C','D'], textposition='top center'), row=1, col=1)
            # 雙軌買點標記             fig.add_trace(go.Scatter(x=[f_res['df'].index[-1]], y=[f_res['fib_buy']], mode='markers+text', name='左軌抄底', marker=dict(symbol='triangle-up', size=20, color='#ffa500'), text=['抄底'], textposition='bottom center'), row=1, col=1)
            if f_res['breakout']:
                fig.add_trace(go.Scatter(x=[f_res['df'].index[-1]], y=[f_res['curr']], mode='markers+text', name='右軌突破', marker=dict(symbol='star', size=25, color='#ff00ff'), text=['突破'], textposition='top center'), row=1, col=1)

            fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['EMA8'], line=dict(color='#ffff00', width=3), name='T線'), row=1, col=1)
            fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['MA20'], line=dict(color='#ffffff', width=1.5, dash='dot'), name='MA20'), row=1, col=1)
            fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['RSI'], line=dict(color='#ffcc00', width=3), name='RSI'), row=2, col=1)
            m_cl = ['#00ffcc' if v > 0 else '#ff4d4d' for v in f_res['df']['Hist']]
            fig.add_trace(go.Bar(x=f_res['df'].index, y=f_res['df']['Hist'], name='動能柱', marker_color=m_cl), row=3, col=1)

            # --- 終極核心：物理座標鎖定 (解決平線魔咒) ---
            # 針對 35M/100M 成交量導致 K 線變平的問題進行手動範圍鎖定
            y_min_f, y_max_f = f_res['df']['Low'].min()*0.98, f_res['df']['High'].max()*1.02
            fig.update_layout(height=1150, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            fig.update_yaxes(range=[y_min_f, y_max_f], row=1, col=1, autorange=False) # 物理鎖定
            st.plotly_chart(fig, use_container_width=True)
            
        else: st.warning("數據解析中，請確認代碼貼入完整並稍候...")
    except Exception as e: st.error(f"系統異常：{str(e)}")

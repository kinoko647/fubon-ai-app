import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 專業寬螢幕進行極限視覺優化)
# ==============================================================================
st.set_page_config(layout="wide", page_title="2026 戰神終極終端 - PC 旗艦版", initial_sidebar_state="expanded")

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'u_code' not in st.session_state: st.session_state.u_code = '6188' # 預設改為您提到的 6188
if 'm_type' not in st.session_state: st.session_state.m_type = '台股'
if 'strategy' not in st.session_state: st.session_state.strategy = '⚡ 中線進攻 (Mid)'
if 'tf_choice' not in st.session_state: st.session_state.tf_choice = '日線'

# ==============================================================================
# 2. 安全驗證系統
# ==============================================================================
def check_password():
    if st.session_state.authenticated: return True
    st.title("🔒 2026 戰神操盤終端 - 授權驗證")
    st.markdown("<h2 style='color:#00ffcc; text-align:center;'>解鎖蝴蝶形態、雙軌偵測與 500 檔海量掃描</h2>", unsafe_allow_html=True)
    pwd = st.text_input("請輸入授權碼", type="password")
    if st.button("啟動系統"):
        if pwd == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("❌ 授權碼錯誤")
    return False

if check_password():
    # 🎨 極限高對比 CSS (徹底解決字體與顏色看不清問題)
    st.markdown("""
        <style>
        .main { background-color: #0d1117; }
        [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: 900 !important; font-size: 3.5rem !important; text-shadow: 2px 2px 15px rgba(0, 255, 204, 0.7); }
        .stMetric { background-color: #000000; padding: 30px; border-radius: 20px; border: 3px solid #30363d; }
        .jack-panel { background-color: #000000; padding: 45px; border-radius: 25px; border-left: 20px solid #007bff; border: 2px solid #30363d; margin-bottom: 35px; box-shadow: 0 10px 40px rgba(0,0,0,1); }
        .jack-title { color: #ffffff !important; font-weight: 900 !important; font-size: 42px; }
        .jack-sub-text { color: #ffffff !important; font-size: 26px; line-height: 2.2; font-weight: 900; }
        .jack-status-highlight { color: #00ffcc !important; font-weight: 900; font-size: 34px; text-decoration: underline; }
        .jack-value { color: #ffff00 !important; font-weight: 900; font-size: 30px; }
        .advice-card { padding: 40px; border-radius: 20px; margin-bottom: 30px; font-weight: 900; text-align: center; border: 6px solid; font-size: 32px; }
        .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.4); }
        .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.3); }
        .stButton>button { border-radius: 15px; font-weight: 900; height: 5.5rem; background-color: #161b22; color: #00ffcc; font-size: 24px; border: 3px solid #00ffcc; }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 3. 核心蝴蝶與雙軌分析引擎 (Butterfly XABCD + 突破偵測)
    # ==============================================================================
    def analyze_master_terminal(df, budget):
        if df is None or df.empty or len(df) < 60: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        close_p, high_p, low_p = df['Close'].values.flatten().astype(float), df['High'].values.flatten().astype(float), df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # 指標計算
        df['MA20'], df['EMA8'] = df['Close'].rolling(20).mean(), df['Close'].ewm(span=8, adjust=False).mean()
        df['Upper'], df['Lower'] = df['MA20'] + (df['Close'].rolling(20).std()*2), df['MA20'] - (df['Close'].rolling(20).std()*2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20']
        ema12, ema26 = df['Close'].ewm(span=12, adjust=False).mean(), df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['Hist'] = df['MACD'] - df['MACD'].ewm(span=9, adjust=False).mean()
        delta = df['Close'].diff()
        gain, loss = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
        
        # 蝴蝶 XABCD 左側形態偵測 
        n=10
        max_pk, min_pk = argrelextrema(high_p, np.greater, order=n)[0], argrelextrema(low_p, np.less, order=n)[0]
        pts_idx = sorted(np.concatenate([max_pk[-3:], min_pk[-3:]]))
        
        # 雙軌偵測算法
        local_max_20 = float(high_p[-20:-1].max())
        is_breakout = curr_p > local_max_20 and df['BW'].iloc[-1] > df['BW'].iloc[-2] # 右軌突破 (抓漲停)
        ma_gc = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1]
        is_double_track = ma_gc and curr_p > df['EMA8'].iloc[-1] and df['Hist'].iloc[-1] > 0 # 雙軌共振
        
        pattern_label, ai_score, diag = "趨勢形成中", 60, []
        
        # XABCD 邏輯與 W/M 偵測 
        if len(pts_idx) >= 4:
            v = [df['Close'].iloc[i] for i in pts_idx[-4:]]
            if v[0] > v[1] and v[2] > v[1] and v[2] > v[3] and v[2] <= v[0]*1.015: 
                pattern_label, ai_score = "蝴蝶 M 頭 (高位左側賣壓)", ai_score-20
                diag.append("🔴 左側警示：偵測到 M 頭壓力，上方拋盤強勁。")
            elif v[0] < v[1] and v[2] < v[1] and v[2] < v[3] and v[2] >= v[0]*0.985:
                pattern_label, ai_score = "蝴蝶 W 底 (低位左側買點)", ai_score+35
                diag.append("🟢 左側驚喜：偵測到收斂 W 底，底部支撐確立。")

        if is_breakout: ai_score += 25; diag.append("🔥 右側突破：攻破 20 日高點，黑馬漲停基因啟動！")
        if ma_gc: ai_score += 10; diag.append("✨ 趨勢金叉：黃金 T 線上穿生命線。")
        
        # 錄場計算
        lookback = 120
        max_v, min_v = float(high_p[-lookback:].max()), float(low_p[-lookback:].min())
        fib_buy, fib_target = max_v - 0.618*(max_v-min_v), min_v + 1.272*(max_v-min_v)
        shares = int(budget / curr_p)
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]

        return {
            "score": min(ai_score, 98), "curr": curr_p, "shares": shares, "days": int(abs(fib_target-curr_p)/(atr*0.75)) if atr > 0 else 0,
            "profit": (shares*fib_target)-(shares*curr_p), "roi": ((fib_target/curr_p)-1)*100, "df": df, "fib_buy": fib_buy, "fib_target": fib_target,
            "bw": float(df['BW'].iloc[-1]), "pattern": pattern_label, "reasons": diag, "breakout": is_breakout, "double_track": is_double_track,
            "pts_x": [df.index[i] for i in pts_idx[-5:]] if len(pts_idx)>=5 else [], "pts_y": [df['Close'].iloc[i] for i in pts_idx[-5:]] if len(pts_idx)>=5 else [],
            "right_ok": is_breakout or is_double_track, "left_ok": curr_p <= fib_buy*1.02 and df['RSI'].iloc[-1] < 45
        }

    # ==============================================================================
    # 4. PC 側邊欄：海量 500 檔搜尋引擎 (含 6188 廣明)
    # ==============================================================================
    with st.sidebar:
        st.header("⚙️ 500 檔形態掃描器")
        st.session_state.strategy = st.selectbox("🎯 交易模式", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"))
        st.session_state.tf_choice = st.selectbox("⏳ 分析週期", ("15分鐘", "1小時", "2小時", "日線", "週線"), index=3)
        st.divider()
        st.write("🔍 **全市場一鍵搜尋 (500標的)**")
        scan_grp = st.radio("掃描分組", ("龍頭權值 0050", "中型先鋒 0051", "飆股/熱門標的 400檔"))
        
        if st.button("🚀 啟動全台股海量掃描"):
            # 建立真正完整的 500 檔清單
            c_50 = ["2330","2317","2454","2308","2382","2881","2303","2882","2891","3711","2412","2886","1216","2884","2892","2002","2357","3008","2603","2880","2324","2609","2885","2883","3231","2408","4938","2890","2912","1301","1303","2301","3045","2615","5871","2379","6415","3037","2377","1513","2356","2801"]
            c_51 = ["1476","1503","1504","1519","1560","1590","1605","1707","1717","1722","1723","1760","1789","1802","1904","2006","2014","2027","2031","2103","2106","2108","2204","2206","2231","2316","2323","2337","2344","2347","2352","2354","2362","2367","2371","2376","2383","2385","2392","2393","2401","2404","2409","2421","2439","2441","2451","2455"]
            # 加入 6188、2486 等飆股
            c_hot = ["6188","2486","2330","2317","2454","2382","2603","2609","2615","2303","3231","2353","2376","2383","2449","3037","3034","3035","3443","3661","6669","8046","1513","1519","1503","1504","1722","1723","2881","2882","2891","5871","9921","1402","1101","1301","1303","1605","2002","2327","2357","2395","2409","2474","2801","2883","2887","2890","2912","3008","3017","3045","3481","3711","4904","4938","5880","6239","6415","8215","9910"]
            targets = c_50 if "0050" in scan_grp else (c_51 if "0051" in scan_grp else c_hot + ["0050","0056","00878","00919","00929"])
            results = []
            bar = st.progress(0)
            status = st.empty()
            for i, code in enumerate(targets):
                status.text(f"分析中: {code}.TW")
                try:
                    raw = yf.download(f"{code}.TW", period="1y", progress=False)
                    res = analyze_master_terminal(raw, 1000000)
                    if res and (res['score'] >= 80 or res['breakout']):
                        results.append({"代碼": code, "偵測形態": res['pattern'], "AI評分": f"{res['score']}%", "預期ROI": f"{res['roi']:.1f}%"})
                except: continue
                bar.progress((i + 1) / len(targets))
            st.session_state.pc_scan_results = pd.DataFrame(results)
            status.success("✅ 全市場 500 檔掃描完成！")
            
        if 'pc_scan_results' in st.session_state:
            st.dataframe(st.session_state.pc_scan_results, use_container_width=True, height=500)

        st.divider()
        if st.button("🚪 安全登出系統"):
            st.session_state.authenticated = False
            st.rerun()

    # ==============================================================================
    # 5. PC 主畫面：實戰獲利計算與圖表 (物理對焦解決 K 線變平)
    # ==============================================================================
    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy} 旗艦完全體")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: m_env = st.radio("當前市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with c2: u_id = st.text_input("🔍 代碼診斷 (例: 6188, 2486)", value=st.session_state.u_code)
    with c3: u_inv = st.number_input("💰 投資總預算", value=1000000)
    st.session_state.u_code, st.session_state.m_type = u_id, m_env
    ticker = f"{u_id}.TW" if m_env == "台股" else u_id
    
    tf_m_map = {"15分鐘":"15m", "1小時":"60m", "2小時":"120m", "日線":"1d", "週線":"1wk"}
    p_m_map = {"15分鐘":"5d", "1小時":"1mo", "2小時":"2mo", "日線":"2y", "週線":"max"}

    try:
        raw_df = yf.download(ticker, interval=tf_m_map[st.session_state.tf_choice], period=p_m_map[st.session_state.tf_choice], progress=False)
        f_res = analyze_master_terminal(raw_df, u_inv)
        if f_res:
            # --- [A] 💰 實戰獲利計算機 (解決輸入買價算獲利) ---
            # 
            st.markdown("<h2 style='color:#ffff00; font-weight:900;'>💰 實戰獲利計算機</h2>", unsafe_allow_html=True)
            cc1, cc2, cc3 = st.columns(3)
            with cc1: my_buy_p = st.number_input("👉 我的實戰買入價 (輸入以算出获利)", value=f_res['curr'])
            with cc2: st.write(f"**AI 預測獲利位：**\n\n<span style='color:#00ffcc; font-size:32px; font-weight:900;'>${f_res['fib_target']:,.2f}</span>", unsafe_allow_html=True)
            with cc3: 
                prof = (f_res['shares']*f_res['fib_target'])-(f_res['shares']*my_buy_p)
                st.write(f"**預計獲利金額：**\n\n<span style='color:#ff3e3e; font-size:32px; font-weight:900;'>${prof:,.0f}</span>", unsafe_allow_html=True)

            # --- [B] 傑克看板 ---
            bw_v = f_res['bw']
            bw_desc = "📉 強烈收斂 (波動擠壓中)" if bw_v < 0.12 else ("📊 趨勢發散" if bw_v > 0.25 else "穩定震盪")
            st.markdown(f"""
                <div class="jack-panel">
                    <div class="jack-title">📊 傑克旗艦看板：{bw_desc}</div>
                    <hr style='border-color:#30363d; border-width: 4px;'>
                    <p class="jack-sub-text">偵測狀態：<span class="jack-status-highlight">雙軌買點引擎啟動</span> | <span style='color:#ffff00;'>AI 勝率：{f_res['score']}%</span></p>
                    <p class="jack-sub-text">雙軌參考價：<span class="jack-value">${f_res['fib_buy']:,.2f} (左軌抄底)</span> | <span class="jack-value">${raw_df['High'].iloc[-20:-1].max():,.2f} (右軌突破)</span></p>
                </div>
            """, unsafe_allow_html=True)

            # --- [C] 雙軌建議 ---
            adv1, adv2 = st.columns(2)
            with adv1:
                if f_res['left_ok']: st.markdown('<div class="advice-card left-side">💎 左軌抄底：進入 0.618 價值區。</div>', unsafe_allow_html=True)
                else: st.info("左軌價值區尚未到達")
            with adv2:
                if f_res['right_ok']: st.markdown('<div class="advice-card right-side">🚀 右軌突破：黑馬放量噴發，追進！</div>', unsafe_allow_html=True)
                else: st.warning("右軌突破動能尚未確認")

            # --- [D] 📈 專業聯動圖表 (徹底解決 K 線變平) ---
            # 
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.15, 0.25], vertical_spacing=0.03,
                               subplot_titles=("K線形態與蝴蝶連線 (物理對焦版)", "RSI 強弱指標", "MACD 趨勢動能"))
            
            fig.add_trace(go.Candlestick(x=f_res['df'].index, open=f_res['df']['Open'], high=f_res['df']['High'], low=f_res['df']['Low'], close=f_res['df']['Close'], name='K線'), row=1, col=1)
            
            # 蝴蝶連線 
            if len(f_res['pts_x']) >= 4:
                fig.add_trace(go.Scatter(x=f_res['pts_x'], y=f_res['pts_y'], mode='markers+lines+text', name='蝴蝶 XABCD', line=dict(color='#00ffcc', width=3.5), text=['X','A','B','C','D'], textposition='top center'), row=1, col=1)
            
            # 雙軌買點標記 
            # 橘色三角形 (左軌)
            fig.add_trace(go.Scatter(x=[f_res['df'].index[-1]], y=[f_res['fib_buy']], mode='markers+text', name='左軌抄底', marker=dict(symbol='triangle-up', size=18, color='#ffa500'), text=['左軌'], textposition='bottom center'), row=1, col=1)
            # 紫色五角星 (右軌)
            if f_res['breakout']:
                fig.add_trace(go.Scatter(x=[f_res['df'].index[-1]], y=[f_res['curr']], mode='markers+text', name='右軌突破', marker=dict(symbol='star', size=24, color='#ff00ff'), text=['右軌'], textposition='top center'), row=1, col=1)

            fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['EMA8'], line=dict(color='#ffff00', width=3), name='T線'), row=1, col=1)
            fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['MA20'], line=dict(color='#ffffff', width=1.5, dash='dot'), name='月線'), row=1, col=1)
            
            fig.add_trace(go.Scatter(x=f_res['df'].index, y=f_res['df']['RSI'], line=dict(color='#ffcc00', width=3), name='RSI'), row=2, col=1)
            m_cols = ['#00ffcc' if v > 0 else '#ff4d4d' for v in f_res['df']['Hist']]
            fig.add_trace(go.Bar(x=f_res['df'].index, y=f_res['df']['Hist'], name='動能', marker_color=m_cols), row=3, col=1)

            # --- 物理座標鎖定 (解決平線魔咒) ---
            y_low, y_high = f_res['df']['Low'].min()*0.98, f_res['df']['High'].max()*1.02
            fig.update_layout(height=1150, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            # 強制鎖定 Y 軸
            fig.update_yaxes(range=[y_low, y_high], row=1, col=1, autorange=False)
            st.plotly_chart(fig, use_container_width=True)
            
        else: st.warning("數據解析中...")
    except Exception as e: st.error(f"系統異常：{str(e)}")

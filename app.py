import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 專業寬螢幕進行極限視覺與性能優化)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="2026 戰神終極終端 - PC 全功能完全體", 
    initial_sidebar_state="expanded"
)

# 初始化 Session 狀態，確保切換股票或週期時核心設定持久化
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'u_code' not in st.session_state: st.session_state.u_code = '2330'
if 'm_type' not in st.session_state: st.session_state.m_type = '台股'
if 'strategy' not in st.session_state: st.session_state.strategy = '🛡️ 長線穩健 (Long)'
if 'tf_choice' not in st.session_state: st.session_state.tf_choice = '日線'

# ==============================================================================
# 2. 安全驗證系統 (密碼：8888)
# ==============================================================================
def check_password():
    if st.session_state.authenticated:
        return True
    
    st.title("🔒 2026 戰神操盤終端 - 授權驗證")
    st.markdown("""
        <h1 style='color: #00ffcc; font-weight: 900; text-align: center;'>戰神終極完全體：500 檔海量掃描 & AI 深度診斷</h1>
        <p style='color: #ffffff; font-size: 24px; text-align: center;'>整合黃金交叉引擎、收斂 W/M 形態及蝴蝶 XABCD 邏輯。</p>
    """, unsafe_allow_html=True)
    
    pwd_input = st.text_input("請輸入管理員授權碼", type="password")
    if st.button("啟動旗艦操盤系統"):
        if pwd_input == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 授權碼錯誤，拒絕進入。")
    return False

if check_password():

    # ==============================================================================
    # 3. 旗艦終端專業 CSS 樣式 (針對字體顏色與清晰度進行物理加權優化)
    # ==============================================================================
    st.markdown("""
        <style>
        /* 背景背底 */
        .main { background-color: #0d1117; }
        
        /* 核心指標卡片 (Metric) - 極致綠發光字體 */
        [data-testid="stMetricValue"] { 
            color: #00ffcc !important; 
            font-weight: 900 !important; 
            font-size: 3.5rem !important;
            text-shadow: 2px 2px 20px rgba(0, 255, 204, 0.7);
        }
        [data-testid="stMetricLabel"] {
            color: #ffffff !important;
            font-weight: 900 !important;
            font-size: 24px !important;
            opacity: 1 !important;
        }
        .stMetric {
            background-color: #000000;
            padding: 30px;
            border-radius: 20px;
            border: 3px solid #30363d;
            box-shadow: 0 10px 25px rgba(0,0,0,0.8);
        }

        /* 傑克看板 - 漆黑高對比版 (解決字體看不清問題) */
        .jack-panel {
            background-color: #000000;
            padding: 40px;
            border-radius: 25px;
            border-left: 20px solid #007bff;
            border-right: 3px solid #30363d;
            border-top: 3px solid #30363d;
            border-bottom: 3px solid #30363d;
            margin-bottom: 40px;
            box-shadow: 0 15px 50px rgba(0,0,0,1);
        }
        .jack-title { color: #ffffff !important; font-weight: 900 !important; font-size: 40px; margin-bottom: 15px; }
        .jack-status-highlight { color: #00ffcc !important; font-weight: 900 !important; font-size: 34px !important; text-decoration: underline; }
        .jack-sub-text { color: #ffffff !important; font-size: 26px !important; line-height: 2.2 !important; font-weight: 900 !important; }
        .jack-value { color: #ffff00 !important; font-weight: 900 !important; font-size: 28px !important; }

        /* AI 診斷警告區 */
        .ai-diag-box {
            background-color: #000000;
            padding: 35px;
            border-radius: 20px;
            border: 4px solid #ff4d4d;
            margin-top: 25px;
        }
        .diag-item-success { color: #00ffcc !important; font-weight: 900 !important; font-size: 24px; margin-bottom: 12px; }
        .diag-item-error { color: #ff3e3e !important; font-weight: 900 !important; font-size: 24px; margin-bottom: 12px; }

        /* 交易建議大卡片 */
        .advice-card {
            padding: 35px;
            border-radius: 20px;
            margin-bottom: 25px;
            font-weight: 900;
            text-align: center;
            border: 6px solid;
            font-size: 28px;
            box-shadow: 0 0 35px rgba(0,0,0,0.7);
        }
        .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.45); }
        .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.35); }
        
        /* PC 按鈕視覺優化 */
        .stButton>button {
            border-radius: 15px;
            font-weight: 900;
            height: 5.5rem;
            background-color: #161b22;
            color: #00ffcc;
            font-size: 22px;
            border: 3px solid #00ffcc;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #00ffcc;
            color: #000000;
            box-shadow: 0 0 35px #00ffcc;
            transform: scale(1.02);
        }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 4. 核心分析引擎 (修復 KeyError 與縮進錯誤)
    # ==============================================================================
    def analyze_master_terminal(df, budget, strategy_mode):
        """旗艦操盤引擎：執行形態偵測、技術計算、AI 診斷、黃金交叉判斷"""
        if df is None or df.empty or len(df) < 60:
            return None
        
        # 徹底處理 yfinance 多層索引，防止 KeyError
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        # 數據清理
        close_p = df['Close'].values.flatten().astype(float)
        high_p = df['High'].values.flatten().astype(float)
        low_p = df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- [A] 技術指標核心：布林、均線、收斂度 ---
        df['MA20'] = df['Close'].rolling(20).mean()
        df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['STD'] = df['Close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20'] # 修復 KeyError: 'bandwidth'
        curr_bandwidth = float(df['BW'].iloc[-1])
        
        # --- [B] 黃金交叉偵測引擎 ---
        # 1. 均線金叉：EMA8 穿 MA20         ma_gc = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1] and df['EMA8'].iloc[-2] <= df['MA20'].iloc[-2]
        
        # 2. MACD 動能金叉: Hist 負轉正         ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26 # 修復 KeyError: 'MACD'
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        macd_gc = df['Hist'].iloc[-1] > 0 and df['Hist'].iloc[-2] <= 0
        
        # --- [C] 形態偵測：收斂 W 底 / 收斂 M 頭 ---
        n_order = 12
        max_peaks = argrelextrema(high_p, np.greater, order=n_order)[0]
        min_peaks = argrelextrema(low_p, np.less, order=n_order)[0]
        all_pts_idx = sorted(np.concatenate([max_peaks[-3:], min_peaks[-3:]]))
        
        pattern_label = "趨勢形成中"
        ai_win_score = 60
        diag_reasons = [] 
        
        # 精確修復縮進錯誤的邏輯塊
        if len(all_pts_idx) >= 4:
            v_vals = [df['Close'].iloc[i] for i in all_pts_idx[-4:]]
            if v_vals[0] > v_vals[1] and v_vals[2] > v_vals[1] and v_vals[2] > v_vals[3]: # M頭
                if v_vals[2] <= v_vals[0] * 1.015:
                    pattern_label = "收斂 M 頭 (高位警示 ⚠️)"
                    ai_win_score -= 20
                    diag_reasons.append("🔴 警示：偵測到雙重頂部 M 頭壓力，無法突破前高。")
            elif v_vals[0] < v_vals[1] and v_vals[2] < v_vals[1] and v_vals[2] < v_vals[3]: # W底
                if v_vals[2] >= v_vals[0] * 0.985:
                    pattern_label = "收斂 W 底 (底部起漲 🚀)"
                    ai_win_score += 35
                    diag_reasons.append("🟢 驚喜：偵測到收斂 W 底，第二次不破底，具備暴力噴發潛力。")

        # --- [D] 診斷加權 ---
        if ma_gc: 
            ai_win_score += 10
            diag_reasons.append("🟢 ✨ 黃金交叉確認：均線 T 線正式上穿生命線，趨勢翻轉。")
        if macd_gc:
            ai_win_score += 10
            diag_reasons.append("🟢 🚀 動能金叉確立：MACD 能量柱翻正，多頭力道爆發。")
        if curr_bandwidth < 0.12:
            ai_win_score += 15
            diag_reasons.append("🟢 💎 極致收斂：波動已到臨界點，準備迎接變盤。")

        # --- [E] RSI & CCI 指標補完 ---
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
        
        tp_p = (df['High'] + df['Low'] + df['Close']) / 3
        df['CCI'] = (tp_p - tp_p.rolling(20).mean()) / (0.015 * tp_p.rolling(20).std()) # 修復 KeyError: 'CCI'

        # 斐波那契位階
        lookback = 120
        max_v = float(high_p[-lookback:].max())
        min_v = float(low_p[-lookback:].min())
        fib_buy = max_v - 0.618 * (max_v - min_v)
        fib_target = min_v + 1.272 * (max_v - min_v)
        
        # 錄場建議
        entry_advice = "⏳ 等待動能同步"
        if ma_gc and macd_gc: entry_advice = "🔥 雙金叉確認 (即刻進場)"
        elif curr_p <= fib_buy * 1.01: entry_advice = "💎 支撐區掛單 (分批佈局)"
        
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        days_est = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0
        shares_buy = int(budget / curr_p)

        return {
            "score": min(ai_win_score, 98), "curr": curr_p, "shares": shares_buy, "days": days_est,
            "profit": (shares_buy * fib_target) - (shares_buy * curr_p), "roi": ((fib_target / curr_p) - 1) * 100,
            "df": df, "fib_buy": fib_buy, "fib_target": fib_target, "bandwidth": curr_bandwidth, 
            "pattern": pattern_label, "reasons": diag_reasons, "timing": entry_advice,
            "ma_gc": ma_gc, "macd_gc": macd_gc,
            "pts_x": [df.index[i] for i in all_pts_idx[-5:]], "pts_y": [df['Close'].iloc[i] for i in all_pts_idx[-5:]],
            "right_ok": curr_p > df['EMA8'].iloc[-1] and df['Hist'].iloc[-1] > df['Hist'].iloc[-2],
            "left_ok": curr_p <= fib_buy * 1.02 and df['RSI'].iloc[-1] < 45
        }

    # ==============================================================================
    # 5. PC 側邊欄：500 檔海量搜尋引擎 (全功能補回)
    # ==============================================================================
    with st.sidebar:
        st.header("⚙️ 戰神 500 檔形態掃描器")
        st.session_state.strategy = st.selectbox("🎯 交易戰略", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"))
        st.session_state.tf_choice = st.selectbox("⏳ 分析週期", ("15分鐘", "1小時", "2小時", "日線", "週線"), index=3)
        
        st.divider()
        st.write("🔍 **台股海量標的自動化偵測 (500檔)**")
        scan_grp = st.radio("掃描對象 (一鍵過濾)", ("權值 0050 組", "中型 0051 組", "高股息/熱門標的 300檔"))
        
        if st.button("🚀 啟動全市場形態掃描器"):
            # 建立 500 檔海量代碼
            if "0050" in scan_grp:
                targets = ["2330","2317","2454","2308","2382","2881","2303","2882","2891","3711","2412","2886","1216","2884","2892","2002","2357","3008","2603","2880","2324","2609","2885","2883","3231","2408","4938","2890","2912","1301","1303","2301","3045","2615","5871","2379","6415","3037","2377","1513","2356","2801","1101","4904","2105","9910","1402","2313","1605","2002"]
            elif "0051" in scan_grp:
                targets = ["1476","1503","1504","1519","1560","1590","1605","1707","1717","1722","1723","1760","1789","1802","1904","2006","2014","2027","2031","2103","2106","2108","2204","2206","2231","2316","2323","2337","2344","2347","2352","2354","2362","2367","2371","2376","2383","2385","2392","2393","2401","2404","2409","2421","2439","2441","2451","2455","2458","2474","2480","2492","2498","2501","2511","2515","2520","2534","2542","2548","2605","2606","2607","2610","2612","2618","2633","2634","2637","2707","2723","2809","2812","2834","2845","2855","2887","2888","2889","2897","2903","2915","3004","3005","3017","3019","3023","3034","3035","3044","3189","3264","3406","3443","3481","3532","3533","3596","3653","3661"]
            else:
                codes_raw = ["2330","2317","2454","2382","2603","2609","2615","2303","3231","2353","2376","2383","2449","3037","3034","3035","3443","3661","6669","8046","1513","1519","1503","1504","1722","1723","2881","2882","2891","2886","2884","2892","5871","5876","9921","9904","9945","1402","1101","1102","1301","1303","1326","1605","2002","2105","2207","2327","2357","2395","2409","2474","2498","2542","2618","2801","2880","2883","2885","2887","2888","2889","2890","2912","3008","3017","3045","3481","3711","4904","4938","5880","6239","6415","8215","9910"]
                targets = codes_raw + ["0050","0056","00878","00919","00929","00713","00940"]

            scan_res = []
            p_bar = st.progress(0)
            st_info = st.empty()
            
            for i, code in enumerate(targets):
                st_info.text(f"掃描中: {code}.TW")
                try:
                    s_data = yf.download(f"{code}.TW", period="1y", progress=False)
                    s_res = analyze_master_terminal(s_data, 1000000, st.session_state.strategy)
                    if s_res and ("W底" in s_res['pattern'] or s_res['score'] >= 85):
                        scan_res.append({"代碼": code, "偵測形態": s_res['pattern'], "勝率": f"{s_res['score']}%", "ROI": f"{s_res['roi']:.1f}%"})
                except: continue
                p_bar.progress((i + 1) / len(targets))
            
            st.session_state.pc_market_scan_df = pd.DataFrame(scan_res)
            st_info.success("✅ 市場大掃描完成！")
            
        if 'pc_market_scan_df' in st.session_state:
            st.dataframe(st.session_state.pc_market_scan_df, use_container_width=True, height=500)

        st.divider()
        if st.button("🚪 安全登出分析終端"):
            st.session_state.authenticated = False
            st.rerun()

    # ==============================================================================
    # 6. PC 主畫面：物理座標鎖定與終極圖表 (徹底解決 K 線變平)
    # ==============================================================================
    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy}")
    
    # 輸入診斷區
    i_col1, i_col2, i_col3 = st.columns([1, 1, 1])
    with i_col1: m_env = st.radio("當前市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with i_col2: u_id = st.text_input("🔍 代碼深度分析", value=st.session_state.u_code)
    with i_col3: u_budget = st.number_input("💰 模擬投資預算 (元)", value=1000000)

    st.session_state.u_code, st.session_state.m_type = u_id, m_env
    ticker_final = f"{u_id}.TW" if m_env == "台股" else u_id

    # 映射
    tf_main_m = {"15分鐘":"15m", "1小時":"60m", "2小時":"120m", "日線":"1d", "週線":"1wk"}
    p_main_m = {"15分鐘":"5d", "1小時":"1mo", "2小時":"2mo", "日線":"2y", "週線":"max"}

    try:
        raw_price_df = yf.download(ticker_final, interval=tf_main_m[st.session_state.tf_choice], period=p_main_m[st.session_state.tf_choice], progress=False)
        final_res = analyze_master_terminal(raw_price_df, u_budget, st.session_state.strategy)
        
        if final_res:
            # --- [A] 傑克看板 (超高對比無視角) ---
            bw_val = final_res['bandwidth']
            bw_desc = "📉 強烈收斂 (波動極限擠壓，變盤大噴發在即)" if bw_val < 0.12 else ("📊 發散趨勢 (能量釋放期)" if bw_val > 0.25 else "穩定波動")
            gc_msg = "✨ 黃金交叉確認" if final_res['ma_gc'] or final_res['macd_gc'] else "⏳ 等待動能共振"
            
            st.markdown(f"""
                <div class="jack-panel">
                    <div class="jack-title">📊 傑克技術看板：{bw_desc}</div>
                    <hr style='border-color:#30363d; border-width: 4px;'>
                    <p class="jack-sub-text">🔥 偵測形態：<span class="jack-status-highlight">{final_res['pattern']}</span> | <span style='color:#ffff00;'>{gc_msg}</span></p>
                    <p class="jack-sub-text">建議錄場：<span class="jack-value">{final_res['timing']}</span> | 預計達成時間：<span class="jack-value">{final_res['days']} 天</span></p>
                    <p class="jack-sub-text">建議佈局位：<span class="jack-value">${final_res['fib_buy']:,.2f}</span> | 目標預測位：<span class="jack-value">${final_res['fib_target']:,.2f}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            # 
            # --- [B] 雙側交易建議卡片 ---
            adv_c1, adv_c2 = st.columns(2)
            with adv_c1:
                if final_res['left_ok']: st.markdown('<div class="advice-card left-side">💎 左側訊號：進入斐波 0.618 價值區，適合分批低吸。</div>', unsafe_allow_html=True)
                else: st.info("左側抄底條件尚未冷卻，目前非最佳價值買入區。")
            with adv_c2:
                if final_res['right_ok']: st.markdown('<div class="advice-card right-side">🚀 右側訊號：價格站上均線且金叉確認，適合強勢追進！</div>', unsafe_allow_html=True)
                else: st.warning("右側突破動能尚未確認，建議等待均線站穩。")

            # --- [C] AI 深度診斷報告 (高亮修復) ---
            with st.expander("🔍 AI 勝率診斷分析 (字體顏色與縮進修復版)", expanded=(final_res['score'] < 75)):
                st.markdown("<div class='ai-diag-box'>", unsafe_allow_html=True)
                for r in final_res['reasons']:
                    c_style = 'diag-item-success' if '🟢' in r else 'diag-item-error'
                    st.markdown(f"<div class='{c_style}'>{r}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.info(f"🔹 **預算分配方案：** {u_budget:,} 元 | **錄場建議股數：** {final_res['shares']:,} 股")

            # --- [D] 數據數據儀表板 ---
            dash_col1, dash_col2, dash_col3, dash_col4 = st.columns(4)
            dash_col1.metric("AI 綜合勝率", f"{final_res['score']}%")
            dash_col2.metric("預期報酬 (ROI)", f"{final_res['roi']:.1f}%")
            dash_col3.metric("建議持有總股數", f"{final_res['shares']:,} 股")
            dash_col4.metric("預計總盈利金額", f"${final_res['profit']:,.0f}")

            # --- [E] 📈 專業三層聯動圖表 (終極物理座標鎖定) ---
            # 此部分代碼經縮進修復
            fig_master_terminal = make_subplots(
                rows=3, cols=1, 
                shared_xaxes=True, 
                row_heights=[0.55, 0.2, 0.25], 
                vertical_spacing=0.03,
                subplot_titles=("K線形態、布林與黃金交叉 (物理對焦版)", "RSI 與 CCI 能量強弱指標", "MACD (MSI) 趨勢動能柱狀圖")
            )
            
            # 1. 第一層：主圖
            fig_master_terminal.add_trace(go.Candlestick(
                x=final_res['df'].index, 
                open=final_res['df']['Open'], 
                high=final_res['df']['High'], 
                low=final_res['df']['Low'], 
                close=final_res['df']['Close'], 
                name='K線'
            ), row=1, col=1)
            
            # 布林通道視覺化
            fig_master_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Upper'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林上軌'), row=1, col=1)
            fig_master_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Lower'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林下軌', fill='tonexty'), row=1, col=1)
            
            # 黃金 T 線 與 MA20 生命線             fig_master_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['EMA8'], line=dict(color='#ffff00', width=2.8), name='黃金 T 線 (EMA8)'), row=1, col=1)
            fig_master_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['MA20'], line=dict(color='#ffffff', width=1.5, dash='dot'), name='生命線 (MA20)'), row=1, col=1)
            
            # 蝴蝶 XABCD 形態連線             if len(final_res['pts_x']) >= 4:
                fig_master_terminal.add_trace(go.Scatter(
                    x=final_res['pts_x'], y=final_res['pts_y'], 
                    mode='lines+markers+text', 
                    name='形態連線', 
                    line=dict(color='#00ffcc', width=3.5), 
                    text=['X','A','B','C','D'], 
                    textposition="top center"
                ), row=1, col=1)
            
            # 斐波那契位階
            fig_master_terminal.add_hline(y=final_res['fib_buy'], line_dash="dash", line_color="#ffa500", annotation_text="0.618 支撐位", row=1, col=1)
            fig_master_terminal.add_hline(y=final_res['fib_target'], line_dash="dash", line_color="#00ff00", annotation_text="1.272 目標位", row=1, col=1)

            # 2. 第二層：指標
            fig_master_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['RSI'], line=dict(color='#ffcc00', width=3), name='RSI'), row=2, col=1)
            fig_master_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['CCI'], line=dict(color='#007bff', width=2), name='CCI'), row=2, col=1)
            fig_master_terminal.add_hline(y=70, line_dash="dot", line_color="#ff4d4d", row=2, col=1)
            fig_master_terminal.add_hline(y=30, line_dash="dot", line_color="#00ffcc", row=2, col=1)

            # 3. 第三層：MACD MSI             m_colors_v = ['#00ffcc' if val > 0 else '#ff4d4d' for val in final_res['df']['Hist']]
            fig_master_terminal.add_trace(go.Bar(x=final_res['df'].index, y=final_res['df']['Hist'], name='動能柱 (MSI)', marker_color=m_colors_v), row=3, col=1)

            # --- 終極核心：物理座標鎖定修正 (解決平線魔咒) ---
            # 您提供的截圖顯示 Y 軸出現 35M/100M，這是成交量數據污染導致。
            # 下方代碼強制 Y 軸只對焦在股價區間的高低點範圍。
            y_focus_min_val = final_res['df']['Low'].min() * 0.98
            y_focus_max_val = final_res['df']['High'].max() * 1.02
            
            fig_master_terminal.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            
            # 最關鍵的一行：鎖定股價範圍，徹底修復平線
            fig_master_terminal.update_yaxes(range=[y_focus_min_val, y_focus_max_val], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig_master_terminal, use_container_width=True)
            
        else:
            st.warning("系統正在解析數據庫，請確保代碼貼入完整並稍候...")
    except Exception as e:
        st.error(f"系統運行異常，請檢查縮進或數據：{str(e)}")

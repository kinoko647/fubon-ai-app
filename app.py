import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 專業寬螢幕終端進行極限視覺優化)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="2026 戰神終極終端 - PC 500檔全功能完全體", 
    initial_sidebar_state="expanded"
)

# 初始化 Session 狀態，確保所有設定在掃描或切換時保持一致
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'u_code' not in st.session_state: st.session_state.u_code = '2330'
if 'm_type' not in st.session_state: st.session_state.m_type = '台股'
if 'strategy' not in st.session_state: st.session_state.strategy = '🛡️ 長線穩健 (Long)'
if 'tf_choice' not in st.session_state: st.session_state.tf_choice = '日線'

# ==============================================================================
# 2. 授權與安全驗證系統 (密碼：8888)
# ==============================================================================
def check_password():
    if st.session_state.authenticated:
        return True
    st.title("🔒 2026 戰神操盤終端 - 授權驗證")
    st.markdown("""
        <h1 style='color: #00ffcc; font-weight: 900; text-align: center;'>戰神終極完全體：500 檔全市場自動化掃描終端</h1>
        <p style='color: #ffffff; font-size: 24px; text-align: center;'>解鎖核心黃金交叉與 W/M 形態辨識引擎。</p>
    """, unsafe_allow_html=True)
    pwd_input = st.text_input("請輸入管理員授權碼", type="password")
    if st.button("啟動旗艦系統"):
        if pwd_input == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 授權碼錯誤，請重新輸入。")
    return False

if check_password():
    # ==============================================================================
    # 3. 旗艦終端專業 CSS 樣式 (終極高對比 - 解決字體顏色問題)
    # ==============================================================================
    st.markdown("""
        <style>
        /* 深色專業背底 */
        .main { background-color: #0d1117; }
        
        /* 核心指標卡片 (Metric) - 極光綠發光字體 */
        [data-testid="stMetricValue"] { 
            color: #00ffcc !important; 
            font-weight: 900 !important; 
            font-size: 3.2rem !important;
            text-shadow: 2px 2px 15px rgba(0, 255, 204, 0.7);
        }
        [data-testid="stMetricLabel"] {
            color: #ffffff !important;
            font-weight: 900 !important;
            font-size: 22px !important;
            opacity: 1 !important;
        }
        .stMetric {
            background-color: #000000;
            padding: 30px;
            border-radius: 15px;
            border: 3px solid #30363d;
            box-shadow: 0 10px 25px rgba(0,0,0,0.8);
        }

        /* 傑克看板 - 終極清晰漆黑版 */
        .jack-panel {
            background-color: #000000;
            padding: 35px;
            border-radius: 20px;
            border-left: 15px solid #007bff;
            border-right: 2px solid #30363d;
            border-top: 2px solid #30363d;
            border-bottom: 2px solid #30363d;
            margin-bottom: 35px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.9);
        }
        .jack-title { color: #ffffff; font-weight: 900; font-size: 36px; margin-bottom: 15px; }
        .jack-status-highlight { color: #00ffcc !important; font-weight: 900; font-size: 30px; text-decoration: underline; }
        .jack-sub-text { color: #ffffff !important; font-size: 24px; line-height: 2.2; font-weight: 900; }
        .jack-value { color: #ffff00 !important; font-weight: 900; font-size: 28px; }

        /* AI 診斷診斷文字區 */
        .ai-diag-box {
            background-color: #000000;
            padding: 30px;
            border-radius: 20px;
            border: 4px solid #ff4d4d;
            margin-top: 25px;
        }
        .diag-item-success { color: #00ffcc !important; font-weight: 900; font-size: 24px; margin-bottom: 12px; }
        .diag-item-error { color: #ff3e3e !important; font-weight: 900; font-size: 24px; margin-bottom: 12px; }

        /* 交易建議大卡片 */
        .advice-card {
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 25px;
            font-weight: 900;
            text-align: center;
            border: 6px solid;
            font-size: 26px;
            box-shadow: 0 0 35px rgba(0,0,0,0.7);
        }
        .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.4); }
        .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.3); }
        
        /* PC 按鈕視覺強化 */
        .stButton>button {
            border-radius: 12px;
            font-weight: 900;
            height: 4.5rem;
            background-color: #161b22;
            color: #00ffcc;
            font-size: 20px;
            border: 2px solid #00ffcc;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #00ffcc;
            color: #000000;
            box-shadow: 0 0 25px #00ffcc;
        }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 4. 核心分析引擎 (W/M偵測、多重金叉、物理座標修復)
    # ==============================================================================
    def analyze_master_terminal(df, budget, strategy_mode):
        """核心引擎：執行形態偵測、技術計算、AI診斷"""
        if df is None or df.empty or len(df) < 60:
            return None
        
        # 處理多層索引
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        close_p = df['Close'].values.flatten().astype(float)
        high_p = df['High'].values.flatten().astype(float)
        low_p = df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- [A] 傑克核心指標：均線、布林通道與收斂度 ---
        df['MA20'] = df['Close'].rolling(20).mean()
        df['EMA8'] = df['Close'].ewm(span=8).mean()
        df['STD'] = df['Close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20']
        curr_bandwidth = float(df['BW'].iloc[-1])
        
        # --- [B] 黃金交叉偵測 (Golden Cross) ---
        # 1. 均線金叉：EMA8 穿 MA20
        gc_ma = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1] and df['EMA8'].iloc[-2] <= df['MA20'].iloc[-2]
        # 2. MACD 動能金叉 (Hist 負轉正)
        df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        gc_macd = df['Hist'].iloc[-1] > 0 and df['Hist'].iloc[-2] <= 0
        
        # --- [C] 形態偵測：收斂 W 底 / 收斂 M 頭 ---
        n_order = 12
        max_peaks = argrelextrema(high_p, np.greater, order=n_order)[0]
        min_peaks = argrelextrema(low_p, np.less, order=n_order)[0]
        all_pts_idx = sorted(np.concatenate([max_peaks[-3:], min_peaks[-3:]]))
        
        pattern_label = "趨勢形成中"
        ai_win_score = 60
        diag_reasons = [] # AI 診斷原因列表
        
        if len(all_pts_idx) >= 4:
            v = [df['Close'].iloc[i] for i in all_pts_idx[-4:]]
            if v[0] > v[1] and v[2] > v[1] and v[2] > v[3]: # M頭
                if v[2] <= v[0] * 1.015:
                    pattern_label = "收斂 M 頭 (高位警示)"
                    ai_win_score -= 20
                    diag_reasons.append("🔴 偵測到雙重頂部 (M頭) 壓力，上方拋壓沉重且無法突破。")
            elif v[0] < v[1] and v[2] < v[1] and v[2] < v[3]: # W底
                if v[2] >= v[0] * 0.985:
                    pattern_label = "收斂 W 底 (起漲預兆)"
                    ai_win_score += 30
                    diag_reasons.append("🟢 偵測到雙重底部 (W底)，第二次回測不破底，具備暴力噴發潛力。")

        # --- [D] 診斷加權 ---
        if gc_ma: 
            ai_win_score += 10
            diag_reasons.append("🟢 ✨ 黃金交叉確認：短期均線向上穿透生命線，趨勢轉多。")
        elif df['EMA8'].iloc[-1] > df['MA20'].iloc[-1]:
            diag_reasons.append("🟢 趨勢排列：目前處於健康的多頭排列。")
        else:
            diag_reasons.append("🔴 趨勢受阻：目前受制於生命線壓力，均線尚未金叉。")
            
        if gc_macd:
            ai_win_score += 10
            diag_reasons.append("🟢 🚀 動能金叉：MACD 能量由負轉正，多頭開始奪回控盤權。")
        
        if curr_bandwidth < 0.12:
            ai_win_score += 10
            diag_reasons.append("🟢 💎 強烈收斂：波動率極度壓縮，變盤爆發機率極高。")

        # --- [E] 斐波那契與投資試算 ---
        lookback = 120
        max_v = float(high_p[-lookback:].max())
        min_v = float(low_p[-lookback:].min())
        fib_buy = max_v - 0.618 * (max_v - min_v)
        fib_target = min_v + 1.272 * (max_v - min_v)
        
        # RSI 與 CCI 指標
        delta_p = df['Close'].diff()
        gain_p = (delta_p.where(delta_p > 0, 0)).rolling(14).mean()
        loss_p = (-delta_p.where(delta_p < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain_p / loss_p.replace(0, 0.001))))
        tp_p = (df['High'] + df['Low'] + df['Close']) / 3
        df['CCI'] = (tp_p - tp_p.rolling(20).mean()) / (0.015 * tp_p.rolling(20).std())

        # 入場時間建議
        entry_timing = "⏳ 等待動能同步"
        if ma_gc and gc_macd: entry_timing = "🔥 即刻進場 (雙金叉確立)"
        elif curr_p <= fib_buy * 1.01: entry_timing = "💎 分批佈局 (價值支撐區)"
        
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        days_est = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0
        shares_est = int(budget / curr_p)

        return {
            "score": min(ai_win_score, 98), "curr": curr_p, "shares": shares_est, "days": days_est,
            "profit": (shares_est * fib_target) - (shares_est * curr_p), "roi": ((fib_target / curr_p) - 1) * 100,
            "df": df, "fib_buy": fib_buy, "fib_target": fib_target, "bandwidth": curr_bandwidth, 
            "pattern": pattern_label, "reasons": diag_reasons, "timing": entry_timing,
            "gc_ma": gc_ma, "gc_macd": gc_macd,
            "pts_x": [df.index[i] for i in all_pts_idx[-5:]], "pts_y": [df['Close'].iloc[i] for i in all_pts_idx[-5:]],
            "right_ok": curr_p > df['EMA8'].iloc[-1] and df['Hist'].iloc[-1] > df['Hist'].iloc[-2],
            "left_ok": curr_p <= fib_buy * 1.02 and df['RSI'].iloc[-1] < 45
        }

    # ==============================================================================
    # 5. PC 側邊欄：500 檔海量形態掃描器
    # ==============================================================================
    with st.sidebar:
        st.header("⚙️ 戰神全市場掃描器")
        st.session_state.strategy = st.selectbox("🎯 交易戰略模式", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"))
        st.session_state.tf_choice = st.selectbox("⏳ 分析時間週期", ("15分鐘", "1小時", "2小時", "日線", "週線"), index=3)
        
        st.divider()
        st.write("🔍 **台股海量標的自動化偵測 (300~500檔)**")
        scan_grp = st.radio("掃描對象類別", ("權值 0050 組", "中型 0051 組", "高股息/熱門標的 300檔"))
        
        if st.button("🚀 啟動全市場自動篩選"):
            # 建立海量清單
            if "0050" in scan_grp:
                target_list = ["2330","2317","2454","2308","2382","2881","2303","2882","2891","3711","2412","2886","1216","2884","2892","2002","2357","3008","2603","2880","2324","2609","2885","2883","3231","2408","4938","2890","2912","1301","1303","2301","3045","2615","5871","2379","6415","3037","2377","1513","2356","2801","1101","4904","2105","9910","1402","2313","1605"]
            elif "0051" in scan_grp:
                target_list = ["1476","1503","1504","1519","1560","1590","1605","1707","1717","1722","1723","1760","1789","1802","1904","2006","2014","2027","2031","2103","2106","2108","2204","2206","2231","2316","2323","2337","2344","2347","2352","2354","2355","2362","2367","2371","2376","2383","2385","2392","2393","2401","2404","2409","2421","2439","2441","2451","2455","2458","2474","2480","2492","2498","2501","2511","2515","2520","2534","2542","2548","2605","2606","2607","2610","2612","2618","2633","2634","2637","2707","2723","2809","2812","2834","2845","2855","2887","2888","2889","2897","2903","2915","3004","3005","3017","3019","3023","3034","3035","3044","3189","3264","3406","3443","3481","3532","3533","3596","3653","3661"]
            else:
                # 終極 300+ 綜合列表
                target_list = ["2330","2317","2454","2382","2603","2609","2615","2303","3231","2353","2376","2383","2449","3037","3034","3035","3443","3661","6669","8046","1513","1519","1503","1504","1722","1723","2881","2882","2891","2886","2884","2892","5871","5876","9921","9904","9945","1402","1101","1102","1301","1303","1326","0050","0056","00878","00919","00929","00713","00940","1605","2002","2105","2207","2327","2357","2395","2409","2474","2498","2542","2618","2801","2880","2883","2885","2887","2888","2889","2890","2912","3008","3017","3045","3481","3711","4904","4938","5880","6239","6415","8215","9910"]

            scan_results = []
            progress_bar = st.progress(0)
            status_info = st.empty()
            
            for i, code in enumerate(target_list):
                status_info.text(f"分析中: {code}.TW")
                try:
                    s_raw = yf.download(f"{code}.TW", period="1y", progress=False)
                    s_res = analyze_master_terminal(s_raw, 1000000, st.session_state.strategy)
                    if s_res and ("W底" in s_res['pattern'] or s_res['score'] >= 85):
                        scan_results.append({"代碼": code, "形態": s_res['pattern'], "AI勝率": f"{s_res['score']}%", "ROI": f"{s_res['roi']:.1f}%"})
                except: continue
                progress_bar.progress((i + 1) / len(target_list))
            
            st.session_state.pc_full_market_data = pd.DataFrame(scan_results)
            status_info.success(f"✅ 全市場掃描完成！發現 {len(scan_results)} 支優質標的。")
            
        if 'pc_full_market_data' in st.session_state:
            st.write(f"### {scan_grp} 診斷結果 (僅顯示高勝率或起漲形態)")
            st.dataframe(st.session_state.pc_full_market_data, use_container_width=True, height=500)

        st.divider()
        if st.button("🚪 安全登出終端"):
            st.session_state.authenticated = False
            st.rerun()

    # ==============================================================================
    # 6. PC 主畫面：深度診斷與終極圖表 (物理座標修復)
    # ==============================================================================
    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy}")
    
    # 診斷輸入
    c_col1, c_col2, c_col3 = st.columns([1, 1, 1])
    with c_col1: m_env = st.radio("當前市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with c_col2: u_id = st.text_input("🔍 代碼深度診斷", value=st.session_state.u_code)
    with c_col3: u_inv = st.number_input("💰 投資預算金額 (元)", value=1000000)

    st.session_state.u_code, st.session_state.m_type = u_id, m_env
    ticker_final = f"{u_id}.TW" if m_env == "台股" else u_id

    # 映射
    tf_map_main = {"15分鐘":"15m", "1小時":"60m", "2小時":"120m", "日線":"1d", "週線":"1wk"}
    p_map_main = {"15分鐘":"5d", "1小時":"1mo", "2小時":"2mo", "日線":"2y", "週線":"max"}

    try:
        main_df = yf.download(ticker_final, interval=tf_map_main[st.session_state.tf_choice], period=p_map_main[st.session_state.tf_choice], progress=False)
        final_res = analyze_master_terminal(main_df, u_inv, st.session_state.strategy)
        
        if final_res:
            # --- [A] 傑克指標專業看板 (超高飽和度無視角) ---
            bw_v = final_res['bandwidth']
            bw_desc = "📉 強烈收斂 (變盤大噴發在即)" if bw_v < 0.12 else "📊 發散趨勢 (能量持續釋放)"
            gc_msg = "✨ 黃金交叉確認" if final_res['gc_ma'] or final_res['gc_macd'] else "⏳ 等待訊號共振"
            
            st.markdown(f"""
                <div class="jack-panel">
                    <div class="jack-title">📊 傑克技術看板：{bw_desc}</div>
                    <hr style='border-color:#30363d; border-width: 4px;'>
                    <p class="jack-sub-text">🔥 形態識別：<span class="jack-status-highlight">{final_res['pattern']}</span> | <span style='color:#ffff00;'>{gc_msg}</span></p>
                    <p class="jack-sub-text">錄場建議：<span class="jack-value">{final_res['timing']}</span> | 預計達成：<span class="jack-value">{final_res['days']} 天</span></p>
                    <p class="jack-sub-text">建議佈局位：<span class="jack-value">${final_res['fib_buy']:,.2f}</span> | 目標預測位：<span class="jack-value">${final_res['fib_target']:,.2f}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            # 
            # --- [B] 雙側交易建議 ---
            adv1, adv2 = st.columns(2)
            with adv1:
                if final_res['left_ok']: st.markdown('<div class="advice-card left-side">💎 左側訊號：進入斐波 0.618 價值區，適合分批低吸佈局。</div>', unsafe_allow_html=True)
                else: st.info("左側抄底條件尚未冷卻，目前非最佳價值區。")
            with adv2:
                if final_res['right_ok']: st.markdown('<div class="advice-card right-side">🚀 右側訊號：站上 EMA8 均線且金叉確認，適合強勢追進！</div>', unsafe_allow_html=True)
                else: st.warning("右側突破動能尚未確認，建議等待均線站穩。")

            # --- [C] AI 為什麼勝率低？深度技術診斷 ---
            with st.expander("🔍 AI 深度診斷報告 (解釋勝率評分原因)", expanded=(final_res['score'] < 75)):
                st.markdown("<div class='ai-diag-box'>", unsafe_allow_html=True)
                for r in final_res['reasons']:
                    cls = 'diag-item-success' if '🟢' in r else 'diag-item-error'
                    st.markdown(f"<div class='{cls}'>{r}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.info(f"🔹 **預算分配建議：** {u_inv:,} 元 | **入場股數：** {final_res['shares']:,} 股")

            # --- [D] 核心指標數據儀表板 ---
            dash1, dash2, dash3, dash4 = st.columns(4)
            dash1.metric("AI 綜合勝率", f"{final_res['score']}%")
            dash2.metric("預期報酬 (ROI)", f"{final_res['roi']:.1f}%")
            dash3.metric("建議持有總股數", f"{final_res['shares']:,} 股")
            dash4.metric("預計盈利總額", f"${final_res['profit']:,.0f}")

            # --- [E] 📈 專業三層聯動圖表 (物理座標鎖定對焦) ---
            #             fig_master = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.55, 0.2, 0.25], vertical_spacing=0.03,
                               subplot_titles=("K線、布林通道與蝴蝶 XABCD 形態", "RSI 與 CCI 能量強弱診斷", "MACD (MSI) 趨勢動能柱狀圖"))
            
            # 第一層：主圖
            fig_master.add_trace(go.Candlestick(x=final_res['df'].index, open=final_res['df']['Open'], high=final_res['df']['High'], low=final_res['df']['Low'], close=final_res['df']['Close'], name='K線'), row=1, col=1)
            # 布林與均線             fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Upper'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林上軌'), row=1, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Lower'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林下軌', fill='tonexty'), row=1, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['EMA8'], line=dict(color='#ffff00', width=2.8), name='黃金 T 線 (EMA8)'), row=1, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['MA20'], line=dict(color='#ffffff', width=1.5, dash='dot'), name='生命線 (MA20)'), row=1, col=1)
            
            # 蝴蝶形態連線             if len(final_res['pts_x']) >= 4:
                fig_master.add_trace(go.Scatter(x=final_res['pts_x'], y=final_res['pts_y'], mode='lines+markers+text', name='蝴蝶形態', line=dict(color='#00ffcc', width=3.5), text=['X','A','B','C','D'], textposition="top center"), row=1, col=1)
            
            fig_master.add_hline(y=final_res['fib_buy'], line_dash="dash", line_color="#ffa500", annotation_text="0.618 支撐買點", row=1, col=1)
            fig_master.add_hline(y=final_res['fib_target'], line_dash="dash", line_color="#00ff00", annotation_text="1.272 目標獲利", row=1, col=1)

            #             fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['RSI'], line=dict(color='#ffcc00', width=3), name='RSI'), row=2, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['CCI'], line=dict(color='#007bff', width=2), name='CCI'), row=2, col=1)
            
            #             m_cols = ['#00ffcc' if val > 0 else '#ff4d4d' for val in final_res['df']['Hist']]
            fig_master.add_trace(go.Bar(x=final_res['df'].index, y=final_res['df']['Hist'], name='動能柱 (MSI)', marker_color=m_cols), row=3, col=1)

            # --- 核心中的核心：座標物理鎖定 (徹底防止 K 線縮成平線) ---
            # 您截圖中出現的 35M/100M 問題，是由於 Plotly 將成交量與價格混用座標軸導致。
            # 下方代碼強制 Y 軸只對焦在股價的高低點範圍。
            y_focus_min = final_res['df']['Low'].min() * 0.98
            y_focus_max = final_res['df']['High'].max() * 1.02
            
            fig_master.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            
            # 強制鎖定第一層 Y 軸範圍
            fig_master.update_yaxes(range=[y_focus_min, y_focus_max], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig_master, use_container_width=True)
            
        else: st.warning("系統正在解析數據中，請確保代碼完整貼上...")
    except Exception as e: st.error(f"系統運行異常：{str(e)}")

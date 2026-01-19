import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 專業操盤終端進行極限視覺優化)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="2026 戰神終極終端 - PC 全功能海量掃描版", 
    initial_sidebar_state="expanded"
)

# 初始化 Session 狀態
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
        <h2 style='color: #00ffcc; font-weight: 900;'>戰神旗艦完全體：海量掃描、形態偵測、黃金交叉。</h2>
        <p style='color: #ffffff; font-size: 20px;'>請輸入管理員授權碼以進入 2026 終極終端。</p>
    """, unsafe_allow_html=True)
    pwd_input = st.text_input("請輸入授權碼", type="password")
    if st.button("確認進入旗艦系統"):
        if pwd_input == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 授權碼錯誤，拒絕訪問。")
    return False

if check_password():
    # ==============================================================================
    # 3. 旗艦終端專業 CSS 樣式 (超高飽和度、極致清晰度優化)
    # ==============================================================================
    st.markdown("""
        <style>
        /* 深色背景優化 */
        .main { background-color: #0d1117; }
        
        /* 核心指標卡片 (Metric) - 極致綠發光字體 */
        [data-testid="stMetricValue"] { 
            color: #00ffcc !important; 
            font-weight: 900 !important; 
            font-size: 3rem !important;
            text-shadow: 2px 2px 15px rgba(0, 255, 204, 0.6);
        }
        [data-testid="stMetricLabel"] {
            color: #ffffff !important;
            font-weight: 900 !important;
            font-size: 22px !important;
        }
        .stMetric {
            background-color: #000000;
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #30363d;
            box-shadow: 0 6px 15px rgba(0,0,0,0.7);
        }

        /* 傑克看板 - 終極清晰版 */
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
        .jack-title { color: #ffffff; font-weight: 900; font-size: 34px; margin-bottom: 12px; }
        .jack-status-highlight { color: #00ffcc; font-weight: 900; font-size: 30px; text-decoration: underline; }
        .jack-sub-text { color: #ffffff; font-size: 24px; line-height: 2; font-weight: 900; }
        .jack-value { color: #ffff00 !important; font-weight: 900; font-size: 26px; }

        /* AI 診斷診斷文字區 */
        .ai-diag-box {
            background-color: #000000;
            padding: 30px;
            border-radius: 15px;
            border: 3px solid #ff4d4d;
            margin-top: 20px;
        }
        .diag-item-success { color: #00ffcc !important; font-weight: 900; font-size: 22px; margin-bottom: 12px; }
        .diag-item-error { color: #ff3e3e !important; font-weight: 900; font-size: 22px; margin-bottom: 12px; }

        /* 交易建議卡片 */
        .advice-card {
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            font-weight: 900;
            text-align: center;
            border: 5px solid;
            font-size: 24px;
            box-shadow: 0 0 30px rgba(0,0,0,0.6);
        }
        .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.4); }
        .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.3); }
        
        /* 側邊欄與按鈕 */
        .stButton>button {
            border-radius: 12px;
            font-weight: 900;
            height: 4.5rem;
            background-color: #161b22;
            color: #00ffcc;
            font-size: 20px;
            border: 2px solid #00ffcc;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #00ffcc;
            color: #000000;
            box-shadow: 0 0 25px #00ffcc;
        }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 4. 核心分析引擎 (W/M 偵測、黃金交叉、蝴蝶、海量數據處理)
    # ==============================================================================
    def analyze_master_terminal(df, budget, strategy_mode):
        if df is None or df.empty or len(df) < 60: return None
        
        # 多層索引處理
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        close_p = df['Close'].values.flatten().astype(float)
        high_p = df['High'].values.flatten().astype(float)
        low_p = df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- [A] 傑克均線與收斂帶 ---
        df['MA20'] = df['Close'].rolling(20).mean()
        df['EMA8'] = df['Close'].ewm(span=8).mean()
        df['Upper'] = df['MA20'] + (df['Close'].rolling(20).std() * 2)
        df['Lower'] = df['MA20'] - (df['Close'].rolling(20).std() * 2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20']
        curr_bw = float(df['BW'].iloc[-1])
        
        # --- [B] 黃金交叉邏輯 ---
        ma_gc = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1] and df['EMA8'].iloc[-2] <= df['MA20'].iloc[-2]
        is_bullish = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1]
        
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        macd_gc = df['Hist'].iloc[-1] > 0 and df['Hist'].iloc[-2] <= 0
        
        # --- [C] 收斂 W 底 / M 頭 偵測 ---
        n_order = 12
        max_peaks = argrelextrema(high_p, np.greater, order=n_order)[0]
        min_peaks = argrelextrema(low_p, np.less, order=n_order)[0]
        all_pts_idx = sorted(np.concatenate([max_peaks[-3:], min_peaks[-3:]]))
        
        pattern_label = "趨勢形成中"
        ai_win_score = 60
        diag_list = []
        
        if len(all_pts_idx) >= 4:
            v = [df['Close'].iloc[i] for i in all_pts_idx[-4:]]
            if v[0] > v[1] and v[2] > v[1] and v[2] > v[3]: # M頭
                if v[2] <= v[0] * 1.01:
                    pattern_label = "收斂 M 頭 (空頭風險)"
                    ai_win_score -= 20
                    diag_list.append("🔴 形態警示：偵測到雙重頂部 M 頭，壓力區無法突破。")
            elif v[0] < v[1] and v[2] < v[1] and v[2] < v[3]: # W底
                if v[2] >= v[0] * 0.99:
                    pattern_label = "收斂 W 底 (底部起漲)"
                    ai_win_score += 30
                    diag_list.append("🟢 形態驚喜：偵測到收斂 W 底，第二次低點不破底，具備起漲動能。")

        # --- [D] 診斷邏輯補完 ---
        if gc_ma: 
            ai_win_score += 10
            diag_list.append("🟢 ✨ 黃金交叉：均線 T 線正式上穿月線，趨勢翻轉。")
        elif is_bullish:
            diag_list.append("🟢 均線目前處於健康的多頭排列。")
        else:
            diag_list.append("🔴 均線空頭排列，目前受制於生命線壓力。")
            
        if macd_gc:
            ai_win_score += 10
            diag_list.append("🟢 🚀 動能金叉：MACD 能量柱由負轉正，多頭力道啟動。")
        
        if curr_bw < 0.12:
            ai_win_score += 10
            diag_list.append("🟢 💎 強烈收斂：波動極限壓縮，大行情即將變盤噴發。")

        # --- [E] 斐波那契全位階與目標 ---
        max_v = float(high_p[-120:].max())
        min_v = float(low_p[-120:].min())
        fib_buy = max_v - 0.618 * (max_v - min_v)
        fib_target = min_v + 1.272 * (max_v - min_v)
        
        # 指標
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
        
        entry_advice = "⏳ 等待訊號確認"
        if gc_ma and gc_macd: entry_advice = "🔥 即刻進場 (雙重確認)"
        elif curr_p <= fib_buy * 1.01: entry_advice = "💎 支撐區掛單佈局"
        
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        days_est = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0
        shares = int(budget / curr_p)

        return {
            "score": min(ai_win_score, 98), "curr": curr_p, "shares": shares, "days": days_est,
            "profit": (shares * fib_target) - (shares * curr_p), "roi": ((fib_target / curr_p) - 1) * 100,
            "df": df, "fib_buy": fib_buy, "fib_target": fib_target, "bw": curr_bw, 
            "pattern": pattern_label, "reasons": diag_list, "timing": entry_advice,
            "pts_x": [df.index[i] for i in all_pts_idx[-5:]], "pts_y": [df['Close'].iloc[i] for i in all_pts_idx[-5:]],
            "ma_gc": ma_gc, "macd_gc": macd_gc, "right_ok": curr_p > df['EMA8'].iloc[-1] and df['Hist'].iloc[-1] > df['Hist'].iloc[-2],
            "left_ok": curr_p <= fib_buy * 1.02 and df['RSI'].iloc[-1] < 45
        }

    # ==============================================================================
    # 5. PC 側邊欄：海量掃描器 (擴展至 150+ 標的)
    # ==============================================================================
    with st.sidebar:
        st.header("⚙️ 戰神海量操盤控制台")
        st.session_state.strategy = st.selectbox("🎯 交易戰略", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"))
        st.session_state.tf_choice = st.selectbox("⏳ 分析週期", ("15分鐘", "1小時", "2小時", "日線", "週線"), index=3)
        
        st.divider()
        st.write("🔍 **全市場海量形態掃描 (150+ 標的)**")
        scan_cat = st.selectbox("選擇掃描類別", ("電子權值 50", "金融/傳產 50", "中型成分股 50", "高股息熱門 50"))
        
        if st.button("🚀 啟動海量自動篩選"):
            # 分類海量代碼清單
            cat_map = {
                "電子權值 50": ["2330","2317","2454","2308","2382","2303","3711","2357","3008","2324","3231","2408","4938","2301","2379","6415","3037","2377","2356","2313","2327","2395","2449","3034","3035","3044","3189","3443","3532","3533","3653","3661","4958","4961","4966","5269","5274","6213","6239","6669","8046","8215","2360","3017","3583","4919","6206","2368","2474","2353"],
                "金融/傳產 50": ["2881","2882","2891","2886","2884","2892","2880","2885","2883","2890","5871","2801","1216","2002","2603","2609","2615","1301","1303","1101","1402","1605","2105","9910","1210","1326","2002","2101","2201","2207","2606","2610","2618","2912","5880","9904","9921","9945","2015","2633","2809","2812","2834","2845","2855","2887","2888","2889","2897","5876"],
                "中型成分股 50": ["1476","1503","1504","1513","1519","1560","1590","1605","1707","1717","1722","1723","1760","1789","1802","1904","2006","2014","2027","2031","2103","2106","2108","2204","2206","2231","2316","2323","2337","2344","2347","2352","2354","2355","2362","2367","2371","2376","2383","2385","2392","2393","2401","2404","2409","2421","2439","2441","2451","2455"],
                "高股息熱門 50": ["0050","0056","00878","00919","00929","00713","00940","006208","0051","0052","2330","2317","2454","2382","2303","2412","2881","2882","2891","2002","2603","1301","2357","2886","2884","2892","2308","1216","2880","2324","2609","3231","2885","4938","2883","2408","2890","2912","1303","2301","3045","2615","5871","2379","6415","3037","2377","1513","2356","2801"]
            }
            target_list = cat_map[scan_cat]
            
            scan_res = []
            p_bar = st.progress(0)
            status_upd = st.empty()
            
            for idx, code in enumerate(target_list):
                status_upd.text(f"海量分析中: {code}.TW")
                try:
                    s_raw = yf.download(f"{code}{'.TW' if code.isdigit() else ''}", period="1y", progress=False)
                    s_res = analyze_master_terminal(s_raw, 1000000, st.session_state.strategy)
                    if s_res:
                        scan_res.append({"代碼": code, "形態": s_res['pattern'], "AI勝率": f"{s_res['score']}%", "ROI": f"{s_res['roi']:.1f}%"})
                except: continue
                p_bar.progress((idx + 1) / len(target_list))
            
            st.session_state.pc_full_scan_report = pd.DataFrame(scan_res)
            status_upd.success(f"✅ {scan_cat} 海量掃描任務完成！")
            
        if 'pc_full_scan_report' in st.session_state:
            st.write(f"### {scan_cat} 診斷結果")
            st.dataframe(st.session_state.pc_full_scan_report, use_container_width=True, height=500)

        st.divider()
        if st.button("🚪 安全登出系統"):
            st.session_state.authenticated = False
            st.rerun()

    # ==============================================================================
    # 6. PC 主畫面顯示邏輯 (大螢幕旗艦佈局)
    # ==============================================================================
    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy}")
    
    col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
    with col_t1: market_env = st.radio("當前市場環境", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with col_t2: user_ticker = st.text_input("🔍 輸入診斷代碼 (例如: 2317)", value=st.session_state.u_code)
    with col_t3: budget_in = st.number_input("💰 投資預算金額 (元)", value=1000000)

    st.session_state.u_code, st.session_state.m_type = user_ticker, market_env
    ticker_final = f"{user_ticker}.TW" if market_env == "台股" else user_ticker

    # yf 映射映射
    tf_map_main = {"15分鐘":"15m", "1小時":"60m", "2小時":"120m", "日線":"1d", "週線":"1wk"}
    p_map_main = {"15分鐘":"5d", "1小時":"1mo", "2小時":"2mo", "日線":"2y", "週線":"max"}

    try:
        main_df = yf.download(ticker_final, interval=tf_map_main[st.session_state.tf_choice], period=p_map_main[st.session_state.tf_choice], progress=False)
        final_res = analyze_master_terminal(main_df, budget_in, st.session_state.strategy)
        
        if final_res:
            # --- [A] 傑克看板 (超高對比無視角) ---
            bw_v = final_res['bw']
            bw_desc = "📉 強烈收斂 (波動極限壓縮，變盤即將噴發)" if bw_v < 0.12 else "📊 發散趨勢 (能量持續釋放)"
            gc_msg = "✨ 黃金交叉確認" if final_res['ma_gc'] or final_res['macd_gc'] else "⏳ 等待動能同步"
            
            st.markdown(f"""
                <div class="jack-panel">
                    <div class="jack-title">📊 傑克技術看板：{bw_desc}</div>
                    <hr style='border-color:#30363d; border-width: 3px;'>
                    <p class="jack-sub-text">🔥 偵測形態：<span class="jack-status-highlight">{final_res['pattern']}</span> | <span style='color:#ffff00;'>{gc_msg}</span></p>
                    <p class="jack-sub-text">建議錄場：<span class="jack-value">{final_res['timing']}</span> | 預計達成時間：<span class="jack-value">{final_res['days']} 天</span></p>
                    <p class="jack-sub-text">建議佈局位：<span class="jack-value">${final_res['fib_buy']:,.2f}</span> | 目標預測位：<span class="jack-value">${final_res['fib_target']:,.2f}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            

            # --- [B] 雙側交易建議卡片 ---
            adv1, adv2 = st.columns(2)
            with adv1:
                if final_res['left_ok']: st.markdown('<div class="advice-card left-side">💎 左側訊號：進入斐波支撐區，RSI 超跌，適合低吸佈局。</div>', unsafe_allow_html=True)
                else: st.info("左側抄底條件尚未滿足")
            with adv2:
                if final_res['right_ok']: st.markdown('<div class="advice-card right-side">🚀 右側訊號：站上均線且金叉確認，適合強勢追進！</div>', unsafe_allow_html=True)
                else: st.warning("右側動能尚未獲得確認")

            # --- [C] AI 深度診斷區 ---
            with st.expander("🔍 AI 深度技術報告 (字體顏色已加粗強化)", expanded=(final_res['score'] < 75)):
                st.markdown("<div class='ai-diag-box'>", unsafe_allow_html=True)
                for r in final_res['reasons']:
                    c_style = 'diag-item-success' if '🟢' in r else 'diag-item-error'
                    st.markdown(f"<div class='{c_style}'>{r}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.info(f"🔹 **預算分配建議：** {budget_in:,} 元 | **可買入股數：** {final_res['shares']:,} 股")

            # --- [D] 數據儀表板 ---
            dash1, dash2, dash3, dash4 = st.columns(4)
            dash1.metric("AI 綜合勝率", f"{final_res['score']}%")
            dash2.metric("預期報酬 (ROI)", f"{final_res['roi']:.1f}%")
            dash3.metric("建議持股總數", f"{final_res['shares']:,} 股")
            dash4.metric("預計盈利總額", f"${final_res['profit']:,.0f}")

            # --- [E] 📈 專業三層聯動圖表 (終極座標物理鎖定) ---
            # 
            fig_master = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.55, 0.2, 0.25], vertical_spacing=0.03,
                               subplot_titles=("K線、布林通道與蝴蝶 XABCD 形態", "RSI 與 CCI 能量強弱診斷", "MACD (MSI) 趨勢動能柱狀圖"))
            
            fig_master.add_trace(go.Candlestick(x=final_res['df'].index, open=final_res['df']['Open'], high=final_res['df']['High'], low=final_res['df']['Low'], close=final_res['df']['Close'], name='K線'), row=1, col=1)
            # 布林與均線
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Upper'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林上軌'), row=1, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Lower'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林下軌', fill='tonexty'), row=1, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['EMA8'], line=dict(color='#ffff00', width=2.8), name='黃金 T 線 (EMA8)'), row=1, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['MA20'], line=dict(color='#ffffff', width=1.5, dash='dot'), name='生命線 (MA20)'), row=1, col=1)
            
            # 蝴蝶形態 
            if len(final_res['pts_x']) >= 4:
                fig_master.add_trace(go.Scatter(x=final_res['pts_x'], y=final_res['pts_y'], mode='lines+markers+text', name='蝴蝶連線', line=dict(color='#00ffcc', width=3.5), text=['X','A','B','C','D'], textposition="top center"), row=1, col=1)
            
            fig_master.add_hline(y=final_res['fib_buy'], line_dash="dash", line_color="#ffa500", annotation_text="0.618 支撐位")
            fig_master.add_hline(y=final_res['fib_target'], line_dash="dash", line_color="#00ff00", annotation_text="1.272 目標位")

            # 
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['RSI'], line=dict(color='#ffcc00', width=3), name='RSI'), row=2, col=1)
            fig_master.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['CCI'], line=dict(color='#007bff', width=2), name='CCI'), row=2, col=1)
            
            macd_colors = ['#00ffcc' if val > 0 else '#ff4d4d' for val in final_res['df']['Hist']]
            fig_master.add_trace(go.Bar(x=final_res['df'].index, y=final_res['df']['Hist'], name='動能柱 (MSI)', marker_color=macd_colors), row=3, col=1)

            # --- 物理鎖定對焦 (徹底防止 K 線變平) ---
            y_min_f = final_res['df']['Low'].min() * 0.98
            y_max_f = final_res['df']['High'].max() * 1.02
            fig_master.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            fig_master.update_yaxes(range=[y_min_f, y_max_f], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig_master, use_container_width=True)
            
        else: st.warning("數據解析中，請確認代碼已完整貼上...")
    except Exception as e: st.error(f"系統運行異常：{str(e)}")

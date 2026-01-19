import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 專業操盤終端視覺優化)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="2026 戰神終極終端 - PC 全功能旗艦", 
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
        <h3 style='color: #00ffcc;'>本系統包含【黃金交叉引擎】與【AI 深度診斷邏輯】</h3>
        <p style='color: #ffffff;'>請輸入 4 位數授權碼解鎖旗艦 PC 功能。</p>
    """, unsafe_allow_html=True)
    pwd_input = st.text_input("請輸入授權碼", type="password")
    if st.button("確認進入系統"):
        if pwd_input == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 授權碼錯誤")
    return False

if check_password():
    # ==============================================================================
    # 3. 旗艦終端專業 CSS 樣式 (極高對比度優化 - 解決字體看不清楚問題)
    # ==============================================================================
    st.markdown("""
        <style>
        /* 背景底色 */
        .main { background-color: #0d1117; }
        
        /* 核心指標卡片 (Metric) - 字體加粗並發光 */
        [data-testid="stMetricValue"] { 
            color: #00ffcc !important; 
            font-weight: 900 !important; 
            font-size: 2.8rem !important;
            text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);
        }
        [data-testid="stMetricLabel"] {
            color: #ffffff !important;
            font-weight: bold !important;
            font-size: 20px !important;
            opacity: 1 !important;
        }
        .stMetric {
            background-color: #161b22;
            padding: 25px;
            border-radius: 12px;
            border: 2px solid #30363d;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }

        /* 傑克指標診斷看板 - 使用深黑金屬底色 */
        .jack-panel {
            background-color: #000000;
            padding: 30px;
            border-radius: 15px;
            border-left: 12px solid #007bff;
            border-right: 1px solid #30363d;
            border-top: 1px solid #30363d;
            border-bottom: 1px solid #30363d;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.8);
        }
        .jack-title { color: #ffffff; font-weight: 900; font-size: 30px; margin-bottom: 10px; }
        .jack-status-highlight { color: #00ffcc; font-weight: 900; font-size: 26px; }
        .jack-sub-text { color: #f0f0f0; font-size: 22px; line-height: 1.8; font-weight: bold; }
        .jack-value { color: #ffff00; font-weight: 900; text-decoration: underline; }

        /* AI 診斷診斷文字區 */
        .ai-diag-box {
            background-color: #161b22;
            padding: 25px;
            border-radius: 12px;
            border: 2px solid #ff4d4d;
            margin-top: 15px;
        }
        .diag-item-success { color: #00ffcc; font-weight: 900; font-size: 18px; margin-bottom: 8px; }
        .diag-item-error { color: #ff4d4d; font-weight: 900; font-size: 18px; margin-bottom: 8px; }

        /* 交易建議高亮卡片 - 增加亮度 */
        .advice-card {
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 15px;
            font-weight: 900;
            text-align: center;
            border: 4px solid;
            font-size: 22px;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.3); }
        .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.25); }
        
        /* PC 側邊欄按鈕強化 */
        .stButton>button {
            border-radius: 10px;
            font-weight: 900;
            height: 4rem;
            background-color: #2b313e;
            color: #00ffcc;
            font-size: 18px;
            border: 2px solid #30363d;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #00ffcc;
            color: #000000;
            box-shadow: 0 0 15px #00ffcc;
        }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 4. 核心分析引擎 (W/M 偵測、黃金交叉、蝴蝶、AI 診斷邏輯)
    # ==============================================================================
    def analyze_master_terminal(df, budget, strategy_mode):
        if df is None or df.empty or len(df) < 60: return None
        
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        close_p = df['Close'].values.flatten().astype(float)
        high_p = df['High'].values.flatten().astype(float)
        low_p = df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- [A] 均線與收斂帶寬 ---
        df['MA20'] = df['Close'].rolling(20).mean()
        df['EMA8'] = df['Close'].ewm(span=8).mean()
        df['STD'] = df['Close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20']
        curr_bw = float(df['BW'].iloc[-1])
        
        # --- [B] 黃金交叉引擎 (EMA8 穿過 MA20 + MACD 金叉) ---
        # 1. 均線黃金交叉
        gc_ma = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1] and df['EMA8'].iloc[-2] <= df['MA20'].iloc[-2]
        is_bullish = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1]
        
        # 2. MACD 動能金叉
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        gc_macd = df['Hist'].iloc[-1] > 0 and df['Hist'].iloc[-2] <= 0
        
        # --- [C] 形態偵測：收斂 W 底 / M 頭 ---
        n_order = 12
        max_peaks = argrelextrema(high_p, np.greater, order=n_order)[0]
        min_peaks = argrelextrema(low_p, np.less, order=n_order)[0]
        all_pts_idx = sorted(np.concatenate([max_peaks[-3:], min_peaks[-3:]]))
        
        pattern_label = "趨勢形成中"
        ai_win_score = 60
        reasons = [] # AI 診斷原因
        
        if len(all_pts_idx) >= 4:
            v = [df['Close'].iloc[i] for i in all_pts_idx[-4:]]
            if v[0] > v[1] and v[2] > v[1] and v[2] > v[3]:
                if v[2] <= v[0] * 1.01:
                    pattern_label = "收斂 M 頭 (高位警示 ⚠️)"
                    ai_win_score -= 20
                    reasons.append("🔴 偵測到雙重頂部(M頭)壓力，上方套牢盤沉重。")
            elif v[0] < v[1] and v[2] < v[1] and v[2] < v[3]:
                if v[2] >= v[0] * 0.99:
                    pattern_label = "收斂 W 底 (起漲預兆 🚀)"
                    ai_win_score += 30
                    reasons.append("🟢 偵測到雙重底部(W底)，第二次回測不破底，強力買盤。")

        # --- [D] 勝率診斷加權 ---
        if gc_ma: 
            ai_win_score += 10
            reasons.append("🟢 ✨ 黃金交叉觸發：短期均線向上穿透生命線。")
        elif is_bullish:
            reasons.append("🟢 均線處於多頭排列狀態。")
        else:
            reasons.append("🔴 均線目前為空頭排列，受壓於 MA20 之下。")
            
        if gc_macd:
            ai_win_score += 10
            reasons.append("🟢 🚀 MACD 能量金叉：動能柱翻正，噴發力道增強。")
        
        if curr_bw < 0.12:
            ai_win_score += 10
            reasons.append("🟢 💎 強烈收斂：波動率極度壓縮，即將出現大變盤。")

        # --- [E] 斐波那契全位階與試算 ---
        max_v = float(high_p[-120:].max())
        min_v = float(low_p[-120:].min())
        fib_buy = max_v - 0.618 * (max_v - min_v)
        fib_target = min_v + 1.272 * (max_v - min_v)
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        df['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

        # 入場時間與左/右側診斷
        entry_timing = "⏳ 等待動能確認"
        if gc_ma and gc_macd: entry_timing = "🔥 即刻錄場 (強勢確認)"
        elif curr_p <= fib_buy * 1.01: entry_timing = "💎 價值區掛單 (分批抄底)"
        
        is_right_ready = curr_p > df['EMA8'].iloc[-1] and df['Hist'].iloc[-1] > df['Hist'].iloc[-2]
        is_left_ready = curr_p <= fib_buy * 1.02 and df['RSI'].iloc[-1] < 45

        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        days_est = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0
        shares = int(budget / curr_p)

        return {
            "score": min(ai_win_score, 98), "curr": curr_p, "shares": shares, "days": days_est,
            "profit": (shares * fib_target) - (shares * curr_p), "roi": ((fib_target / curr_p) - 1) * 100,
            "df": df, "fib_buy": fib_buy, "fib_target": fib_target, "bw": curr_bw, 
            "pattern": pattern_label, "reasons": reasons, "timing": entry_timing,
            "pts_x": [df.index[i] for i in all_pts_idx[-5:]], "pts_y": [df['Close'].iloc[i] for i in all_pts_idx[-5:]],
            "gc_ma": gc_ma, "gc_macd": gc_macd, "right_ok": is_right_ready, "left_ok": is_left_ready
        }

    # ==============================================================================
    # 5. PC 側邊欄：全掃描器 + 時區選擇
    # ==============================================================================
    with st.sidebar:
        st.header("⚙️ 終極操盤控制台")
        st.session_state.strategy = st.selectbox("🎯 交易模式", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"))
        st.session_state.tf_choice = st.selectbox("⏳ 分析時間週期", ("15分鐘", "1小時", "2小時", "日線", "週線"), index=3)
        tf_map = {"15分鐘":"15m", "1小時":"60m", "2小時":"120m", "日線":"1d", "週線":"1wk"}
        p_map = {"15分鐘":"5d", "1小時":"1mo", "2小時":"2mo", "日線":"2y", "週線":"max"}
        
        st.divider()
        st.write("🔍 **全台股 50 大形態智慧掃描**")
        if st.button("🚀 執行自動市場掃描"):
            tw_top_list = ["2330","2317","2454","2308","2382","2881","2882","2303","2891","3711","2412","2886","1216","2884","2892","2002","2357","3008","2603","2880","2324","2609","2885","2883","3231","2408","4938","2890","2912","1301","1303","2301","3045","2615","5871","2379","6415","3037","2377","1513","2356","2801","1101","4904","2105","9910","1402","2313","1605"]
            scan_res = []
            p_bar = st.progress(0)
            for idx, code in enumerate(tw_top_list):
                try:
                    s_raw = yf.download(f"{code}.TW", period="1y", progress=False)
                    s_res = analyze_master_terminal(s_raw, 1000000, st.session_state.strategy)
                    if s_res: scan_res.append({"代碼": code, "形態": s_res['pattern'], "AI勝率": f"{s_res['score']}%", "預期ROI": f"{s_res['roi']:.1f}%"})
                except: continue
                p_bar.progress((idx + 1) / len(tw_top_list))
            st.session_state.full_scan_report = pd.DataFrame(scan_res)
            
        if 'full_scan_report' in st.session_state:
            st.dataframe(st.session_state.full_scan_report, use_container_width=True, height=400)

        st.divider()
        if st.button("🚪 安全登出"):
            st.session_state.authenticated = False
            st.rerun()

    # ==============================================================================
    # 6. PC 主畫面顯示邏輯 (大螢幕旗艦佈局)
    # ==============================================================================
    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy}")
    
    col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
    with col_t1: market_env = st.radio("當前市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with col_t2: user_ticker = st.text_input("🔍 代碼輸入", value=st.session_state.u_code)
    with col_t3: budget_input = st.number_input("💰 投資預算 (元)", value=1000000)

    st.session_state.u_code, st.session_state.m_type = user_ticker, market_env
    ticker_final = f"{user_ticker}.TW" if market_env == "台股" else user_ticker

    try:
        main_raw_df = yf.download(ticker_final, interval=tf_map[st.session_state.tf_choice], period=p_map[st.session_state.tf_choice], progress=False)
        final_res = analyze_master_terminal(main_raw_df, budget_input, st.session_state.strategy)
        
        if final_res:
            # --- [A] 傑克指標看板 (超高對比文字) ---
            bw_v = final_res['bw']
            bw_desc = "📉 強烈收斂 (波動極限擠壓)" if bw_v < 0.12 else "📊 趨勢發散"
            gc_msg = "✨ 黃金交叉確認" if final_res['gc_ma'] or final_res['gc_macd'] else "⏳ 等待動能"
            
            st.markdown(f"""
                <div class="jack-panel">
                    <div class="jack-title">📊 傑克技術看板：{bw_desc} | <span style='color:#ffff00;'>{gc_msg}</span></div>
                    <hr style='border-color:#30363d; border-width: 2px;'>
                    <p class="jack-sub-text">🔥 目前形態偵測：<span class="jack-status-highlight">{final_res['pattern']}</span></p>
                    <p class="jack-sub-text">錄場建議：<span class="jack-value">{final_res['timing']}</span> | 預計達成：<span class="jack-value">{final_res['days']} 天</span></p>
                    <p class="jack-sub-text">建議佈局價：<span class="jack-value">${final_res['fib_buy']:,.2f}</span> | 目標預測價：<span class="jack-value">${final_res['fib_target']:,.2f}</span></p>
                </div>
            """, unsafe_allow_html=True)

            # --- [B] 雙側交易建議卡片 (超亮版) ---
            adv_c1, adv_c2 = st.columns(2)
            with adv_c1:
                if final_res['left_ok']: st.markdown('<div class="advice-card left-side">💎 左側訊號：進入斐波那契價值區，適合分批低吸。</div>', unsafe_allow_html=True)
                else: st.info("左側抄底條件尚未滿足。")
            with adv_c2:
                if final_res['right_ok']: st.markdown('<div class="advice-card right-side">🚀 右側訊號：站上均線且黃金交叉確認，適合動能追進！</div>', unsafe_allow_html=True)
                else: st.warning("右側突破動能尚未確認。")

            # --- [C] AI 深度診斷區 ---
            with st.expander("🔍 AI 深度技術診斷分析報告 (為什麼勝率低？)", expanded=(final_res['score'] < 75)):
                st.markdown("<div class='ai-diag-box'>", unsafe_allow_html=True)
                for r in final_res['reasons']:
                    cls = 'diag-item-success' if '🟢' in r else 'diag-item-error'
                    st.markdown(f"<div class='{cls}'>{r}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.info(f"🔹 入場預算分配：{budget_input:,} 元\n🔹 建議買入：{final_res['shares']:,} 股")

            # --- [D] 數據數據儀表板 ---
            metric_c1, metric_c2, metric_c3, metric_c4 = st.columns(4)
            metric_c1.metric("AI 綜合勝率", f"{final_res['score']}%")
            metric_c2.metric("預期報酬 (ROI)", f"{final_res['roi']:.1f}%")
            metric_c3.metric("建議持有總股數", f"{final_res['shares']:,} 股")
            metric_c4.metric("預計總獲利金額", f"${final_res['profit']:,.0f}")

            # --- [E] 📈 專業三層聯動圖表 (物理座標鎖定) ---
            # 
            fig_terminal = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.55, 0.2, 0.25], vertical_spacing=0.03,
                               subplot_titles=("K線、布林通道與蝴蝶 XABCD 形態", "RSI 與 CCI 能量分析指標", "MACD (MSI) 趨勢動能柱狀圖"))
            
            fig_terminal.add_trace(go.Candlestick(x=final_res['df'].index, open=final_res['df']['Open'], high=final_res['df']['High'], low=final_res['df']['Low'], close=final_res['df']['Close'], name='K線'), row=1, col=1)
            # 布林通道視覺化 
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Upper'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林上軌'), row=1, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Lower'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林下軌', fill='tonexty'), row=1, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['EMA8'], line=dict(color='#ffff00', width=2.5), name='黃金 T 線 (EMA8)'), row=1, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['MA20'], line=dict(color='#ffffff', width=1.5, dash='dot'), name='生命線 (MA20)'), row=1, col=1)
            
            # 蝴蝶 XABCD 形態連線 
            if len(final_res['pts_x']) >= 4:
                fig_terminal.add_trace(go.Scatter(x=final_res['pts_x'], y=final_res['pts_y'], mode='lines+markers+text', name='蝴蝶連線', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D'], textposition="top center"), row=1, col=1)
            
            fig_terminal.add_hline(y=final_res['fib_buy'], line_dash="dash", line_color="#ffa500", annotation_text="0.618 支撐位", row=1, col=1)
            fig_terminal.add_hline(y=final_res['fib_target'], line_dash="dash", line_color="#00ff00", annotation_text="1.272 目標位", row=1, col=1)

            # 
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['RSI'], line=dict(color='#ffcc00', width=2.5), name='RSI'), row=2, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['CCI'], line=dict(color='#007bff', width=1.5), name='CCI'), row=2, col=1)
            fig_terminal.add_hline(y=70, line_dash="dot", line_color="#ff4d4d", row=2, col=1)
            fig_terminal.add_hline(y=30, line_dash="dot", line_color="#00ffcc", row=2, col=1)

            # 
            m_colors = ['#00ffcc' if v > 0 else '#ff4d4d' for v in final_res['df']['Hist']]
            fig_terminal.add_trace(go.Bar(x=final_res['df'].index, y=final_res['df']['Hist'], name='動能柱 (MSI)', marker_color=m_colors), row=3, col=1)

            # --- 核心：終極物理座標鎖定修正 (徹底防止 K 線變平) ---
            y_min_f = final_res['df']['Low'].min() * 0.98
            y_max_f = final_res['df']['High'].max() * 1.02
            fig_terminal.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            fig_terminal.update_yaxes(range=[y_min_f, y_max_f], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig_terminal, use_container_width=True)
            
        else: st.warning("數據解析中，請確保代碼完整貼上並稍候...")
    except Exception as e: st.error(f"系統運行異常：{str(e)}")

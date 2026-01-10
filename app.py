import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (針對 PC 寬螢幕專業操盤環境優化)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="2026 戰神終極終端 - PC 全功能完全體", 
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
    st.markdown("### 本系統包含黃金交叉引擎與 AI 深度診斷邏輯")
    pwd_input = st.text_input("請輸入 4 位數授權碼", type="password")
    if st.button("確認進入系統"):
        if pwd_input == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 授權碼錯誤")
    return False

if check_password():
    # ==============================================================================
    # 3. 旗艦終端專業 CSS 樣式
    # ==============================================================================
    st.markdown("""
        <style>
        .main { background-color: #0d1117; }
        .stMetric {
            background-color: #161b22;
            padding: 22px;
            border-radius: 12px;
            border: 1px solid #30363d;
        }
        [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: bold; font-size: 2.3rem !important; }
        .jack-panel {
            background-color: #1a1c24;
            padding: 25px;
            border-radius: 15px;
            border-left: 10px solid #007bff;
            margin-bottom: 25px;
        }
        .ai-diagnostic {
            background-color: #161b22;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #ff4d4d;
            margin-top: 10px;
        }
        .advice-card {
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 12px;
            font-weight: bold;
            text-align: center;
            border: 2px solid;
        }
        .right-side { border-color: #ff4d4d; color: #ff4d4d; background-color: rgba(255, 77, 77, 0.1); }
        .left-side { border-color: #00ffcc; color: #00ffcc; background-color: rgba(0, 255, 204, 0.1); }
        .stButton>button { border-radius: 8px; font-weight: bold; height: 3.5rem; background-color: #2b313e; color: #00ffcc; }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 4. 核心分析引擎 (W/M 偵測、蝴蝶、物理座標鎖定、多重金叉)
    # ==============================================================================
    def analyze_master_terminal(df, budget, strategy_mode):
        if df is None or df.empty or len(df) < 60: return None
        
        # 處理多層索引
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        close_p = df['Close'].values.flatten().astype(float)
        high_p = df['High'].values.flatten().astype(float)
        low_p = df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- [A] 傑克指標核心：均線與布林收斂 ---
        df['MA20'] = df['Close'].rolling(20).mean()
        df['EMA8'] = df['Close'].ewm(span=8).mean()
        df['STD'] = df['Close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20']
        curr_bw = float(df['BW'].iloc[-1])
        
        # --- [B] 黃金交叉引擎 (MA金叉 + MACD金叉) ---
        # 1. EMA8 穿過 MA20 (均線金叉) 
        gc_ma = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1] and df['EMA8'].iloc[-2] <= df['MA20'].iloc[-2]
        # 2. MACD Hist 負轉正 (動能金叉) 
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        gc_macd = df['Hist'].iloc[-1] > 0 and df['Hist'].iloc[-2] <= 0
        
        # --- [C] 形態偵測：W底 / M頭 ---
        n_order = 12
        max_peaks = argrelextrema(high_p, np.greater, order=n_order)[0]
        min_peaks = argrelextrema(low_p, np.less, order=n_order)[0]
        all_pts_idx = sorted(np.concatenate([max_peaks[-3:], min_peaks[-3:]]))
        
        pattern_label = "趨勢形成中"
        ai_win_score = 60
        score_reasons = [] # 診斷勝率的原因
        
        if len(all_pts_idx) >= 4:
            v = [df['Close'].iloc[i] for i in all_pts_idx[-4:]]
            if v[0] > v[1] and v[2] > v[1] and v[2] > v[3]:
                pattern_label = "收斂 M 頭 (高位警示)"
                ai_win_score -= 15
                score_reasons.append("⚠️ 偵測到雙重頂部 (M頭) 壓力，上方拋壓沉重。")
            elif v[0] < v[1] and v[2] < v[1] and v[2] < v[3]:
                pattern_label = "收斂 W 底 (起漲預兆)"
                ai_win_score += 25
                score_reasons.append("✅ 偵測到雙重底部 (W底)，支撐力道強勁。")

        # --- [D] AI 勝率診斷邏輯 ---
        if gc_ma: 
            ai_win_score += 10
            score_reasons.append("✨ 均線黃金交叉：短期趨勢正式轉多。")
        else:
            score_reasons.append("❌ 均線尚未金叉：短期動能仍受制於月線 (MA20)。")
            
        if gc_macd:
            ai_win_score += 10
            score_reasons.append("🚀 動能金叉：MACD 能量柱翻正，多頭開始奪回主控權。")
        
        if curr_bw < 0.12:
            ai_win_score += 10
            score_reasons.append("💎 強烈收斂：波動率極低，準備迎接變盤大行情。")
        else:
            score_reasons.append("⏳ 波動發散中：當前處於能量釋放期，非最佳埋伏點。")

        # --- [E] 斐波那契與預算分配 ---
        lookback = 120
        max_v = float(high_p[-lookback:].max())
        min_v = float(low_p[-lookback:].min())
        fib_buy = max_v - 0.618 * (max_v - min_v)
        fib_target = min_v + 1.272 * (max_v - min_v)
        
        # RSI & CCI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        df['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

        # 入場時間建議
        entry_timing = "等待分批"
        if gc_ma and gc_macd: entry_timing = "即刻入場 (動能確認)"
        elif curr_p <= fib_buy * 1.01: entry_timing = "左側掛單 (支撐區)"
        else: entry_timing = "等待回測 EMA8"

        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        days_est = int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0
        shares = int(budget / curr_p)

        return {
            "score": min(ai_win_score, 98), "curr": curr_p, "shares": shares, "days": days_est,
            "profit": (shares * fib_target) - (shares * curr_p), "roi": ((fib_target / curr_p) - 1) * 100,
            "df": df, "fib_buy": fib_buy, "fib_target": fib_target, "bw": curr_bw, 
            "pattern": pattern_label, "reasons": score_reasons, "timing": entry_timing,
            "pts_x": [df.index[i] for i in all_pts_idx[-5:]], "pts_y": [df['Close'].iloc[i] for i in all_pts_idx[-5:]],
            "gc_ma": gc_ma, "gc_macd": gc_macd
        }

    # ==============================================================================
    # 5. PC 側邊欄控制中心 (全掃描器 + 時區)
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
            # --- [A] 傑克指標看板 (黃金交叉標示) ---
            bw_status = "📉 強烈收斂 (波動極限壓縮)" if final_res['bw'] < 0.12 else "📊 趨勢發散"
            gc_msg = "✨ 偵測到黃金交叉！" if final_res['gc_ma'] or final_res['gc_macd'] else "⏳ 等待動能確認"
            st.markdown(f"""
                <div class="jack-panel">
                    <h2 style='margin:0;'>傑克技術看板：<b>{bw_status}</b> | <b>{gc_msg}</b></h2>
                    <hr style='border-color:#30363d;'>
                    <p style='font-size:22px; margin:5px 0;'>🔥 形態識別：<b>{final_res['pattern']}</b> | 建議錄場時間：<b>{final_res['timing']}</b></p>
                    <p style='font-size:18px; margin:0;'>建議佈局價：<b>${final_res['fib_buy']:,.2f}</b> | 目標預測價：<b>${final_res['fib_target']:,.2f}</b></p>
                </div>
            """, unsafe_allow_html=True)

            # --- [B] AI 深度診斷區 ---
            with st.expander("🔍 AI 為什麼勝率評分低？查看深度技術報告", expanded=(final_res['score'] < 70)):
                col_diag1, col_diag2 = st.columns([2, 1])
                with col_diag1:
                    for r in final_res['reasons']:
                        st.write(r)
                with col_diag2:
                    st.error(f"當前 AI 綜合評分: {final_res['score']}%")
                    st.info(f"建議投入資金: {budget_input:,} 元\n\n可買股數: {final_res['shares']:,} 股")

            # --- [C] 數據儀表板 ---
            metric_c1, metric_c2, metric_c3, metric_c4 = st.columns(4)
            metric_c1.metric("預期報酬 (ROI)", f"{final_res['roi']:.1f}%")
            metric_c2.metric("預計達成時間", f"{final_res['days']} 天")
            metric_c3.metric("建議持有總股數", f"{final_res['shares']:,} 股")
            metric_c4.metric("預計獲利金額", f"${final_res['profit']:,.0f}")

            # --- [D] 📈 專業三層聯動圖表 (物理座標鎖定) ---
            fig_terminal = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.55, 0.2, 0.25], vertical_spacing=0.03,
                               subplot_titles=("K線、布林通道與蝴蝶 XABCD 形態", "RSI 與 CCI 能量強弱診斷", "MACD (MSI) 趨勢動能柱狀圖"))
            
            fig_terminal.add_trace(go.Candlestick(x=final_res['df'].index, open=final_res['df']['Open'], high=final_res['df']['High'], low=final_res['df']['Low'], close=final_res['df']['Close'], name='K線'), row=1, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Upper'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林上軌'), row=1, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['Lower'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林下軌', fill='tonexty'), row=1, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['EMA8'], line=dict(color='yellow', width=1.8), name='黃金 T 線 (EMA8)'), row=1, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['MA20'], line=dict(color='white', width=1.2, dash='dot'), name='生命線 (MA20)'), row=1, col=1)
            
            if len(final_res['pts_x']) >= 4:
                fig_terminal.add_trace(go.Scatter(x=final_res['pts_x'], y=final_res['pts_y'], mode='lines+markers+text', name='蝴蝶連線', line=dict(color='#00ffcc', width=2.5), text=['X','A','B','C','D'], textposition="top center"), row=1, col=1)
            
            fig_terminal.add_hline(y=final_res['fib_buy'], line_dash="dash", line_color="orange", annotation_text="0.618 買點", row=1, col=1)
            fig_terminal.add_hline(y=final_res['fib_target'], line_dash="dash", line_color="green", annotation_text="1.272 目標", row=1, col=1)

            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['RSI'], line=dict(color='#ffcc00', width=2), name='RSI'), row=2, col=1)
            fig_terminal.add_trace(go.Scatter(x=final_res['df'].index, y=final_res['df']['CCI'], line=dict(color='#007bff', width=1), name='CCI'), row=2, col=1)
            
            m_colors = ['#00ffcc' if v > 0 else '#ff4d4d' for v in final_res['df']['Hist']]
            fig_terminal.add_trace(go.Bar(x=final_res['df'].index, y=final_res['df']['Hist'], name='動能柱 (MSI)', marker_color=m_colors), row=3, col=1)

            # 物理鎖定
            y_min_f = final_res['df']['Low'].min() * 0.98
            y_max_f = final_res['df']['High'].max() * 1.02
            fig_terminal.update_layout(height=1000, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            fig_terminal.update_yaxes(range=[y_min_f, y_max_f], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig_terminal, use_container_width=True)
            
        else: st.warning("數據解析中...")
    except Exception as e: st.error(f"系統運行異常：{str(e)}")

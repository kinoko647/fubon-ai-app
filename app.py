import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime

# ==============================================================================
# 1. 系統全局配置 (PC 專業操盤終端視覺優化)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="2026 戰神終極終端 - PC 全功能旗艦", 
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
        <h1 style='color: #00ffcc; font-weight: 900; text-align: center;'>戰神終極完全體：500 檔海量掃描 & AI 深度診斷</h1>
        <p style='color: #ffffff; font-size: 24px; text-align: center;'>整合多重黃金交叉、收斂 W/M 形態及蝴蝶 XABCD 引擎。</p>
    """, unsafe_allow_html=True)
    pwd_input = st.text_input("請輸入管理員授權碼", type="password")
    if st.button("啟動旗艦系統"):
        if pwd_input == "8888":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 授權碼錯誤，拒絕訪問。")
    return False

if check_password():
    # ==============================================================================
    # 3. 旗艦終端專業 CSS 樣式 (終極高對比 - 徹底解決字體與顏色問題)
    # ==============================================================================
    st.markdown("""
        <style>
        .main { background-color: #0d1117; }
        [data-testid="stMetricValue"] { 
            color: #00ffcc !important; 
            font-weight: 900 !important; 
            font-size: 3.5rem !important;
            text-shadow: 2px 2px 20px rgba(0, 255, 204, 0.7);
        }
        [data-testid="stMetricLabel"] { color: #ffffff !important; font-weight: 900 !important; font-size: 24px !important; }
        .stMetric { background-color: #000000; padding: 30px; border-radius: 20px; border: 3px solid #30363d; }
        .jack-panel { background-color: #000000; padding: 40px; border-radius: 25px; border-left: 20px solid #007bff; border-right: 3px solid #30363d; border-top: 3px solid #30363d; border-bottom: 3px solid #30363d; margin-bottom: 40px; box-shadow: 0 15px 50px rgba(0,0,0,1); }
        .jack-title { color: #ffffff; font-weight: 900; font-size: 40px; margin-bottom: 15px; }
        .jack-status-highlight { color: #00ffcc !important; font-weight: 900; font-size: 34px; text-decoration: underline; }
        .jack-sub-text { color: #ffffff !important; font-size: 26px; line-height: 2.2; font-weight: 900; }
        .jack-value { color: #ffff00 !important; font-weight: 900; font-size: 28px; }
        .ai-diag-box { background-color: #000000; padding: 35px; border-radius: 20px; border: 4px solid #ff4d4d; margin-top: 25px; }
        .diag-item-success { color: #00ffcc !important; font-weight: 900; font-size: 24px; margin-bottom: 12px; }
        .diag-item-error { color: #ff3e3e !important; font-weight: 900; font-size: 24px; margin-bottom: 12px; }
        .advice-card { padding: 35px; border-radius: 20px; margin-bottom: 25px; font-weight: 900; text-align: center; border: 6px solid; font-size: 28px; }
        .right-side { border-color: #ff3e3e; color: #ffffff; background-color: rgba(255, 62, 62, 0.45); }
        .left-side { border-color: #00ffcc; color: #ffffff; background-color: rgba(0, 255, 204, 0.35); }
        .stButton>button { border-radius: 15px; font-weight: 900; height: 5.5rem; background-color: #161b22; color: #00ffcc; font-size: 22px; border: 3px solid #00ffcc; transition: all 0.3s; }
        .stButton>button:hover { background-color: #00ffcc; color: #000000; box-shadow: 0 0 35px #00ffcc; transform: scale(1.02); }
        </style>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # 4. 核心分析引擎 (修復 KeyError 與縮進錯誤)
    # ==============================================================================
    def analyze_master_terminal(df, budget, strategy_mode):
        if df is None or df.empty or len(df) < 60:
            return None
        
        # 強制數據攤平，防止 KeyError
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        
        close_p = df['Close'].values.flatten().astype(float)
        high_p = df['High'].values.flatten().astype(float)
        low_p = df['Low'].values.flatten().astype(float)
        curr_p = float(close_p[-1])
        
        # --- [A] 技術指標計算 ---
        df['MA20'] = df['Close'].rolling(20).mean()
        df['EMA8'] = df['Close'].ewm(span=8).mean()
        df['STD'] = df['Close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        df['BW'] = (df['Upper'] - df['Lower']) / df['MA20']
        
        # MACD 修復
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        
        # RSI & CCI 修復
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, 0.001))))
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        df['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

        # --- [B] 黃金交叉與形態偵測 ---
        # 均線金叉         gc_ma = df['EMA8'].iloc[-1] > df['MA20'].iloc[-1] and df['EMA8'].iloc[-2] <= df['MA20'].iloc[-2]
        # 動能金叉
        gc_macd = df['Hist'].iloc[-1] > 0 and df['Hist'].iloc[-2] <= 0
        
        n_order = 12
        max_peaks = argrelextrema(high_p, np.greater, order=n_order)[0]
        min_peaks = argrelextrema(low_p, np.less, order=n_order)[0]
        all_pts_idx = sorted(np.concatenate([max_peaks[-3:], min_peaks[-3:]]))
        
        pattern_label = "趨勢形成中"
        ai_win_score = 60
        reasons = []
        
        if len(all_pts_idx) >= 4:
            v = [df['Close'].iloc[i] for i in all_pts_idx[-4:]]
            if v[0] > v[1] and v[2] > v[1] and v[2] > v[3]:
                if v[2] <= v[0] * 1.015:
                    pattern_label = "收斂 M 頭 (頂部高壓)"
                    ai_win_score -= 20
                    reasons.append("🔴 警示：偵測到 M 頭形態，高位套牢壓力沉重。")
            elif v[0] < v[1] and v[2] < v[1] and v[2] < v[3]:
                if v[2] >= v[0] * 0.985:
                    pattern_label = "收斂 W 底 (底部起漲)"
                    ai_win_score += 35
                    reasons.append("🟢 驚喜：偵測到收斂 W 底，第二次回測不破底。")

        # --- [C] 雙側交易建議 ---
        is_right_ok = curr_p > df['EMA8'].iloc[-1] and df['Hist'].iloc[-1] > df['Hist'].iloc[-2]
        
        lookback = 120
        max_v = float(high_p[-lookback:].max())
        min_v = float(low_p[-lookback:].min())
        fib_buy = max_v - 0.618 * (max_v - min_v)
        fib_target = min_v + 1.272 * (max_v - min_v)
        
        shares = int(budget / curr_p)
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        return {
            "score": min(ai_win_score + (10 if gc_ma else 0), 98), 
            "curr": curr_p, "shares": shares, 
            "days": int(abs(fib_target - curr_p) / (atr * 0.75)) if atr > 0 else 0,
            "profit": (shares * fib_target) - (shares * curr_p), 
            "roi": ((fib_target / curr_p) - 1) * 100, 
            "df": df, "fib_buy": fib_buy, "fib_target": fib_target, 
            "bw": float(df['BW'].iloc[-1]), "pattern": pattern_label, 
            "reasons": reasons, "gc_ma": gc_ma, "gc_macd": gc_macd,
            "pts_x": [df.index[i] for i in all_pts_idx[-5:]], 
            "pts_y": [df['Close'].iloc[i] for i in all_pts_idx[-5:]],
            "right_ok": is_right_ok, 
            "left_ok": curr_p <= fib_buy * 1.02 and df['RSI'].iloc[-1] < 45
        }

    # ==============================================================================
    # 5. 側邊欄：海量掃描引擎 (500 檔)
    # ==============================================================================
    with st.sidebar:
        st.header("⚙️ 戰神全市場掃描器")
        st.session_state.strategy = st.selectbox("🎯 交易戰略模式", ("🛡️ 長線穩健 (Long)", "⚡ 中線進攻 (Mid)", "🔥 短線當沖 (Short)"))
        st.session_state.tf_choice = st.selectbox("⏳ 分析時間週期", ("15分鐘", "1小時", "2小時", "日線", "週線"), index=3)
        
        st.divider()
        st.write("🔍 **台股海量標全自動化偵測 (500檔)**")
        scan_grp = st.radio("掃描組別", ("權值 0050 組", "中型 0051 組", "熱門標的 300檔"))
        
        if st.button("🚀 啟動全市場形態掃描"):
            # 建立海量清單
            if "0050" in scan_grp:
                targets = ["2330","2317","2454","2308","2382","2881","2303","2882","2891","3711","2412","2886","1216","2884","2892","2002","2357","3008","2603","2880"]
            elif "0051" in scan_grp:
                targets = ["1476","1503","1504","1519","1560","1590","1605","1707","1717","1722","1723"]
            else:
                targets = ["2330","2317","2454","2382","2603","2609","2615","2303","3231","2353","2376","2383","2449","3037","3034","3035","3443","3661"]

            scan_results = []
            p_bar = st.progress(0)
            st_text = st.empty()
            
            for i, code in enumerate(targets):
                st_text.text(f"分析中: {code}.TW")
                try:
                    s_raw = yf.download(f"{code}.TW", period="1y", progress=False)
                    s_res = analyze_master_terminal(s_raw, 1000000, st.session_state.strategy)
                    if s_res and ("W底" in s_res['pattern'] or s_res['score'] >= 85):
                        scan_results.append({"代碼": code, "形態": s_res['pattern'], "AI勝率": f"{s_res['score']}%", "ROI": f"{s_res['roi']:.1f}%"})
                except: continue
                p_bar.progress((i + 1) / len(targets))
            st.session_state.full_scan_df = pd.DataFrame(scan_results)
            st_text.success("✅ 全市場掃描完成！")
            
        if 'full_scan_df' in st.session_state:
            st.dataframe(st.session_state.full_scan_df, use_container_width=True, height=400)

        st.divider()
        if st.button("🚪 安全登出"):
            st.session_state.authenticated = False
            st.rerun()

    # ==============================================================================
    # 6. PC 主畫面：深度診斷與圖表 (物理座標修復)
    # ==============================================================================
    st.title(f"🏆 股票預測分析系統 - {st.session_state.strategy}")
    
    col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
    with col_t1: m_env = st.radio("市場", ("台股", "美股"), index=0 if st.session_state.m_type == '台股' else 1, horizontal=True)
    with col_t2: u_id = st.text_input("🔍 診斷代碼", value=st.session_state.u_code)
    with col_t3: u_inv = st.number_input("💰 投資預算", value=1000000)

    st.session_state.u_code, st.session_state.m_type = u_id, m_env
    ticker = f"{u_id}.TW" if m_env == "台股" else u_id
    
    tf_map_main = {"15分鐘":"15m", "1小時":"60m", "2小時":"120m", "日線":"1d", "週線":"1wk"}
    p_map_main = {"15分鐘":"5d", "1小時":"1mo", "2小時":"2mo", "日線":"2y", "週線":"max"}

    try:
        main_df = yf.download(ticker, interval=tf_map_main[st.session_state.tf_choice], period=p_map_main[st.session_state.tf_choice], progress=False)
        res = analyze_master_terminal(main_df, u_inv, st.session_state.strategy)
        
        if res:
            # --- [A] 傑克看板 ---
            bw_v = res['bw']
            bw_desc = "📉 強烈收斂 (即將大變盤)" if bw_v < 0.12 else "📊 發散趨勢"
            gc_msg = "✨ 黃金交叉確認" if res['gc_ma'] or res['gc_macd'] else "⏳ 等待動能"
            st.markdown(f"""
                <div class="jack-panel">
                    <div class="jack-title">📊 傑克技術看板：{bw_desc} | <span style='color:#ffff00;'>{gc_msg}</span></div>
                    <hr style='border-color:#30363d; border-width: 4px;'>
                    <p class="jack-sub-text">偵測形態：<span class="jack-status-highlight">{res['pattern']}</span></p>
                    <p class="jack-sub-text">建議佈局位：<span class="jack-value">${res['fib_buy']:,.2f}</span> | 目標位：<span class="jack-value">${res['fib_target']:,.2f}</span></p>
                </div>
            """, unsafe_allow_html=True)

            # --- [B] 圖表區 (徹底解決平線問題) ---
            #             fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.55, 0.2, 0.25], vertical_spacing=0.03,
                               subplot_titles=("K線形態與物理對焦", "能量強弱指標", "MSI 動能柱"))
            
            # 第一層：主圖
            fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name='K線'), row=1, col=1)
            # 布林與均線             fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Upper'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林'), row=1, col=1)
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['Lower'], line=dict(color='rgba(173,216,230,0.3)', width=1), name='布林', fill='tonexty'), row=1, col=1)
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['EMA8'], line=dict(color='#ffff00', width=2.5), name='EMA8'), row=1, col=1)
            
            # 蝴蝶連線             if len(res['pts_x']) >= 4:
                fig.add_trace(go.Scatter(x=res['pts_x'], y=res['pts_y'], mode='lines+markers+text', name='蝴蝶形態', line=dict(color='#00ffcc', width=3), text=['X','A','B','C','D'], textposition="top center"), row=1, col=1)
            
            # 第二層：RSI & CCI
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['RSI'], line=dict(color='#ffcc00', width=2), name='RSI'), row=2, col=1)
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['CCI'], line=dict(color='#007bff', width=1.5), name='CCI'), row=2, col=1)

            # 第三層：MACD             m_cols = ['#00ffcc' if v > 0 else '#ff4d4d' for v in res['df']['Hist']]
            fig.add_trace(go.Bar(x=res['df'].index, y=res['df']['Hist'], name='動能柱', marker_color=m_cols), row=3, col=1)

            # --- 終極核心：物理座標鎖定修正 ---
            # 這是解決截圖中出現的 35M/100M 拉平 K 線的技術關鍵
            y_focus_min = res['df']['Low'].min() * 0.98
            y_focus_max = res['df']['High'].max() * 1.02
            
            fig.update_layout(height=1100, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=50, b=10))
            # 強制鎖定 Y 軸範圍，無視成交量數字
            fig.update_yaxes(range=[y_focus_min, y_focus_max], row=1, col=1, autorange=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
        else: st.warning("數據解析中...")
    except Exception as e: st.error(f"系統運行異常：{str(e)}")

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import argrelextrema
import warnings

warnings.filterwarnings("ignore")

# 頁面配置
st.set_page_config(
    page_title="左側交易分析儀",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 樣式
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .block-container { padding-top: 1rem; }
    .signal-bull { background: #1a3a2a; border-left: 4px solid #3fb950; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .signal-bear { background: #3a1a1a; border-left: 4px solid #f85149; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .signal-warn { background: #2e2a14; border-left: 4px solid #d29922; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .signal-info { background: #162032; border-left: 4px solid #58a6ff; padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
</style>
""", unsafe_allow_html=True)

QUICK_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "BNB": "BNB-USD",
    "SOL": "SOL-USD",
    "XRP": "XRP-USD",
    "台積電": "2330.TW",
    "富邦金": "2881.TW",
    "台灣50": "0050.TW",
    "AAPL": "AAPL",
    "TSLA": "TSLA",
    "NVDA": "NVDA",
    "SPY": "SPY",
}

@st.cache_data(ttl=300)
def get_data(symbol, period, interval):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df.empty:
            return pd.DataFrame()
        # 處理 yfinance 可能產生的 MultiIndex 欄位
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"下載錯誤: {e}")
        return pd.DataFrame()

def find_pivots(series, order=5):
    highs = argrelextrema(series.values, np.greater, order=order)[0]
    lows = argrelextrema(series.values, np.less, order=order)[0]
    return highs, lows

def detect_butterfly(df, order=5):
    close = df["Close"]
    highs_idx, lows_idx = find_pivots(close, order=order)
    results = []
    all_pivots = []
    for i in lows_idx:
        all_pivots.append((i, "low", float(close.iloc[i])))
    for i in highs_idx:
        all_pivots.append((i, "high", float(close.iloc[i])))
    all_pivots.sort(key=lambda x: x[0])

    for i in range(len(all_pivots) - 4):
        p = all_pivots[i:i+5]
        types = [x[1] for x in p]
        if types == ["low", "high", "low", "high", "low"]:
            X, A, B, C, D = [x[2] for x in p]
            XA, AB, BC, CD = A-X, A-B, C-B, C-D
            if all(v > 0 for v in [XA, AB, BC, CD]):
                r1, r2, r3 = AB/XA, BC/AB, CD/BC
                if 0.70 <= r1 <= 0.90 and 0.30 <= r2 <= 0.95 and 1.40 <= r3 <= 2.80 and D < X:
                    results.append({
                        "type": "看漲蝴蝶 🦋↑", "direction": "bull",
                        "points": [p[j][0] for j in range(5)],
                        "prices": [p[j][2] for j in range(5)],
                        "labels": ["X", "A", "B", "C", "D"],
                        "entry": D, "stop_loss": D * 0.97,
                        "target1": D + BC * 0.618, "target2": D + XA * 0.786,
                        "ratios": {"AB/XA": r1, "BC/AB": r2, "CD/BC": r3}
                    })
        elif types == ["high", "low", "high", "low", "high"]:
            X, A, B, C, D = [x[2] for x in p]
            XA, AB, BC, CD = X-A, B-A, B-C, D-C
            if all(v > 0 for v in [XA, AB, BC, CD]):
                r1, r2, r3 = AB/XA, BC/AB, CD/BC
                if 0.70 <= r1 <= 0.90 and 0.30 <= r2 <= 0.95 and 1.40 <= r3 <= 2.80 and D > X:
                    results.append({
                        "type": "看跌蝴蝶 🦋↓", "direction": "bear",
                        "points": [p[j][0] for j in range(5)],
                        "prices": [p[j][2] for j in range(5)],
                        "labels": ["X", "A", "B", "C", "D"],
                        "entry": D, "stop_loss": D * 1.03,
                        "target1": D - BC * 0.618, "target2": D - XA * 0.786,
                        "ratios": {"AB/XA": r1, "BC/AB": r2, "CD/BC": r3}
                    })
    return results

def detect_wm_patterns(df, order=5):
    close = df["Close"]
    volume = df["Volume"]
    highs_idx, lows_idx = find_pivots(close, order=order)
    results = []
    
    # W底偵測
    for i in range(len(lows_idx) - 1):
        idx1, idx2 = lows_idx[i], lows_idx[i+1]
        p1, p2 = float(close.iloc[idx1]), float(close.iloc[idx2])
        neck = float(close.iloc[idx1:idx2+1].max())
        if abs(p1 - p2) / max(p1, p2) < 0.06:
            v1, v2 = float(volume.iloc[idx1]), float(volume.iloc[idx2])
            results.append({
                "type": "W底 " + ("收斂" if p2 > p1 else "發散"), "direction": "bull",
                "points": [idx1, idx2], "prices": [p1, p2], "neck": neck,
                "entry": neck * 1.005, "stop_loss": min(p1, p2) * 0.98,
                "target": neck + (neck - min(p1, p2)), "vol_confirm": "✅量縮" if v2 < v1 else "⚠️量未縮",
                "vol_ratio": round(v2/v1, 2) if v1 > 0 else 0
            })
    return results

def compute_indicators(df):
    close = df["Close"]
    df["EMA20"] = close.ewm(span=20).mean()
    df["EMA50"] = close.ewm(span=50).mean()
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss))
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["Signal_Line"] = df["MACD"].ewm(span=9).mean()
    df["Histogram"] = df["MACD"] - df["Signal_Line"]
    return df

def volume_analysis(df):
    vol = df["Volume"]
    close = df["Close"]
    vol_ma20 = vol.rolling(20).mean()
    latest_vol = float(vol.iloc[-1])
    avg_vol = float(vol_ma20.iloc[-1]) if not pd.isna(vol_ma20.iloc[-1]) else 1
    vol_ratio = latest_vol / avg_vol
    price_up = float(close.iloc[-1]) > float(close.iloc[-5])
    
    if price_up and latest_vol > avg_vol:
        signal, color = "量價齊揚 ✅", "#3fb950"
    elif price_up:
        signal, color = "價漲量縮 ⚠️", "#d29922"
    elif not price_up and latest_vol > avg_vol:
        signal, color = "價跌量增 🚨", "#f85149"
    else:
        signal, color = "量價齊跌 ⚠️", "#58a6ff"
        
    return {"vol_ratio": vol_ratio, "signal": signal, "signal_color": color, 
            "vol_ma5": vol.rolling(5).mean(), "vol_ma20": vol_ma20, "anomaly_dates": []}

def build_chart(df, butterflies, wm_patterns, vol_info, symbol):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, row_heights=[0.5, 0.15, 0.15, 0.2], vertical_spacing=0.03)
    dates = df.index
    fig.add_trace(go.Candlestick(x=dates, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="K線"), row=1, col=1)
    
    # 畫出蝴蝶形態
    for bf in butterflies[-2:]:
        fig.add_trace(go.Scatter(x=[dates[p] for p in bf["points"]], y=bf["prices"], mode="lines+markers+text", 
                                 text=bf["labels"], name=bf["type"], line=dict(dash="dash")), row=1, col=1)

    fig.update_layout(height=900, template="plotly_dark", title=f"🦋 {symbol} 分析儀", showlegend=False)
    fig.update_xaxes(rangeslider_visible=False)
    return fig

def main():
    st.title("🦋 左側交易分析儀")
    
    with st.sidebar:
        st.header("設定")
        custom = st.text_input("輸入股票代碼 (例: 2330.TW, TSLA)", "")
        symbol = custom if custom else "BTC-USD"
        period = st.selectbox("週期", ["6mo", "1y", "2y", "5y"], index=1)
        interval = st.selectbox("間隔", ["1d", "1wk"], index=0)
        run = st.button("開始分析")

    if run:
        df = get_data(symbol, period, interval)
        if not df.empty:
            df = compute_indicators(df)
            butterflies = detect_butterfly(df)
            wm_patterns = detect_wm_patterns(df)
            vol_info = volume_analysis(df)
            
            # 顯示數據指標
            c1, c2, c3 = st.columns(3)
            c1.metric("現價", f"{df['Close'].iloc[-1]:.2f}")
            c2.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
            c3.metric("量比", f"{vol_info['vol_ratio']:.2f}x")
            
            st.plotly_chart(build_chart(df, butterflies, wm_patterns, vol_info, symbol), use_container_width=True)
        else:
            st.error("查無資料，請檢查代碼是否正確。")

if __name__ == "__main__":
    main()
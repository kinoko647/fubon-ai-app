“””
左側交易分析儀 - Streamlit + Plotly 版
支援：BTC / 加密貨幣 / 台股 / 美股
功能：蝴蝶形態、W/M形態、發散/收斂、交易量分析
“””

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import argrelextrema
import warnings
warnings.filterwarnings(‘ignore’)

# ─────────────────────────────────────────────────────────────

# 頁面設定

# ─────────────────────────────────────────────────────────────

st.set_page_config(
page_title=“左側交易分析儀”,
page_icon=“🦋”,
layout=“wide”,
initial_sidebar_state=“expanded”
)

st.markdown(”””

<style>
    .main { background-color: #0d1117; }
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .block-container { padding-top: 1rem; }
    .signal-bull { background: #1a3a2a; border-left: 4px solid #3fb950;
                   padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .signal-bear { background: #3a1a1a; border-left: 4px solid #f85149;
                   padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .signal-warn { background: #2e2a14; border-left: 4px solid #d29922;
                   padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    .signal-info { background: #162032; border-left: 4px solid #58a6ff;
                   padding: 10px 14px; border-radius: 6px; margin: 6px 0; }
    h1, h2, h3 { color: #e6edf3 !important; }
    .stSelectbox label, .stTextInput label, .stSlider label { color: #8b949e !important; }
</style>

“””, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────

# 快捷代碼列表

# ─────────────────────────────────────────────────────────────

QUICK_SYMBOLS = {
“🪙 BTC”: “BTC-USD”,
“🔷 ETH”: “ETH-USD”,
“🟡 BNB”: “BNB-USD”,
“🔵 SOL”: “SOL-USD”,
“🟠 XRP”: “XRP-USD”,
“📱 台積電”: “2330.TW”,
“🏦 富邦金”: “2881.TW”,
“📊 台灣50”: “0050.TW”,
“🍎 Apple”: “AAPL”,
“🚗 Tesla”: “TSLA”,
“🔍 Google”: “GOOGL”,
“📦 Amazon”: “AMZN”,
“💻 Nvidia”: “NVDA”,
“📈 SPY”: “SPY”,
}

# ─────────────────────────────────────────────────────────────

# 資料獲取

# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
df = yf.download(symbol, period=period, interval=interval, progress=False)
if df.empty:
return pd.DataFrame()
if isinstance(df.columns, pd.MultiIndex):
df.columns = df.columns.get_level_values(0)
df.dropna(inplace=True)
return df

# ─────────────────────────────────────────────────────────────

# 極值偵測

# ─────────────────────────────────────────────────────────────

def find_pivots(series: pd.Series, order: int = 5):
highs = argrelextrema(series.values, np.greater, order=order)[0]
lows = argrelextrema(series.values, np.less, order=order)[0]
return highs, lows

# ─────────────────────────────────────────────────────────────

# 蝴蝶形態

# ─────────────────────────────────────────────────────────────

def detect_butterfly(df: pd.DataFrame, order: int = 5):
close = df[‘Close’]
highs_idx, lows_idx = find_pivots(close, order=order)
results = []

```
all_pivots = []
for i in lows_idx:
    all_pivots.append((i, 'low', float(close.iloc[i])))
for i in highs_idx:
    all_pivots.append((i, 'high', float(close.iloc[i])))
all_pivots.sort(key=lambda x: x[0])

for i in range(len(all_pivots) - 4):
    p = all_pivots[i:i+5]
    types = [x[1] for x in p]

    # 看漲蝴蝶
    if types == ['low', 'high', 'low', 'high', 'low']:
        X, A, B, C, D = [x[2] for x in p]
        XA = A - X
        AB = A - B
        BC = C - B
        CD = C - D
        if XA > 0 and AB > 0 and BC > 0 and CD > 0:
            r1, r2, r3 = AB/XA, BC/AB, CD/BC
            if 0.70 <= r1 <= 0.90 and 0.30 <= r2 <= 0.95 and 1.40 <= r3 <= 2.80 and D < X:
                results.append({
                    'type': '看漲蝴蝶 🦋↑', 'direction': 'bull',
                    'points': [p[j][0] for j in range(5)],
                    'prices': [p[j][2] for j in range(5)],
                    'labels': ['X', 'A', 'B', 'C', 'D'],
                    'entry': D, 'stop_loss': D * 0.97,
                    'target1': D + BC * 0.618, 'target2': D + XA * 0.786,
                    'ratios': {'AB/XA': r1, 'BC/AB': r2, 'CD/BC': r3}
                })

    # 看跌蝴蝶
    if types == ['high', 'low', 'high', 'low', 'high']:
        X, A, B, C, D = [x[2] for x in p]
        XA = X - A
        AB = B - A
        BC = B - C
        CD = D - C
        if XA > 0 and AB > 0 and BC > 0 and CD > 0:
            r1, r2, r3 = AB/XA, BC/AB, CD/BC
            if 0.70 <= r1 <= 0.90 and 0.30 <= r2 <= 0.95 and 1.40 <= r3 <= 2.80 and D > X:
                results.append({
                    'type': '看跌蝴蝶 🦋↓', 'direction': 'bear',
                    'points': [p[j][0] for j in range(5)],
                    'prices': [p[j][2] for j in range(5)],
                    'labels': ['X', 'A', 'B', 'C', 'D'],
                    'entry': D, 'stop_loss': D * 1.03,
                    'target1': D - BC * 0.618, 'target2': D - XA * 0.786,
                    'ratios': {'AB/XA': r1, 'BC/AB': r2, 'CD/BC': r3}
                })
return results
```

# ─────────────────────────────────────────────────────────────

# W底 / M頭

# ─────────────────────────────────────────────────────────────

def detect_wm_patterns(df: pd.DataFrame, order: int = 5):
close = df[‘Close’]
volume = df[‘Volume’]
highs_idx, lows_idx = find_pivots(close, order=order)
results = []

```
# W底
for i in range(len(lows_idx) - 1):
    idx1, idx2 = lows_idx[i], lows_idx[i+1]
    p1, p2 = float(close.iloc[idx1]), float(close.iloc[idx2])
    between = close.iloc[idx1:idx2+1]
    neck = float(between.max())
    price_diff = abs(p1 - p2) / max(p1, p2)
    neck_height = (neck - min(p1, p2)) / min(p1, p2)
    if price_diff < 0.06 and neck_height > 0.02:
        v1, v2 = float(volume.iloc[idx1]), float(volume.iloc[idx2])
        if p2 < p1:
            sub, div = '發散W底 ⚠️', 'diverge'
        elif p2 > p1:
            sub, div = '收斂W底 ✅', 'converge'
        else:
            sub, div = '標準W底', 'equal'
        vol_txt = '✅量縮確認' if v2 < v1 else '⚠️量未縮'
        results.append({
            'type': f'W底 {sub}', 'direction': 'bull', 'divergence': div,
            'points': [idx1, idx2], 'prices': [p1, p2],
            'neck': neck, 'entry': neck * 1.005,
            'stop_loss': min(p1, p2) * 0.98,
            'target': neck + (neck - min(p1, p2)),
            'vol_confirm': vol_txt, 'vol_ratio': round(v2/v1, 2) if v1 > 0 else 0
        })

# M頭
for i in range(len(highs_idx) - 1):
    idx1, idx2 = highs_idx[i], highs_idx[i+1]
    p1, p2 = float(close.iloc[idx1]), float(close.iloc[idx2])
    between = close.iloc[idx1:idx2+1]
    neck = float(between.min())
    price_diff = abs(p1 - p2) / max(p1, p2)
    neck_depth = (max(p1, p2) - neck) / max(p1, p2)
    if price_diff < 0.06 and neck_depth > 0.02:
        v1, v2 = float(volume.iloc[idx1]), float(volume.iloc[idx2])
        if p2 > p1:
            sub, div = '發散M頭 ⚠️', 'diverge'
        elif p2 < p1:
            sub, div = '收斂M頭 ✅', 'converge'
        else:
            sub, div = '標準M頭', 'equal'
        vol_txt = '✅量縮確認' if v2 < v1 else '⚠️量放大'
        results.append({
            'type': f'M頭 {sub}', 'direction': 'bear', 'divergence': div,
            'points': [idx1, idx2], 'prices': [p1, p2],
            'neck': neck, 'entry': neck * 0.995,
            'stop_loss': max(p1, p2) * 1.02,
            'target': neck - (max(p1, p2) - neck),
            'vol_confirm': vol_txt, 'vol_ratio': round(v2/v1, 2) if v1 > 0 else 0
        })
return results
```

# ─────────────────────────────────────────────────────────────

# 指標計算

# ─────────────────────────────────────────────────────────────

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
close = df[‘Close’]
df[‘EMA20’] = close.ewm(span=20).mean()
df[‘EMA50’] = close.ewm(span=50).mean()
delta = close.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
df[‘RSI’] = 100 - (100 / (1 + gain / loss))
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
df[‘MACD’] = ema12 - ema26
df[‘Signal_Line’] = df[‘MACD’].ewm(span=9).mean()
df[‘Histogram’] = df[‘MACD’] - df[‘Signal_Line’]
return df

# ─────────────────────────────────────────────────────────────

# 量能分析

# ─────────────────────────────────────────────────────────────

def volume_analysis(df: pd.DataFrame) -> dict:
vol = df[‘Volume’]
close = df[‘Close’]
vol_ma20 = vol.rolling(20).mean()
vol_ma5 = vol.rolling(5).mean()
latest_vol = float(vol.iloc[-1])
avg_vol = float(vol_ma20.iloc[-1]) if not pd.isna(vol_ma20.iloc[-1]) else 1
vol_ratio = latest_vol / avg_vol if avg_vol > 0 else 1
price_up = float(close.iloc[-1]) > float(close.iloc[-5])
vol_up = latest_vol > avg_vol
if price_up and vol_up:
signal, color = ‘量價齊揚 ✅ (健康上漲)’, ‘#3fb950’
elif price_up and not vol_up:
signal, color = ‘價漲量縮 ⚠️ (動能不足)’, ‘#d29922’
elif not price_up and vol_up:
signal, color = ‘價跌量增 🚨 (恐慌賣出)’, ‘#f85149’
else:
signal, color = ‘量價齊跌 ⚠️ (縮量整理)’, ‘#58a6ff’
anomaly = vol[vol > vol_ma20 * 2].index.tolist()
return {
‘vol_ma5’: vol_ma5, ‘vol_ma20’: vol_ma20,
‘vol_ratio’: vol_ratio, ‘signal’: signal,
‘signal_color’: color, ‘anomaly_dates’: anomaly[-5:]
}

# ─────────────────────────────────────────────────────────────

# Plotly 主圖

# ─────────────────────────────────────────────────────────────

def build_chart(df, butterflies, wm_patterns, vol_info, symbol):
fig = make_subplots(
rows=4, cols=1, shared_xaxes=True,
row_heights=[0.50, 0.18, 0.16, 0.16],
vertical_spacing=0.02,
subplot_titles=(’’, ‘成交量’, ‘RSI’, ‘MACD’)
)

```
dates = df.index
close = df['Close'].values
open_ = df['Open'].values
high = df['High'].values
low = df['Low'].values
volume = df['Volume'].values

# K線
fig.add_trace(go.Candlestick(
    x=dates, open=open_, high=high, low=low, close=close,
    name='K線',
    increasing_line_color='#3fb950', decreasing_line_color='#f85149',
    increasing_fillcolor='#3fb950', decreasing_fillcolor='#f85149',
), row=1, col=1)

# EMA
fig.add_trace(go.Scatter(x=dates, y=df['EMA20'], name='EMA20',
                          line=dict(color='#f0a500', width=1.2), opacity=0.8), row=1, col=1)
fig.add_trace(go.Scatter(x=dates, y=df['EMA50'], name='EMA50',
                          line=dict(color='#58a6ff', width=1.2), opacity=0.8), row=1, col=1)

# ── 蝴蝶形態標記 ──
for bf in butterflies[-2:]:
    pts = bf['points']
    prices = bf['prices']
    color = '#3fb950' if bf['direction'] == 'bull' else '#f85149'
    bf_dates = [dates[p] for p in pts]

    fig.add_trace(go.Scatter(
        x=bf_dates, y=prices, mode='lines+markers+text',
        name=bf['type'], line=dict(color=color, width=1.5, dash='dash'),
        marker=dict(size=9, color=color, symbol='circle'),
        text=bf['labels'], textposition='top center',
        textfont=dict(size=10, color=color),
    ), row=1, col=1)

    # 進場/止損/目標水平線
    for lvl, name, lc in [
        (bf['entry'], '進場', color),
        (bf['stop_loss'], '止損', '#f85149'),
        (bf['target1'], '目標1', '#3fb950'),
    ]:
        fig.add_hline(y=lvl, line_dash='dot', line_color=lc,
                      line_width=0.8, opacity=0.5, row=1, col=1,
                      annotation_text=f"{name}: {lvl:.2f}",
                      annotation_font_color=lc, annotation_font_size=9)

# ── W底/M頭標記 ──
for wm in wm_patterns[-2:]:
    pts = wm['points']
    prices = wm['prices']
    color = '#3fb950' if wm['direction'] == 'bull' else '#f85149'
    wm_dates = [dates[p] for p in pts]
    marker_sym = 'triangle-up' if wm['direction'] == 'bull' else 'triangle-down'

    fig.add_trace(go.Scatter(
        x=wm_dates, y=prices, mode='markers',
        name=wm['type'],
        marker=dict(size=14, color=color, symbol=marker_sym),
    ), row=1, col=1)

    # 頸線
    fig.add_hline(y=wm['neck'], line_dash='dashdot', line_color=color,
                  line_width=1.2, opacity=0.7, row=1, col=1,
                  annotation_text=f"頸線: {wm['neck']:.2f}",
                  annotation_font_color=color, annotation_font_size=9,
                  annotation_position='right')

    # 目標線
    fig.add_hline(y=wm['target'], line_dash='dot', line_color='#d29922',
                  line_width=0.8, opacity=0.5, row=1, col=1,
                  annotation_text=f"目標: {wm['target']:.2f}",
                  annotation_font_color='#d29922', annotation_font_size=9,
                  annotation_position='right')

# ── 成交量 ──
vol_colors = ['#3fb950' if close[i] >= open_[i] else '#f85149'
              for i in range(len(df))]
fig.add_trace(go.Bar(
    x=dates, y=volume, name='成交量',
    marker_color=vol_colors, opacity=0.65,
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=dates, y=vol_info['vol_ma5'], name='量MA5',
    line=dict(color='#f0a500', width=1), opacity=0.85
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=dates, y=vol_info['vol_ma20'], name='量MA20',
    line=dict(color='#58a6ff', width=1), opacity=0.85
), row=2, col=1)

# 異常量標記
for ad in vol_info['anomaly_dates']:
    if ad in df.index:
        v = float(df.loc[ad, 'Volume'])
        fig.add_trace(go.Scatter(
            x=[ad], y=[v], mode='markers+text',
            marker=dict(size=8, color='#d29922', symbol='star'),
            text=['異常'], textposition='top center',
            textfont=dict(size=8, color='#d29922'),
            showlegend=False
        ), row=2, col=1)

# ── RSI ──
fig.add_trace(go.Scatter(x=dates, y=df['RSI'], name='RSI',
                          line=dict(color='#58a6ff', width=1.5)), row=3, col=1)
fig.add_hline(y=70, line_dash='dash', line_color='#f85149', line_width=0.8, row=3, col=1)
fig.add_hline(y=30, line_dash='dash', line_color='#3fb950', line_width=0.8, row=3, col=1)
fig.add_hline(y=50, line_dash='dot', line_color='#8b949e', line_width=0.5, row=3, col=1)
fig.add_hrect(y0=70, y1=100, fillcolor='#f85149', opacity=0.05, row=3, col=1)
fig.add_hrect(y0=0, y1=30, fillcolor='#3fb950', opacity=0.05, row=3, col=1)

# ── MACD ──
hist_colors = ['#3fb950' if v >= 0 else '#f85149' for v in df['Histogram'].fillna(0)]
fig.add_trace(go.Bar(x=dates, y=df['Histogram'], name='MACD柱',
                      marker_color=hist_colors, opacity=0.7), row=4, col=1)
fig.add_trace(go.Scatter(x=dates, y=df['MACD'], name='MACD',
                          line=dict(color='#f0a500', width=1.2)), row=4, col=1)
fig.add_trace(go.Scatter(x=dates, y=df['Signal_Line'], name='Signal',
                          line=dict(color='#58a6ff', width=1)), row=4, col=1)
fig.add_hline(y=0, line_color='#8b949e', line_width=0.5, row=4, col=1)

# ── 樣式 ──
fig.update_layout(
    title=dict(text=f'🦋  {symbol}  左側交易分析儀', font=dict(size=16, color='#e6edf3')),
    paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
    font=dict(color='#8b949e', size=11),
    height=820,
    legend=dict(bgcolor='rgba(13,17,23,0.8)', bordercolor='#30363d',
                borderwidth=1, font=dict(size=9)),
    xaxis_rangeslider_visible=False,
    margin=dict(l=60, r=60, t=60, b=40),
)

for i in range(1, 5):
    fig.update_xaxes(
        gridcolor='#21262d', showgrid=True,
        zerolinecolor='#30363d', row=i, col=1
    )
    fig.update_yaxes(
        gridcolor='#21262d', showgrid=True,
        zerolinecolor='#30363d', row=i, col=1
    )

fig.update_yaxes(range=[0, 100], row=3, col=1)
return fig
```

# ─────────────────────────────────────────────────────────────

# Streamlit UI

# ─────────────────────────────────────────────────────────────

def main():
st.title(“🦋 左側交易分析儀”)
st.caption(“支援 BTC / 加密貨幣 / 台股 / 美股　｜　蝴蝶形態 × W底M頭 × 量能分析”)

```
# ── 側邊欄 ──
with st.sidebar:
    st.markdown("### ⚙️ 分析設定")

    # 快捷按鈕
    st.markdown("**快捷選擇**")
    cols = st.columns(2)
    quick_symbol = None
    for idx, (label, sym) in enumerate(QUICK_SYMBOLS.items()):
        if cols[idx % 2].button(label, key=f"btn_{sym}", use_container_width=True):
            quick_symbol = sym

    st.markdown("---")
    custom = st.text_input("自訂代碼", placeholder="e.g. 2330.TW / TSLA / BTC-USD")
    symbol = custom.strip() if custom.strip() else (quick_symbol or "BTC-USD")

    period = st.selectbox("時間週期", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    interval = st.selectbox("K棒間隔", ["1d", "1h", "15m", "5m"], index=0)
    pivot_order = st.slider("極值靈敏度（越小越靈敏）", 3, 12, 5)

    st.markdown("---")
    run = st.button("🔍 開始分析", use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown("""
```

**⚠️ 風險提示**

- 本工具僅供技術分析參考
- 左側交易屬**預判性進場**，形態完成需等突破確認
- 槓桿交易風險極高，務必設定止損
- 不構成任何投資建議
  “””)
  
  # ── 主體 ──
  
  if run or quick_symbol:
  if not symbol:
  st.warning(“請輸入或選擇一個代碼”)
  return
  
  ```
    with st.spinner(f"📡 正在下載 {symbol} 資料..."):
        df = get_data(symbol, period=period, interval=interval)
  
    if df.empty:
        st.error(f"❌ 無法取得 {symbol} 資料，請確認代碼是否正確")
        return
  
    df = compute_indicators(df)
    butterflies = detect_butterfly(df, order=pivot_order)
    wm_patterns = detect_wm_patterns(df, order=pivot_order)
    vol_info = volume_analysis(df)
  
    # ── 頂部指標卡 ──
    current = float(df['Close'].iloc[-1])
    prev = float(df['Close'].iloc[-2])
    chg = (current / prev - 1) * 100
    rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 0
    macd_val = float(df['MACD'].iloc[-1]) if not pd.isna(df['MACD'].iloc[-1]) else 0
  
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("現價", f"{current:,.4f}", f"{chg:+.2f}%")
    c2.metric("RSI(14)", f"{rsi:.1f}",
              "超買 ⚠️" if rsi > 70 else ("超賣 ⚠️" if rsi < 30 else "正常"))
    c3.metric("量比", f"{vol_info['vol_ratio']:.2f}x")
    c4.metric("🦋蝴蝶形態", f"{len(butterflies)} 個",
              f"看漲{sum(1 for b in butterflies if b['direction']=='bull')} / 看跌{sum(1 for b in butterflies if b['direction']=='bear')}")
    c5.metric("W底/M頭", f"{len(wm_patterns)} 個",
              f"W底{sum(1 for w in wm_patterns if w['direction']=='bull')} / M頭{sum(1 for w in wm_patterns if w['direction']=='bear')}")
  
    # ── 量能信號橫幅 ──
    sig_class = ('signal-bull' if '齊揚' in vol_info['signal']
                 else 'signal-bear' if '恐慌' in vol_info['signal']
                 else 'signal-warn')
    st.markdown(f'<div class="{sig_class}"><b>📊 量能信號：</b>{vol_info["signal"]}</div>',
                unsafe_allow_html=True)
  
    # ── 主圖 ──
    fig = build_chart(df, butterflies, wm_patterns, vol_info, symbol)
    st.plotly_chart(fig, use_container_width=True)
  
    # ── 形態詳情 ──
    col_a, col_b = st.columns(2)
  
    with col_a:
        st.markdown("### 🦋 蝴蝶形態詳情")
        if butterflies:
            for bf in butterflies[-4:]:
                color_class = 'signal-bull' if bf['direction'] == 'bull' else 'signal-bear'
                st.markdown(f"""
  ```

<div class="{color_class}">
<b>{bf['type']}</b><br>
進場：<code>{bf['entry']:.4f}</code>　
止損：<code>{bf['stop_loss']:.4f}</code>　
目標1：<code>{bf['target1']:.4f}</code>　
目標2：<code>{bf['target2']:.4f}</code><br>
<small>Fib — AB/XA: {bf['ratios']['AB/XA']:.3f} | BC/AB: {bf['ratios']['BC/AB']:.3f} | CD/BC: {bf['ratios']['CD/BC']:.3f}</small>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="signal-info">目前未偵測到標準蝴蝶形態<br><small>可嘗試調整「極值靈敏度」或更長時間週期</small></div>',
                            unsafe_allow_html=True)

```
    with col_b:
        st.markdown("### 📐 W底 / M頭形態詳情")
        if wm_patterns:
            for wm in wm_patterns[-4:]:
                color_class = 'signal-bull' if wm['direction'] == 'bull' else 'signal-bear'
                st.markdown(f"""
```

<div class="{color_class}">
<b>{wm['type']}</b><br>
頸線：<code>{wm['neck']:.4f}</code>　
進場：<code>{wm['entry']:.4f}</code>　
止損：<code>{wm['stop_loss']:.4f}</code>　
目標：<code>{wm['target']:.4f}</code><br>
<small>{wm['vol_confirm']}　量比：{wm['vol_ratio']}</small>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="signal-info">目前未偵測到W底/M頭形態<br><small>可嘗試調整「極值靈敏度」或更長時間週期</small></div>',
                            unsafe_allow_html=True)

```
    # ── 資料表 ──
    with st.expander("📄 查看原始資料（最近20筆）"):
        show_df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'EMA20', 'EMA50', 'RSI', 'MACD']].tail(20)
        st.dataframe(show_df.style.format("{:.4f}"), use_container_width=True)

else:
    # 預設畫面
    st.markdown("""
```

<div style="text-align:center; padding: 60px 0; color: #8b949e;">
<h2>👈 從左側選擇標的開始分析</h2>
<p>支援 BTC、ETH 等加密貨幣，台股（2330.TW），美股（AAPL、TSLA）</p>
<br>
<table style="margin: 0 auto; color: #8b949e; font-size:14px; border-collapse: collapse;">
<tr><th style="padding:8px 20px; border-bottom: 1px solid #30363d;">功能</th><th style="padding:8px 20px; border-bottom: 1px solid #30363d;">說明</th></tr>
<tr><td style="padding:6px 20px;">🦋 蝴蝶形態</td><td style="padding:6px 20px;">X-A-B-C-D Fibonacci 結構，自動判斷看漲/看跌</td></tr>
<tr><td style="padding:6px 20px;">📐 W底 / M頭</td><td style="padding:6px 20px;">收斂/發散判斷 + 頸線突破進場點</td></tr>
<tr><td style="padding:6px 20px;">📊 量能分析</td><td style="padding:6px 20px;">量比、量價背離、異常量偵測</td></tr>
<tr><td style="padding:6px 20px;">📈 RSI / MACD</td><td style="padding:6px 20px;">超買超賣 + 趨勢動能確認</td></tr>
</table>
</div>
""", unsafe_allow_html=True)

if **name** == “**main**”:
main()
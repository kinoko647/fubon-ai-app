import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy.signal import argrelextrema
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# 字體與顏色設定
# ─────────────────────────────────────────────────────────────
plt.rcParams['font.family'] = ['Microsoft JhengHei', 'PingFang TC', 'DejaVu Sans']
plt.rcParams['axes.facecolor'] = '#0d1117'
plt.rcParams['figure.facecolor'] = '#0d1117'
plt.rcParams['text.color'] = '#e6edf3'
plt.rcParams['axes.labelcolor'] = '#8b949e'
plt.rcParams['xtick.color'] = '#8b949e'
plt.rcParams['ytick.color'] = '#8b949e'
plt.rcParams['axes.edgecolor'] = '#30363d'
plt.rcParams['grid.color'] = '#21262d'

BULL_COLOR = '#3fb950'   # 做多綠
BEAR_COLOR = '#f85149'   # 做空紅
NEUTRAL_COLOR = '#58a6ff' # 中性藍
WARNING_COLOR = '#d29922' # 警告黃


# ─────────────────────────────────────────────────────────────
# 1. 資料獲取
# ─────────────────────────────────────────────────────────────
def get_data(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """
    下載行情資料
    symbol: 'BTC-USD' 或 股票代碼如 '2330.TW' / 'AAPL'
    period: 1mo, 3mo, 6mo, 1y, 2y
    interval: 1d, 1h, 4h (注意yfinance對4h不支援，請用1h)
    """
    print(f"\n📡 正在下載 {symbol} 資料 (週期:{period}, 間隔:{interval})...")
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError(f"❌ 無法取得 {symbol} 資料，請確認代碼是否正確")
    
    # 統一欄位名稱（yfinance v0.2+ 可能是 MultiIndex）
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df.dropna(inplace=True)
    print(f"✅ 取得 {len(df)} 筆資料 ({df.index[0].date()} ~ {df.index[-1].date()})")
    return df


# ─────────────────────────────────────────────────────────────
# 2. 極值點偵測（高低點）
# ─────────────────────────────────────────────────────────────
def find_pivots(series: pd.Series, order: int = 5):
    """尋找局部高點與低點，order 為左右比較的K棒數"""
    highs = argrelextrema(series.values, np.greater, order=order)[0]
    lows = argrelextrema(series.values, np.less, order=order)[0]
    return highs, lows


# ─────────────────────────────────────────────────────────────
# 3. 蝴蝶形態偵測 (Butterfly Pattern)
# ─────────────────────────────────────────────────────────────
def detect_butterfly(df: pd.DataFrame, order: int = 5):
    """
    蝴蝶形態規則 (Gartley/Butterfly 變體)：
    看漲蝴蝶：X低 → A高 → B低 → C高 → D低 (D < X)
    看跌蝴蝶：X高 → A低 → B高 → C低 → D高 (D > X)
    
    Fibonacci 比例：
    AB = 0.786 * XA
    BC = 0.382 ~ 0.886 * AB
    CD = 1.618 ~ 2.618 * BC
    """
    close = df['Close']
    highs_idx, lows_idx = find_pivots(close, order=order)
    
    results = []
    
    # 看漲蝴蝶：找 低-高-低-高-低 結構
    all_pivots = []
    for i in lows_idx:
        all_pivots.append((i, 'low', close.iloc[i]))
    for i in highs_idx:
        all_pivots.append((i, 'high', close.iloc[i]))
    all_pivots.sort(key=lambda x: x[0])
    
    for i in range(len(all_pivots) - 4):
        p = all_pivots[i:i+5]
        types = [x[1] for x in p]
        
        # 看漲：low-high-low-high-low
        if types == ['low', 'high', 'low', 'high', 'low']:
            X, A, B, C, D = [x[2] for x in p]
            XA = A - X
            AB = A - B
            BC = C - B
            CD = C - D
            
            if XA > 0 and AB > 0 and BC > 0 and CD > 0:
                ratio_AB_XA = AB / XA
                ratio_BC_AB = BC / AB
                ratio_CD_BC = CD / BC
                
                if (0.70 <= ratio_AB_XA <= 0.90 and
                    0.30 <= ratio_BC_AB <= 0.95 and
                    1.40 <= ratio_CD_BC <= 2.80 and
                    D < X):  # 蝴蝶條件：D低於X
                    
                    results.append({
                        'type': '看漲蝴蝶 🦋↑',
                        'direction': 'bull',
                        'points': [p[j][0] for j in range(5)],
                        'prices': [p[j][2] for j in range(5)],
                        'labels': ['X', 'A', 'B', 'C', 'D'],
                        'entry': D,
                        'stop_loss': D * 0.97,
                        'target1': D + BC * 0.618,
                        'target2': D + XA * 0.786,
                        'ratios': {'AB/XA': ratio_AB_XA, 'BC/AB': ratio_BC_AB, 'CD/BC': ratio_CD_BC}
                    })
        
        # 看跌：high-low-high-low-high
        if types == ['high', 'low', 'high', 'low', 'high']:
            X, A, B, C, D = [x[2] for x in p]
            XA = X - A
            AB = B - A
            BC = B - C
            CD = D - C
            
            if XA > 0 and AB > 0 and BC > 0 and CD > 0:
                ratio_AB_XA = AB / XA
                ratio_BC_AB = BC / AB
                ratio_CD_BC = CD / BC
                
                if (0.70 <= ratio_AB_XA <= 0.90 and
                    0.30 <= ratio_BC_AB <= 0.95 and
                    1.40 <= ratio_CD_BC <= 2.80 and
                    D > X):  # 蝴蝶條件：D高於X
                    
                    results.append({
                        'type': '看跌蝴蝶 🦋↓',
                        'direction': 'bear',
                        'points': [p[j][0] for j in range(5)],
                        'prices': [p[j][2] for j in range(5)],
                        'labels': ['X', 'A', 'B', 'C', 'D'],
                        'entry': D,
                        'stop_loss': D * 1.03,
                        'target1': D - BC * 0.618,
                        'target2': D - XA * 0.786,
                        'ratios': {'AB/XA': ratio_AB_XA, 'BC/AB': ratio_BC_AB, 'CD/BC': ratio_CD_BC}
                    })
    
    return results


# ─────────────────────────────────────────────────────────────
# 4. W底/M頭形態偵測 + 發散/收斂
# ─────────────────────────────────────────────────────────────
def detect_wm_patterns(df: pd.DataFrame, order: int = 5):
    """
    W底（雙底）：兩個相近低點，中間有反彈高點
    M頭（雙頂）：兩個相近高點，中間有回落低點
    發散：兩個低點/高點距離越來越大 → 趨勢延伸
    收斂：兩個低點/高點距離越來越小 → 趨勢反轉準備
    """
    close = df['Close']
    volume = df['Volume']
    highs_idx, lows_idx = find_pivots(close, order=order)
    
    results = []
    
    # ── W底偵測 ──
    for i in range(len(lows_idx) - 1):
        idx1, idx2 = lows_idx[i], lows_idx[i+1]
        p1, p2 = close.iloc[idx1], close.iloc[idx2]
        
        # 兩低點之間找最高點（頸線）
        between = close.iloc[idx1:idx2+1]
        neck_idx = between.idxmax()
        neck_price = between.max()
        
        # W底條件：兩低點相近（差距 < 5%），頸線明顯高於低點
        price_diff = abs(p1 - p2) / max(p1, p2)
        neck_height = (neck_price - min(p1, p2)) / min(p1, p2)
        
        if price_diff < 0.05 and neck_height > 0.03:
            # 判斷收斂/發散
            vol1 = volume.iloc[idx1]
            vol2 = volume.iloc[idx2]
            
            if p2 < p1:  # 第二低點更低 → 發散（假突破警惕）
                pattern_sub = '發散W底（假突破風險⚠️）'
                divergence = 'diverge'
            elif p2 > p1:  # 第二低點更高 → 收斂（底部確認）
                pattern_sub = '收斂W底（底部確認✅）'
                divergence = 'converge'
            else:
                pattern_sub = '標準W底'
                divergence = 'equal'
            
            # 量能確認：第二低點成交量應小於第一低點（縮量）
            vol_confirm = '✅量縮確認' if vol2 < vol1 else '⚠️量未縮'
            
            results.append({
                'type': f'W底 {pattern_sub}',
                'direction': 'bull',
                'divergence': divergence,
                'points': [idx1, idx2],
                'prices': [p1, p2],
                'neck': neck_price,
                'entry': neck_price * 1.005,  # 突破頸線0.5%進場
                'stop_loss': min(p1, p2) * 0.98,
                'target': neck_price + (neck_price - min(p1, p2)),  # 等幅量度
                'vol_confirm': vol_confirm,
                'vol_ratio': round(vol2/vol1, 2)
            })
    
    # ── M頭偵測 ──
    for i in range(len(highs_idx) - 1):
        idx1, idx2 = highs_idx[i], highs_idx[i+1]
        p1, p2 = close.iloc[idx1], close.iloc[idx2]
        
        between = close.iloc[idx1:idx2+1]
        neck_idx = between.idxmin()
        neck_price = between.min()
        
        price_diff = abs(p1 - p2) / max(p1, p2)
        neck_depth = (max(p1, p2) - neck_price) / max(p1, p2)
        
        if price_diff < 0.05 and neck_depth > 0.03:
            vol1 = volume.iloc[idx1]
            vol2 = volume.iloc[idx2]
            
            if p2 > p1:  # 第二高點更高 → 發散（持續上漲可能）
                pattern_sub = '發散M頭（持續上漲⚠️）'
                divergence = 'diverge'
            elif p2 < p1:  # 第二高點更低 → 收斂（頭部確認）
                pattern_sub = '收斂M頭（頭部確認✅）'
                divergence = 'converge'
            else:
                pattern_sub = '標準M頭'
                divergence = 'equal'
            
            vol_confirm = '✅量縮確認' if vol2 < vol1 else '⚠️量放大（謹慎）'
            
            results.append({
                'type': f'M頭 {pattern_sub}',
                'direction': 'bear',
                'divergence': divergence,
                'points': [idx1, idx2],
                'prices': [p1, p2],
                'neck': neck_price,
                'entry': neck_price * 0.995,
                'stop_loss': max(p1, p2) * 1.02,
                'target': neck_price - (max(p1, p2) - neck_price),
                'vol_confirm': vol_confirm,
                'vol_ratio': round(vol2/vol1, 2)
            })
    
    return results


# ─────────────────────────────────────────────────────────────
# 5. 交易量分析
# ─────────────────────────────────────────────────────────────
def volume_analysis(df: pd.DataFrame) -> dict:
    """交易量趨勢分析：量價關係、異常量能偵測"""
    vol = df['Volume']
    close = df['Close']
    
    # 20日均量
    vol_ma20 = vol.rolling(20).mean()
    # 5日均量
    vol_ma5 = vol.rolling(5).mean()
    
    # 最新量能倍數
    latest_vol = vol.iloc[-1]
    avg_vol = vol_ma20.iloc[-1]
    vol_ratio = latest_vol / avg_vol if avg_vol > 0 else 1
    
    # 量價背離偵測（價漲量縮 or 價跌量縮）
    price_up = close.iloc[-1] > close.iloc[-5]
    vol_up = vol.iloc[-1] > vol_ma20.iloc[-1]
    
    if price_up and vol_up:
        signal = '量價齊揚 ✅ (健康上漲)'
        signal_color = BULL_COLOR
    elif price_up and not vol_up:
        signal = '價漲量縮 ⚠️ (上漲動能不足)'
        signal_color = WARNING_COLOR
    elif not price_up and vol_up:
        signal = '價跌量增 🚨 (恐慌性賣出)'
        signal_color = BEAR_COLOR
    else:
        signal = '量價齊跌 ⚠️ (縮量整理)'
        signal_color = NEUTRAL_COLOR
    
    # 尋找最近異常大量（超過均量2倍）
    anomaly_idx = vol[vol > vol_ma20 * 2].index.tolist()
    
    return {
        'vol_ma5': vol_ma5,
        'vol_ma20': vol_ma20,
        'vol_ratio': vol_ratio,
        'signal': signal,
        'signal_color': signal_color,
        'anomaly_dates': anomaly_idx[-5:],  # 最近5次異常
    }


# ─────────────────────────────────────────────────────────────
# 6. 技術指標
# ─────────────────────────────────────────────────────────────
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df['Close']
    
    # EMA
    df['EMA20'] = close.ewm(span=20).mean()
    df['EMA50'] = close.ewm(span=50).mean()
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    
    return df


# ─────────────────────────────────────────────────────────────
# 7. 主繪圖函數
# ─────────────────────────────────────────────────────────────
def plot_analysis(symbol: str, df: pd.DataFrame, butterfly_patterns: list,
                  wm_patterns: list, vol_info: dict):
    
    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor('#0d1117')
    
    gs = GridSpec(4, 2, figure=fig, hspace=0.08, wspace=0.3,
                  height_ratios=[3, 1, 1, 1])
    
    ax_price = fig.add_subplot(gs[0, :])    # 主圖：價格
    ax_vol = fig.add_subplot(gs[1, :])      # 交易量
    ax_rsi = fig.add_subplot(gs[2, 0])     # RSI
    ax_macd = fig.add_subplot(gs[2, 1])    # MACD
    ax_info = fig.add_subplot(gs[3, :])    # 信號資訊

    close = df['Close']
    dates = df.index
    x = np.arange(len(df))
    
    # ── 主圖：K線 + EMA ──
    ax_price.set_facecolor('#0d1117')
    
    # 繪製陰陽線
    for i in range(len(df)):
        o, h, l, c = df['Open'].iloc[i], df['High'].iloc[i], df['Low'].iloc[i], df['Close'].iloc[i]
        color = BULL_COLOR if c >= o else BEAR_COLOR
        ax_price.plot([i, i], [l, h], color=color, linewidth=0.8, alpha=0.7)
        ax_price.add_patch(plt.Rectangle((i - 0.3, min(o, c)), 0.6, abs(c - o),
                                          facecolor=color, edgecolor=color, alpha=0.85))
    
    # EMA
    valid_ema20 = df['EMA20'].dropna()
    valid_ema50 = df['EMA50'].dropna()
    ax_price.plot(x[-len(valid_ema20):], valid_ema20.values, color='#f0a500',
                  linewidth=1.2, label='EMA20', alpha=0.8)
    ax_price.plot(x[-len(valid_ema50):], valid_ema50.values, color='#58a6ff',
                  linewidth=1.2, label='EMA50', alpha=0.8)
    
    # ── 蝴蝶形態繪製 ──
    for bf in butterfly_patterns[-2:]:  # 只畫最近2個
        pts = bf['points']
        prices = bf['prices']
        color = BULL_COLOR if bf['direction'] == 'bull' else BEAR_COLOR
        
        # 連線
        ax_price.plot(pts, prices, color=color, linewidth=1.5,
                      linestyle='--', alpha=0.7, zorder=5)
        
        # 標記點
        for j, (pt, pr, lb) in enumerate(zip(pts, prices, bf['labels'])):
            marker = 'v' if lb in ['A', 'C'] and bf['direction'] == 'bull' else '^'
            if lb in ['X', 'D']:
                marker = '*'
            ax_price.scatter(pt, pr, color=color, s=80, zorder=10, marker='o')
            ax_price.annotate(f'{lb}\n{pr:.1f}', (pt, pr),
                              xytext=(0, 12 if j % 2 == 0 else -18),
                              textcoords='offset points',
                              fontsize=7, color=color, fontweight='bold',
                              ha='center')
        
        # 進場線
        ax_price.axhline(bf['entry'], color=color, linestyle=':', linewidth=1, alpha=0.6)
        ax_price.axhline(bf['stop_loss'], color=BEAR_COLOR, linestyle=':', linewidth=0.8, alpha=0.5)
        ax_price.axhline(bf['target1'], color=BULL_COLOR, linestyle=':', linewidth=0.8, alpha=0.5)
    
    # ── W/M 形態繪製 ──
    for wm in wm_patterns[-2:]:
        pts = wm['points']
        prices = wm['prices']
        color = BULL_COLOR if wm['direction'] == 'bull' else BEAR_COLOR
        neck = wm['neck']
        
        # 頸線
        ax_price.axhline(neck, color=color, linestyle='-.',
                         linewidth=1.2, alpha=0.6)
        ax_price.annotate(f"頸線 {neck:.1f}", (x[-1], neck),
                          fontsize=7.5, color=color, ha='right',
                          va='bottom', fontweight='bold')
        
        # 底/頂部標記
        for pt, pr in zip(pts, prices):
            ax_price.scatter(pt, pr, color=color, s=100, zorder=10,
                             marker='^' if wm['direction'] == 'bull' else 'v')
        
        # 目標線
        ax_price.axhline(wm['target'], color=WARNING_COLOR,
                         linestyle=':', linewidth=1, alpha=0.5)
    
    ax_price.set_title(f'  {symbol}  左側交易分析儀  |  {dates[-1].date()}',
                       fontsize=14, color='#e6edf3', fontweight='bold', pad=10, loc='left')
    ax_price.legend(loc='upper left', framealpha=0.2, fontsize=8)
    ax_price.set_xlim(-1, len(df) + 5)
    ax_price.set_xticks([])
    ax_price.grid(True, alpha=0.15)
    
    # ── 交易量圖 ──
    ax_vol.set_facecolor('#0d1117')
    vol_colors = [BULL_COLOR if df['Close'].iloc[i] >= df['Open'].iloc[i]
                  else BEAR_COLOR for i in range(len(df))]
    ax_vol.bar(x, df['Volume'].values, color=vol_colors, alpha=0.6, width=0.8)
    ax_vol.plot(x[-len(vol_info['vol_ma5'].dropna()):],
                vol_info['vol_ma5'].dropna().values, color='#f0a500',
                linewidth=1, label='量MA5', alpha=0.85)
    ax_vol.plot(x[-len(vol_info['vol_ma20'].dropna()):],
                vol_info['vol_ma20'].dropna().values, color='#58a6ff',
                linewidth=1, label='量MA20', alpha=0.85)
    
    # 異常量標記
    for ad in vol_info['anomaly_dates']:
        if ad in df.index:
            ai = df.index.get_loc(ad)
            ax_vol.annotate('異常量', (ai, df['Volume'].iloc[ai]),
                            xytext=(0, 5), textcoords='offset points',
                            fontsize=6, color=WARNING_COLOR, ha='center')
    
    ax_vol.set_ylabel('成交量', fontsize=8)
    ax_vol.legend(loc='upper left', framealpha=0.2, fontsize=7)
    ax_vol.set_xlim(-1, len(df) + 5)
    ax_vol.set_xticks([])
    ax_vol.grid(True, alpha=0.1)
    
    # ── RSI ──
    ax_rsi.set_facecolor('#0d1117')
    rsi = df['RSI'].dropna()
    rsi_x = x[-len(rsi):]
    ax_rsi.plot(rsi_x, rsi.values, color=NEUTRAL_COLOR, linewidth=1.2)
    ax_rsi.axhline(70, color=BEAR_COLOR, linestyle='--', linewidth=0.8, alpha=0.7)
    ax_rsi.axhline(30, color=BULL_COLOR, linestyle='--', linewidth=0.8, alpha=0.7)
    ax_rsi.axhline(50, color='#8b949e', linestyle=':', linewidth=0.5, alpha=0.5)
    ax_rsi.fill_between(rsi_x, rsi.values, 70,
                        where=(rsi.values >= 70), alpha=0.2, color=BEAR_COLOR)
    ax_rsi.fill_between(rsi_x, rsi.values, 30,
                        where=(rsi.values <= 30), alpha=0.2, color=BULL_COLOR)
    ax_rsi.set_ylabel('RSI', fontsize=8)
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_xlim(-1, len(df) + 5)
    ax_rsi.set_xticks([])
    ax_rsi.grid(True, alpha=0.1)
    ax_rsi.annotate(f"RSI: {rsi.iloc[-1]:.1f}", (rsi_x[-1], rsi.iloc[-1]),
                    xytext=(5, 0), textcoords='offset points',
                    fontsize=8, color=NEUTRAL_COLOR, fontweight='bold')
    
    # ── MACD ──
    ax_macd.set_facecolor('#0d1117')
    macd = df['MACD'].dropna()
    signal = df['Signal'].dropna()
    hist = df['Histogram'].dropna()
    macd_x = x[-len(macd):]
    
    hist_colors = [BULL_COLOR if v >= 0 else BEAR_COLOR for v in hist.values]
    ax_macd.bar(macd_x[-len(hist):], hist.values, color=hist_colors, alpha=0.6, width=0.8)
    ax_macd.plot(macd_x, macd.values, color='#f0a500', linewidth=1, label='MACD')
    ax_macd.plot(macd_x[-len(signal):], signal.values, color=NEUTRAL_COLOR,
                 linewidth=1, label='Signal')
    ax_macd.axhline(0, color='#8b949e', linewidth=0.5)
    ax_macd.set_ylabel('MACD', fontsize=8)
    ax_macd.legend(loc='upper left', framealpha=0.2, fontsize=7)
    ax_macd.set_xlim(-1, len(df) + 5)
    ax_macd.set_xticks([])
    ax_macd.grid(True, alpha=0.1)
    
    # ── 信號資訊區 ──
    ax_info.set_facecolor('#161b22')
    ax_info.set_xlim(0, 10)
    ax_info.set_ylim(0, 1)
    ax_info.axis('off')
    
    # 統計信號
    bull_signals = [p for p in butterfly_patterns if p['direction'] == 'bull']
    bear_signals = [p for p in butterfly_patterns if p['direction'] == 'bear']
    bull_wm = [p for p in wm_patterns if p['direction'] == 'bull']
    bear_wm = [p for p in wm_patterns if p['direction'] == 'bear']
    
    info_text = (
        f"蝴蝶形態：看漲 {len(bull_signals)} 個  |  看跌 {len(bear_signals)} 個    "
        f"W/M形態：W底 {len(bull_wm)} 個  |  M頭 {len(bear_wm)} 個    "
        f"量能信號：{vol_info['signal']}    "
        f"量比：{vol_info['vol_ratio']:.2f}x"
    )
    ax_info.text(5, 0.6, info_text, fontsize=9, color='#e6edf3',
                ha='center', va='center', fontweight='bold')
    
    # 最新價格
    current_price = close.iloc[-1]
    price_change = (close.iloc[-1] / close.iloc[-2] - 1) * 100
    p_color = BULL_COLOR if price_change >= 0 else BEAR_COLOR
    ax_info.text(5, 0.2,
                 f"現價：{current_price:.4f}    "
                 f"漲跌：{'▲' if price_change >= 0 else '▼'} {abs(price_change):.2f}%    "
                 f"RSI：{df['RSI'].iloc[-1]:.1f}",
                 fontsize=10, color=p_color, ha='center', va='center', fontweight='bold')
    
    # X軸日期（底部）
    tick_positions = np.linspace(0, len(df)-1, min(10, len(df)), dtype=int)
    ax_vol.set_xticks(tick_positions)
    ax_vol.set_xticklabels([str(dates[i].date()) for i in tick_positions],
                            rotation=30, fontsize=7)
    
    plt.savefig(f'{symbol.replace("-", "_")}_analysis.png',
                dpi=150, bbox_inches='tight', facecolor='#0d1117')
    print(f"\n💾 圖表已儲存：{symbol.replace('-', '_')}_analysis.png")
    plt.show()


# ─────────────────────────────────────────────────────────────
# 8. 主程式
# ─────────────────────────────────────────────────────────────
def analyze(symbol: str, period: str = "6mo", interval: str = "1d",
            pivot_order: int = 5):
    """
    完整左側交易分析
    
    參數：
    ─────────────────────────────
    symbol      代碼範例：
                  BTC/加密貨幣 → 'BTC-USD', 'ETH-USD'
                  台股        → '2330.TW', '0050.TW'
                  美股        → 'AAPL', 'TSLA', 'SPY'
    period      時間週期：1mo / 3mo / 6mo / 1y / 2y
    interval    K棒間隔：1d / 1h / 5m
    pivot_order 極值靈敏度（越大越不靈敏）：3~10
    """
    
    print("=" * 60)
    print(f"  🔍 左側交易分析儀  |  {symbol}")
    print("=" * 60)
    
    # 下載資料
    df = get_data(symbol, period=period, interval=interval)
    
    # 計算指標
    df = compute_indicators(df)
    
    # 偵測形態
    print("\n🦋 蝴蝶形態偵測中...")
    butterflies = detect_butterfly(df, order=pivot_order)
    
    print(f"📊 W底/M頭形態偵測中...")
    wm = detect_wm_patterns(df, order=pivot_order)
    
    print(f"📈 交易量分析中...")
    vol_info = volume_analysis(df)
    
    # 輸出文字報告
    print("\n" + "─" * 60)
    print("  📋 分析報告")
    print("─" * 60)
    
    if butterflies:
        print(f"\n【蝴蝶形態】共偵測 {len(butterflies)} 個")
        for b in butterflies[-3:]:
            print(f"\n  ● {b['type']}")
            print(f"    進場價：{b['entry']:.4f}")
            print(f"    止損價：{b['stop_loss']:.4f}")
            print(f"    目標1：{b['target1']:.4f}")
            print(f"    目標2：{b['target2']:.4f}")
            print(f"    Fib比例：AB/XA={b['ratios']['AB/XA']:.3f}, "
                  f"BC/AB={b['ratios']['BC/AB']:.3f}, "
                  f"CD/BC={b['ratios']['CD/BC']:.3f}")
    else:
        print("\n【蝴蝶形態】未偵測到標準蝴蝶")
    
    if wm:
        print(f"\n【W底/M頭形態】共偵測 {len(wm)} 個")
        for w in wm[-3:]:
            print(f"\n  ● {w['type']}")
            print(f"    頸線：{w['neck']:.4f}")
            print(f"    進場：{w['entry']:.4f}")
            print(f"    止損：{w['stop_loss']:.4f}")
            print(f"    目標：{w['target']:.4f}")
            print(f"    量能：{w['vol_confirm']}（量比={w['vol_ratio']}）")
    else:
        print("\n【W底/M頭形態】未偵測到標準形態")
    
    print(f"\n【量能分析】")
    print(f"  {vol_info['signal']}")
    print(f"  當前量比：{vol_info['vol_ratio']:.2f}x（相對20日均量）")
    if vol_info['anomaly_dates']:
        print(f"  最近異常量日期：{[str(d.date()) for d in vol_info['anomaly_dates']]}")
    
    # 繪圖
    plot_analysis(symbol, df, butterflies, wm, vol_info)
    
    return {'butterflies': butterflies, 'wm_patterns': wm, 'vol': vol_info, 'df': df}


# ─────────────────────────────────────────────────────────────
# 9. 使用範例
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    
    print("\n" + "═" * 60)
    print("  左側交易分析儀  |  支援BTC & 股票")
    print("═" * 60)
    print("\n範例代碼：")
    print("  BTC        → 'BTC-USD'")
    print("  以太坊      → 'ETH-USD'")
    print("  台積電      → '2330.TW'")
    print("  台灣50     → '0050.TW'")
    print("  Apple      → 'AAPL'")
    print("  Tesla      → 'TSLA'")
    
    symbol = input("\n請輸入代碼（直接Enter使用BTC-USD）：").strip()
    if not symbol:
        symbol = "BTC-USD"
    
    period = input("時間週期 [1mo/3mo/6mo/1y] (Enter=6mo)：").strip() or "6mo"
    interval = input("K棒間隔 [1d/1h] (Enter=1d)：").strip() or "1d"
    result = analyze(symbol, period=period, interval=interval, pivot_order=5)
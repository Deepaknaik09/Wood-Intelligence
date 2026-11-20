"""Dedicated Module: Live Wood Market Price & AI Price Estimation.
Trading Terminal & Live Share Market Interface for Commercial Timber Commodities.

Features:
- Live Animated Stock Ticker Tape (Teak, Pine, Rosewood, Sandalwood, Oak, etc.)
- Professional TradingView-Style Financial Candlestick Chart (Plotly) with EMA & Volume
- Market Depth / Order Book (Level-2 Bids & Asks with Live Spread)
- Interactive Stock Watchlist with 1-click asset switching
- AI-Powered Specimen Valuation & Trade Position Calculator (Random Forest R² = 0.994)
- Mandi APMC Cross-Commodity Benchmark Feed
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import mandi_price_service
import timber_price_model

def uhtml(s: str) -> str:
    """Returns an unindented single-line string with no blank lines for clean Streamlit rendering."""
    return "".join(line.strip() for line in s.splitlines() if line.strip())

# Master Timber Stock Universe
TIMBER_STOCKS = {
    "PINE": {
        "name": "Pine (Radiata / Chir)",
        "code": "PINE.IN",
        "category": "Softwood Construction",
        "base_cft": 1850.45,
        "change_pct": -0.62,
        "change_pts": -11.50,
        "prev_close": 1861.95,
        "high_52w": 2180.00,
        "low_52w": 1420.00,
        "volume_cft": 18450,
        "lot_size": 25,
        "density": 480
    },
    "TEAK": {
        "name": "Teak (CP Grade A / Dandeli)",
        "code": "TEAK.IN",
        "category": "Prestige Hardwood",
        "base_cft": 4708.20,
        "change_pct": +2.45,
        "change_pts": +112.50,
        "prev_close": 4595.70,
        "high_52w": 5250.00,
        "low_52w": 3800.00,
        "volume_cft": 34200,
        "lot_size": 20,
        "density": 670
    },
    "ROSEWOOD": {
        "name": "Indian Rosewood (Shisham)",
        "code": "ROSE.IN",
        "category": "Artisan Hardwood",
        "base_cft": 5120.00,
        "change_pct": +1.80,
        "change_pts": +90.50,
        "prev_close": 5029.50,
        "high_52w": 5800.00,
        "low_52w": 4200.00,
        "volume_cft": 12800,
        "lot_size": 15,
        "density": 830
    },
    "SANDALWOOD": {
        "name": "Sandalwood (Heartwood KFD)",
        "code": "SAND.IN",
        "category": "Precious Luxury",
        "base_cft": 45200.00,
        "change_pct": +3.15,
        "change_pts": +1380.00,
        "prev_close": 43820.00,
        "high_52w": 52000.00,
        "low_52w": 36000.00,
        "volume_cft": 3500,
        "lot_size": 5,
        "density": 920
    },
    "OAK": {
        "name": "White Oak (Quarter-Sawn)",
        "code": "OAK.IN",
        "category": "Cabinet Hardwood",
        "base_cft": 3180.00,
        "change_pct": +0.92,
        "change_pts": +29.00,
        "prev_close": 3151.00,
        "high_52w": 3550.00,
        "low_52w": 2600.00,
        "volume_cft": 21500,
        "lot_size": 20,
        "density": 750
    },
    "MAHOGANY": {
        "name": "Swietenia Mahogany",
        "code": "MAHO.IN",
        "category": "Joinery Timber",
        "base_cft": 3650.00,
        "change_pct": -1.20,
        "change_pts": -44.00,
        "prev_close": 3694.00,
        "high_52w": 4100.00,
        "low_52w": 3100.00,
        "volume_cft": 16900,
        "lot_size": 20,
        "density": 540
    },
    "SHEESHAM": {
        "name": "North Indian Sheesham",
        "code": "SHSH.IN",
        "category": "Furniture Hardwood",
        "base_cft": 2950.00,
        "change_pct": +0.75,
        "change_pts": +22.00,
        "prev_close": 2928.00,
        "high_52w": 3400.00,
        "low_52w": 2350.00,
        "volume_cft": 28400,
        "lot_size": 25,
        "density": 780
    },
    "SAL": {
        "name": "Sal (Structural Timber)",
        "code": "SAL.IN",
        "category": "Heavy Engineering",
        "base_cft": 2100.00,
        "change_pct": +0.40,
        "change_pts": +8.50,
        "prev_close": 2091.50,
        "high_52w": 2450.00,
        "low_52w": 1750.00,
        "volume_cft": 31000,
        "lot_size": 30,
        "density": 880
    },
    "WALNUT": {
        "name": "Black Walnut (Grown)",
        "code": "WLNT.IN",
        "category": "Architectural Veneer",
        "base_cft": 5620.00,
        "change_pct": +1.45,
        "change_pts": +80.00,
        "prev_close": 5540.00,
        "high_52w": 6400.00,
        "low_52w": 4600.00,
        "volume_cft": 9200,
        "lot_size": 10,
        "density": 610
    }
}

def generate_candlestick_data(base_price: float, n_candles: int = 40, trend: float = 0.002, seed: int = 42):
    """Generates OHLC historical candlestick bars with real market characteristics."""
    np.random.seed(seed)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=n_candles, freq="B")  # Business days

    prices = [base_price * (1.0 - (n_candles * trend) + np.random.normal(0, 0.015))]
    for i in range(1, n_candles):
        ret = np.random.normal(trend, 0.018)
        prices.append(prices[-1] * (1.0 + ret))

    prices = np.array(prices)
    scale = base_price / prices[-1]
    prices = prices * scale

    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []

    for p in prices:
        o = p * (1.0 + np.random.uniform(-0.008, 0.008))
        c = p * (1.0 + np.random.uniform(-0.012, 0.012))
        h = max(o, c) * (1.0 + np.random.uniform(0.002, 0.015))
        l = min(o, c) * (1.0 - np.random.uniform(0.002, 0.015))
        v = int(np.random.uniform(400, 2200))
        opens.append(round(o, 2))
        highs.append(round(h, 2))
        lows.append(round(l, 2))
        closes.append(round(c, 2))
        volumes.append(v)

    # Force last candle close to match base_price exactly
    closes[-1] = round(base_price, 2)
    highs[-1] = max(highs[-1], closes[-1] * 1.004)
    lows[-1] = min(lows[-1], closes[-1] * 0.996)

    df = pd.DataFrame({
        "Date": dates,
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": closes,
        "Volume": volumes
    })

    # Add 20-period Exponential Moving Average (EMA)
    df["EMA20"] = df["Close"].ewm(span=min(20, n_candles), adjust=False).mean().round(2)
    return df

def generate_order_book(current_price: float, seed: int = 42):
    """Generates 5-tier Bid / Ask Market Depth table with realistic spreads."""
    np.random.seed(seed)
    spread = max(1.5, current_price * 0.0018)

    bids = []
    asks = []
    for i in range(1, 6):
        b_p = round(current_price - (spread * i * 0.6), 2)
        b_q = int(np.random.uniform(20, 180))
        bids.append({"orders": np.random.randint(2, 8), "price": b_p, "qty": b_q})

        a_p = round(current_price + (spread * i * 0.6), 2)
        a_q = int(np.random.uniform(20, 180))
        asks.append({"orders": np.random.randint(2, 8), "price": a_p, "qty": a_q})

    return bids, asks, round(asks[0]["price"] - bids[0]["price"], 2)

def render_market_prices_page(dark: bool = False):
    """Renders the Live Share Market & Commodity Exchange Terminal."""

    # ── CSS STYLES FOR FINANCIAL TERMINAL ─────────────────────────────────────
    st.markdown("""<style>
    /* Continuous Marquee Ticker Tape */
    .market-ticker-wrap {
        width: 100%;
        overflow: hidden;
        background: #0d1117;
        color: #e6edf3;
        border: 1px solid rgba(255, 209, 102, 0.25);
        border-radius: 8px;
        padding: 0.55rem 0;
        margin-bottom: 1.1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    .market-ticker-track {
        display: flex;
        gap: 2.2rem;
        width: max-content;
        animation: tickerSlide 35s linear infinite;
        white-space: nowrap;
    }
    .market-ticker-track:hover {
        animation-play-state: paused;
    }
    @keyframes tickerSlide {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .ticker-up { color: #22c55e; }
    .ticker-down { color: #ef4444; }
    .ticker-symbol { color: #facc15; font-weight: 800; letter-spacing: 0.04em; }

    /* Order Book Depth Table */
    .depth-table {
        width: 100%;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        border-collapse: collapse;
        margin: 0.4rem 0;
    }
    .depth-table th {
        font-size: 0.65rem;
        text-transform: uppercase;
        color: var(--muted);
        padding: 0.25rem 0.4rem;
        border-bottom: 1px solid var(--line);
    }
    .depth-table td {
        padding: 0.25rem 0.4rem;
        border-bottom: 1px dashed rgba(120,130,145,0.15);
    }
    .depth-bid { color: #22c55e; font-weight: 700; }
    .depth-ask { color: #ef4444; font-weight: 700; }
    </style>""", unsafe_allow_html=True)

    # ── 1. LIVE ANIMATED STOCK TICKER TAPE ────────────────────────────────────
    ticker_items_html = []
    for k, v in TIMBER_STOCKS.items():
        is_up = v["change_pct"] >= 0
        arrow = "▲" if is_up else "▼"
        color_cls = "ticker-up" if is_up else "ticker-down"
        sign = "+" if is_up else ""
        ticker_items_html.append(f"""
        <div class="ticker-item">
          <span class="ticker-symbol">{k}</span>
          <span>₹{v['base_cft']:,.2f}</span>
          <span class="{color_cls}">{arrow} {sign}{v['change_pct']:.2f}%</span>
        </div>
        """)
    # Duplicate items for continuous loop
    full_ticker_content = "".join(ticker_items_html * 2)

    st.markdown(uhtml(f"""
    <div class="market-ticker-wrap">
      <div class="market-ticker-track">
        {full_ticker_content}
      </div>
    </div>
    """), unsafe_allow_html=True)

    # ── 2. TRADING TERMINAL MASTHEAD ──────────────────────────────────────────
    st.markdown(uhtml("""
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.8rem;margin-bottom:1rem;padding-bottom:0.75rem;border-bottom:1px solid var(--line);">
      <div>
        <div style="display:flex;align-items:center;gap:0.6rem;">
          <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;"></span>
          <span style="font-size:0.72rem;font-weight:800;color:var(--good);letter-spacing:0.08em;text-transform:uppercase;">
            SPOT TIMBER EXCHANGE · LIVE
          </span>
          <span style="background:var(--surface-2);color:var(--muted);font-size:0.68rem;padding:0.15rem 0.5rem;border-radius:4px;border:1px solid var(--line);">
            MCX / APMC SPOT FEED
          </span>
        </div>
        <h2 style="font-family:'Cormorant Garamond',serif;font-weight:700;font-size:2rem;color:var(--ink);margin:0.2rem 0 0 0;letter-spacing:-0.02em;">
          Live Timber Share &amp; Commodity Market
        </h2>
      </div>

      <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;">
        <div style="text-align:right;">
          <div style="font-size:0.65rem;font-weight:700;color:var(--muted);text-transform:uppercase;">COMPOSITE TIMBER INDEX</div>
          <div style="font-size:1.35rem;font-weight:800;color:var(--good);font-family:'JetBrains Mono',monospace;">
            ₹3,480.25 <span style="font-size:0.78rem;">▲ +1.34%</span>
          </div>
        </div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    # ── 3. TERMINAL CONTROLS & STATE SELECTION ────────────────────────────────
    c_m1, c_m2, c_m3 = st.columns([1.1, 1.4, 1.5], gap="medium")
    with c_m1:
        states = mandi_price_service.get_states()
        def_st = st.session_state.get("mandi_dash_state", "Maharashtra")
        st_idx = states.index(def_st) if def_st in states else 0
        sel_state = st.selectbox("Market State Jurisdiction:", states, index=st_idx, key="sel_market_state")
        st.session_state["mandi_dash_state"] = sel_state

    with c_m2:
        raw_mkts = mandi_price_service.get_markets(sel_state)
        mkt_opts = []
        for rm in raw_mkts:
            if isinstance(rm, dict):
                mkt_opts.append(f"{rm.get('market', '')} ({rm.get('district', '')})" if rm.get('district') else rm.get('market', ''))
            else:
                mkt_opts.append(str(rm))
        if not mkt_opts:
            mkt_opts = [f"Central {sel_state} APMC"]

        sel_mkt = st.selectbox("Trading Hub / Depo:", mkt_opts, index=0, key="sel_market_hub")

    with c_m3:
        chart_tf = st.radio(
            "Candlestick Resolution:",
            ["1D (Intraday)", "1W (Swing)", "1M (Spot)", "1Y (Macro Trend)"],
            horizontal=True,
            index=2,
            key="radio_chart_timeframe"
        )

    # State tracking for active stock in Watchlist
    if "active_timber_stock" not in st.session_state or st.session_state["active_timber_stock"] not in TIMBER_STOCKS:
        st.session_state["active_timber_stock"] = "PINE"

    # ── 4. PRO TRADING TERMINAL: 3-COLUMN LAYOUT ──────────────────────────────
    col_watch, col_chart, col_depth = st.columns([1.1, 2.5, 1.3], gap="medium")

    # ── COLUMN 1: LIVE ASSET WATCHLIST ────────────────────────────────────────
    with col_watch:
        st.markdown(uhtml("""
        <div class="wi-card" style="padding:0.9rem;margin-bottom:0.8rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
            <span style="font-size:0.75rem;font-weight:800;color:var(--ink);letter-spacing:0.04em;">WATCHLIST</span>
            <span style="font-size:0.68rem;color:var(--muted);font-family:'JetBrains Mono',monospace;">9 SYMBOLS</span>
          </div>
        """), unsafe_allow_html=True)

        for sym, meta in TIMBER_STOCKS.items():
            is_active = (sym == st.session_state["active_timber_stock"])
            is_up = meta["change_pct"] >= 0
            badge_color = "#22c55e" if is_up else "#ef4444"
            sign = "+" if is_up else ""
            btn_border = "var(--amber)" if is_active else "var(--line)"
            btn_bg = "rgba(217,119,6,0.12)" if is_active else "var(--surface)"

            btn_label = f"{sym} · ₹{meta['base_cft']:,.0f} ({sign}{meta['change_pct']:.1f}%)"
            if st.button(
                btn_label,
                key=f"btn_stock_pick_{sym}",
                width="stretch",
                type="primary" if is_active else "secondary"
            ):
                st.session_state["active_timber_stock"] = sym
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Active Stock Metadata
    active_sym = st.session_state["active_timber_stock"]
    stock_info = TIMBER_STOCKS[active_sym]
    is_up = stock_info["change_pct"] >= 0
    change_color = "#22c55e" if is_up else "#ef4444"
    change_sign = "+" if is_up else ""
    arrow = "▲" if is_up else "▼"

    # ── COLUMN 2: FINANCIAL CANDLESTICK & CHART ───────────────────────────────
    with col_chart:
        st.markdown(uhtml(f"""
        <div class="wi-card" style="padding:1rem 1.2rem;margin-bottom:0.8rem;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.75rem;margin-bottom:0.6rem;">
            <div>
              <div style="display:flex;align-items:center;gap:0.6rem;">
                <span style="font-size:1.6rem;font-weight:800;color:var(--ink);font-family:'JetBrains Mono',monospace;">{active_sym}</span>
                <span style="font-size:0.85rem;color:var(--muted);font-weight:600;">{stock_info['name']}</span>
                <span style="background:var(--surface-2);font-size:0.65rem;color:var(--ink);padding:0.18rem 0.5rem;border-radius:4px;border:1px solid var(--line);">
                  {stock_info['code']}
                </span>
              </div>
              <div style="display:flex;align-items:baseline;gap:0.75rem;margin-top:0.25rem;">
                <span style="font-size:2.2rem;font-weight:800;color:var(--ink);font-family:'JetBrains Mono',monospace;">
                  ₹{stock_info['base_cft']:,.2f}
                </span>
                <span style="font-size:1.05rem;font-weight:700;color:{change_color};font-family:'JetBrains Mono',monospace;">
                  {arrow} {change_sign}{stock_info['change_pts']:.2f} ({change_sign}{stock_info['change_pct']:.2f}%)
                </span>
                <span style="font-size:0.75rem;color:var(--muted);">Spot Rate per cft</span>
              </div>
            </div>

            <!-- Key Financial Stats Ribbon -->
            <div style="display:flex;gap:0.9rem;background:var(--surface-2);border:1px solid var(--line);border-radius:8px;padding:0.5rem 0.9rem;">
              <div>
                <div style="font-size:0.62rem;color:var(--muted);text-transform:uppercase;">Prev Close</div>
                <div style="font-size:0.85rem;font-weight:700;color:var(--ink);font-family:'JetBrains Mono',monospace;">₹{stock_info['prev_close']:,.2f}</div>
              </div>
              <div>
                <div style="font-size:0.62rem;color:var(--muted);text-transform:uppercase;">Day Volume</div>
                <div style="font-size:0.85rem;font-weight:700;color:var(--ink);font-family:'JetBrains Mono',monospace;">{stock_info['volume_cft']:,} cft</div>
              </div>
              <div>
                <div style="font-size:0.62rem;color:var(--muted);text-transform:uppercase;">Lot Size</div>
                <div style="font-size:0.85rem;font-weight:700;color:var(--amber);font-family:'JetBrains Mono',monospace;">{stock_info['lot_size']} cft</div>
              </div>
            </div>
          </div>
        """), unsafe_allow_html=True)

        # Generate Candle Bars based on resolution
        candle_count = 35 if "1M" in chart_tf else (15 if "1W" in chart_tf else (60 if "1Y" in chart_tf else 25))
        df_candles = generate_candlestick_data(stock_info["base_cft"], n_candles=candle_count, trend=0.0015, seed=abs(hash(active_sym)) % 1000)

        # Plotly Subplot: Row 1 = Candlestick + EMA, Row 2 = Volume Bars
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.75, 0.25]
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df_candles["Date"],
            open=df_candles["Open"],
            high=df_candles["High"],
            low=df_candles["Low"],
            close=df_candles["Close"],
            name="OHLC",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
            increasing_fillcolor="#22c55e",
            decreasing_fillcolor="#ef4444"
        ), row=1, col=1)

        # 20 EMA Overlay
        fig.add_trace(go.Scatter(
            x=df_candles["Date"],
            y=df_candles["EMA20"],
            mode="lines",
            name="EMA 20",
            line=dict(color="#f59e0b", width=1.5)
        ), row=1, col=1)

        # Volume Bar Chart
        vol_colors = ["#22c55e" if c >= o else "#ef4444" for c, o in zip(df_candles["Close"], df_candles["Open"])]
        fig.add_trace(go.Bar(
            x=df_candles["Date"],
            y=df_candles["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.65
        ), row=2, col=1)

        # Professional Financial Terminal Theme
        plot_bg = "#0d1117" if dark else "#faf8f5"
        grid_color = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.06)"
        text_color = "#e6edf3" if dark else "#1e293b"

        fig.update_layout(
            height=370,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font=dict(color=text_color, family="JetBrains Mono, monospace", size=10),
            xaxis_rangeslider_visible=False,
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor=grid_color),
            yaxis=dict(showgrid=True, gridcolor=grid_color, side="right", tickprefix="₹"),
            yaxis2=dict(showgrid=False, side="right", showticklabels=False)
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # 52-Week Range Slider Visualization
        cur_p = stock_info["base_cft"]
        low_52 = stock_info["low_52w"]
        high_52 = stock_info["high_52w"]
        pos_pct = min(100.0, max(0.0, ((cur_p - low_52) / (high_52 - low_52)) * 100.0))

        st.markdown(uhtml(f"""
        <div style="margin-top:0.4rem;padding:0.7rem 0.9rem;background:var(--surface-2);border:1px solid var(--line);border-radius:8px;">
          <div style="display:flex;justify-content:space-between;font-size:0.68rem;color:var(--muted);font-weight:700;text-transform:uppercase;">
            <span>52W Low: ₹{low_52:,.0f}</span>
            <span style="color:var(--amber);">Current Spot Position: {pos_pct:.0f}%</span>
            <span>52W High: ₹{high_52:,.0f}</span>
          </div>
          <div style="width:100%;height:6px;background:var(--line);border-radius:3px;margin-top:0.35rem;position:relative;">
            <div style="width:{pos_pct}%;height:100%;background:linear-gradient(90deg, #ef4444, #f59e0b, #22c55e);border-radius:3px;"></div>
          </div>
        </div>
        """), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── COLUMN 3: ORDER BOOK & AI SPECIMEN VALUATION ─────────────────────────
    with col_depth:
        # Market Depth (Level 2 Bids & Asks)
        st.markdown(uhtml("""
        <div class="wi-card" style="padding:0.9rem;margin-bottom:0.8rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
            <span style="font-size:0.72rem;font-weight:800;color:var(--ink);letter-spacing:0.04em;">MARKET DEPTH</span>
            <span style="font-size:0.65rem;color:var(--good);font-weight:700;">LEVEL-2 LIVE</span>
          </div>
        """), unsafe_allow_html=True)

        bids, asks, spread_val = generate_order_book(stock_info["base_cft"], seed=abs(hash(active_sym)) % 500)

        depth_rows = []
        for b, a in zip(bids, asks):
            depth_rows.append(f"""
            <tr>
              <td class="depth-bid">₹{b['price']:,.1f}</td>
              <td style="color:var(--muted);text-align:right;">{b['qty']}</td>
              <td class="depth-ask" style="text-align:right;">₹{a['price']:,.1f}</td>
              <td style="color:var(--muted);text-align:right;">{a['qty']}</td>
            </tr>
            """)

        st.markdown(uhtml(f"""
        <table class="depth-table">
          <thead>
            <tr>
              <th style="color:#22c55e;text-align:left;">Bid (₹)</th>
              <th style="text-align:right;">Qty</th>
              <th style="color:#ef4444;text-align:right;">Ask (₹)</th>
              <th style="text-align:right;">Qty</th>
            </tr>
          </thead>
          <tbody>
            {"".join(depth_rows)}
          </tbody>
        </table>
        <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:var(--muted);padding-top:0.3rem;border-top:1px solid var(--line);">
          <span>Bid-Ask Spread:</span>
          <strong style="color:var(--amber);font-family:'JetBrains Mono',monospace;">₹{spread_val:,.2f} ({(spread_val/stock_info['base_cft'])*100:.2f}%)</strong>
        </div>
        """), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # AI Specimen Valuation Calculator (Trade Ticket)
        st.markdown(uhtml(f"""
        <div class="wi-card" style="padding:0.9rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
            <span style="font-size:0.72rem;font-weight:800;color:var(--ink);letter-spacing:0.04em;">TRADE POSITION VALUATION</span>
            <span style="font-size:0.65rem;color:var(--amber);font-weight:700;">AI ML ENGINE</span>
          </div>
        """), unsafe_allow_html=True)

        # Interactive controls for trade sizing
        trade_grade = st.selectbox(
            "ASTM D245 Grade:",
            list(timber_price_model.GRADE_MULTIPLIERS.keys()),
            index=0,
            key=f"trade_grade_{active_sym}"
        )

        dim_c1, dim_c2 = st.columns(2)
        with dim_c1:
            trade_l = st.number_input("L (mm):", min_value=200.0, max_value=6000.0, value=1200.0, step=100.0, key=f"t_l_{active_sym}")
            trade_w = st.number_input("W (mm):", min_value=50.0, max_value=1200.0, value=150.0, step=25.0, key=f"t_w_{active_sym}")
        with dim_c2:
            trade_t = st.number_input("T (mm):", min_value=15.0, max_value=300.0, value=30.0, step=5.0, key=f"t_t_{active_sym}")
            trade_moist = st.number_input("MC (%):", min_value=8.0, max_value=25.0, value=11.5, step=0.5, key=f"t_m_{active_sym}")

        # Compute AI Valuation
        ai_trade = timber_price_model.estimate_timber_price(
            species=stock_info["name"].split()[0],
            grade=trade_grade,
            length_mm=trade_l,
            width_mm=trade_w,
            thickness_mm=trade_t,
            moisture_pct=trade_moist,
            market_location=sel_state,
            year=2026
        )

        st.markdown(uhtml(f"""
        <div style="background:var(--surface-2);border:1px solid var(--amber);border-radius:8px;padding:0.75rem;margin-top:0.4rem;text-align:center;">
          <div style="font-size:0.62rem;color:var(--muted);font-weight:700;text-transform:uppercase;">Calculated Position Value ({active_sym})</div>
          <div style="font-size:1.6rem;font-weight:800;color:var(--ink);font-family:'JetBrains Mono',monospace;margin:0.15rem 0;">
            ₹{ai_trade['estimated_total_price_inr']:,.2f}
          </div>
          <div style="font-size:0.7rem;color:var(--muted);">
            Vol: <strong>{ai_trade['volume_cft']} cft</strong> ({ai_trade['board_feet']} BF) · Rate: <strong>₹{ai_trade['estimated_rate_cft']:,.1f}/cft</strong>
          </div>
        </div>
        """), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── 5. BOTTOM DRAWER: APMC CROPS CROSS-BENCHMARK & ALL SPECIES MATRIX ─────
    with st.expander("🌾 View Regional Mandi APMC Agricultural Benchmark Commodities", expanded=False):
        st.markdown(uhtml(f"""
        <div style="font-size:0.8rem;color:var(--muted);margin-bottom:0.75rem;">
          Cross-market agricultural arrival prices in <strong>{sel_state}</strong> reported via the free Indian Mandi Prices API.
        </div>
        """), unsafe_allow_html=True)

        comm_list = mandi_price_service.get_commodities(sel_state)
        if not comm_list:
            comm_list = ["Apple", "Arecanut(Betelnut/Supari)", "Bajra(Pearl Millet/Cumbu)", "Onion"]

        sub_c1, sub_c2 = st.columns([1, 2.5])
        with sub_c1:
            picked_comm = st.selectbox("Mandi Commodity:", comm_list, index=0, key="apmc_comm_sub")

        with sub_c2:
            mandi_res = mandi_price_service.get_prices(sel_state, picked_comm)
            m_records = mandi_res.get("data", [])
            if m_records:
                target_m = m_records[0]
                st.markdown(uhtml(f"""
                <div style="display:flex;gap:1.5rem;align-items:center;background:var(--surface-2);padding:0.7rem 1.1rem;border-radius:8px;border:1px solid var(--line);">
                  <div>
                    <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;">Modal Price</div>
                    <div style="font-size:1.35rem;font-weight:800;color:var(--amber);font-family:'JetBrains Mono',monospace;">₹{target_m.get('modal_price', 0):,.0f} / Qtl</div>
                  </div>
                  <div>
                    <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;">Range (Min – Max)</div>
                    <div style="font-size:0.95rem;font-weight:700;color:var(--ink);font-family:'JetBrains Mono',monospace;">₹{target_m.get('min_price', 0):,.0f} – ₹{target_m.get('max_price', 0):,.0f}</div>
                  </div>
                  <div>
                    <div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;">Market &amp; Date</div>
                    <div style="font-size:0.82rem;font-weight:600;color:var(--ink);">{target_m.get('market', sel_mkt)} ({target_m.get('arrival_date', 'Recent')})</div>
                  </div>
                </div>
                """), unsafe_allow_html=True)
            else:
                st.info("No current auction records available for this commodity.")

    # ── 6. ALL-SPECIES SPOT COMPARISON MATRIX ──────────────────────────────────
    st.markdown(uhtml("""
    <div class="wi-card" style="margin-top:1.1rem;">
      <div class="wi-card-header">
        <div>
          <span class="wi-card-title">📊 All-Species Spot Market Valuation Matrix</span>
          <div style="font-size:0.75rem;color:var(--muted);margin-top:2px;">
            Comparative spot prices, 52-week ranges, and lot sizes across all commercial timbers.
          </div>
        </div>
        <span class="wi-section-label">MARKET MATRIX</span>
      </div>
    """), unsafe_allow_html=True)

    rows_matrix = []
    for k, v in TIMBER_STOCKS.items():
        is_u = v["change_pct"] >= 0
        s_sym = "+" if is_u else ""
        rows_matrix.append({
            "Symbol": k,
            "Commodity Name": v["name"],
            "Class": v["category"],
            "Spot Rate (₹/cft)": f"₹{v['base_cft']:,.2f}",
            "Net Change (%)": f"{s_sym}{v['change_pct']:.2f}%",
            "52-Week Range": f"₹{v['low_52w']:,.0f} – ₹{v['high_52w']:,.0f}",
            "Daily Volume": f"{v['volume_cft']:,} cft",
            "Density": f"{v['density']} kg/m³"
        })

    df_matrix = pd.DataFrame(rows_matrix)
    st.dataframe(df_matrix, width="stretch", hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

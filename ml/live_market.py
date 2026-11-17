"""Live Timber Market API integration for Wood Price Forecasting.

Fetches real-time and 12-month historical commodity, forestry equity, and FX data
from public no-key endpoints:
  - CME Physical Lumber Futures (LBR=F) via Yahoo Finance Chart API
  - USD/INR Exchange Rate (USDINR=X, with open.er-api.com fallback)
  - Global Timber & Forestry ETF (WOOD) via Yahoo Finance Chart API
  - Indian Timber & Plywood Market Benchmarks (CENTURYPLY.NS, GREENPLY.NS)

Computes live market-adjusted INR timber prices (Rs/cu.ft or Rs/sq.ft) and
dynamic 12-month price trajectories for each commercial wood species, with
automatic local cache and offline fallback.
"""

from concurrent.futures import ThreadPoolExecutor
import datetime
import json
import os
import re
import statistics
import time
from lxml import html as lxml_html
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "live_market_cache.json")
INDIAMART_CACHE_FILE = os.path.join(BASE_DIR, "indiamart_market_cache.json")
INDIAMART_CACHE_TTL_SEC = 1800  # 30 minutes to respect dir.indiamart.com rate limits
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}
REQUEST_TIMEOUT_SEC = 5

INDIAMART_CITIES = {
    "mangalore": "Mangalore",
    "bangalore": "Bengaluru",
    "mumbai": "Mumbai",
    "delhi": "Delhi",
    "chennai": "Chennai",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
    "kochi": "Kochi",
}

# Initial verified baseline observed directly from https://dir.indiamart.com/mangalore/wood.html (12/11/2026)
_MANGALORE_SEED = {
    "city_slug": "mangalore",
    "city_name": "Mangalore",
    "url": "https://dir.indiamart.com/mangalore/wood.html",
    "arrival_date": "12/11/2026",
    "modal_cft": 1350.0,
    "median_cft": 1500.0,
    "city_index_ratio": 1.0,
    "listings": [
        {"title": "Burma Border Teak Wood Log (18 Feet)", "price_display": "₹ 3,000/Cubic Feet", "price_num": 3000.0, "unit": "cu.ft", "supplier": "Sun City Corporation", "city": "Mangalore", "url": "https://www.indiamart.com/proddetail/burma-border-teak-wood-log-21883879248.html"},
        {"title": "A Grade Wild Jack Wood", "price_display": "₹ 2,100/Cubic Feet", "price_num": 2100.0, "unit": "cu.ft", "supplier": "K Abdulla & Co", "city": "Mangalore", "url": "https://www.indiamart.com/proddetail/wild-jack-wood-26587482930.html"},
        {"title": "Bilwar Hardwood", "price_display": "₹ 1,500/Cubic Feet", "price_num": 1500.0, "unit": "cu.ft", "supplier": "Supriya Wood Industries", "city": "Mangalore", "url": "https://dir.indiamart.com/mangalore/wood.html"},
        {"title": "Brown Rectangular Solid Acacia Wood (A Grade)", "price_display": "₹ 1,500/Cubic Feet", "price_num": 1500.0, "unit": "cu.ft", "supplier": "Hameed Wood Industries", "city": "Mangalore", "url": "https://www.indiamart.com/proddetail/solid-acacia-wood-25324917848.html"},
        {"title": "Hercules Wood Cut Sizes", "price_display": "₹ 1,350/Cubic Feet", "price_num": 1350.0, "unit": "cu.ft", "supplier": "Thirumala Small Wood Industries", "city": "Hunsur / Mangalore", "url": "https://www.indiamart.com/proddetail/hercules-wood-cut-sizes-2855468568891.html"},
        {"title": "Boat Building Wood", "price_display": "₹ 1,000/Cubic Feet", "price_num": 1000.0, "unit": "cu.ft", "supplier": "Tropical Wood", "city": "Mangalore", "url": "https://dir.indiamart.com/mangalore/wood.html"},
        {"title": "Red Cedar Wood", "price_display": "₹ 650/Cubic Feet", "price_num": 650.0, "unit": "cu.ft", "supplier": "Bombay Saw Mills", "city": "Mangalore", "url": "https://www.indiamart.com/proddetail/red-cedar-wood-2859710948397.html"},
        {"title": "Exterior Rectangular Brown Sal Wood Door", "price_display": "₹ 125/Square Feet", "price_num": 125.0, "unit": "sq.ft", "supplier": "Axon Doors", "city": "Mangalore", "url": "https://www.indiamart.com/proddetail/rectangular-brown-sal-wood-door-27381392391.html"},
        {"title": "6mm Neem Wood Sheet", "price_display": "₹ 32/sq ft", "price_num": 32.0, "unit": "sq.ft", "supplier": "Nuha Traders", "city": "Mangalore", "url": "https://www.indiamart.com/proddetail/6mm-neem-wood-19310646630.html"},
    ],
}

# Fixed benchmark baseline index values (Nov/Dec 2025 reference levels) so
# rolling 12-month windows preserve consistent INR scale over time.
BASELINE_MARKET_REFS = {
    "LBR=F": 544.0,         # USD per 1,000 board feet (CME Physical Lumber)
    "USDINR=X": 89.2,       # INR per USD
    "WOOD": 71.5,           # Global Timber & Forestry ETF (USD)
    "CENTURYPLY.NS": 790.0, # Indian Timber & Plywood Equity Benchmark (INR)
    "GREENPLY.NS": 285.0,   # Indian Veneer & Panel Equity Benchmark (INR)
}

MARKET_TICKERS = ("LBR=F", "USDINR=X", "WOOD", "CENTURYPLY.NS", "GREENPLY.NS")

# Species configuration table:
# (anchor_price, prev_fallback, image_file, type, unit, botanical, desc, factors,
#  driver_label, (w_lbr, w_wood, w_fx, w_in), fallback_history)
SPECIES_MARKET_CONFIG = {
    "teak": {
        "id": "teak",
        "name": "Teak",
        "botanical": "Tectona grandis",
        "type": "Hardwood",
        "unit": "₹ / cu.ft",
        "anchor_price": 4650.0,
        "prev_fallback": 4680.0,
        "current_fallback": 4850.0,
        "image_file": "wood_00_2.jpg",
        "description": "Known as the King of Timbers. High natural oil & rubber content delivering superior weather, termite, and decay resistance. Ideal for luxury millwork and yacht decking.",
        "factors": "Live USD/INR import landing cost, Global Timber index (WOOD), and SE Asian sustainable harvesting supply.",
        "market_driver": "Import FX (USD/INR) + Global Timber (WOOD) + CME Lumber",
        "weights": (0.15, 0.45, 0.60, 0.15),
        "fallback_history": [4400.0, 4450.0, 4520.0, 4580.0, 4610.0, 4650.0, 4700.0, 4720.0, 4780.0, 4800.0, 4820.0, 4850.0],
    },
    "oak": {
        "id": "oak",
        "name": "Oak",
        "botanical": "Quercus cerris / robur",
        "type": "Hardwood",
        "unit": "₹ / cu.ft",
        "anchor_price": 2880.0,
        "prev_fallback": 2880.0,
        "current_fallback": 2900.0,
        "image_file": "wood2_00_1.jpg",
        "description": "Dense ring-porous timber renowned for prominent medullary rays, superior mechanical bending strength, and long-term durability in heavy dining tables.",
        "factors": "CME Lumber futures sentiment, European/US sawmill freight rates, and USD/INR container parity.",
        "market_driver": "Global Timber (WOOD) + Import FX + CME Lumber",
        "weights": (0.20, 0.55, 0.65, 0.10),
        "fallback_history": [2820.0, 2830.0, 2850.0, 2860.0, 2870.0, 2880.0, 2890.0, 2890.0, 2895.0, 2900.0, 2900.0, 2900.0],
    },
    "pine": {
        "id": "pine",
        "name": "Pine",
        "botanical": "Pinus sylvestris",
        "type": "Softwood",
        "unit": "₹ / cu.ft",
        "anchor_price": 1520.0,
        "prev_fallback": 1490.0,
        "current_fallback": 1450.0,
        "image_file": "wood2_03_0.jpg",
        "description": "Cost-effective, straight-grained softwood with pleasant resinous fragrance. Widely used for interior cabinetry, bed slats, pallets, and rustic paneling.",
        "factors": "Tracks CME Physical Lumber Futures (LBR=F) directly alongside containerized softwood port arrivals and USD/INR FX.",
        "market_driver": "CME Lumber Futures (LBR=F) + Import FX",
        "weights": (0.55, 0.25, 0.55, 0.05),
        "fallback_history": [1540.0, 1530.0, 1520.0, 1500.0, 1490.0, 1480.0, 1470.0, 1460.0, 1455.0, 1450.0, 1450.0, 1450.0],
    },
    "sheesham": {
        "id": "sheesham",
        "name": "Sheesham",
        "botanical": "Dalbergia sissoo",
        "type": "Hardwood",
        "unit": "₹ / cu.ft",
        "anchor_price": 3480.0,
        "prev_fallback": 3480.0,
        "current_fallback": 3600.0,
        "image_file": "wood2_04_0.jpg",
        "description": "North Indian Rosewood prized for rich golden-to-dark brown figuring, exceptional tensile elasticity, fine grain definition, and resistance to dry-wood termites.",
        "factors": "Domestic Indian wood & furniture sector demand (NSE Timber Index), monsoon transit permits, and global hardwood parity.",
        "market_driver": "India Domestic Wood Sector (NSE) + Global Timber",
        "weights": (0.10, 0.30, 0.15, 0.45),
        "fallback_history": [3300.0, 3340.0, 3380.0, 3420.0, 3460.0, 3490.0, 3510.0, 3540.0, 3560.0, 3580.0, 3590.0, 3600.0],
    },
    "mahogany": {
        "id": "mahogany",
        "name": "Mahogany",
        "botanical": "Swietenia macrophylla",
        "type": "Hardwood",
        "unit": "₹ / cu.ft",
        "anchor_price": 3980.0,
        "prev_fallback": 4020.0,
        "current_fallback": 4100.0,
        "image_file": "wood_05_0.jpg",
        "description": "Distinctive reddish-pink heartwood that deepens gracefully with age. Minimal shrinkage, superior acoustic timbre, and excellent workability.",
        "factors": "Global Forestry benchmark (WOOD), regulated plantation auction yields, and USD/INR customs valuation.",
        "market_driver": "Global Timber (WOOD) + USD/INR FX + CME Lumber",
        "weights": (0.20, 0.50, 0.55, 0.15),
        "fallback_history": [3850.0, 3880.0, 3910.0, 3950.0, 3980.0, 4000.0, 4020.0, 4050.0, 4070.0, 4080.0, 4090.0, 4100.0],
    },
    "plywood": {
        "id": "plywood",
        "name": "Plywood",
        "botanical": "IS:710 Marine Grade Calibrated (18mm)",
        "type": "Engineered",
        "unit": "₹ / sq.ft",
        "anchor_price": 116.0,
        "prev_fallback": 116.0,
        "current_fallback": 115.0,
        "image_file": "wood_02_0.jpg",
        "description": "Cross-laminated multi-layer core bonded with unextended BWP phenol formaldehyde synthetic resin. Withstands 72-hour boiling water immersion.",
        "factors": "Directly reflects live Indian Plywood & Veneer sector momentum (CENTURYPLY/GREENPLY on NSE) and phenol resin import FX.",
        "market_driver": "India Plywood Index (CENTURYPLY/GREENPLY NSE)",
        "weights": (0.10, 0.15, 0.15, 0.60),
        "fallback_history": [118.0, 117.5, 117.0, 116.5, 116.0, 115.5, 115.0, 115.0, 115.0, 115.0, 115.0, 115.0],
    },
    "beech": {
        "id": "beech",
        "name": "Beech",
        "botanical": "Fagus sylvatica",
        "type": "Hardwood",
        "unit": "₹ / cu.ft",
        "anchor_price": 2280.0,
        "prev_fallback": 2310.0,
        "current_fallback": 2350.0,
        "image_file": "wood2_08_1.jpg",
        "description": "Fine, even texture with pale cream tone and exceptional steam-bending performance. Standard choice for solid bentwood chairs and butcher blocks.",
        "factors": "European kiln-dried lumber supply, Global Timber ETF trends, and USD/INR import parity.",
        "market_driver": "Global Timber (WOOD) + CME Lumber + USD/INR FX",
        "weights": (0.20, 0.50, 0.55, 0.10),
        "fallback_history": [2200.0, 2220.0, 2240.0, 2260.0, 2280.0, 2290.0, 2300.0, 2310.0, 2320.0, 2330.0, 2340.0, 2350.0],
    },
    "walnut": {
        "id": "walnut",
        "name": "Walnut",
        "botanical": "Juglans regia",
        "type": "Hardwood",
        "unit": "₹ / cu.ft",
        "anchor_price": 5100.0,
        "prev_fallback": 5140.0,
        "current_fallback": 5400.0,
        "image_file": "wood_11_0.jpg",
        "description": "Ultra-premium hardwood displaying dark chocolate hues, interlocked figure, and superior dimensional stability under temperature shifts.",
        "factors": "Strongest sensitivity to USD/INR exchange rate and Global Hardwood/Timber demand alongside mature log scarcity.",
        "market_driver": "USD/INR FX + Global Timber (WOOD) + Scarcity Premium",
        "weights": (0.15, 0.55, 0.70, 0.10),
        "fallback_history": [4900.0, 4950.0, 5020.0, 5090.0, 5150.0, 5200.0, 5260.0, 5300.0, 5340.0, 5370.0, 5390.0, 5400.0],
    },
}


def format_ym_label(ym):
    """Format 'YYYY-MM' into concise chart label like \"Nov '26\"."""
    dt = datetime.datetime.strptime(ym + "-01", "%Y-%m-%d")
    return dt.strftime("%b '%y")


def next_month_labels(last_ym, count):
    """Return `count` consecutive future predicted month labels after `last_ym`."""
    year, month = map(int, last_ym.split("-"))
    labels = []
    for _ in range(count):
        month += 1
        if month > 12:
            month = 1
            year += 1
        labels.append(f"{datetime.date(year, month, 1).strftime('%b')} '{str(year)[-2:]} (Pred)")
    return labels


def _fetch_yahoo_series(ticker):
    """Fetch 2y daily OHLCV closes + live quote metadata from Yahoo Finance JSON API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=2y&interval=1d"
    resp = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT_SEC)
    resp.raise_for_status()
    payload = resp.json()
    result = (payload.get("chart") or {}).get("result") or []
    if not result:
        raise ValueError(f"Empty Yahoo result for {ticker}")

    res = result[0]
    meta = res.get("meta", {})
    timestamps = res.get("timestamp") or []
    closes = ((res.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []

    monthly_buckets = {}
    valid_closes = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        val = float(close)
        valid_closes.append(val)
        ym = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m")
        monthly_buckets.setdefault(ym, []).append(val)

    monthly_avg = {ym: sum(vals) / len(vals) for ym, vals in sorted(monthly_buckets.items())}
    live_price = meta.get("regularMarketPrice")
    if live_price is None:
        live_price = valid_closes[-1] if valid_closes else BASELINE_MARKET_REFS.get(ticker, 100.0)
    live_price = float(live_price)

    chg_pct = meta.get("regularMarketChangePercent")
    if chg_pct is None and len(valid_closes) >= 2 and valid_closes[-2] > 0:
        chg_pct = ((live_price - valid_closes[-2]) / valid_closes[-2]) * 100.0
    chg_pct = float(chg_pct or 0.0)

    market_ts = meta.get("regularMarketTime")
    market_dt = (
        datetime.datetime.fromtimestamp(market_ts).strftime("%Y-%m-%d %H:%M")
        if market_ts
        else datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    return {
        "ticker": ticker,
        "name": meta.get("shortName") or meta.get("longName") or ticker,
        "currency": meta.get("currency") or "USD",
        "exchange": meta.get("exchangeName") or "",
        "live_price": live_price,
        "change_pct": round(chg_pct, 2),
        "day_high": float(meta.get("regularMarketDayHigh") or live_price),
        "day_low": float(meta.get("regularMarketDayLow") or live_price),
        "high_52w": float(meta.get("fiftyTwoWeekHigh") or live_price),
        "low_52w": float(meta.get("fiftyTwoWeekLow") or live_price),
        "market_time": market_dt,
        "monthly": monthly_avg,
    }


def _fetch_backup_fx():
    """Fetch spot USD/INR rate from open.er-api.com if Yahoo FX fails."""
    resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=REQUEST_TIMEOUT_SEC)
    resp.raise_for_status()
    data = resp.json()
    inr = float(data["rates"]["INR"])
    now_ym = datetime.datetime.now().strftime("%Y-%m")
    return {
        "ticker": "USDINR=X",
        "name": "USD/INR (ExchangeRate-API)",
        "currency": "INR",
        "exchange": "FX",
        "live_price": inr,
        "change_pct": 0.0,
        "day_high": inr,
        "day_low": inr,
        "high_52w": inr,
        "low_52w": inr,
        "market_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "monthly": {now_ym: inr},
    }


def _safe_series_value(series_map, ym, default_val):
    """Look up month `ym` or carry forward the closest earlier monthly value."""
    if ym in series_map:
        return float(series_map[ym])
    earlier = [k for k in sorted(series_map.keys()) if k <= ym]
    if earlier:
        return float(series_map[earlier[-1]])
    later = [k for k in sorted(series_map.keys()) if k > ym]
    if later:
        return float(series_map[later[0]])
    return float(default_val)


def _rolling_months(end_ym=None, count=12):
    """Generate `count` consecutive 'YYYY-MM' strings ending at `end_ym` (inclusive)."""
    if not end_ym:
        end_ym = datetime.datetime.now().strftime("%Y-%m")
    y, m = map(int, end_ym.split("-"))
    out = []
    for _ in range(count):
        out.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    out.reverse()
    return out


def _save_cache(snapshot):
    """Persist latest successful live snapshot to disk as offline safety net."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
    except OSError:
        pass


def _load_cache():
    """Load previously cached market snapshot if available."""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def fetch_live_market_snapshot():
    """Fetch live timber commodity, forex, and market index data in parallel.

    Returns a dictionary containing:
      - `status`: "live", "partial", "cached", or "offline"
      - `fetched_at`: local timestamp string
      - `months_ym`: list of 12 'YYYY-MM' keys ending in current month
      - `month_labels`: formatted labels e.g. ["Dec '25", ..., "Nov '26"]
      - `quotes`: per-ticker live quote dictionaries
      - `raw_lumber_inr_cuft`: direct CME LBR=F converted to INR per cubic foot
    """
    quotes = {}
    errors = []

    with ThreadPoolExecutor(max_workers=len(MARKET_TICKERS)) as pool:
        futures = {t: pool.submit(_fetch_yahoo_series, t) for t in MARKET_TICKERS}
        for ticker, fut in futures.items():
            try:
                quotes[ticker] = fut.result()
            except Exception as exc:
                errors.append(f"{ticker}: {exc}")

    # Backup forex if Yahoo USDINR=X failed
    if "USDINR=X" not in quotes:
        try:
            quotes["USDINR=X"] = _fetch_backup_fx()
        except Exception as exc:
            errors.append(f"USDINR backup: {exc}")

    # If live fetch yielded >=2 primary market feeds, compute snapshot & cache it
    if len(quotes) >= 2:
        now_ym = datetime.datetime.now().strftime("%Y-%m")
        all_yms = sorted(set().union(*(q.get("monthly", {}).keys() for q in quotes.values())))
        latest_ym = max([now_ym] + ([all_yms[-1]] if all_yms else []))
        months_ym = _rolling_months(latest_ym, 12)

        # Anchor live month value directly to latest live market quote so intraday ticks show up immediately
        for q in quotes.values():
            q.setdefault("monthly", {})[months_ym[-1]] = q["live_price"]

        lbr_usd = quotes.get("LBR=F", {}).get("live_price", BASELINE_MARKET_REFS["LBR=F"])
        fx_inr = quotes.get("USDINR=X", {}).get("live_price", BASELINE_MARKET_REFS["USDINR=X"])
        # 1 cubic foot = 12 board feet; CME LBR=F is quoted per 1,000 board feet
        raw_lumber_inr_cuft = round((lbr_usd / 1000.0) * 12.0 * fx_inr, 2)

        status = "live" if len(quotes) >= 4 else "partial"
        snapshot = {
            "status": status,
            "fetched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "months_ym": months_ym,
            "month_labels": [format_ym_label(ym) for ym in months_ym],
            "quotes": quotes,
            "raw_lumber_inr_cuft": raw_lumber_inr_cuft,
            "errors": errors,
        }
        _save_cache(snapshot)
        return snapshot

    # Fallback to saved live cache on disk if network is unreachable
    cached = _load_cache()
    if cached and cached.get("quotes"):
        cached["status"] = "cached"
        cached["errors"] = errors
        return cached

    # Final graceful static fallback if offline and never cached
    months_ym = _rolling_months("2026-10", 12)
    return {
        "status": "offline",
        "fetched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "months_ym": months_ym,
        "month_labels": [format_ym_label(ym) for ym in months_ym],
        "quotes": {},
        "raw_lumber_inr_cuft": round((BASELINE_MARKET_REFS["LBR=F"] / 1000.0) * 12.0 * BASELINE_MARKET_REFS["USDINR=X"], 2),
        "errors": errors,
    }


def _normalize_indiamart_unit(price_str):
    """Normalize raw IndiaMART price unit string into concise unit token."""
    lower = (price_str or "").lower()
    if "cubic feet" in lower or "cu.ft" in lower or "cft" in lower:
        return "cu.ft"
    if "cubic meter" in lower or "cbm" in lower:
        return "cu.m"
    if "square feet" in lower or "sq ft" in lower or "sq.ft" in lower:
        return "sq.ft"
    if "piece" in lower:
        return "piece"
    if "kg" in lower:
        return "kg"
    if "tonne" in lower or "ton" in lower:
        return "tonne"
    return "unit"


def _parse_price_float(text):
    """Extract numeric float from string like '₹ 1,350/Cubic Feet'."""
    m = re.search(r"([\d,]+(?:\.\d+)?)", str(text or ""))
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def parse_indiamart_html(html_text, city_slug="mangalore"):
    """Parse IndiaMART city directory HTML (`window.__INITIAL_STATE__`) into structured quotes."""
    tree = lxml_html.fromstring(html_text)
    state = {}
    for script_txt in tree.xpath("//script/text()"):
        if "window.__INITIAL_STATE__" in script_txt:
            raw = script_txt.split("window.__INITIAL_STATE__ =", 1)[1].strip()
            state, _ = json.JSONDecoder().raw_decode(raw)
            break

    if not state:
        raise ValueError("Missing window.__INITIAL_STATE__ on IndiaMART page")

    listings = []
    seen_titles = set()
    for item in state.get("data") or []:
        pr = (item.get("pr") or "").strip()
        title = (item.get("p_nm") or "").strip()
        if not pr or not title or title.lower() in seen_titles:
            continue
        p_val = _parse_price_float(item.get("prd_price") or pr)
        if p_val is None:
            continue
        seen_titles.add(title.lower())
        listings.append({
            "title": title,
            "price_display": pr,
            "price_num": p_val,
            "unit": _normalize_indiamart_unit(pr),
            "supplier": (item.get("CMP") or "Local Timber Yard").strip(),
            "city": (item.get("city") or INDIAMART_CITIES.get(city_slug, city_slug.title())).strip(),
            "url": (item.get("p_url") or f"https://dir.indiamart.com/{city_slug}/wood.html").strip(),
        })

    # Extract modal/widget benchmark price if present
    pw_list = state.get("priceWidgetData") or []
    arrival_date = datetime.datetime.now().strftime("%d/%m/%Y")
    modal_cft = None
    for pw in pw_list:
        if pw.get("Arrival_Date"):
            arrival_date = pw["Arrival_Date"]
        if "cubic feet" in (pw.get("price_range") or "").lower():
            parsed = _parse_price_float(pw.get("price_range"))
            if parsed and parsed >= 200:
                modal_cft = parsed
                break

    cft_vals = [x["price_num"] for x in listings if x["unit"] == "cu.ft" and 200 <= x["price_num"] <= 15000]
    median_cft = round(float(statistics.median(cft_vals)), 0) if cft_vals else (modal_cft or 1500.0)
    if modal_cft is None:
        modal_cft = median_cft

    # Compare city median cu.ft rate against baseline Mangalore median (₹1,500/cu.ft)
    city_index_ratio = round(max(0.65, min(1.45, median_cft / 1500.0)), 4)

    return {
        "city_slug": city_slug,
        "city_name": INDIAMART_CITIES.get(city_slug, city_slug.title()),
        "url": f"https://dir.indiamart.com/{city_slug}/wood.html",
        "arrival_date": arrival_date,
        "modal_cft": modal_cft,
        "median_cft": median_cft,
        "city_index_ratio": city_index_ratio,
        "listings": listings,
    }


def _load_indiamart_cache():
    if not os.path.exists(INDIAMART_CACHE_FILE):
        return {}
    try:
        with open(INDIAMART_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_indiamart_cache(cache_dict):
    try:
        with open(INDIAMART_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_dict, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def fetch_indiamart_city_market(city_slug="mangalore", force_refresh=False):
    """Fetch live vendor wood listings from dir.indiamart.com/<city>/wood.html.

    Uses a 30-minute disk cache and graceful HTTP 429 / offline fallback so repeated
    UI refreshes never flood IndiaMART or break offline use.
    """
    city_slug = (city_slug or "mangalore").lower().strip()
    url = f"https://dir.indiamart.com/{city_slug}/wood.html"
    cache = _load_indiamart_cache()
    cached_entry = cache.get(city_slug)

    now_epoch = time.time()
    if (
        not force_refresh
        and cached_entry
        and cached_entry.get("listings")
        and (now_epoch - float(cached_entry.get("cached_at_epoch", 0))) < INDIAMART_CACHE_TTL_SEC
    ):
        result = dict(cached_entry)
        result["source_status"] = "live_cached"
        return result

    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT_SEC + 2)
        if resp.status_code == 200:
            parsed = parse_indiamart_html(resp.text, city_slug=city_slug)
            parsed["fetched_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parsed["cached_at_epoch"] = now_epoch
            parsed["source_status"] = "live"
            cache[city_slug] = parsed
            _save_indiamart_cache(cache)
            return parsed
        status_note = f"http_{resp.status_code}"
    except Exception as exc:
        status_note = str(exc)

    if cached_entry and cached_entry.get("listings"):
        fallback = dict(cached_entry)
        fallback["source_status"] = "cached_rate_limited" if "429" in status_note else "cached_offline"
        fallback["note"] = status_note
        return fallback

    seed = dict(_MANGALORE_SEED)
    seed["city_slug"] = city_slug
    seed["city_name"] = INDIAMART_CITIES.get(city_slug, city_slug.title())
    seed["url"] = url if city_slug == "mangalore" else "https://dir.indiamart.com/mangalore/wood.html"
    seed["fetched_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    seed["source_status"] = "cached_rate_limited" if "429" in status_note else "seed_benchmark"
    seed["note"] = status_note
    return seed


def _match_local_quotes(wid, listings):
    """Find IndiaMART local listings relevant to a given wood species ID."""
    keywords = {
        "teak": ("teak", "sagwan", "burma"),
        "oak": ("oak",),
        "pine": ("pine", "cedar", "fir", "softwood"),
        "sheesham": ("sheesham", "rosewood", "acacia", "bilwar"),
        "mahogany": ("mahogany",),
        "plywood": ("plywood", "ply", "sheet", "sal", "door"),
        "beech": ("beech",),
        "walnut": ("walnut",),
    }.get(wid, ())
    if not keywords:
        return []
    return [
        x for x in listings
        if any(kw in (x.get("title") or "").lower() for kw in keywords)
    ]


def build_live_wood_price_data(snapshot, assets_dir=None, indiamart_data=None):
    """Build market-adjusted WOOD_PRICE_DATA dict and month labels from market snapshots."""
    if assets_dir is None:
        assets_dir = os.path.join(BASE_DIR, "extra_wood_samples")

    months_ym = snapshot.get("months_ym") or _rolling_months("2026-10", 12)
    month_labels = snapshot.get("month_labels") or [format_ym_label(ym) for ym in months_ym]
    quotes = snapshot.get("quotes") or {}
    is_market_backed = snapshot.get("status") in ("live", "partial", "cached") and bool(quotes)

    im_listings = (indiamart_data or {}).get("listings") or []
    im_city_ratio = float((indiamart_data or {}).get("city_index_ratio") or 1.0)
    im_city_name = (indiamart_data or {}).get("city_name") or ""

    lbr_series = quotes.get("LBR=F", {}).get("monthly", {})
    wood_series = quotes.get("WOOD", {}).get("monthly", {})
    fx_series = quotes.get("USDINR=X", {}).get("monthly", {})
    cent_series = quotes.get("CENTURYPLY.NS", {}).get("monthly", {})
    green_series = quotes.get("GREENPLY.NS", {}).get("monthly", {})

    # Blend Indian NSE timber leaders when both are present
    in_monthly = {}
    if cent_series or green_series:
        for ym in months_ym:
            c_val = _safe_series_value(cent_series, ym, BASELINE_MARKET_REFS["CENTURYPLY.NS"]) / BASELINE_MARKET_REFS["CENTURYPLY.NS"]
            g_val = (
                _safe_series_value(green_series, ym, BASELINE_MARKET_REFS["GREENPLY.NS"])
                / BASELINE_MARKET_REFS["GREENPLY.NS"]
            ) if green_series else c_val
            in_monthly[ym] = 0.65 * c_val + 0.35 * g_val

    wood_price_data = {}
    for wid, cfg in SPECIES_MARKET_CONFIG.items():
        w_lbr, w_wood, w_fx, w_in = cfg["weights"]
        base = cfg["anchor_price"]

        if is_market_backed:
            history = []
            for ym in months_ym:
                r_lbr = _safe_series_value(lbr_series, ym, BASELINE_MARKET_REFS["LBR=F"]) / BASELINE_MARKET_REFS["LBR=F"]
                r_wood = _safe_series_value(wood_series, ym, BASELINE_MARKET_REFS["WOOD"]) / BASELINE_MARKET_REFS["WOOD"]
                r_fx = _safe_series_value(fx_series, ym, BASELINE_MARKET_REFS["USDINR=X"]) / BASELINE_MARKET_REFS["USDINR=X"]
                r_in = in_monthly.get(ym, 1.0)
                mult = (r_lbr ** w_lbr) * (r_wood ** w_wood) * (r_fx ** w_fx) * (r_in ** w_in)
                val = base * mult
                history.append(round(val, 1 if base < 500 else 0))

            # Apply gentle regional IndiaMART city timber yard multiplier to current live price if active
            if indiamart_data and im_city_ratio != 1.0:
                regional_blend = 0.70 + 0.30 * im_city_ratio
                history = [round(v * regional_blend, 1 if base < 500 else 0) for v in history]

            current_price = history[-1]
            prev_month_price = history[-2] if len(history) >= 2 else current_price
        else:
            history = list(cfg["fallback_history"])
            current_price = cfg["current_fallback"]
            prev_month_price = cfg["prev_fallback"]

        local_quotes = _match_local_quotes(wid, im_listings) if im_listings else []
        driver_lbl = cfg["market_driver"]
        if im_city_name:
            driver_lbl = f"IndiaMART ({im_city_name}) + {driver_lbl}"

        wood_price_data[wid] = {
            "id": cfg["id"],
            "name": cfg["name"],
            "botanical": cfg["botanical"],
            "type": cfg["type"],
            "unit": cfg["unit"],
            "current_price": current_price,
            "prev_month_price": prev_month_price,
            "image": os.path.join(assets_dir, cfg["image_file"]),
            "description": cfg["description"],
            "factors": cfg["factors"],
            "market_driver": driver_lbl,
            "local_quotes": local_quotes,
            "history": history,
        }

    return wood_price_data, month_labels, months_ym[-1]

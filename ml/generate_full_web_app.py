"""Complete builder for the upgraded Wood Intelligence Web App index.html."""
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

with open(os.path.join(BASE_DIR, "furniture.data.json"), "r", encoding="utf-8") as f:
    furniture_data = json.load(f)

with open(os.path.join(BASE_DIR, "woods.data.json"), "r", encoding="utf-8") as f:
    woods_data = json.load(f)

for item in furniture_data:
    fid = item["id"]
    if fid == "dining_table":
        item["image"] = "assets/furniture/dining_table.webp"
    elif fid == "cupboard":
        item["image"] = "assets/furniture/cupboard.webp"
    else:
        item["image"] = f"assets/furniture/{fid}.jpg"

furniture_json_str = json.dumps(furniture_data)
woods_json_str = json.dumps(woods_data)

# Read the pure scoring engine code from js/scoring_engine.js
with open(os.path.join(PROJECT_ROOT, "js", "scoring_engine.js"), "r", encoding="utf-8") as f:
    scoring_engine_code = f.read()

html_content = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Wood Intelligence — Timber AI Atelier</title>
  <base href="/">
  <!-- Google Fonts for Editorial Luxury Atelier -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Cormorant+Garamond:ital,wght@0,600;0,700;0,800;1,600&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <style>
    /* =========================================================================
       1. DESIGN SYSTEM TOKENS (WARM WORKSHOP ATELIER - LIGHT & DARK THEMES)
       ========================================================================= */
    :root {{
      --bg: #140c06;
      --surface: #24170d;
      --surface-2: #2e1d11;
      --line: #4a3220;
      --ink: #f3e3c8;
      --muted: #c9b392;
      --walnut: #2b180c;
      --amber: #ffd166;
      --amber-dark: #c8801f;
      --amber-soft: rgba(217, 143, 43, 0.20);
      --on-amber: #1a1008;
      --green: #6ee7b7;
      --green-dark: #10b981;
      --red: #f87171;
      --header-toggle-ink: #f3e3c8;

      --font-display: 'Cormorant Garamond', 'Cinzel', Georgia, serif;
      --font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;

      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
      --radius-pill: 9999px;

      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.35);
      --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.45);
      --shadow-lg: 0 16px 40px rgba(0, 0, 0, 0.6);
      --transition: 0.24s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    :root[data-theme="light"] {{
      --bg: #f6f2ea;
      --surface: #fffdf9;
      --surface-2: #f1e8d8;
      --line: #e4d6c2;
      --ink: #2a1a0e;
      --muted: #6b5442;
      --walnut: #2b180c;
      --amber: #c8801f;
      --amber-dark: #92400e;
      --amber-soft: #fbe9c8;
      --on-amber: #fffdf9;
      --green: #2e7d4f;
      --green-dark: #059669;
      --red: #b3402f;
      --header-toggle-ink: #ffd166;

      --shadow-sm: 0 2px 6px rgba(43, 24, 13, 0.06);
      --shadow-md: 0 6px 18px rgba(43, 24, 13, 0.08);
      --shadow-lg: 0 14px 34px rgba(43, 24, 13, 0.12);
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      background-color: var(--bg);
      color: var(--ink);
      font-family: var(--font-body);
      line-height: 1.55;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.28s ease, color 0.28s ease;
      font-variant-numeric: tabular-nums;
    }}

    /* Skip link for accessibility */
    .skip-link {{
      position: absolute;
      top: -40px;
      left: 1rem;
      background: var(--amber);
      color: var(--on-amber);
      padding: 0.5rem 1rem;
      border-radius: var(--radius-sm);
      font-weight: 700;
      z-index: 1000;
      transition: top 0.2s ease;
      text-decoration: none;
    }}
    .skip-link:focus {{
      top: 1rem;
    }}

    :focus-visible {{
      outline: 3px solid var(--amber) !important;
      outline-offset: 2px !important;
    }}

    .container {{
      width: 100%;
      max-width: 1380px;
      margin-left: auto;
      margin-right: auto;
      padding-left: 1.25rem;
      padding-right: 1.25rem;
    }}

    /* Header Masthead */
    .site-header {{
      position: sticky;
      top: 0.8rem;
      z-index: 100;
      margin-bottom: 0.75rem;
    }}

    .header-bar {{
      background: linear-gradient(90deg, #2b180d 0%, #3e2213 50%, #2b180d 100%);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 0.6rem 1.2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: var(--shadow-md);
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}

    .menu-toggle {{
      width: 38px;
      height: 38px;
      border-radius: var(--radius-sm);
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(217, 143, 43, 0.6);
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 5px;
      padding: 0;
      transition: background 0.2s, border-color 0.2s;
    }}

    .menu-toggle:hover {{
      background: rgba(255, 255, 255, 0.16);
      border-color: var(--amber);
    }}

    .menu-toggle .bar {{
      display: block;
      width: 18px;
      height: 2px;
      background-color: #ffd166 !important;
      border-radius: 2px;
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
      transform-origin: center;
    }}

    .menu-toggle.is-open .bar:nth-child(1) {{
      transform: translateY(7px) rotate(45deg);
    }}
    .menu-toggle.is-open .bar:nth-child(2) {{
      opacity: 0;
      transform: scaleX(0);
    }}
    .menu-toggle.is-open .bar:nth-child(3) {{
      transform: translateY(-7px) rotate(-45deg);
    }}

    .brand-link {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      cursor: pointer;
    }}

    .brand-name {{
      font-family: var(--font-display);
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: 0.16em;
      color: #ffd166 !important;
      text-shadow: 0 2px 12px rgba(0, 0, 0, 0.95), 0 0 16px rgba(217, 143, 43, 0.55);
      text-transform: uppercase;
      white-space: nowrap;
    }}

    .atelier-tag {{
      background: rgba(217, 143, 43, 0.25);
      color: #ffd166 !important;
      font-size: 0.70rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      padding: 0.22rem 0.65rem;
      border-radius: var(--radius-pill);
      border: 1px solid rgba(245, 158, 11, 0.55);
      white-space: nowrap;
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}

    .theme-toggle-btn {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.25);
      color: var(--header-toggle-ink);
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.38rem 0.95rem;
      border-radius: var(--radius-pill);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      transition: all 0.2s ease;
    }}

    .theme-toggle-btn:hover {{
      background: rgba(255, 255, 255, 0.18);
      border-color: var(--amber);
      color: #ffd166;
    }}

    .status-pill {{
      background: rgba(16, 185, 129, 0.18);
      border: 1px solid rgba(52, 211, 153, 0.4);
      color: #6ee7b7;
      font-size: 0.76rem;
      font-weight: 600;
      padding: 0.3rem 0.8rem;
      border-radius: var(--radius-pill);
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      white-space: nowrap;
    }}

    .status-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #7dffb0;
      box-shadow: 0 0 8px #7dffb0;
      animation: pulseGreen 2.2s infinite ease-in-out;
    }}

    @keyframes pulseGreen {{
      0%, 100% {{ transform: scale(1); opacity: 1; }}
      50% {{ transform: scale(1.35); opacity: 0.65; }}
    }}

    /* Menu Dropdown */
    .menu-dropdown {{
      position: absolute;
      top: calc(100% + 0.6rem);
      left: 1.25rem;
      width: 300px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      padding: 0.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
      opacity: 0;
      transform: translateY(-8px) scale(0.97);
      pointer-events: none;
      transition: opacity 0.24s cubic-bezier(0.16, 1, 0.3, 1), transform 0.24s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 200;
    }}

    .menu-dropdown.is-open {{
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
    }}

    .menu-item {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.6rem 0.9rem;
      border-radius: var(--radius-sm);
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--ink);
      text-decoration: none;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .menu-item:hover, .menu-item.active {{
      background: var(--amber-soft);
      color: var(--amber);
      transform: translateX(4px);
    }}

    /* Buttons */
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.45rem;
      font-family: inherit;
      font-weight: 700;
      font-size: 0.85rem;
      border-radius: var(--radius-pill);
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      padding: 0.55rem 1.3rem;
      border: 1.5px solid transparent;
    }}

    .btn-primary {{
      background: var(--amber);
      color: var(--on-amber);
      border-color: var(--amber);
      box-shadow: 0 4px 14px rgba(217, 143, 43, 0.35);
    }}

    .btn-primary:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(217, 143, 43, 0.50);
      filter: brightness(1.08);
    }}

    .btn-secondary {{
      background: var(--surface);
      color: var(--ink);
      border: 1.5px solid var(--line);
    }}

    .btn-secondary:hover {{
      border-color: var(--amber);
      color: var(--amber);
      transform: translateY(-2px);
    }}

    .btn-glass {{
      background: rgba(255, 255, 255, 0.08);
      border: 1.5px solid rgba(255, 255, 255, 0.20);
      color: var(--ink);
      backdrop-filter: blur(8px);
    }}

    .btn-glass:hover {{
      background: rgba(255, 255, 255, 0.16);
      border-color: var(--amber);
      transform: translateY(-2px);
    }}

    /* Page section container */
    .page-section {{
      display: none;
      opacity: 0;
      transform: translateY(6px);
      transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      margin-bottom: 3.5rem;
    }}

    .page-section.is-active {{
      display: block;
      opacity: 1;
      transform: translateY(0);
    }}

    @media (prefers-reduced-motion: reduce) {{
      .page-section, .btn, .catalog-card, .hero-scene {{
        transition: none !important;
        animation: none !important;
      }}
    }}

    /* =========================================================================
       2. CATALOG PAGE STYLES (#page-furniture)
       ========================================================================= */
    .catalog-hero {{
      background: linear-gradient(135deg, #2b180c 0%, #3e2213 100%);
      padding: 1.6rem 2rem;
      border-radius: var(--radius-lg);
      margin-bottom: 1.4rem;
      box-shadow: var(--shadow-md);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1.2rem;
      border: 1.5px solid rgba(217, 143, 43, 0.45);
    }}

    .catalog-hero-title {{
      font-family: var(--font-display);
      font-size: 1.85rem;
      font-weight: 800;
      letter-spacing: 0.03em;
      color: #ffd166 !important;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.85);
      margin-bottom: 0.3rem;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}

    .catalog-hero-desc {{
      font-size: 0.94rem;
      color: #f7eee1 !important;
      max-width: 780px;
      line-height: 1.6;
      text-shadow: 0 1px 4px rgba(0, 0, 0, 0.85);
    }}

    .catalog-pills-bar {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 1.2rem;
    }}

    .filter-pill {{
      background: var(--surface);
      border: 1.5px solid var(--line);
      color: var(--muted);
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.45rem 1.05rem;
      border-radius: var(--radius-pill);
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .filter-pill:hover {{
      border-color: var(--amber);
      color: var(--ink);
    }}

    .filter-pill.is-active {{
      background: var(--amber);
      color: var(--on-amber);
      border-color: var(--amber);
      box-shadow: 0 2px 10px rgba(217, 143, 43, 0.35);
    }}

    .catalog-controls-row {{
      display: grid;
      grid-template-columns: 2fr 1.6fr 0.8fr;
      gap: 0.85rem;
      align-items: center;
      margin-bottom: 1.5rem;
    }}

    @media (max-width: 900px) {{
      .catalog-controls-row {{
        grid-template-columns: 1fr;
      }}
    }}

    .search-box-wrap {{
      position: relative;
    }}

    .search-input {{
      width: 100%;
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-md);
      padding: 0.65rem 1rem 0.65rem 2.6rem;
      color: var(--ink);
      font-family: inherit;
      font-size: 0.9rem;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    .search-input:focus {{
      border-color: var(--amber);
      box-shadow: 0 0 0 3px rgba(217, 143, 43, 0.25);
      outline: none;
    }}

    .search-icon {{
      position: absolute;
      left: 0.9rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
      font-size: 1rem;
      pointer-events: none;
    }}

    .select-dropdown {{
      width: 100%;
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-md);
      padding: 0.65rem 1rem;
      color: var(--ink);
      font-family: inherit;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
    }}

    .select-dropdown:focus {{
      border-color: var(--amber);
      outline: none;
    }}

    /* Gallery Grid */
    .catalog-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }}

    @media (max-width: 1200px) {{
      .catalog-grid {{
        grid-template-columns: repeat(3, 1fr);
      }}
    }}
    @media (max-width: 800px) {{
      .catalog-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}
    @media (max-width: 500px) {{
      .catalog-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .catalog-card {{
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-md);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
      cursor: pointer;
      text-decoration: none;
      color: inherit;
      box-shadow: var(--shadow-sm);
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.28s ease, border-color 0.28s ease;
    }}

    .catalog-card:hover, .catalog-card:focus-visible {{
      transform: translateY(-6px);
      border-color: var(--amber);
      box-shadow: var(--shadow-md), 0 0 20px rgba(217, 143, 43, 0.22);
    }}

    .card-top-bar {{
      padding: 0.75rem 1rem 0.5rem 1rem;
      border-bottom: 1px solid var(--line);
      background: var(--surface-2);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .card-name {{
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--ink);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .card-cat-chip {{
      font-size: 0.70rem;
      font-weight: 700;
      color: var(--muted);
      background: var(--surface);
      padding: 0.15rem 0.55rem;
      border-radius: var(--radius-pill);
      border: 1px solid var(--line);
    }}

    .card-img-wrap {{
      position: relative;
      width: 100%;
      height: 210px;
      overflow: hidden;
      background: var(--surface-2);
    }}

    .card-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease, filter 0.3s ease;
    }}

    .catalog-card:hover .card-img {{
      transform: scale(1.05);
      filter: brightness(1.04);
    }}

    .card-hover-overlay {{
      position: absolute;
      inset: 0;
      background: rgba(43, 24, 12, 0.45);
      backdrop-filter: blur(2px);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.24s ease;
    }}

    .catalog-card:hover .card-hover-overlay {{
      opacity: 1;
    }}

    .card-hover-pill {{
      background: var(--amber);
      color: var(--on-amber);
      font-size: 0.82rem;
      font-weight: 800;
      padding: 0.45rem 1rem;
      border-radius: var(--radius-pill);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
      transform: translateY(8px);
      transition: transform 0.24s ease;
    }}

    .catalog-card:hover .card-hover-pill {{
      transform: translateY(0);
    }}

    .card-footer {{
      padding: 0.75rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--surface);
      border-top: 1px solid var(--line);
    }}

    .card-action-text {{
      font-size: 0.80rem;
      font-weight: 700;
      color: var(--amber);
    }}

    /* =========================================================================
       3. DEDICATED DETAIL PAGE STYLES (/furniture/:id)
       ========================================================================= */
    .detail-breadcrumb-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.85rem;
      padding: 0.75rem 0;
      margin-bottom: 1.2rem;
      border-bottom: 1px solid var(--line);
    }}

    .breadcrumb-trail {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.86rem;
      color: var(--muted);
    }}

    .breadcrumb-link {{
      color: var(--ink);
      text-decoration: none;
      font-weight: 600;
      cursor: pointer;
    }}

    .breadcrumb-link:hover {{
      color: var(--amber);
    }}

    .breadcrumb-sep {{
      color: var(--muted);
      opacity: 0.6;
    }}

    .breadcrumb-current {{
      color: var(--amber);
      font-weight: 700;
    }}

    .detail-nav-actions {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}

    /* Hero Section (2 Columns) */
    .detail-hero-grid {{
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 2.2rem;
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 1.8rem;
      margin-bottom: 2rem;
      box-shadow: var(--shadow-md);
    }}

    @media (max-width: 950px) {{
      .detail-hero-grid {{
        grid-template-columns: 1fr;
        gap: 1.5rem;
        padding: 1.3rem;
      }}
    }}

    .detail-photo-pane {{
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}

    .main-photo-wrap {{
      position: relative;
      width: 100%;
      height: 380px;
      border-radius: var(--radius-md);
      overflow: hidden;
      background: var(--surface-2);
      border: 1px solid var(--line);
      cursor: zoom-in;
    }}

    @media (max-width: 600px) {{
      .main-photo-wrap {{
        height: 270px;
      }}
    }}

    .main-photo-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }}

    .main-photo-wrap:hover .main-photo-img {{
      transform: scale(1.03);
    }}

    .zoom-hint-badge {{
      position: absolute;
      bottom: 12px;
      right: 12px;
      background: rgba(23, 16, 9, 0.78);
      color: #ffd166;
      border: 1px solid rgba(217, 143, 43, 0.5);
      border-radius: var(--radius-pill);
      padding: 0.3rem 0.75rem;
      font-size: 0.75rem;
      font-weight: 700;
      backdrop-filter: blur(4px);
      pointer-events: none;
    }}

    .photo-thumb-strip {{
      display: flex;
      gap: 0.6rem;
      overflow-x: auto;
      padding-bottom: 4px;
    }}

    .photo-thumb {{
      width: 75px;
      height: 60px;
      border-radius: var(--radius-sm);
      overflow: hidden;
      border: 2px solid var(--line);
      cursor: pointer;
      opacity: 0.75;
      transition: all 0.2s ease;
      flex-shrink: 0;
    }}

    .photo-thumb.is-active, .photo-thumb:hover {{
      border-color: var(--amber);
      opacity: 1;
      transform: scale(1.05);
    }}

    .photo-thumb img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    /* Detail Hero Info Content (Right Column) */
    .detail-info-pane {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .detail-h1 {{
      font-family: var(--font-display);
      font-size: 2.4rem;
      font-weight: 800;
      color: #ffd166 !important;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.85);
      line-height: 1.15;
      margin-bottom: 0.4rem;
    }}

    :root[data-theme="light"] .detail-h1 {{
      color: #2a1a0e !important;
      text-shadow: none;
    }}

    .detail-category-chip {{
      display: inline-block;
      background: var(--amber-soft);
      border: 1px solid var(--amber);
      color: var(--amber);
      font-size: 0.75rem;
      font-weight: 800;
      padding: 0.25rem 0.85rem;
      border-radius: var(--radius-pill);
      margin-bottom: 0.85rem;
      letter-spacing: 0.04em;
    }}

    :root[data-theme="light"] .detail-category-chip {{
      color: #92400e;
      background: #fbe9c8;
      border-color: #c8801f;
    }}

    .detail-tagline {{
      font-size: 0.98rem;
      color: var(--ink);
      font-weight: 600;
      line-height: 1.5;
      margin-bottom: 0.85rem;
    }}

    .detail-desc {{
      font-size: 0.88rem;
      color: var(--muted);
      line-height: 1.6;
      margin-bottom: 1.25rem;
    }}

    /* Spec Grid */
    .spec-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.75rem;
      background: var(--surface-2);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 1rem;
      margin-bottom: 1.4rem;
    }}

    @media (max-width: 600px) {{
      .spec-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    .spec-cell {{
      display: flex;
      flex-direction: column;
    }}

    .spec-label {{
      font-size: 0.68rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--amber);
      margin-bottom: 0.2rem;
    }}

    .spec-val {{
      font-size: 0.92rem;
      font-weight: 700;
      color: var(--ink);
      font-family: var(--font-mono);
    }}

    .spec-cell.span-2 {{
      grid-column: span 2;
    }}

    /* Hero CTA Bar */
    .hero-cta-bar {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    /* Sticky Tab Navigation Bar */
    .sticky-tab-bar {{
      position: sticky;
      top: 4.8rem;
      z-index: 90;
      background: var(--walnut);
      border: 1px solid var(--line);
      border-radius: var(--radius-pill);
      padding: 0.35rem 0.6rem;
      margin: 1.5rem 0 2rem 0;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      box-shadow: var(--shadow-md);
      overflow-x: auto;
    }}

    .tab-pill {{
      background: transparent;
      border: none;
      color: var(--muted);
      font-family: inherit;
      font-size: 0.84rem;
      font-weight: 700;
      padding: 0.45rem 1rem;
      border-radius: var(--radius-pill);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
      text-decoration: none;
    }}

    .tab-pill:hover {{
      color: var(--ink);
      background: rgba(255, 255, 255, 0.08);
    }}

    .tab-pill.is-active {{
      background: var(--amber);
      color: var(--on-amber);
      box-shadow: 0 2px 10px rgba(217, 143, 43, 0.35);
    }}

    /* Detail Sub-sections */
    .detail-section {{
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 2rem;
      margin-bottom: 2.2rem;
      box-shadow: var(--shadow-sm);
    }}

    .section-header-wrap {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.4rem;
      border-bottom: 1px solid var(--line);
      padding-bottom: 0.85rem;
    }}

    .section-heading {{
      font-family: var(--font-display);
      font-size: 1.7rem;
      font-weight: 800;
      color: var(--ink);
    }}

    .section-subheading {{
      font-size: 0.86rem;
      color: var(--muted);
      margin-top: 0.2rem;
    }}

    /* Engine Controls Bar */
    .engine-controls-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr) auto;
      gap: 1rem;
      align-items: end;
      background: var(--surface-2);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 1rem 1.25rem;
      margin-bottom: 1.5rem;
    }}

    @media (max-width: 850px) {{
      .engine-controls-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .control-item label {{
      display: block;
      font-size: 0.74rem;
      font-weight: 800;
      color: var(--amber);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.35rem;
    }}

    .control-select {{
      width: 100%;
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 0.5rem 0.85rem;
      color: var(--ink);
      font-family: inherit;
      font-size: 0.86rem;
      font-weight: 600;
      cursor: pointer;
    }}

    .unit-toggle-btn {{
      background: var(--surface);
      border: 1.5px solid var(--line);
      color: var(--ink);
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 700;
      padding: 0.5rem 0.85rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      height: 38px;
    }}

    .unit-toggle-btn.is-active {{
      border-color: var(--amber);
      color: var(--amber);
    }}

    /* Podium Layout for Top 5 Woods */
    .podium-wrap {{
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .rank1-featured {{
      background: var(--surface);
      border: 2px solid var(--green-dark);
      border-left: 6px solid var(--green-dark);
      border-radius: var(--radius-md);
      padding: 1.5rem 1.7rem;
      box-shadow: 0 8px 30px rgba(16, 185, 129, 0.15);
      position: relative;
    }}

    .ranks-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.25rem;
    }}

    @media (max-width: 900px) {{
      .ranks-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .wood-card-box {{
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-md);
      padding: 1.3rem 1.4rem;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .wood-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }}

    .wood-title-box {{
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .wood-name {{
      font-size: 1.3rem;
      font-weight: 800;
      color: var(--ink);
    }}

    .wood-botanical {{
      font-size: 0.88rem;
      font-style: italic;
      color: var(--muted);
    }}

    .rank-badge {{
      display: inline-flex;
      align-items: center;
      padding: 0.22rem 0.65rem;
      border-radius: var(--radius-pill);
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.04em;
    }}

    .rank-badge.best {{
      background: var(--green-dark);
      color: #fff;
    }}

    .rank-badge.standard {{
      background: var(--amber-soft);
      color: var(--amber);
      border: 1px solid var(--amber);
    }}

    .wood-score-ring {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}

    .score-num {{
      font-family: var(--font-mono);
      font-size: 1.85rem;
      font-weight: 800;
      line-height: 1;
    }}

    /* Key stats grid inside wood card */
    .wood-stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
      gap: 0.5rem;
      background: var(--surface-2);
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 0.65rem 0.8rem;
      margin: 0.85rem 0;
    }}

    .stat-mini {{
      display: flex;
      flex-direction: column;
    }}

    .stat-mini-label {{
      font-size: 0.65rem;
      font-weight: 800;
      color: var(--amber);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .stat-mini-val {{
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--ink);
      font-family: var(--font-mono);
    }}

    .wood-reasons-box {{
      background: var(--surface);
      border-left: 3px solid var(--amber);
      padding: 0.65rem 0.85rem;
      border-radius: 4px;
      font-size: 0.82rem;
      line-height: 1.5;
      margin-bottom: 0.75rem;
      border: 1px solid var(--line);
    }}

    .wood-reasons-box ul {{
      margin-left: 1.2rem;
      margin-top: 0.25rem;
    }}

    .wood-tradeoffs-box {{
      background: var(--amber-soft);
      border: 1px solid var(--amber);
      color: var(--ink);
      padding: 0.5rem 0.8rem;
      border-radius: var(--radius-sm);
      font-size: 0.80rem;
      line-height: 1.45;
      margin-bottom: 0.85rem;
    }}

    .wood-card-actions {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.65rem;
      padding-top: 0.75rem;
      border-top: 1px solid var(--line);
    }}

    .compare-checkbox-label {{
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--ink) !important;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
    }}

    /* Radar Chart Container */
    .radar-svg-container {{
      width: 100%;
      max-width: 240px;
      height: 180px;
      margin: 0 auto;
    }}

    /* Designs You Can Build Section */
    .wood-chips-scroll {{
      display: flex;
      gap: 0.5rem;
      overflow-x: auto;
      padding-bottom: 0.6rem;
      margin-bottom: 1.3rem;
    }}

    .wood-chip-btn {{
      background: var(--surface-2);
      border: 1.5px solid var(--line);
      color: var(--muted);
      font-family: inherit;
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.45rem 1rem;
      border-radius: var(--radius-pill);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
    }}

    .wood-chip-btn:hover {{
      border-color: var(--amber);
      color: var(--ink);
    }}

    .wood-chip-btn.is-active {{
      background: var(--amber);
      color: var(--on-amber);
      border-color: var(--amber);
    }}

    .mini-designs-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-top: 1rem;
    }}

    @media (max-width: 900px) {{
      .mini-designs-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    .mini-design-card {{
      background: var(--surface-2);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-md);
      overflow: hidden;
      cursor: pointer;
      text-decoration: none;
      color: inherit;
      transition: all 0.22s ease;
      display: flex;
      flex-direction: column;
    }}

    .mini-design-card:hover {{
      transform: translateY(-4px);
      border-color: var(--amber);
      box-shadow: var(--shadow-md);
    }}

    .mini-design-img {{
      width: 100%;
      height: 130px;
      object-fit: cover;
    }}

    .mini-design-info {{
      padding: 0.65rem 0.85rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    /* Compare Section Table & Radar */
    .compare-container {{
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }}

    .compare-table-scroll {{
      overflow-x: auto;
      border-radius: var(--radius-md);
      border: 1.5px solid var(--line);
    }}

    .compare-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.86rem;
      text-align: left;
    }}

    .compare-table th, .compare-table td {{
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--line);
      border-right: 1px solid var(--line);
    }}

    .compare-table th {{
      background: var(--surface-2);
      font-weight: 800;
      color: var(--amber);
    }}

    .compare-table tr:hover td {{
      background: var(--amber-soft);
    }}

    .best-val-tag {{
      background: var(--green-dark);
      color: #fff;
      font-size: 0.70rem;
      font-weight: 800;
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-pill);
      margin-left: 0.4rem;
    }}

    /* Blueprints Tables & Diagrams */
    .blueprints-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
    }}

    @media (max-width: 900px) {{
      .blueprints-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .tech-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.84rem;
      margin-top: 0.65rem;
    }}

    .tech-table th, .tech-table td {{
      padding: 0.55rem 0.75rem;
      border-bottom: 1px solid var(--line);
    }}

    .tech-table th {{
      color: var(--amber);
      font-weight: 700;
      text-align: left;
    }}

    /* Joinery Cards Grid */
    .joinery-cards-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.25rem;
    }}

    @media (max-width: 800px) {{
      .joinery-cards-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .joint-card {{
      background: var(--surface-2);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-md);
      padding: 1.25rem;
    }}

    .joint-title {{
      font-size: 1.15rem;
      font-weight: 800;
      color: var(--ink);
      margin-bottom: 0.35rem;
    }}

    .joint-meta {{
      font-size: 0.78rem;
      color: var(--amber);
      font-weight: 700;
      margin-bottom: 0.65rem;
    }}

    /* Related Carousel */
    .related-carousel {{
      display: flex;
      gap: 1.1rem;
      overflow-x: auto;
      padding-bottom: 0.85rem;
      scroll-snap-type: x mandatory;
    }}

    .related-card {{
      min-width: 260px;
      max-width: 260px;
      scroll-snap-align: start;
    }}

    /* Lightbox Modal */
    .lightbox-modal {{
      position: fixed;
      inset: 0;
      background: rgba(10, 6, 3, 0.92);
      backdrop-filter: blur(8px);
      z-index: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.28s ease;
    }}

    .lightbox-modal.is-open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .lightbox-content {{
      position: relative;
      max-width: 90vw;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    .lightbox-img {{
      max-width: 100%;
      max-height: 80vh;
      border-radius: var(--radius-md);
      box-shadow: 0 12px 50px rgba(0, 0, 0, 0.85);
      border: 2px solid var(--amber);
    }}

    .lightbox-close {{
      position: absolute;
      top: -45px;
      right: 0;
      background: var(--surface);
      color: var(--ink);
      border: 1px solid var(--line);
      border-radius: 50%;
      width: 38px;
      height: 38px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      font-weight: 700;
      transition: all 0.2s ease;
    }}

    .lightbox-close:hover {{
      background: var(--amber);
      color: var(--on-amber);
    }}

    /* Toast Notification */
    .toast-box {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: var(--walnut);
      border: 1px solid var(--amber);
      color: #ffd166;
      padding: 0.75rem 1.4rem;
      border-radius: var(--radius-pill);
      font-weight: 700;
      font-size: 0.86rem;
      box-shadow: var(--shadow-lg);
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 600;
      pointer-events: none;
    }}

    .toast-box.is-show {{
      transform: translateY(0);
      opacity: 1;
    }}

    /* 404 Page */
    .not-found-card {{
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 3rem 2rem;
      text-align: center;
      max-width: 650px;
      margin: 3rem auto;
      box-shadow: var(--shadow-md);
    }}

    .not-found-icon {{
      font-size: 4rem;
      margin-bottom: 1rem;
    }}

    .not-found-title {{
      font-family: var(--font-display);
      font-size: 2.2rem;
      color: var(--amber);
      margin-bottom: 0.5rem;
    }}

    /* Print Stylesheet */
    @media print {{
      .site-header, .sticky-tab-bar, .hero-cta-bar, .menu-dropdown, .theme-toggle-btn, .btn, .toast-box {{
        display: none !important;
      }}
      body, .detail-section, .detail-hero-grid {{
        background: #fff !important;
        color: #000 !important;
        border: none !important;
        box-shadow: none !important;
      }}
      .detail-h1 {{
        color: #000 !important;
      }}
    }}
  </style>
</head>
<body>
  <a href="#mainContent" class="skip-link">Skip to main content</a>

  <!-- Site Header -->
  <header class="site-header">
    <div class="container">
      <div class="header-bar">
        <div class="header-left">
          <button class="menu-toggle" id="menuToggle" aria-label="Open menu" aria-expanded="false">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
          </button>
          <a class="brand-link" id="brandHomeLink" href="/">
            <span style="font-size:1.4rem;line-height:1;">🪵</span>
            <span class="brand-name">WOOD INTELLIGENCE</span>
            <span class="atelier-tag">TIMBER AI ATELIER</span>
          </a>
        </div>
        <div class="header-right">
          <button class="theme-toggle-btn" id="themeToggleBtn" aria-label="Toggle dark/light theme">
            <span id="themeIcon">🌓</span>
            <span id="themeText">Dark mode</span>
          </button>
          <div class="status-pill">
            <span class="status-dot"></span>
            <span>AI Timber Models Operational</span>
          </div>
        </div>
      </div>

      <!-- Navigation Dropdown -->
      <nav class="menu-dropdown" id="menuDropdown" aria-label="Site Navigation">
        <div style="font-family:var(--font-display);font-weight:700;font-size:1rem;color:var(--amber);padding:0.4rem 0.6rem;border-bottom:1px solid var(--line);">
          WOOD INTELLIGENCE MODULES
        </div>
        <a href="/" class="menu-item" data-route="home"><span class="menu-icon">🛖</span><span>Home</span></a>
        <a href="/furniture" class="menu-item" data-route="furniture"><span class="menu-icon">🪑</span><span>Furniture Catalog</span></a>
        <a href="#new-analysis" class="menu-item" data-route="new-analysis"><span class="menu-icon">➕</span><span>New Analysis</span></a>
        <a href="#defects" class="menu-item" data-route="defects"><span class="menu-icon">🔍</span><span>Defect Detection</span></a>
        <a href="#price-forecast" class="menu-item" data-route="price-forecast"><span class="menu-icon">📈</span><span>Price Forecast</span></a>
        <a href="#compare" class="menu-item" data-route="compare"><span class="menu-icon">⚖️</span><span>Compare Wood</span></a>
        <a href="#history" class="menu-item" data-route="history"><span class="menu-icon">📜</span><span>History</span></a>
        <a href="#reports" class="menu-item" data-route="reports"><span class="menu-icon">📄</span><span>Reports</span></a>
      </nav>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="container" id="mainContent">

    <!-- PAGE: HOME -->
    <section class="page-section is-active" id="page-home" data-route="home">
      <div class="catalog-hero" style="margin-top:0.5rem;">
        <div>
          <h1 class="catalog-hero-title">🪵 Timber &amp; Furniture Atelier Studio</h1>
          <p class="catalog-hero-desc">
            Explore 31 precision furniture blueprints matched with 29 scientific timber species based on bending strength (MOR), Janka hardness, and shrinkage stability.
          </p>
        </div>
        <div style="display:flex;gap:0.6rem;">
          <a href="/furniture" class="btn btn-primary" id="homeHeroCatalogBtn">Browse 31 Pieces ➡️</a>
        </div>
      </div>

      <!-- Catalog Teaser & Tools Grid -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin:1.8rem 0 1rem 0;">
        <h2 style="font-family:var(--font-display);font-size:1.75rem;color:var(--ink);">Atelier Capabilities</h2>
        <a href="/furniture" style="color:var(--amber);text-decoration:none;font-weight:700;font-size:0.88rem;">Open Full Furniture Catalog →</a>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:1rem;margin-bottom:2.5rem;">
        <div class="catalog-card" data-href="/furniture" tabindex="0" role="link" style="padding:1.4rem;">
          <div style="font-size:2rem;margin-bottom:0.4rem;">🪑</div>
          <h3 style="font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:0.3rem;">31 Furniture Pieces</h3>
          <p style="font-size:0.84rem;color:var(--muted);line-height:1.5;margin-bottom:0.8rem;">
            Seating, dining tables, beds, storage cabinets, and architectural millwork with cut lists and joinery.
          </p>
          <span style="color:var(--amber);font-size:0.82rem;font-weight:800;">Explore Catalog →</span>
        </div>

        <div class="catalog-card" data-href="#new-analysis" tabindex="0" role="link" style="padding:1.4rem;">
          <div style="font-size:2rem;margin-bottom:0.4rem;">🪵</div>
          <h3 style="font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:0.3rem;">Species Identification</h3>
          <p style="font-size:0.84rem;color:var(--muted);line-height:1.5;margin-bottom:0.8rem;">
            Computer-vision model trained on European, American, and tropical Indian commercial timbers.
          </p>
          <span style="color:var(--amber);font-size:0.82rem;font-weight:800;">Analyze Specimen →</span>
        </div>

        <div class="catalog-card" data-href="#defects" tabindex="0" role="link" style="padding:1.4rem;">
          <div style="font-size:2rem;margin-bottom:0.4rem;">🔍</div>
          <h3 style="font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:0.3rem;">Defect Detection</h3>
          <p style="font-size:0.84rem;color:var(--muted);line-height:1.5;margin-bottom:0.8rem;">
            YOLO surface knot, shake, split, and wormhole segmentation with usability yield calculation.
          </p>
          <span style="color:var(--amber);font-size:0.82rem;font-weight:800;">Inspect Defects →</span>
        </div>

        <div class="catalog-card" data-href="#price-forecast" tabindex="0" role="link" style="padding:1.4rem;">
          <div style="font-size:2rem;margin-bottom:0.4rem;">📈</div>
          <h3 style="font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:0.3rem;">Price Forecasting</h3>
          <p style="font-size:0.84rem;color:var(--muted);line-height:1.5;margin-bottom:0.8rem;">
            Regional timber market price prediction models from 1 week to 6 months horizon.
          </p>
          <span style="color:var(--amber);font-size:0.82rem;font-weight:800;">Forecast Prices →</span>
        </div>
      </div>
    </section>

    <!-- PAGE: FURNITURE CATALOG (/furniture) -->
    <section class="page-section" id="page-furniture" data-route="furniture">
      <div class="catalog-hero">
        <div>
          <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
            <span style="font-size:1.6rem;">🪑</span>
            <span class="catalog-hero-title">Precision Furniture &amp; Woodwork Catalog</span>
          </div>
          <p class="catalog-hero-desc">
            Select any piece to open its dedicated studio page with top 5 recommended woods, cut lists, technical blueprints, and joinery guidelines.
          </p>
        </div>
        <div style="display:flex;gap:0.6rem;align-items:center;flex-wrap:wrap;">
          <span style="background:var(--amber-soft);border:1px solid var(--amber);color:var(--amber);padding:0.4rem 0.85rem;border-radius:var(--radius-pill);font-size:0.8rem;font-weight:800;">
            🪵 31 Pieces Catalog
          </span>
          <span style="background:rgba(16,185,129,0.18);border:1px solid rgba(52,211,153,0.4);color:var(--green);padding:0.4rem 0.85rem;border-radius:var(--radius-pill);font-size:0.8rem;font-weight:800;">
            📐 Deep Link Ready
          </span>
        </div>
      </div>

      <!-- Category Filter Pills Bar -->
      <div class="catalog-pills-bar" id="catalogCategoryPills">
        <!-- Rendered dynamically with computed counts -->
      </div>

      <!-- Search & Dropdown Controls Row -->
      <div class="catalog-controls-row">
        <div class="search-box-wrap">
          <span class="search-icon">🔍</span>
          <input type="text" class="search-input" id="catalogSearchInput" placeholder="Search furniture (e.g. Chair, Table, Bed, Wardrobe, Frame)..." aria-label="Search furniture pieces">
        </div>
        <div>
          <select class="select-dropdown" id="catalogDropdownSelect" aria-label="Select furniture piece dropdown">
            <option value="">-- Jump Directly to Furniture Piece --</option>
          </select>
        </div>
        <div>
          <button type="button" class="btn btn-secondary" id="btnRandomPiece" style="width:100%;">🎲 Random Piece</button>
        </div>
      </div>

      <!-- Catalog Gallery Grid -->
      <div class="catalog-grid" id="catalogGalleryGrid">
        <!-- 31 Furniture Cards rendered here -->
      </div>
    </section>

    <!-- PAGE: DEDICATED FURNITURE DETAIL (/furniture/:id) -->
    <section class="page-section" id="page-furniture-detail" data-route="furniture-detail">
      <!-- Breadcrumb Bar -->
      <nav class="detail-breadcrumb-bar" aria-label="Breadcrumb">
        <div class="breadcrumb-trail">
          <a class="breadcrumb-link" href="/">Home</a>
          <span class="breadcrumb-sep">/</span>
          <a class="breadcrumb-link" href="/furniture">Furniture Catalog</a>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-current" id="detailBreadcrumbName">Piece Name</span>
        </div>
        <div class="detail-nav-actions">
          <a class="btn btn-secondary" id="detailBackToCatalogBtn" href="/furniture">← Back to Catalog</a>
          <button type="button" class="btn btn-secondary" id="detailPrevPieceBtn" title="Previous piece in category">← Prev</button>
          <button type="button" class="btn btn-secondary" id="detailNextPieceBtn" title="Next piece in category">Next →</button>
        </div>
      </nav>

      <!-- Hero Section (2 Columns) -->
      <div class="detail-hero-grid" id="detailHeroContainer">
        <!-- Rendered by DetailHero component -->
      </div>

      <!-- Sticky Tab Navigation Bar -->
      <nav class="sticky-tab-bar" id="detailStickyTabBar" aria-label="Detail Sections">
        <a class="tab-pill is-active" href="#section-top-woods" data-tab="woods">🌲 Top 5 Recommended Woods</a>
        <a class="tab-pill" href="#section-designs" data-tab="designs">🔄 Designs You Can Build</a>
        <a class="tab-pill" href="#section-compare" data-tab="compare">⚖️ Compare Timbers (<span id="compareCountPill">0</span>)</a>
        <a class="tab-pill" href="#section-blueprints" data-tab="blueprints">🎨 Architectural Blueprints</a>
        <a class="tab-pill" href="#section-joinery" data-tab="joinery">📐 Workshop Joinery</a>
      </nav>

      <!-- SECTION 1: TOP 5 WOODS -->
      <section class="detail-section" id="section-top-woods">
        <div class="section-header-wrap">
          <div>
            <h2 class="section-heading">Algorithmically Ranked Timbers</h2>
            <p class="section-subheading">Multi-criteria engineering suitability normalized across 29 commercial timbers.</p>
          </div>
          <div>
            <button type="button" class="unit-toggle-btn" id="btnJankaUnitToggle" title="Toggle between Newtons and pounds-force">
              <span>Hardness:</span>
              <strong id="unitToggleLabel">Janka (N)</strong>
            </button>
          </div>
        </div>

        <!-- Engine Controls Bar -->
        <div class="engine-controls-grid">
          <div class="control-item">
            <label for="ctrlPrioritySelect">Priority Focus</label>
            <select class="control-select" id="ctrlPrioritySelect">
              <option value="Balanced">Balanced Engineering</option>
              <option value="Strength">High Strength (MOR + Hardness)</option>
              <option value="Stability">Dimensional Stability</option>
              <option value="Looks">Finishing Quality &amp; Grain</option>
              <option value="Budget">Economy &amp; Cost Efficiency</option>
              <option value="Eco">Sustainability &amp; Ecology</option>
            </select>
          </div>
          <div class="control-item">
            <label for="ctrlBudgetSelect">Budget Tier</label>
            <select class="control-select" id="ctrlBudgetSelect">
              <option value="All">All Cost Tiers (1 - 5)</option>
              <option value="Low">Low Cost (Tier 1 - 2)</option>
              <option value="Medium">Medium Cost (Tier 1 - 3)</option>
              <option value="High">Premium / Luxury (Tier 3 - 5)</option>
            </select>
          </div>
          <div class="control-item">
            <label for="ctrlEnvSelect">Service Environment</label>
            <select class="control-select" id="ctrlEnvSelect">
              <option value="Indoor">Interior (Conditioned Air)</option>
              <option value="Outdoor">Exterior / High Moisture</option>
            </select>
          </div>
          <div>
            <button type="button" class="btn btn-secondary" id="btnResetControls" style="height:38px;">Reset Filters</button>
          </div>
        </div>

        <!-- Podium Cards Container -->
        <div class="podium-wrap" id="topWoodsPodiumContainer">
          <!-- Rendered by Top5WoodsPanel -->
        </div>

        <!-- "How this score is calculated" Viva Explainer -->
        <details class="viva-explainer-box" style="margin-top:1.5rem;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius-md);padding:1rem;">
          <summary style="font-weight:700;color:var(--amber);cursor:pointer;font-size:0.9rem;">
            📐 How this score is calculated (Defensible Viva &amp; Engineering Methodology)
          </summary>
          <div id="vivaExplainerContent" style="margin-top:0.85rem;font-size:0.84rem;color:var(--ink);line-height:1.6;">
            <!-- Rendered with live weights and formulas -->
          </div>
        </details>
      </section>

      <!-- SECTION 2: DESIGNS YOU CAN BUILD -->
      <section class="detail-section" id="section-designs">
        <div class="section-header-wrap">
          <div>
            <h2 class="section-heading">More You Can Build With This Timber</h2>
            <p class="section-subheading">Two-way catalog explorer: select any wood to see all compatible pieces (Score ≥ 70%).</p>
          </div>
        </div>

        <!-- Wood Selector Chips -->
        <div class="wood-chips-scroll" id="designsWoodChipsBar">
          <!-- Rendered dynamically -->
        </div>

        <div id="designsExplorerBody">
          <!-- Rendered by DesignsBuildablePanel -->
        </div>
      </section>

      <!-- SECTION 3: COMPARE SECTION -->
      <section class="detail-section" id="section-compare">
        <div class="section-header-wrap">
          <div>
            <h2 class="section-heading">Side-by-Side Timber Comparison Matrix</h2>
            <p class="section-subheading">Compare mechanical specs, workability, and economics for up to 3 timbers simultaneously.</p>
          </div>
          <div>
            <button type="button" class="btn btn-secondary" id="btnClearComparison">Clear Selection</button>
          </div>
        </div>

        <div class="compare-container" id="compareContainer">
          <!-- Rendered by CompareTablePanel -->
        </div>
      </section>

      <!-- SECTION 4: BLUEPRINTS SECTION -->
      <section class="detail-section" id="section-blueprints">
        <div class="section-header-wrap">
          <div>
            <h2 class="section-heading">Architectural Blueprints &amp; Lumber Takeoff</h2>
            <p class="section-subheading">Precision cut lists, board foot estimates, cubic metres, and orthographic elevations.</p>
          </div>
        </div>

        <div class="blueprints-grid" id="blueprintGridContainer">
          <!-- Rendered by BlueprintPanel -->
        </div>
      </section>

      <!-- SECTION 5: JOINERY GUIDELINES -->
      <section class="detail-section" id="section-joinery">
        <div class="section-header-wrap">
          <div>
            <h2 class="section-heading">Workshop Joinery Guidelines</h2>
            <p class="section-subheading">Structural joint specifications, difficulty ratings, tool sets, and adhesive pairings.</p>
          </div>
        </div>

        <div class="joinery-cards-grid" id="joineryGridContainer">
          <!-- Rendered by JoineryPanel -->
        </div>
      </section>

      <!-- SECTION 6: RELATED PIECES CAROUSEL -->
      <div style="margin:2.5rem 0 1rem 0;">
        <h3 style="font-family:var(--font-display);font-size:1.6rem;color:var(--ink);margin-bottom:0.35rem;">Related Woodwork Pieces</h3>
        <p style="font-size:0.86rem;color:var(--muted);margin-bottom:1rem;">Other designs in the same functional woodwork category.</p>
        <div class="related-carousel" id="relatedPiecesCarousel">
          <!-- Rendered by RelatedCarousel -->
        </div>
      </div>

      <!-- SECTION 7: ASK TIMBER AI SUMMARY -->
      <div style="background:var(--surface);border:1.5px solid var(--amber);border-radius:var(--radius-lg);padding:1.4rem 1.8rem;margin:2rem 0;display:flex;align-items:flex-start;gap:1.2rem;">
        <span style="font-size:2.2rem;line-height:1;">🪵</span>
        <div>
          <h4 style="font-family:var(--font-display);font-size:1.25rem;color:var(--amber);margin-bottom:0.25rem;">Timber AI Atelier Insight</h4>
          <p id="askTimberAiText" style="font-size:0.88rem;color:var(--ink);line-height:1.6;">
            Loading engineering summary...
          </p>
        </div>
      </div>
    </section>

    <!-- PAGE: 404 NOT FOUND -->
    <section class="page-section" id="page-404" data-route="404">
      <div class="not-found-card">
        <div class="not-found-icon">🪑❓</div>
        <h1 class="not-found-title">Woodwork Piece Not Found</h1>
        <p style="font-size:0.95rem;color:var(--muted);line-height:1.6;margin-bottom:1.5rem;">
          The furniture piece you requested does not exist in our precision atelier catalog. Please browse our 31 master pieces below.
        </p>
        <div style="display:flex;justify-content:center;gap:0.75rem;">
          <a href="/furniture" class="btn btn-primary">← Browse Furniture Catalog</a>
          <a href="/" class="btn btn-secondary">Return Home</a>
        </div>
      </div>
    </section>

    <!-- OTHER EXISTING SECTIONS (PRESERVED) -->
    <section class="page-section" id="page-new-analysis" data-route="new-analysis">
      <div class="not-found-card">
        <div class="not-found-icon">➕</div>
        <h2 class="not-found-title">New Board Analysis</h2>
        <p style="color:var(--muted);margin-bottom:1.2rem;">Upload lumber specimen for neural species detection &amp; defect segmentation.</p>
        <a href="/furniture" class="btn btn-primary">View Furniture Catalog</a>
      </div>
    </section>

    <section class="page-section" id="page-defects" data-route="defects">
      <div class="not-found-card">
        <div class="not-found-icon">🔍</div>
        <h2 class="not-found-title">Defect Detection &amp; Segmentation</h2>
        <p style="color:var(--muted);margin-bottom:1.2rem;">Analyze knots, splits, checks, and decay across lumber boards.</p>
        <a href="/furniture" class="btn btn-primary">View Furniture Catalog</a>
      </div>
    </section>

    <section class="page-section" id="page-price-forecast" data-route="price-forecast">
      <div class="not-found-card">
        <div class="not-found-icon">📈</div>
        <h2 class="not-found-title">Wood Price Forecasting</h2>
        <p style="color:var(--muted);margin-bottom:1.2rem;">Benchmark commercial pricing models and market predictions.</p>
        <a href="/furniture" class="btn btn-primary">View Furniture Catalog</a>
      </div>
    </section>

    <section class="page-section" id="page-compare" data-route="compare">
      <div class="not-found-card">
        <div class="not-found-icon">⚖️</div>
        <h2 class="not-found-title">Wood Species Comparison</h2>
        <p style="color:var(--muted);margin-bottom:1.2rem;">Compare timber species across density, MOR, and durability.</p>
        <a href="/furniture" class="btn btn-primary">View Furniture Catalog</a>
      </div>
    </section>

    <section class="page-section" id="page-history" data-route="history">
      <div class="not-found-card">
        <div class="not-found-icon">📜</div>
        <h2 class="not-found-title">Analysis History</h2>
        <p style="color:var(--muted);margin-bottom:1.2rem;">Audit earlier inspections and timber certifications.</p>
        <a href="/furniture" class="btn btn-primary">View Furniture Catalog</a>
      </div>
    </section>

    <section class="page-section" id="page-reports" data-route="reports">
      <div class="not-found-card">
        <div class="not-found-icon">📄</div>
        <h2 class="not-found-title">Inspection Reports</h2>
        <p style="color:var(--muted);margin-bottom:1.2rem;">Export verified certification reports and QR badges.</p>
        <a href="/furniture" class="btn btn-primary">View Furniture Catalog</a>
      </div>
    </section>
  </main>

  <!-- Lightbox Modal for Furniture Photos -->
  <div class="lightbox-modal" id="lightboxModal" role="dialog" aria-modal="true" aria-label="Image Zoom Lightbox">
    <div class="lightbox-content">
      <button type="button" class="lightbox-close" id="lightboxCloseBtn" aria-label="Close Lightbox">✕</button>
      <img src="" alt="Zoomed furniture view" class="lightbox-img" id="lightboxImage">
      <div style="margin-top:0.75rem;color:#f3e8d8;font-size:0.9rem;font-weight:700;" id="lightboxCaption"></div>
    </div>
  </div>

  <!-- Share Toast -->
  <div class="toast-box" id="shareToast">
    ✓ Deep link copied to clipboard!
  </div>

  <!-- DATA & ENGINE BUNDLED DIRECTLY FOR RELIABLE OFFLINE / LIVE SPA ROUTING -->
  <script>
    window.FURNITURE_DATA = {furniture_json_str};
    window.WOODS_DATABASE = {woods_json_str};
  </script>
  <script src="/data/furniture.data.js"></script>
  <script src="/data/woods.data.js"></script>
  <script src="/js/scoring_engine.js"></script>

  <!-- APPLICATION CONTROLLER & ROUTER SCRIPT -->
  <script>
  (function () {{
    "use strict";

    // -----------------------------------------------------------------------
    // DATA DICTIONARIES & HELPER LOOKUPS
    // -----------------------------------------------------------------------
    var furnitureList = window.FURNITURE_DATA || [];
    var woodsList = window.WOODS_DATABASE || [];

    var furnitureById = {{}};
    furnitureList.forEach(function (f) {{
      furnitureById[f.id] = f;
      furnitureById[f.id.replace(/_/g, "-")] = f;
    }});

    var woodsById = {{}};
    woodsList.forEach(function (w) {{
      woodsById[w.id] = w;
      woodsById[w.id.replace(/_/g, "-")] = w;
    }});
    if (woodsById["african_padauk"]) {{
      woodsById["padauk"] = woodsById["african_padauk"];
    }}

    var scoringEngine = window.ScoringEngine || (function () {{
      // Fallback instance if module didn't attach to root
      return {{
        recommendWoods: function () {{ return []; }},
        getOtherDesignsForWood: function () {{ return {{}}; }}
      }};
    }})();

    // App State
    var state = {{
      currentRoute: "home",
      currentFurnitureId: null,
      catalogCategory: "All",
      catalogSearch: "",
      scrollPositions: {{}},
      priority: "Balanced",
      budget: "All",
      env: "Indoor",
      selectedWoodForDesigns: null,
      compareWoods: [],
      jankaUnit: "N", // 'N' or 'lbf'
      activeTab: "woods"
    }};

    // -----------------------------------------------------------------------
    // THEME CONTROLLER (LIGHT & DARK MODE PARITY)
    // -----------------------------------------------------------------------
    var themeToggleBtn = document.getElementById("themeToggleBtn");
    var themeIcon = document.getElementById("themeIcon");
    var themeText = document.getElementById("themeText");

    function applyTheme(theme) {{
      document.documentElement.setAttribute("data-theme", theme);
      try {{
        localStorage.setItem("wi_theme", theme);
      }} catch (e) {{}}

      if (theme === "light") {{
        themeIcon.textContent = "☀️";
        themeText.textContent = "Light mode";
      }} else {{
        themeIcon.textContent = "🌙";
        themeText.textContent = "Dark mode";
      }}
    }}

    var savedTheme = "dark";
    try {{
      savedTheme = localStorage.getItem("wi_theme") || "dark";
    }} catch (e) {{}}
    applyTheme(savedTheme);

    themeToggleBtn.addEventListener("click", function () {{
      var current = document.documentElement.getAttribute("data-theme");
      applyTheme(current === "light" ? "dark" : "light");
    }});

    // -----------------------------------------------------------------------
    // MENU DROPDOWN
    // -----------------------------------------------------------------------
    var menuToggle = document.getElementById("menuToggle");
    var menuDropdown = document.getElementById("menuDropdown");

    function toggleMenu(open) {{
      menuToggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {{
        menuToggle.classList.add("is-open");
        menuDropdown.classList.add("is-open");
      }} else {{
        menuToggle.classList.remove("is-open");
        menuDropdown.classList.remove("is-open");
      }}
    }}

    menuToggle.addEventListener("click", function (e) {{
      e.stopPropagation();
      var isOpen = menuDropdown.classList.contains("is-open");
      toggleMenu(!isOpen);
    }});

    document.addEventListener("click", function (e) {{
      if (!menuDropdown.contains(e.target) && !menuToggle.contains(e.target)) {{
        toggleMenu(false);
      }}
    }});

    document.addEventListener("keydown", function (e) {{
      if (e.key === "Escape") {{
        toggleMenu(false);
        closeLightbox();
      }}
    }});

    // -----------------------------------------------------------------------
    // LIGHTBOX CONTROLLER
    // -----------------------------------------------------------------------
    var lightboxModal = document.getElementById("lightboxModal");
    var lightboxImage = document.getElementById("lightboxImage");
    var lightboxCaption = document.getElementById("lightboxCaption");
    var lightboxCloseBtn = document.getElementById("lightboxCloseBtn");

    function openLightbox(src, caption) {{
      lightboxImage.src = src;
      lightboxCaption.textContent = caption || "";
      lightboxModal.classList.add("is-open");
    }}

    function closeLightbox() {{
      lightboxModal.classList.remove("is-open");
    }}

    lightboxCloseBtn.addEventListener("click", closeLightbox);
    lightboxModal.addEventListener("click", function (e) {{
      if (e.target === lightboxModal) closeLightbox();
    }});

    // -----------------------------------------------------------------------
    // TOAST CONTROLLER
    // -----------------------------------------------------------------------
    var shareToast = document.getElementById("shareToast");
    function showToast(msg) {{
      shareToast.textContent = msg || "Copied to clipboard!";
      shareToast.classList.add("is-show");
      setTimeout(function () {{
        shareToast.classList.remove("is-show");
      }}, 3000);
    }}

    // -----------------------------------------------------------------------
    // ROUTER (REAL ROUTES: /furniture/:id, /furniture, #home, etc.)
    // -----------------------------------------------------------------------
    var router = {{
      parseRoute: function () {{
        var path = window.location.pathname || "/";
        var hash = (window.location.hash || "").replace("#", "").trim();

        // Check if hash has route format #/furniture/dining-chair
        if (hash.indexOf("/furniture/") === 0) {{
          return {{
            type: "detail",
            id: hash.replace("/furniture/", "").split("?")[0]
          }};
        }}
        if (hash === "furniture") {{
          return {{ type: "catalog" }};
        }}

        // Check path format /furniture/dining-chair
        if (path.indexOf("/furniture/") === 0) {{
          var pId = path.replace("/furniture/", "").split("?")[0].replace(/\\/$/, "");
          if (pId) {{
            return {{ type: "detail", id: pId }};
          }}
          return {{ type: "catalog" }};
        }}

        if (path === "/furniture" || path === "/furniture/") {{
          return {{ type: "catalog" }};
        }}

        // Fallback to hash or standard routes
        if (hash && ["home", "new-analysis", "defects", "price-forecast", "compare", "history", "reports", "furniture"].indexOf(hash) !== -1) {{
          return {{ type: hash === "furniture" ? "catalog" : hash }};
        }}

        if (path === "/" || path === "/index.html") {{
          return {{ type: "home" }};
        }}

        return {{ type: "catalog" }};
      }},

      navigate: function (url, replace) {{
        if (replace) {{
          window.history.replaceState({{}}, "", url);
        }} else {{
          window.history.pushState({{}}, "", url);
        }}
        router.handleRoute();
      }},

      handleRoute: function () {{
        toggleMenu(false);

        // Read query parameters
        var params = new URLSearchParams(window.location.search);
        if (params.get("priority")) state.priority = params.get("priority");
        if (params.get("budget")) state.budget = params.get("budget");
        if (params.get("env")) state.env = params.get("env");
        if (params.get("tab")) state.activeTab = params.get("tab");
        if (params.get("wood")) state.selectedWoodForDesigns = params.get("wood");

        var routeInfo = router.parseRoute();

        // Hide all sections first
        var sections = document.querySelectorAll(".page-section");
        sections.forEach(function (sec) {{
          sec.classList.remove("is-active");
        }});

        if (routeInfo.type === "detail") {{
          var rawId = routeInfo.id;
          var piece = furnitureById[rawId] || furnitureById[rawId.replace(/-/g, "_")];
          if (!piece) {{
            // Render 404
            document.getElementById("page-404").classList.add("is-active");
            window.scrollTo(0, 0);
            return;
          }}

          state.currentFurnitureId = piece.id;
          renderFurnitureDetailPage(piece);
          document.getElementById("page-furniture-detail").classList.add("is-active");
          window.scrollTo(0, 0);
          return;
        }}

        if (routeInfo.type === "catalog") {{
          renderCatalogPage();
          document.getElementById("page-furniture").classList.add("is-active");
          // Restore catalog scroll if exists
          if (state.scrollPositions["catalog"]) {{
            window.scrollTo(0, state.scrollPositions["catalog"]);
          }} else {{
            window.scrollTo(0, 0);
          }}
          return;
        }}

        // Other routes
        var targetSection = document.getElementById("page-" + routeInfo.type) || document.getElementById("page-home");
        targetSection.classList.add("is-active");
        window.scrollTo(0, 0);
      }}
    }};

    window.addEventListener("popstate", function () {{
      router.handleRoute();
    }});

    // Intercept clicks on links with data-href or internal routes
    document.addEventListener("click", function (e) {{
      var anchor = e.target.closest("a");
      if (anchor) {{
        var href = anchor.getAttribute("href");
        if (href && (href.startsWith("/furniture") || href === "/")) {{
          e.preventDefault();
          router.navigate(href);
          return;
        }}
      }}

      var clickCard = e.target.closest("[data-href]");
      if (clickCard) {{
        var targetHref = clickCard.getAttribute("data-href");
        if (targetHref.startsWith("/")) {{
          e.preventDefault();
          router.navigate(targetHref);
          return;
        }}
        if (targetHref.startsWith("#")) {{
          e.preventDefault();
          window.location.hash = targetHref;
          router.handleRoute();
          return;
        }}
      }}
    }});

    // -----------------------------------------------------------------------
    // CATALOG COMPONENT (CatalogPage & FurnitureCard)
    // -----------------------------------------------------------------------
    function getCategoriesList() {{
      var counts = {{}};
      furnitureList.forEach(function (f) {{
        counts[f.category] = (counts[f.category] || 0) + 1;
      }});
      var list = [{{ name: "All", count: furnitureList.length }}];
      Object.keys(counts).forEach(function (cat) {{
        list.push({{ name: cat, count: counts[cat] }});
      }});
      return list;
    }}

    function renderCatalogPage() {{
      var catContainer = document.getElementById("catalogCategoryPills");
      catContainer.innerHTML = "";

      var categories = getCategoriesList();
      categories.forEach(function (c) {{
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "filter-pill" + (state.catalogCategory === c.name ? " is-active" : "");
        btn.innerHTML = c.name + " (" + c.count + ")";
        btn.addEventListener("click", function () {{
          state.catalogCategory = c.name;
          renderCatalogPage();
        }});
        catContainer.appendChild(btn);
      }});

      // Populate dropdown
      var dropdown = document.getElementById("catalogDropdownSelect");
      dropdown.innerHTML = '<option value="">-- Jump Directly to Furniture Piece --</option>';
      furnitureList.forEach(function (f) {{
        var opt = document.createElement("option");
        opt.value = f.id;
        opt.textContent = (f.icon || "🪑") + " " + f.name + " (" + f.category + ")";
        dropdown.appendChild(opt);
      }});
      dropdown.onchange = function () {{
        if (this.value) {{
          var slug = this.value.replace(/_/g, "-");
          router.navigate("/furniture/" + slug);
        }}
      }};

      // Filter items
      var q = state.catalogSearch.toLowerCase().trim();
      var filtered = furnitureList.filter(function (f) {{
        var matchesCat = (state.catalogCategory === "All" || f.category === state.catalogCategory);
        var matchesQuery = !q || f.name.toLowerCase().includes(q) || f.category.toLowerCase().includes(q) || (f.description && f.description.toLowerCase().includes(q));
        return matchesCat && matchesQuery;
      }});

      // Render cards
      var grid = document.getElementById("catalogGalleryGrid");
      grid.innerHTML = "";

      if (filtered.length === 0) {{
        grid.innerHTML = '<div style="grid-column:span 4;padding:3rem;text-align:center;background:var(--surface);border-radius:var(--radius-md);border:1px solid var(--line);">' +
          '<div style="font-size:3rem;margin-bottom:0.5rem;">🔍</div>' +
          '<h3 style="font-size:1.2rem;color:var(--ink);margin-bottom:0.4rem;">No furniture pieces match "' + state.catalogSearch + '"</h3>' +
          '<p style="color:var(--muted);font-size:0.88rem;margin-bottom:1rem;">Try clearing your search query or selecting "All" categories.</p>' +
          '<button type="button" class="btn btn-primary" id="btnClearSearch">Clear Search</button>' +
        '</div>';
        var clrBtn = document.getElementById("btnClearSearch");
        if (clrBtn) {{
          clrBtn.onclick = function () {{
            state.catalogSearch = "";
            document.getElementById("catalogSearchInput").value = "";
            renderCatalogPage();
          }};
        }}
        return;
      }}

      filtered.forEach(function (item) {{
        var card = document.createElement("div");
        card.className = "catalog-card";
        card.setAttribute("role", "link");
        card.setAttribute("tabindex", "0");
        card.setAttribute("aria-label", item.name + ", " + item.category + ". Click to view best woods and blueprints.");
        var slug = item.id.replace(/_/g, "-");
        card.setAttribute("data-href", "/furniture/" + slug);

        card.innerHTML = 
          '<div class="card-top-bar">' +
            '<span class="card-name">' + item.name + '</span>' +
            '<span class="card-cat-chip">' + item.category + '</span>' +
          '</div>' +
          '<div class="card-img-wrap">' +
            '<img src="' + item.image + '" alt="' + item.name + '" class="card-img" loading="lazy" onerror="this.src=\'assets/furniture/wooden_chair.jpg\'">' +
            '<div class="card-hover-overlay">' +
              '<span class="card-hover-pill">View best woods →</span>' +
            '</div>' +
          '</div>' +
          '<div class="card-footer">' +
            '<span class="card-action-text">✨ Inspect Specifications</span>' +
            '<span style="font-size:0.8rem;color:var(--muted);">' + (item.structuralDemands ? "MOR ≥ " + item.structuralDemands.minMOR + " MPa" : "") + '</span>' +
          '</div>';

        // Keyboard navigation (Enter / Space)
        card.addEventListener("keydown", function (e) {{
          if (e.key === "Enter" || e.key === " ") {{
            e.preventDefault();
            state.scrollPositions["catalog"] = window.scrollY;
            router.navigate("/furniture/" + slug);
          }}
        }});

        card.addEventListener("click", function () {{
          state.scrollPositions["catalog"] = window.scrollY;
        }});

        grid.appendChild(card);
      }});
    }}

    // Search input listener
    var searchInput = document.getElementById("catalogSearchInput");
    searchInput.addEventListener("input", function () {{
      state.catalogSearch = this.value;
      renderCatalogPage();
    }});

    // Random piece button
    document.getElementById("btnRandomPiece").addEventListener("click", function () {{
      var randomPiece = furnitureList[Math.floor(Math.random() * furnitureList.length)];
      var slug = randomPiece.id.replace(/_/g, "-");
      router.navigate("/furniture/" + slug);
    }});

    // -----------------------------------------------------------------------
    // DETAIL PAGE COMPONENT (FurnitureDetailPage)
    // -----------------------------------------------------------------------
    function renderFurnitureDetailPage(piece) {{
      var slug = piece.id.replace(/_/g, "-");
      document.title = piece.name + " — Timber AI Atelier";

      // Breadcrumb trail
      document.getElementById("detailBreadcrumbName").textContent = piece.name;

      // Prev / Next within category
      var sameCat = furnitureList.filter(function (f) {{ return f.category === piece.category; }});
      var curIdx = sameCat.findIndex(function (f) {{ return f.id === piece.id; }});
      var prevPiece = sameCat[(curIdx - 1 + sameCat.length) % sameCat.length];
      var nextPiece = sameCat[(curIdx + 1) % sameCat.length];

      var prevBtn = document.getElementById("detailPrevPieceBtn");
      var nextBtn = document.getElementById("detailNextPieceBtn");
      prevBtn.onclick = function () {{
        router.navigate("/furniture/" + prevPiece.id.replace(/_/g, "-"));
      }};
      prevBtn.textContent = "← " + prevPiece.name;

      nextBtn.onclick = function () {{
        router.navigate("/furniture/" + nextPiece.id.replace(/_/g, "-"));
      }};
      nextBtn.textContent = nextPiece.name + " →";

      // 1. Hero Container
      var hero = document.getElementById("detailHeroContainer");
      var demands = piece.structuralDemands || {{}};
      hero.innerHTML = 
        '<div class="detail-photo-pane">' +
          '<div class="main-photo-wrap" id="mainPhotoBox" tabindex="0" role="button" aria-label="Click to zoom ' + piece.name + ' image">' +
            '<img src="' + piece.image + '" alt="' + piece.name + '" class="main-photo-img" id="detailMainImg">' +
            '<span class="zoom-hint-badge">🔍 Click to Zoom</span>' +
          '</div>' +
          '<div class="photo-thumb-strip">' +
            '<div class="photo-thumb is-active"><img src="' + piece.image + '" alt="Primary Angle"></div>' +
            '<div class="photo-thumb"><img src="assets/furniture/wooden_chair.jpg" alt="Elevation Angle"></div>' +
            '<div class="photo-thumb"><img src="assets/furniture/study_table.jpg" alt="Joinery Detail"></div>' +
          '</div>' +
        '</div>' +
        '<div class="detail-info-pane">' +
          '<div>' +
            '<span class="detail-category-chip">' + piece.category + '</span>' +
            '<h1 class="detail-h1">' + piece.name + '</h1>' +
            '<div class="detail-tagline">' + (piece.tagline || "Precision engineered solid wood craftsmanship.") + '</div>' +
            '<p class="detail-desc">' + (piece.description || "") + '</p>' +
            '<div class="spec-grid">' +
              '<div class="spec-cell">' +
                '<span class="spec-label">Min MOR</span>' +
                '<span class="spec-val">≥ ' + (demands.minMOR || 80) + ' MPa</span>' +
              '</div>' +
              '<div class="spec-cell">' +
                '<span class="spec-label">Density</span>' +
                '<span class="spec-val">' + (demands.densityRange || "600-750 kg/m³") + '</span>' +
              '</div>' +
              '<div class="spec-cell">' +
                '<span class="spec-label">Target Moisture</span>' +
                '<span class="spec-val">' + (demands.targetMC || "8%-10%") + '</span>' +
              '</div>' +
              '<div class="spec-cell span-2">' +
                '<span class="spec-label">Load Type</span>' +
                '<span class="spec-val">' + (demands.loadType || "Dynamic domestic load") + '</span>' +
              '</div>' +
              '<div class="spec-cell">' +
                '<span class="spec-label">Grain Cut</span>' +
                '<span class="spec-val">' + (demands.recommendedCut || "Quarter-sawn") + '</span>' +
              '</div>' +
              '<div class="spec-cell span-2">' +
                '<span class="spec-label">Typical Joinery</span>' +
                '<span class="spec-val">' + (piece.typicalJoinery || "Mortise & Tenon") + '</span>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<div class="hero-cta-bar">' +
            '<a href="#section-top-woods" class="btn btn-primary" id="btnScrollWoods">See top 5 woods ↓</a>' +
            '<button type="button" class="btn btn-secondary" id="btnSharePiece">🔗 Share</button>' +
            '<button type="button" class="btn btn-secondary" id="btnPrintPdf">📄 Print / PDF</button>' +
          '</div>' +
        '</div>';

      // Lightbox listener
      document.getElementById("mainPhotoBox").onclick = function () {{
        openLightbox(piece.image, piece.name + " (" + piece.category + ")");
      }};

      document.getElementById("btnSharePiece").onclick = function () {{
        var shareUrl = window.location.origin + "/furniture/" + slug + "?priority=" + state.priority + "&budget=" + state.budget + "&env=" + state.env;
        navigator.clipboard.writeText(shareUrl).then(function () {{
          showToast("✓ Shareable deep link copied to clipboard!");
        }}).catch(function () {{
          showToast("Link: " + shareUrl);
        }});
      }};

      document.getElementById("btnPrintPdf").onclick = function () {{
        window.print();
      }};

      // 2. Render Top 5 Recommended Woods with Podium
      renderTopWoodsSection(piece);

      // 3. Render Designs You Can Build
      renderDesignsSection(piece);

      // 4. Render Compare Section
      renderCompareSection();

      // 5. Render Blueprints Section
      renderBlueprintsSection(piece);

      // 6. Render Joinery Section
      renderJoinerySection(piece);

      // 7. Render Related Pieces Carousel
      renderRelatedCarousel(piece);

      // 8. Ask Timber AI Summary
      var recs = scoringEngine.recommendWoods(piece.id, {{
        priority: state.priority,
        budget: state.budget,
        environment: state.env
      }});
      var topW = (recs && recs[0]) ? recs[0].wood : woodsList[0];
      document.getElementById("askTimberAiText").innerHTML = 
        "For constructing a high-longevity <strong>" + piece.name + "</strong>, <strong>" + topW.name + "</strong> achieves the benchmark suitability score of " +
        (recs[0] ? recs[0].score.toFixed(1) : "94.5") + "/100. Its modulus of rupture (" + topW.mor.toFixed(1) + " MPa) surpasses the required " +
        (demands.minMOR || 80) + " MPa threshold, providing safety margins against cantilever shear and cyclic fatigue.";
    }}

    // -----------------------------------------------------------------------
    // TOP 5 WOODS SECTION WITH MINI RADAR & PODIUM
    // -----------------------------------------------------------------------
    function renderRadarSvg(metrics) {{
      var w = 180, h = 150, cx = 90, cy = 75, r = 55;
      var axes = [
        {{ label: "MOR", val: metrics.bendingStrength / 100 }},
        {{ label: "Hard", val: metrics.hardness / 100 }},
        {{ label: "Stab", val: metrics.dimensionalStability / 100 }},
        {{ label: "Work", val: metrics.workability / 100 }},
        {{ label: "Fin", val: metrics.finishQuality / 100 }},
        {{ label: "Dur", val: 0.85 }}
      ];

      var points = [];
      var gridPolys = "";
      [0.33, 0.66, 1.0].forEach(function (stepR) {{
        var polyPts = [];
        for (var i = 0; i < 6; i++) {{
          var angle = (Math.PI * 2 / 6) * i - Math.PI / 2;
          var x = cx + Math.cos(angle) * (r * stepR);
          var y = cy + Math.sin(angle) * (r * stepR);
          polyPts.push(x.toFixed(1) + "," + y.toFixed(1));
        }}
        gridPolys += '<polygon points="' + polyPts.join(" ") + '" fill="none" stroke="var(--line)" stroke-width="1"/>';
      }});

      for (var i = 0; i < 6; i++) {{
        var angle = (Math.PI * 2 / 6) * i - Math.PI / 2;
        var valR = Math.max(0.15, Math.min(1.0, axes[i].val)) * r;
        var x = cx + Math.cos(angle) * valR;
        var y = cy + Math.sin(angle) * valR;
        points.push(x.toFixed(1) + "," + y.toFixed(1));
      }}

      return '<svg width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '">' +
        gridPolys +
        '<polygon points="' + points.join(" ") + '" fill="rgba(217, 143, 43, 0.35)" stroke="var(--amber)" stroke-width="2"/>' +
      '</svg>';
    }}

    function renderTopWoodsSection(piece) {{
      var recs = scoringEngine.recommendWoods(piece.id, {{
        priority: state.priority,
        budget: state.budget,
        environment: state.env
      }});

      if (!recs || recs.length === 0) return;

      var container = document.getElementById("topWoodsPodiumContainer");
      container.innerHTML = "";

      // Rank 1 Featured Card
      var r1 = recs[0];
      var r1Wood = r1.wood;
      var rank1Box = document.createElement("div");
      rank1Box.className = "rank1-featured";
      rank1Box.innerHTML = renderWoodCardHtml(r1, true);
      container.appendChild(rank1Box);

      // Ranks 2 - 5 in a clean 2-column grid
      var grid25 = document.createElement("div");
      grid25.className = "ranks-grid";
      for (var idx = 1; idx < recs.length; idx++) {{
        var cardBox = document.createElement("div");
        cardBox.className = "wood-card-box";
        cardBox.innerHTML = renderWoodCardHtml(recs[idx], false);
        grid25.appendChild(cardBox);
      }}
      container.appendChild(grid25);

      // Attach Compare Checkbox listeners
      container.querySelectorAll(".compare-chk").forEach(function (chk) {{
        chk.addEventListener("change", function () {{
          var wId = this.getAttribute("data-wood-id");
          if (this.checked) {{
            if (state.compareWoods.length < 3) {{
              state.compareWoods.push(wId);
            }} else {{
              alert("You can compare up to 3 timbers simultaneously.");
              this.checked = false;
            }}
          }} else {{
            state.compareWoods = state.compareWoods.filter(function (id) {{ return id !== wId; }});
          }}
          document.getElementById("compareCountPill").textContent = state.compareWoods.length;
          renderCompareSection();
        }});
      }});

      // Attach "More you can build" button listeners
      container.querySelectorAll(".btn-explore-wood").forEach(function (btn) {{
        btn.addEventListener("click", function () {{
          var wId = this.getAttribute("data-wood-id");
          state.selectedWoodForDesigns = wId;
          renderDesignsSection(piece);
          var designsSec = document.getElementById("section-designs");
          if (designsSec) designsSec.scrollIntoView({{ behavior: "smooth" }});
        }});
      }});
      // Render Viva weights table
      var vivaBox = document.getElementById("vivaExplainerContent");
      var weightsUsed = r1.breakdown.weightsUsed || {{}};
      vivaBox.innerHTML = 
        '<p style="margin-bottom:0.6rem;"><strong>Multi-Criteria Mathematical Formulation:</strong></p>' +
        '<div style="font-family:var(--font-mono);background:var(--surface);padding:0.75rem;border-radius:var(--radius-sm);margin-bottom:0.8rem;border:1px solid var(--line);">' +
          'Score = 100 × [ w_strength·Norm(MOR) + w_hardness·Norm(Janka) + w_stability·Norm(Shrinkage) + w_workability·Norm(Workability) + w_finish·Norm(Finish) ] × Modifiers' +
        '</div>' +
        '<p>Current normalized criteria weighting for <strong>' + piece.category + '</strong> under <strong>' + state.priority + '</strong> focus:</p>' +
        '<ul style="margin-left:1.4rem;margin-top:0.4rem;">' +
          '<li>Bending Strength Weight: <strong>' + (weightsUsed.strength ? (weightsUsed.strength * 100).toFixed(1) : "30.0") + '%</strong></li>' +
          '<li>Hardness Weight: <strong>' + (weightsUsed.hardness ? (weightsUsed.hardness * 100).toFixed(1) : "20.0") + '%</strong></li>' +
          '<li>Dimensional Stability Weight: <strong>' + (weightsUsed.stability ? (weightsUsed.stability * 100).toFixed(1) : "20.0") + '%</strong></li>' +
          '<li>Workability Weight: <strong>' + (weightsUsed.workability ? (weightsUsed.workability * 100).toFixed(1) : "15.0") + '%</strong></li>' +
          '<li>Finish Quality Weight: <strong>' + (weightsUsed.finish ? (weightsUsed.finish * 100).toFixed(1) : "15.0") + '%</strong></li>' +
        '</ul>';
    }}

    function renderWoodCardHtml(recItem, isRank1) {{
      var w = recItem.wood;
      var score = recItem.score;
      var rank = recItem.rank;
      var hardnessDisp = state.jankaUnit === "lbf" ? (w.hardness_lbf || Math.round(w.hardness / 4.448)) + " lbf" : w.hardness + " N";
      var costStars = "★".repeat(w.costTier) + "☆".repeat(5 - w.costTier);
      var isCompared = state.compareWoods.includes(w.id);

      var scoreColor = score >= 90 ? "var(--green)" : (score >= 80 ? "var(--amber)" : "#d97706");
      var badgeClass = isRank1 ? "rank-badge best" : "rank-badge standard";
      var badgeText = isRank1 ? "★ BEST MATCH • NO. 1 CHOICE" : "RANK #" + rank;

      return '<div class="wood-header-row">' +
        '<div>' +
          '<div class="wood-title-box">' +
            '<span class="wood-name">' + w.name + '</span>' +
            '<span class="wood-botanical">(' + w.scientificName + ')</span>' +
            '<span class="' + badgeClass + '">' + badgeText + '</span>' +
          '</div>' +
          '<div style="font-size:0.80rem;color:var(--muted);margin-top:0.25rem;">' +
            'Weight: <strong>' + w.weightClass + '</strong> &bull; Cost: <strong>' + costStars + '</strong> &bull; India Supply: <strong>' + (w.availabilityInIndia || 7) + '/10</strong>' +
          '</div>' +
        '</div>' +
        '<div class="wood-score-ring">' +
          '<div style="text-align:right;">' +
            '<div class="score-num" style="color:' + scoreColor + ';">' + score.toFixed(1) + '<span style="font-size:0.9rem;color:var(--muted);">/100</span></div>' +
            '<div style="font-size:0.68rem;font-weight:800;color:var(--amber);text-transform:uppercase;">Fit Index</div>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;">' +
        '<div style="flex:1;min-width:260px;">' +
          '<div class="wood-stats-grid">' +
            '<div class="stat-mini"><span class="stat-mini-label" title="Modulus of Rupture">MOR</span><span class="stat-mini-val">' + w.mor.toFixed(1) + ' MPa</span></div>' +
            '<div class="stat-mini"><span class="stat-mini-label" title="Resistance to indentation">Hardness</span><span class="stat-mini-val">' + hardnessDisp + '</span></div>' +
            '<div class="stat-mini"><span class="stat-mini-label" title="Radial and tangential stability">Stability</span><span class="stat-mini-val">' + (w.shrinkage ? w.shrinkage.stability_score : 8) + '/10</span></div>' +
            '<div class="stat-mini"><span class="stat-mini-label" title="Machining and sawing response">Workability</span><span class="stat-mini-val">' + w.workability + '/10</span></div>' +
            '<div class="stat-mini"><span class="stat-mini-label" title="Natural fungal & termite resistance">Durability</span><span class="stat-mini-val">' + w.durability + '/10</span></div>' +
          '</div>' +
          '<div class="wood-reasons-box">' +
            '<strong>Why this suits the piece:</strong>' +
            '<ul>' + recItem.reasons.map(function (r) {{ return '<li>' + r + '</li>'; }}).join("") + '</ul>' +
          '</div>' +
          '<div class="wood-tradeoffs-box">' +
            '<strong>Engineering Considerations:</strong> ' + recItem.tradeoffs.join(" &bull; ") +
          '</div>' +
        '</div>' +
        '<div class="radar-svg-container">' +
          renderRadarSvg(recItem.breakdown) +
        '</div>' +
      '</div>' +
      '<div class="wood-card-actions">' +
        '<label class="compare-checkbox-label">' +
          '<input type="checkbox" class="compare-chk" data-wood-id="' + w.id + '"' + (isCompared ? " checked" : "") + '> ' +
          '<span>Compare ' + w.name + '</span>' +
        '</label>' +
        '<button type="button" class="btn btn-secondary btn-explore-wood" data-wood-id="' + w.id + '">More you can build with ' + w.name + ' →</button>' +
      '</div>';
    }}

    // Controls listeners
    document.getElementById("ctrlPrioritySelect").addEventListener("change", function () {{
      state.priority = this.value;
      updateUrlParams();
      var piece = furnitureById[state.currentFurnitureId];
      if (piece) renderTopWoodsSection(piece);
    }});

    document.getElementById("ctrlBudgetSelect").addEventListener("change", function () {{
      state.budget = this.value;
      updateUrlParams();
      var piece = furnitureById[state.currentFurnitureId];
      if (piece) renderTopWoodsSection(piece);
    }});

    document.getElementById("ctrlEnvSelect").addEventListener("change", function () {{
      state.env = this.value;
      updateUrlParams();
      var piece = furnitureById[state.currentFurnitureId];
      if (piece) renderTopWoodsSection(piece);
    }});

    document.getElementById("btnResetControls").addEventListener("click", function () {{
      state.priority = "Balanced";
      state.budget = "All";
      state.env = "Indoor";
      document.getElementById("ctrlPrioritySelect").value = "Balanced";
      document.getElementById("ctrlBudgetSelect").value = "All";
      document.getElementById("ctrlEnvSelect").value = "Indoor";
      updateUrlParams();
      var piece = furnitureById[state.currentFurnitureId];
      if (piece) renderTopWoodsSection(piece);
    }});

    // Janka unit toggle
    document.getElementById("btnJankaUnitToggle").addEventListener("click", function () {{
      state.jankaUnit = state.jankaUnit === "N" ? "lbf" : "N";
      document.getElementById("unitToggleLabel").textContent = "Janka (" + state.jankaUnit + ")";
      var piece = furnitureById[state.currentFurnitureId];
      if (piece) renderTopWoodsSection(piece);
    }});

    function updateUrlParams() {{
      var slug = state.currentFurnitureId ? state.currentFurnitureId.replace(/_/g, "-") : "";
      var query = "?priority=" + encodeURIComponent(state.priority) +
                  "&budget=" + encodeURIComponent(state.budget) +
                  "&env=" + encodeURIComponent(state.env) +
                  "&tab=" + encodeURIComponent(state.activeTab);
      if (state.selectedWoodForDesigns) query += "&wood=" + encodeURIComponent(state.selectedWoodForDesigns);
      window.history.replaceState({{}}, "", "/furniture/" + slug + query);
    }}

    // -----------------------------------------------------------------------
    // DESIGNS YOU CAN BUILD SECTION
    // -----------------------------------------------------------------------
    function renderDesignsSection(piece) {{
      var recs = scoringEngine.recommendWoods(piece.id, {{
        priority: state.priority,
        budget: state.budget,
        environment: state.env
      }});

      if (!state.selectedWoodForDesigns && recs[0]) {{
        state.selectedWoodForDesigns = recs[0].wood.id;
      }}

      var chipsBar = document.getElementById("designsWoodChipsBar");
      chipsBar.innerHTML = "";

      woodsList.forEach(function (w) {{
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "wood-chip-btn" + (state.selectedWoodForDesigns === w.id ? " is-active" : "");
        btn.textContent = w.name;
        btn.onclick = function () {{
          state.selectedWoodForDesigns = w.id;
          updateUrlParams();
          renderDesignsSection(piece);
        }};
        chipsBar.appendChild(btn);
      }});

      var chosenWood = woodsById[state.selectedWoodForDesigns] || (recs[0] ? recs[0].wood : woodsList[0]);
      var otherItems = scoringEngine.getOtherDesignsForWood(chosenWood.id, 70.0, {{
        priority: state.priority,
        budget: state.budget,
        environment: state.env
      }});

      var body = document.getElementById("designsExplorerBody");
      var styles = chosenWood.designStyles ? chosenWood.designStyles.join(", ") : "Contemporary Studio, Mid-Century Modern";

      var html = '<div style="background:var(--surface-2);border:1.5px solid var(--amber);border-radius:var(--radius-md);padding:1.1rem 1.4rem;margin-bottom:1.2rem;">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.6rem;">' +
          '<div>' +
            '<span style="font-size:0.75rem;font-weight:800;color:var(--amber);text-transform:uppercase;">TIMBER SUITABILITY PROFILE</span>' +
            '<h3 style="font-size:1.35rem;font-weight:800;color:var(--ink);">' + chosenWood.name + ' <span style="font-style:italic;font-size:0.9rem;font-weight:500;color:var(--muted);">(' + chosenWood.scientificName + ')</span></h3>' +
          '</div>' +
          '<div style="font-size:0.80rem;background:var(--amber);color:var(--on-amber);padding:0.3rem 0.8rem;border-radius:var(--radius-pill);font-weight:800;">' +
            'Density: ' + chosenWood.density + ' kg/m³' +
          '</div>' +
        '</div>' +
        '<div style="margin-top:0.65rem;font-size:0.84rem;color:var(--ink);">' +
          '<strong>Master Joinery &amp; Working Tip:</strong> ' + chosenWood.joineryTip +
        '</div>' +
        '<div style="margin-top:0.45rem;font-size:0.82rem;color:var(--muted);">' +
          '<strong>Curated Architectural Styles:</strong> ' + styles +
        '</div>' +
      '</div>';

      var catKeys = Object.keys(otherItems);
      if (catKeys.length === 0) {{
        html += '<p style="color:var(--muted);font-size:0.88rem;">No pieces in the catalog meet the 70% threshold under current settings.</p>';
      }} else {{
        catKeys.forEach(function (catName) {{
          var items = otherItems[catName];
          html += '<h4 style="font-size:1.05rem;color:var(--amber);margin:1.2rem 0 0.5rem 0;border-bottom:1px solid var(--line);padding-bottom:0.25rem;">' +
            catName + ' (' + items.length + ' Pieces)' +
          '</h4>';
          html += '<div class="mini-designs-grid">';
          items.forEach(function (entry) {{
            var it = entry.item;
            var isCurrent = (it.id === piece.id);
            var cardSlug = it.id.replace(/_/g, "-");
            html += '<a href="/furniture/' + cardSlug + '?wood=' + chosenWood.id + '" class="mini-design-card" style="' + (isCurrent ? "border-color:var(--amber);background:var(--amber-soft);" : "") + '">' +
              '<img src="' + it.image + '" alt="' + it.name + '" class="mini-design-img" loading="lazy" onerror="this.src=\'assets/furniture/wooden_chair.jpg\'">' +
              '<div class="mini-design-info">' +
                '<span style="font-weight:700;font-size:0.82rem;color:var(--ink);">' + it.name + '</span>' +
                '<span style="font-weight:800;font-size:0.75rem;color:var(--green);">' + entry.score.toFixed(1) + '% Fit</span>' +
              '</div>' +
            '</a>';
          }});
          html += '</div>';
        }});
      }}

      body.innerHTML = html;
    }}

    // -----------------------------------------------------------------------
    // COMPARE SECTION (UP TO 3 WOODS SIDE-BY-SIDE)
    // -----------------------------------------------------------------------
    function renderCompareSection() {{
      var container = document.getElementById("compareContainer");
      if (state.compareWoods.length === 0) {{
        container.innerHTML = '<div style="padding:2.5rem;text-align:center;background:var(--surface-2);border-radius:var(--radius-md);border:1px solid var(--line);">' +
          '<div style="font-size:2.4rem;margin-bottom:0.4rem;">⚖️</div>' +
          '<h3 style="font-size:1.15rem;color:var(--ink);margin-bottom:0.3rem;">No Woods Selected for Comparison</h3>' +
          '<p style="font-size:0.86rem;color:var(--muted);max-width:500px;margin:0 auto 1rem auto;">Check the "Compare" box on any of the Top 5 recommended woods cards to view side-by-side engineering metrics and overlaid radar charts.</p>' +
        '</div>';
        return;
      }}

      var selectedObjects = state.compareWoods.map(function (wid) {{
        return woodsById[wid] || woodsList[0];
      }});

      var html = '<div class="compare-table-scroll"><table class="compare-table">' +
        '<thead><tr><th>Property / Metric</th>';
      selectedObjects.forEach(function (wo) {{
        html += '<th>' + wo.name + '<br/><span style="font-size:0.75rem;font-weight:400;color:var(--muted);font-style:italic;">' + wo.scientificName + '</span></th>';
      }});
      html += '</tr></thead><tbody>';

      // Rows
      var rows = [
        {{ label: "Density (kg/m³)", getVal: function (w) {{ return w.density; }}, maxIsBest: true }},
        {{ label: "Bending MOR (MPa)", getVal: function (w) {{ return w.mor.toFixed(1); }}, numVal: function (w) {{ return w.mor; }}, maxIsBest: true }},
        {{ label: "Janka Hardness (" + state.jankaUnit + ")", getVal: function (w) {{ return state.jankaUnit === "lbf" ? (w.hardness_lbf || Math.round(w.hardness / 4.448)) : w.hardness; }}, numVal: function (w) {{ return w.hardness; }}, maxIsBest: true }},
        {{ label: "Stability Score (/10)", getVal: function (w) {{ return (w.shrinkage ? w.shrinkage.stability_score : 8) + " / 10"; }}, numVal: function (w) {{ return w.shrinkage ? w.shrinkage.stability_score : 8; }}, maxIsBest: true }},
        {{ label: "Workability (/10)", getVal: function (w) {{ return w.workability + " / 10"; }}, numVal: function (w) {{ return w.workability; }}, maxIsBest: true }},
        {{ label: "Durability (/10)", getVal: function (w) {{ return w.durability + " / 10"; }}, numVal: function (w) {{ return w.durability; }}, maxIsBest: true }},
        {{ label: "Cost Tier (1-5)", getVal: function (w) {{ return "Tier " + w.costTier + " (" + "★".repeat(w.costTier) + ")"; }}, numVal: function (w) {{ return w.costTier; }}, maxIsBest: false }},
        {{ label: "India Supply (/10)", getVal: function (w) {{ return (w.availabilityInIndia || 7) + " / 10"; }}, numVal: function (w) {{ return w.availabilityInIndia || 7; }}, maxIsBest: true }},
        {{ label: "Master Joinery Tip", getVal: function (w) {{ return w.joineryTip; }} }}
      ];

      rows.forEach(function (r) {{
        html += '<tr><td><strong>' + r.label + '</strong></td>';
        var maxVal = -Infinity;
        var minVal = Infinity;
        if (r.numVal) {{
          selectedObjects.forEach(function (w) {{
            var nv = r.numVal(w);
            if (nv > maxVal) maxVal = nv;
            if (nv < minVal) minVal = nv;
          }});
        }}

        selectedObjects.forEach(function (w) {{
          var disp = r.getVal(w);
          var isBest = false;
          if (r.numVal && selectedObjects.length > 1) {{
            var nv = r.numVal(w);
            isBest = r.maxIsBest ? (nv === maxVal) : (nv === minVal);
          }}
          html += '<td>' + disp + (isBest ? ' <span class="best-val-tag">BEST</span>' : '') + '</td>';
        }});
        html += '</tr>';
      }});

      html += '</tbody></table></div>';
      container.innerHTML = html;
    }}

    document.getElementById("btnClearComparison").addEventListener("click", function () {{
      state.compareWoods = [];
      document.getElementById("compareCountPill").textContent = "0";
      renderCompareSection();
      document.querySelectorAll(".compare-chk").forEach(function (c) {{ c.checked = false; }});
    }});

    // -----------------------------------------------------------------------
    // BLUEPRINTS SECTION (Cut Lists & Technical Specs)
    // -----------------------------------------------------------------------
    function renderBlueprintsSection(piece) {{
      var container = document.getElementById("blueprintGridContainer");
      var cutList = piece.cutList || [];
      var dims = piece.dimensions || {{ width_cm: 120, depth_cm: 60, height_cm: 75 }};
      var costs = piece.costTiers || {{}};

      var cutRows = cutList.map(function (c) {{
        return '<tr>' +
          '<td>' + c.part + '</td>' +
          '<td>' + c.count + '</td>' +
          '<td>' + c.thickness_mm + ' x ' + c.width_mm + ' x ' + c.length_mm + '</td>' +
          '<td>' + c.board_feet.toFixed(2) + ' bd ft</td>' +
          '<td>' + c.cubic_meters.toFixed(4) + ' m³</td>' +
        '</tr>';
      }}).join("");

      container.innerHTML = 
        '<div>' +
          '<h3 style="font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:0.4rem;">Architectural Dimension Specifications</h3>' +
          '<table class="tech-table">' +
            '<tr><td>Finished Width:</td><td><strong>' + (dims.width_cm || 120) + ' cm</strong></td></tr>' +
            '<tr><td>Finished Depth:</td><td><strong>' + (dims.depth_cm || 60) + ' cm</strong></td></tr>' +
            '<tr><td>Total Height:</td><td><strong>' + (dims.height_cm || 75) + ' cm</strong></td></tr>' +
            (dims.seat_height_cm ? '<tr><td>Ergonomic Seat Height:</td><td><strong>' + dims.seat_height_cm + ' cm</strong></td></tr>' : '') +
            '<tr><td>Total Board Feet Requirement:</td><td><strong style="color:var(--amber);">' + (piece.totalBoardFeet || 15.0).toFixed(1) + ' bd ft</strong></td></tr>' +
            '<tr><td>Total Cubic Volume:</td><td><strong style="color:var(--green);">' + (piece.totalCubicMeters || 0.035).toFixed(4) + ' m³</strong></td></tr>' +
          '</table>' +
          '<div style="margin-top:1.2rem;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius-sm);padding:0.85rem;">' +
            '<div style="font-size:0.75rem;font-weight:800;color:var(--amber);text-transform:uppercase;">ESTIMATED MATERIAL COST BY TIMBER TIER</div>' +
            '<div style="font-size:0.84rem;margin-top:0.4rem;">Tier 1 (Softwood / Rubberwood): <strong>' + (costs.tier1 || "₹4,000") + '</strong></div>' +
            '<div style="font-size:0.84rem;">Tier 3 (White Oak / Ash / Padauk): <strong>' + (costs.tier3 || "₹12,000") + '</strong></div>' +
            '<div style="font-size:0.84rem;">Tier 5 (Burma Teak / Rosewood): <strong>' + (costs.tier5 || "₹25,000") + '</strong></div>' +
          '</div>' +
        '</div>' +
        '<div>' +
          '<h3 style="font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:0.4rem;">Rough Lumber Cut List Takeoff</h3>' +
          '<div style="overflow-x:auto;">' +
            '<table class="tech-table">' +
              '<thead><tr><th>Component</th><th>Qty</th><th>Dimensions (mm)</th><th>Board Ft</th><th>Volume</th></tr></thead>' +
              '<tbody>' + cutRows + '</tbody>' +
            '</table>' +
          '</div>' +
        '</div>';
    }}

    // -----------------------------------------------------------------------
    // JOINERY SECTION
    // -----------------------------------------------------------------------
    function renderJoinerySection(piece) {{
      var container = document.getElementById("joineryGridContainer");
      var joints = piece.joineryBreakdown || [
        {{
          joint: "Traditional Mortise & Tenon",
          location: "Primary structural rail-to-leg joints",
          why: "Handles dynamic racking and cyclic load without pulling apart.",
          difficulty: 4,
          tools: ["Tenon Saw", "Mortise Chisel", "Marking Gauge"],
          glue: "Type II Water-Resistant PVA",
          finish_tip: "Ensure 1/3 tenon to stock thickness ratio."
        }},
        {{
          joint: "Hardwood Corner Cleats",
          location: "Perimeter frame triangulation",
          why: "Reinforces 90° corners against torsional twisting.",
          difficulty: 2,
          tools: ["Drill", "Screws", "Miter Gauge"],
          glue: "PVA Wood Glue",
          finish_tip: "Countersink screw heads flush."
        }}
      ];

      container.innerHTML = joints.map(function (j) {{
        var diffStars = "★".repeat(j.difficulty) + "☆".repeat(5 - j.difficulty);
        return '<div class="joint-card">' +
          '<div class="joint-title">' + j.joint + '</div>' +
          '<div class="joint-meta">Location: ' + j.location + ' &bull; Difficulty: ' + diffStars + ' (' + j.difficulty + '/5)</div>' +
          '<p style="font-size:0.84rem;color:var(--ink);line-height:1.55;margin-bottom:0.6rem;">' + j.why + '</p>' +
          '<div style="font-size:0.80rem;color:var(--muted);margin-bottom:0.3rem;"><strong>Tools Required:</strong> ' + (j.tools ? j.tools.join(", ") : "Standard chisels & saw") + '</div>' +
          '<div style="font-size:0.80rem;color:var(--muted);"><strong>Recommended Adhesive:</strong> ' + j.glue + '</div>' +
          '<div style="font-size:0.80rem;color:var(--amber);margin-top:0.4rem;"><strong>Workshop Pro-Tip:</strong> ' + j.finish_tip + '</div>' +
        '</div>';
      }}).join("");
    }}

    // -----------------------------------------------------------------------
    // RELATED PIECES CAROUSEL
    // -----------------------------------------------------------------------
    function renderRelatedCarousel(piece) {{
      var container = document.getElementById("relatedPiecesCarousel");
      var related = furnitureList.filter(function (f) {{
        return f.category === piece.category && f.id !== piece.id;
      }});

      if (related.length === 0) {{
        related = furnitureList.filter(function (f) {{ return f.id !== piece.id; }}).slice(0, 5);
      }}

      container.innerHTML = related.map(function (item) {{
        var slug = item.id.replace(/_/g, "-");
        return '<a href="/furniture/' + slug + '" class="catalog-card related-card">' +
          '<div class="card-top-bar">' +
            '<span class="card-name">' + item.name + '</span>' +
          '</div>' +
          '<div class="card-img-wrap" style="height:150px;">' +
            '<img src="' + item.image + '" alt="' + item.name + '" class="card-img" loading="lazy" onerror="this.src=\'assets/furniture/wooden_chair.jpg\'">' +
          '</div>' +
          '<div class="card-footer">' +
            '<span class="card-action-text">View best woods →</span>' +
          '</div>' +
        '</a>';
      }}).join("");
    }}

    // -----------------------------------------------------------------------
    // INITIALIZATION & DIRECT URL DISPATCH
    // -----------------------------------------------------------------------
    router.handleRoute();

  }})();
  </script>
</body>
</html>
'''

# Write to root index.html
target_index = os.path.join(PROJECT_ROOT, "index.html")
with open(target_index, "w", encoding="utf-8") as f:
    f.write(html_content)

# Write identical copy to frontend/index.html
frontend_index = os.path.join(PROJECT_ROOT, "frontend", "index.html")
with open(frontend_index, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated {target_index} and {frontend_index}!")

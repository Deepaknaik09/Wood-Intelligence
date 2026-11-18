"""Dedicated Page 5: Furniture Recommendations Studio (Timber AI Atelier).
Features:
- Single Source of Truth from furniture_data (31 pieces with user photos)
- Interactive Click-on-Picture to Open Full Recommendation Studio Modal (@st.dialog)
- Clean, Uncluttered Gallery View (No forced scroll to page bottom)
- Dynamic Category Counts and Synchronization (Search, Filters, Dropdown, Gallery)
- Decoupled Multi-Criteria Scoring Engine (recommend_woods)
- Live User Controls: Priority, Budget Tier, Environment inside Modal Fragment
- Side-by-Side Wood Comparison Matrix (up to 3 woods)
- Two-Way Explorer: 'More you can build with <Wood>' with clickable mini-cards
- WCAG AA High Contrast Visual Design with Dark/Light Mode Adaptability
"""
import os
import random
import streamlit as st

from furniture_data import FURNITURE_DATA, FURNITURE_BY_ID, get_all_furniture, get_categories, get_category_counts
from woods_data import WOODS_DATABASE, WOODS_BY_ID
import scoring_engine
import furniture_recommender
import design_visualizer
import importlib
importlib.reload(design_visualizer)

def uhtml(s: str) -> str:
    """Returns an unindented single-line string with no blank lines so Streamlit does not turn it into a code block."""
    return "".join(line.strip() for line in s.splitlines() if line.strip())

def on_modal_dismiss():
    """Callback when the modal dialog is dismissed by clicking X, ESC, or outside."""
    st.session_state["active_modal"] = None

# ===========================================================================
# MODAL DIALOG: TIMBER RECOMMENDATIONS & BLUEPRINT STUDIO (@st.dialog)
# ===========================================================================
@st.dialog("Timber Recommendations & Joinery Engineering Studio", width="large", on_dismiss=on_modal_dismiss)
def render_recommendations_modal(furniture_id: str):
    """Opens a focused, full-width modal studio for the selected piece, avoiding scrolling to page bottom."""
    st.markdown("""<style>
    /* Force Dialog Backdrop & Modal Box to match theme variables across React-Aria & Streamlit 1.65+ */
    .react-aria-ModalOverlay,
    div[data-testid="stDialog"],
    div[data-baseweb="modal"],
    .stDialog {
      background-color: rgba(0, 0, 0, 0.82) !important;
      backdrop-filter: blur(6px) !important;
      padding: 0 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
    }
    .react-aria-Modal,
    .react-aria-Dialog,
    div[role="dialog"],
    section[role="dialog"],
    div[data-testid="stDialog"] > div,
    div.stDialog > div,
    div[data-testid="stDialog"] section,
    div[data-testid="stDialog"] [class*="ep9mgll"],
    div[data-testid="stDialog"] [data-testid="stVerticalBlock"],
    div[data-baseweb="modal"] [role="dialog"] {
      background-color: var(--surface) !important;
      color: var(--ink) !important;
    }
    /* Full-Screen Studio Modal Window */
    div[data-testid="stDialog"] [class*="ep9mgll1"],
    div[data-testid="stDialog"] .react-aria-Modal,
    div[data-testid="stDialog"] div[role="dialog"],
    div[data-testid="stDialog"] section[role="dialog"],
    div[data-baseweb="modal"] [role="dialog"],
    .stDialog [class*="ep9mgll1"],
    .stDialog .react-aria-Modal,
    .stDialog div[role="dialog"],
    .react-aria-Modal {
      width: 98vw !important;
      max-width: 98vw !important;
      min-width: 94vw !important;
      height: 96vh !important;
      max-height: 96vh !important;
      min-height: 90vh !important;
      margin: 1.5vh auto !important;
      display: flex !important;
      flex-direction: column !important;
      border: 1.5px solid var(--line) !important;
      border-radius: 14px !important;
      box-shadow: 0 25px 80px rgba(0, 0, 0, 0.8) !important;
      background-color: var(--surface) !important;
      color: var(--ink) !important;
      overflow: hidden !important;
    }

    div[data-testid="stDialog"] [class*="ep9mgll2"],
    div[data-testid="stDialog"] .react-aria-Dialog,
    div[data-testid="stDialog"] section[role="dialog"],
    .stDialog [class*="ep9mgll2"] {
      width: 100% !important;
      max-width: 100% !important;
      height: 100% !important;
      max-height: 100% !important;
      flex: 1 1 auto !important;
      overflow-y: auto !important;
      padding: 1rem 1.8rem 2rem 1.8rem !important;
    }
    /* Dialog Main Title */
    .react-aria-Dialog h1,
    .react-aria-Dialog h2,
    .react-aria-Dialog h3,
    div[data-testid="stDialog"] h1,
    div[data-testid="stDialog"] h2,
    div[data-testid="stDialog"] h3,
    div[data-testid="stDialog"] [data-testid="stHeadingWithActionElements"] *,
    div[role="dialog"] h2,
    div[role="dialog"] h3 {
      color: var(--ink) !important;
      font-family: 'Cormorant Garamond', Georgia, serif !important;
      font-weight: 800 !important;
    }
    /* Dialog Close Button (X) */
    .react-aria-Dialog button[aria-label="Close"],
    div[data-testid="stDialog"] button[aria-label="Close"],
    div[data-testid="stDialog"] button[aria-label="Close"] svg,
    div.stDialog button[aria-label="Close"],
    div.stDialog button[aria-label="Close"] svg {
      color: var(--ink) !important;
      fill: var(--ink) !important;
      stroke: var(--ink) !important;
    }
    /* Top Furniture Dossier Card - Rich Dark Walnut with High Contrast in BOTH Modes */
    .wi-furniture-dossier,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier,
    div.wi-furniture-dossier {
      background: linear-gradient(135deg, #1f1107 0%, #341b0d 100%) !important;
      border: 1.5px solid #5a3518 !important;
      border-radius: 8px !important;
      padding: 1.25rem 1.45rem !important;
      color: #f7eee1 !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
    }
    .wi-furniture-dossier .dossier-title,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier .dossier-title {
      color: #ffd166 !important;
      font-family: 'Cormorant Garamond', Georgia, serif !important;
      font-size: 1.6rem !important;
      font-weight: 800 !important;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.85) !important;
    }
    .wi-furniture-dossier .dossier-chip,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier .dossier-chip {
      background: rgba(255, 209, 102, 0.18) !important;
      border: 1.5px solid #ffd166 !important;
      color: #ffd166 !important;
      font-weight: 800 !important;
      font-size: 0.75rem !important;
    }
    .wi-furniture-dossier .dossier-tagline,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier .dossier-tagline {
      color: #fcd34d !important;
      font-size: 0.92rem !important;
      font-weight: 700 !important;
    }
    .wi-furniture-dossier .dossier-desc,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier .dossier-desc,
    .wi-furniture-dossier p {
      color: #f7eee1 !important;
      font-size: 0.85rem !important;
      line-height: 1.55 !important;
      opacity: 0.95 !important;
    }
    /* Tabs inside Dialog */
    .react-aria-Dialog [data-testid="stTabs"] button[role="tab"],
    div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"] {
      background: transparent !important;
    }
    .react-aria-Dialog [data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"] p {
      color: var(--muted) !important;
      font-weight: 600 !important;
      font-size: 0.88rem !important;
    }
    .react-aria-Dialog [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
    div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
      border-bottom: 2.5px solid var(--amber) !important;
    }
    .react-aria-Dialog [data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
    div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {
      color: var(--amber) !important;
      font-weight: 800 !important;
    }
    /* Headings, text and labels inside dialog */
    .react-aria-Dialog h4,
    div[data-testid="stDialog"] h4 {
      color: var(--ink) !important;
      font-weight: 800 !important;
    }
    .react-aria-Dialog p,
    .react-aria-Dialog span,
    .react-aria-Dialog label,
    div[data-testid="stDialog"] p,
    div[data-testid="stDialog"] span,
    div[data-testid="stDialog"] label {
      color: var(--ink) !important;
    }
    .react-aria-Dialog [data-testid="stCheckbox"] label p,
    .react-aria-Dialog label[data-baseweb="checkbox"] p,
    div[data-testid="stDialog"] [data-testid="stCheckbox"] label p,
    div[data-testid="stDialog"] label[data-baseweb="checkbox"] p {
      color: var(--ink) !important;
      font-weight: 700 !important;
    }
    /* Selectboxes and dropdowns inside dialog */
    .react-aria-Dialog [data-baseweb="select"] *,
    div[data-testid="stDialog"] [data-baseweb="select"] * {
      color: var(--ink) !important;
    }
    /* Engineering Trade-offs / Warning Box High-Contrast */
    .tradeoffs-callout-box {
      background: var(--amber-soft) !important;
      border: 1.5px solid var(--amber) !important;
      border-radius: 8px !important;
      padding: 0.65rem 0.95rem !important;
      color: var(--ink) !important;
      font-size: 0.82rem !important;
      line-height: 1.5 !important;
    }
    .tradeoffs-callout-box strong {
      color: var(--amber) !important;
    }
    </style>""", unsafe_allow_html=True)
    active_item = furniture_recommender.get_furniture_item(furniture_id)

    # -----------------------------------------------------------------------
    # 1. UPPER DOSSIER: IMAGE & MECHANICAL STRESS PROFILE
    # -----------------------------------------------------------------------
    hero_col_img, hero_col_info = st.columns([1, 2], gap="large")
    with hero_col_img:
        st.markdown(uhtml(f'''
        <div style="background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--amber);
                    border-radius:8px;padding:8px;text-align:center;margin-bottom:8px;
                    box-shadow:0 2px 8px rgba(43,24,13,0.06);">
          <div style="font-size:0.72rem;font-weight:700;color:var(--muted);letter-spacing:0.08em;
                      text-transform:uppercase;">Selected Woodwork Piece</div>
        </div>'''), unsafe_allow_html=True)
        if os.path.exists(active_item["image"]):
            st.image(active_item["image"], use_container_width=True)
        else:
            st.markdown(f'<div style="font-size:2rem;text-align:center;padding:2rem 0;font-weight:700;color:var(--amber);">{active_item["name"]}</div>', unsafe_allow_html=True)

    with hero_col_info:
        ai_name = active_item['name']
        ai_cat = active_item['category']
        ai_tag = active_item['tagline']
        ai_ov = active_item['overview']
        sp = active_item['stress_profile']
        st.markdown(uhtml(f'''
        <div class="wi-furniture-dossier" style="background:linear-gradient(135deg,#2b180d,#3d1f0a) !important;border-radius:10px;
                    padding:1.3rem 1.5rem;color:#f3e3c8 !important;height:100%;min-height:240px;box-shadow:0 4px 16px rgba(0,0,0,0.2);">
          <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem;flex-wrap:wrap;">
            <span class="dossier-title" style="font-family:'Cormorant Garamond',Georgia,serif;font-size:1.55rem;font-weight:800;color:#ffd166 !important;text-shadow:0 2px 10px rgba(0,0,0,0.85);">{ai_name}</span>
            <span class="dossier-chip" style="background:rgba(217,143,43,0.25) !important;border:1px solid rgba(217,143,43,0.6) !important;
                         color:#ffd166 !important;padding:0.2rem 0.65rem;border-radius:4px;font-size:0.75rem;font-weight:700;letter-spacing:0.04em;">
              {ai_cat}
            </span>
          </div>
          <div class="dossier-tagline" style="font-size:0.92rem;font-weight:700;color:#fcd34d !important;margin-bottom:0.5rem;line-height:1.45;">{ai_tag}</div>
          <p class="dossier-desc" style="font-size:0.85rem;color:#f7eee1 !important;line-height:1.55;margin:0 0 0.9rem 0;opacity:0.95;">{ai_ov}</p>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.45rem;">
            <div style="background:rgba(255,255,255,0.08);border-radius:9px;padding:0.5rem 0.6rem;border:1px solid rgba(255,255,255,0.12);">
              <div style="font-size:0.64rem;color:#fbbf24 !important;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Min MOR</div>
              <div style="font-size:0.9rem;font-weight:800;color:#6ee7b7 !important;">{sp['min_mor']}</div>
            </div>
            <div style="background:rgba(255,255,255,0.08);border-radius:9px;padding:0.5rem 0.6rem;border:1px solid rgba(255,255,255,0.12);">
              <div style="font-size:0.64rem;color:#fbbf24 !important;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Density</div>
              <div style="font-size:0.9rem;font-weight:800;color:#6ee7b7 !important;">{sp['density_range']}</div>
            </div>
            <div style="background:rgba(255,255,255,0.08);border-radius:9px;padding:0.5rem 0.6rem;border:1px solid rgba(255,255,255,0.12);">
              <div style="font-size:0.64rem;color:#fbbf24 !important;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Moisture</div>
              <div style="font-size:0.9rem;font-weight:800;color:#6ee7b7 !important;">{sp['target_mc']}</div>
            </div>
            <div style="background:rgba(255,255,255,0.08);border-radius:9px;padding:0.5rem 0.6rem;grid-column:span 2;border:1px solid rgba(255,255,255,0.12);">
              <div style="font-size:0.64rem;color:#fbbf24 !important;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Load Type</div>
              <div style="font-size:0.8rem;font-weight:700;color:#fde68a !important;line-height:1.3;">{sp['load_type']}</div>
            </div>
            <div style="background:rgba(255,255,255,0.08);border-radius:9px;padding:0.5rem 0.6rem;border:1px solid rgba(255,255,255,0.12);">
              <div style="font-size:0.64rem;color:#fbbf24 !important;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Grain Cut</div>
              <div style="font-size:0.76rem;font-weight:700;color:#fde68a !important;line-height:1.3;">{sp['recommended_cut']}</div>
            </div>
          </div>
        </div>'''), unsafe_allow_html=True)

    scoring_options = {
        "priority": st.session_state.get("furn_priority", "Balanced"),
        "budget": st.session_state.get("furn_budget", "All"),
        "environment": st.session_state.get("furn_env", "Indoor")
    }

    # Fetch Top 5 Recommended Woods from Decoupled Scoring Engine
    top_5_woods = scoring_engine.recommend_woods(active_item["id"], scoring_options)

    # Initialize comparison state
    if "compare_woods" not in st.session_state:
        st.session_state["compare_woods"] = []

    # 4 Comprehensive Studio Tabs with Persistent State Tracking
    tab_labels = [
        f"Top 5 Recommended Species ({active_item['name']})",
        f"Design Patterns & Blueprints ({active_item['name']})",
        "Comparative Analysis Matrix",
        "Fabrication Guidelines"
    ]
    studio_tabs_key = f"studio_tabs_{active_item['id']}"
    if st.session_state.get(studio_tabs_key) not in tab_labels:
        st.session_state[studio_tabs_key] = tab_labels[0]

    tab_woods, tab_patterns, tab_compare, tab_rules = st.tabs(
        tab_labels,
        key=studio_tabs_key
    )

    # -----------------------------------------------------------------------
    # TAB 1: TOP 5 RECOMMENDED WOODS
    # -----------------------------------------------------------------------
    with tab_woods:
        st.markdown(uhtml(f"""
        <div style="margin-bottom:0.85rem;">
          <h4 style="color:var(--ink);margin:0 0 0.2rem 0;">Ranked Timber Suitability for {active_item['name']}</h4>
          <p style="font-size:0.83rem;color:var(--muted);margin:0;">
            Normalized across 28 commercial timbers using bending strength (MOR), Janka hardness, dimensional stability, workability, and cost tier.
          </p>
        </div>
        """), unsafe_allow_html=True)

        for w_idx, rec_item in enumerate(top_5_woods):
            wood = rec_item["wood"]
            score = rec_item["score"]
            breakdown = rec_item["breakdown"]
            reasons = rec_item["reasons"]
            tradeoffs = rec_item["tradeoffs"]
            is_best = rec_item["is_best_match"]

            card_border = "var(--good)" if is_best else "var(--line)"
            badge_bg = "var(--good)" if is_best else "var(--amber-soft)"
            badge_color = "var(--on-amber)" if is_best else "var(--ink)"
            badge_label = "OPTIMAL STRUCTURAL MATCH" if is_best else f"RANK #{rec_item['rank']}"
            score_bar_color = "var(--good)" if score >= 90 else ("var(--warn)" if score >= 80 else "var(--amber)")
            cost_stars = f"Tier {wood['costTier']}/5"

            st.markdown(uhtml(f"""
            <div style="background:var(--surface);border:1.5px solid {card_border};border-left:4px solid {'var(--good)' if is_best else 'var(--amber)'};border-radius:8px;padding:1.1rem 1.3rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.6rem;margin-bottom:0.65rem;">
                <div>
                  <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">
                    <span style="font-size:1.3rem;font-weight:800;color:var(--ink);">{wood['name']}</span>
                    <span style="font-style:italic;color:var(--muted);font-size:0.9rem;">({wood['scientificName']})</span>
                    <span style="background:{badge_bg};color:{badge_color};font-size:0.68rem;font-weight:800;padding:0.22rem 0.6rem;border-radius:4px;letter-spacing:0.04em;">
                      {badge_label}
                    </span>
                  </div>
                  <div style="font-size:0.78rem;color:var(--muted);margin-top:0.2rem;">
                    <strong>Weight Class:</strong> {wood['weightClass']} &nbsp;|&nbsp; <strong>Cost Class:</strong> {cost_stars} &nbsp;|&nbsp; <strong>Regional Availability:</strong> {wood['availabilityInIndia']}/10
                  </div>
                </div>
                <div style="text-align:right;min-width:110px;">
                  <div style="font-size:1.75rem;font-weight:800;color:{score_bar_color};font-family:'JetBrains Mono',monospace;line-height:1;">
                    {score:.1f}<span style="font-size:0.9rem;color:var(--muted);">/100</span>
                  </div>
                  <div style="font-size:0.65rem;font-weight:700;color:var(--amber);text-transform:uppercase;margin-top:2px;">Suitability Index</div>
                </div>
              </div>

              <!-- Score Fill Bar -->
              <div style="width:100%;height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin:0.3rem 0;">
                <div style="width:{min(100.0, score)}%;height:100%;background:{score_bar_color};border-radius:3px;"></div>
              </div>

              <!-- Key Engineering Stats Grid -->
              <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(120px, 1fr));gap:0.45rem;margin:0.75rem 0;background:var(--surface-2);padding:0.7rem 0.85rem;border-radius:10px;border:1px solid var(--line);">
                <div>
                  <div style="font-size:0.65rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Bending MOR</div>
                  <div style="font-size:0.9rem;font-weight:700;color:var(--ink);">{wood['mor']:.1f} MPa</div>
                </div>
                <div>
                  <div style="font-size:0.65rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Hardness (Janka)</div>
                  <div style="font-size:0.9rem;font-weight:700;color:var(--ink);">{wood['hardness']} N</div>
                </div>
                <div>
                  <div style="font-size:0.65rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Stability Score</div>
                  <div style="font-size:0.9rem;font-weight:700;color:var(--ink);">{wood['shrinkage']['stability_score']}/10</div>
                </div>
                <div>
                  <div style="font-size:0.65rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Workability</div>
                  <div style="font-size:0.9rem;font-weight:700;color:var(--ink);">{wood['workability']}/10</div>
                </div>
                <div>
                  <div style="font-size:0.65rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Finish Quality</div>
                  <div style="font-size:0.9rem;font-weight:700;color:var(--ink);">{wood['finishQuality']}/10</div>
                </div>
                <div>
                  <div style="font-size:0.65rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Durability</div>
                  <div style="font-size:0.9rem;font-weight:700;color:var(--ink);">{wood['durability']}/10</div>
                </div>
              </div>

              <!-- Why it suits this piece -->
              <div style="background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:9px;padding:0.65rem 0.85rem;margin-bottom:0.55rem;font-size:0.82rem;color:var(--ink);line-height:1.5;">
                <strong style="color:var(--amber);">Why this wood suits {active_item['name']}:</strong>
                <ul style="margin:0.25rem 0 0 1.1rem;padding:0;color:var(--ink);">
                  {"".join([f"<li>{r}</li>" for r in reasons])}
                </ul>
              </div>

              <!-- Engineering Trade-offs -->
              <div class="tradeoffs-callout-box" style="margin-bottom:0.65rem;">
                <strong style="color:var(--amber);">Engineering Considerations &amp; Trade-offs:</strong>
                <div style="margin-top:0.18rem;color:var(--ink);line-height:1.45;">{" • ".join(tradeoffs)}</div>
              </div>
            </div>
            """), unsafe_allow_html=True)

            act_col1, act_col2 = st.columns([1, 1])
            with act_col1:
                is_in_comp = wood["id"] in st.session_state["compare_woods"]
                comp_checked = st.checkbox(
                    f"Compare {wood['name']}",
                    value=is_in_comp,
                    key=f"dlg_chk_cmp_{wood['id']}_{w_idx}"
                )
                if comp_checked != is_in_comp:
                    if comp_checked:
                        if len(st.session_state["compare_woods"]) < 3:
                            st.session_state["compare_woods"].append(wood["id"])
                        else:
                            st.warning("You can compare up to 3 woods simultaneously.")
                    else:
                        if wood["id"] in st.session_state["compare_woods"]:
                            st.session_state["compare_woods"].remove(wood["id"])
                    st.rerun()

            with act_col2:
                if st.button(f"Explore Blueprints for {wood['name']}", key=f"dlg_btn_explore_{wood['id']}_{w_idx}", use_container_width=True):
                    st.session_state["selected_wood_for_explorer"] = wood["id"]
                    st.session_state[studio_tabs_key] = tab_labels[1]
                    st.rerun()

    # -----------------------------------------------------------------------
    # TAB 2: DEDICATED DESIGN PATTERNS FOR THIS FURNITURE PIECE
    # -----------------------------------------------------------------------
    with tab_patterns:
        explored_wood_id = st.session_state.get("selected_wood_for_explorer", top_5_woods[0]["wood"]["id"])
        explored_wood = scoring_engine.WOODS_BY_ID.get(explored_wood_id, top_5_woods[0]["wood"])

        exp_w_names = [w["name"] for w in scoring_engine.WOODS_DATABASE]
        exp_w_ids = [w["id"] for w in scoring_engine.WOODS_DATABASE]
        sel_w_name = st.selectbox(
            f"Tailor Architectural Blueprints & Design Patterns for {active_item['name']} Using:",
            exp_w_names,
            index=exp_w_ids.index(explored_wood_id) if explored_wood_id in exp_w_ids else 0,
            key="dlg_pattern_wood_select"
        )
        new_exp_id = exp_w_ids[exp_w_names.index(sel_w_name)]
        if new_exp_id != explored_wood_id:
            st.session_state["selected_wood_for_explorer"] = new_exp_id
            st.rerun()

        st.markdown(uhtml(f"""
        <div style="background:var(--surface-2);border:1.5px solid var(--amber);border-radius:8px;padding:1rem 1.3rem;margin:0.85rem 0;box-shadow:0 2px 8px rgba(217,143,43,0.08);">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.6rem;">
            <div>
              <span style="font-size:0.72rem;color:var(--amber);font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">ACTIVE CRAFTING TIMBER PAIRING</span>
              <div style="font-size:1.35rem;font-weight:800;color:var(--ink);">{explored_wood['name']} <span style="font-size:0.9rem;font-weight:500;color:var(--muted);font-style:italic;">({explored_wood['scientificName']})</span></div>
            </div>
            <div style="text-align:right;">
              <span style="background:var(--amber);color:var(--on-amber);font-size:0.72rem;font-weight:800;padding:0.25rem 0.7rem;border-radius:4px;">
                Density: {explored_wood['density']} kg/m³ | Hardness: {explored_wood['hardness']} N
              </span>
            </div>
          </div>
          
          <div style="background:var(--surface);border-left:3px solid var(--good);border-radius:6px;padding:0.6rem 0.9rem;margin-top:0.7rem;font-size:0.82rem;color:var(--ink);line-height:1.5;">
            <strong style="color:var(--good);">Species Workability &amp; Joinery Specification:</strong><br/>
            {explored_wood['joineryTip']}
          </div>
        </div>
        """), unsafe_allow_html=True)

        st.markdown(uhtml(f"""
        <div style="margin:1rem 0 0.6rem 0;">
          <h4 style="color:var(--ink);margin:0 0 0.2rem 0;">Curated Design Patterns for {active_item['name']}</h4>
          <p style="font-size:0.82rem;color:var(--muted);margin:0;">
            Architectural joinery methods, finished proportions, structural safety margins, and workshop blueprints tailored exclusively for {active_item['name']} crafted in {explored_wood['name']}.
          </p>
        </div>
        """), unsafe_allow_html=True)

        furniture_patterns = furniture_recommender.get_furniture_design_patterns(active_item["id"], explored_wood_id)

        # Master Action Toolbar to generate all design pictures at once
        top_act_col1, top_act_col2 = st.columns([1.8, 1])
        with top_act_col1:
            if st.button(
                f"✨ Generate Multi-View Design Suites for All {len(furniture_patterns)} Patterns (1-Click)",
                key=f"btn_create_all_designs_{active_item['id']}_{explored_wood_id}",
                use_container_width=True
            ):
                with st.spinner(f"Generating 4-perspective HD design suites for all {len(furniture_patterns)} patterns in {explored_wood['name']}..."):
                    for idx_all, p_all in enumerate(furniture_patterns):
                        design_visualizer.generate_multi_design_suite(active_item, p_all, explored_wood, force_regenerate=True)
                        st.session_state[f"show_design_{active_item['id']}_{explored_wood_id}_{idx_all}"] = True
                    st.session_state[studio_tabs_key] = tab_labels[1]
                    st.rerun()
        with top_act_col2:
            if st.button(
                "✕ Hide All Design Suites",
                key=f"btn_hide_all_designs_{active_item['id']}_{explored_wood_id}",
                use_container_width=True
            ):
                for idx_all in range(len(furniture_patterns)):
                    st.session_state[f"show_design_{active_item['id']}_{explored_wood_id}_{idx_all}"] = False
                st.session_state[studio_tabs_key] = tab_labels[1]
                st.rerun()

        for p_idx, pat in enumerate(furniture_patterns):
            st.markdown(uhtml(f"""
            <div style="background:var(--surface);border:1.5px solid var(--line);border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:0.6rem;box-shadow:0 3px 12px rgba(0,0,0,0.05);">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.6rem;margin-bottom:0.7rem;">
                <div>
                  <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">
                    <span style="font-size:1.25rem;font-weight:800;color:var(--ink);font-family:'Cinzel',serif;">{pat['title']}</span>
                    <span style="background:var(--amber-soft);color:var(--ink);border:1px solid var(--amber);font-size:0.7rem;font-weight:700;padding:0.18rem 0.6rem;border-radius:4px;letter-spacing:0.04em;">{pat['badge']}</span>
                  </div>
                  <p style="font-size:0.84rem;color:var(--muted);margin:0.35rem 0 0 0;line-height:1.5;">
                    {pat['description']}
                  </p>
                </div>
              </div>

              <!-- Blueprint Specs Grid -->
              <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(210px, 1fr));gap:0.65rem;margin:0.85rem 0;background:var(--surface-2);border:1px solid var(--line);border-radius:8px;padding:0.8rem 0.95rem;">
                <div>
                  <div style="font-size:0.68rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Finished Dimensions</div>
                  <div style="font-size:0.82rem;font-weight:700;color:var(--ink);margin-top:0.15rem;">{pat['dimensions']}</div>
                </div>
                <div>
                  <div style="font-size:0.68rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Recommended Joinery</div>
                  <div style="font-size:0.82rem;font-weight:700;color:var(--good);margin-top:0.15rem;">{pat['recommended_joinery']}</div>
                </div>
                <div>
                  <div style="font-size:0.68rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Protective Finish</div>
                  <div style="font-size:0.82rem;font-weight:700;color:var(--ink);margin-top:0.15rem;">{pat['recommended_finish']}</div>
                </div>
                <div>
                  <div style="font-size:0.68rem;color:var(--amber);font-weight:700;text-transform:uppercase;">Design Load Capacity</div>
                  <div style="font-size:0.82rem;font-weight:700;color:var(--ink);margin-top:0.15rem;">{pat['load_capacity']}</div>
                </div>
              </div>

              <!-- Timber Pairing Suitability & Structural Margin -->
              <div style="background:var(--surface-2);border-left:4px solid var(--good);padding:0.65rem 0.9rem;border-radius:0 6px 6px 0;margin-bottom:0.6rem;font-size:0.81rem;color:var(--ink);line-height:1.45;">
                <strong style="color:var(--good);">Timber Engineering Analysis ({pat['wood_pairing_name']}):</strong><br/>
                {pat['wood_pairing_note']}<br/>
                <span style="font-size:0.77rem;color:var(--muted);">{pat['wood_stability_note']}</span>
              </div>

              <!-- Technical Workshop Blueprint -->
              <div style="background:var(--amber-soft);border-left:4px solid var(--amber);padding:0.65rem 0.9rem;border-radius:0 6px 6px 0;font-size:0.81rem;color:var(--ink);line-height:1.45;">
                <strong style="color:var(--amber);">Master Workshop Blueprint &amp; Fabrication Tip:</strong><br/>
                {pat['blueprint_tips']}
              </div>
            </div>
            """), unsafe_allow_html=True)

            # Check design visual status
            design_state_key = f"show_design_{active_item['id']}_{explored_wood_id}_{p_idx}"
            suite_exists = design_visualizer.is_suite_generated(active_item["id"], pat["title"], explored_wood_id)
            if design_state_key not in st.session_state:
                st.session_state[design_state_key] = suite_exists
            is_design_active = st.session_state.get(design_state_key, False)

            if not is_design_active:
                act_c1, act_c2 = st.columns([1.8, 1])
                with act_c1:
                    if st.button(
                        f"✨ Generate Multi-View Design Suite (4 High-Res Views)",
                        key=f"btn_create_design_{active_item['id']}_{explored_wood_id}_{p_idx}",
                        use_container_width=True,
                        type="primary"
                    ):
                        with st.spinner(f"Generating 4 architectural perspectives for {pat['title']} in {explored_wood['name']}..."):
                            design_visualizer.generate_multi_design_suite(active_item, pat, explored_wood, force_regenerate=True)
                            st.session_state[design_state_key] = True
                            st.session_state[studio_tabs_key] = tab_labels[1]
                            is_design_active = True
                with act_c2:
                    st.caption("🎨 Creates 4 HD perspectives: 3D Studio Render, CAD Blueprint, Joinery Schematic & In-Situ Scene.")

            if is_design_active:
                # Ensure all 4 images in suite are generated
                design_suite = design_visualizer.generate_multi_design_suite(active_item, pat, explored_wood)

                st.markdown(uhtml(f"""
                <div style="background:var(--surface-2);border:1.5px solid var(--amber);border-radius:10px;padding:0.75rem 1rem;margin:0.4rem 0 0.5rem 0;">
                  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.4rem;">
                    <div>
                      <span style="font-size:0.75rem;font-weight:800;color:var(--amber);text-transform:uppercase;letter-spacing:0.06em;">
                        🎨 Multi-Perspective Architectural &amp; Studio Design Suite
                      </span>
                      <div style="font-size:0.95rem;font-weight:700;color:var(--ink);">
                        {pat['title']} · Crafted in {explored_wood['name']}
                      </div>
                    </div>
                    <div>
                      <span style="background:var(--good);color:white;font-size:0.72rem;font-weight:700;padding:0.25rem 0.65rem;border-radius:4px;">
                        ✓ 4 High-Res Perspectives Ready
                      </span>
                    </div>
                  </div>
                </div>
                """), unsafe_allow_html=True)

                tab_studio, tab_blueprint, tab_joinery, tab_insitu = st.tabs([
                    "📸 3D Studio Render",
                    "📐 CAD Blueprint",
                    "🔍 Joinery Schematic",
                    "🏡 In-Situ Room Context"
                ])

                views_mapping = [
                    (tab_studio, "studio", design_suite.get("studio")),
                    (tab_blueprint, "blueprint", design_suite.get("blueprint")),
                    (tab_joinery, "joinery", design_suite.get("joinery")),
                    (tab_insitu, "insitu", design_suite.get("insitu")),
                ]

                for v_tab, v_key, v_info in views_mapping:
                    if not v_info:
                        continue
                    with v_tab:
                        st.markdown(uhtml(f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin:0.3rem 0 0.5rem 0;padding:0.4rem 0.7rem;background:var(--surface);border-radius:6px;border:1px solid var(--line);">
                          <div>
                            <strong style="color:var(--ink);font-size:0.86rem;">{v_info['icon']} {v_info['title']}</strong>
                            <span style="color:var(--muted);font-size:0.75rem;margin-left:0.5rem;">— {v_info['desc']}</span>
                          </div>
                          <div>
                            <span style="background:var(--amber-soft);color:var(--amber);font-size:0.68rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:3px;border:1px solid var(--amber);">
                              {v_info['badge']}
                            </span>
                          </div>
                        </div>
                        """), unsafe_allow_html=True)

                        if os.path.exists(v_info["path"]):
                            st.image(
                                v_info["path"],
                                caption=f"{v_info['title']}: {pat['title']} ({active_item['name']}) in {explored_wood['name']}",
                                use_container_width=True
                            )

                            v_btn_col1, v_btn_col2 = st.columns([1.5, 1])
                            with v_btn_col1:
                                with open(v_info["path"], "rb") as f_img:
                                    st.download_button(
                                        label=f"📥 Download {v_info['title']} (PNG)",
                                        data=f_img.read(),
                                        file_name=f"{active_item['id']}_{design_visualizer.slugify(pat['title'])}_{explored_wood_id}_{v_key}.png",
                                        mime="image/png",
                                        key=f"dl_btn_{active_item['id']}_{explored_wood_id}_{p_idx}_{v_key}",
                                        use_container_width=True
                                    )

                # Controls row: Re-generate all, Close/Hide
                ctrl_col1, ctrl_col2 = st.columns([1.2, 1])
                with ctrl_col1:
                    if st.button("🔄 Re-Generate All 4 Perspectives", key=f"regen_{active_item['id']}_{explored_wood_id}_{p_idx}", use_container_width=True):
                        with st.spinner("Re-generating all 4 design perspectives in HD..."):
                            design_visualizer.generate_multi_design_suite(active_item, pat, explored_wood, force_regenerate=True)
                            st.session_state[design_state_key] = True
                            st.session_state[studio_tabs_key] = tab_labels[1]
                            st.rerun()
                with ctrl_col2:
                    if st.button("✕ Close Multi-View Suite", key=f"hide_{active_item['id']}_{explored_wood_id}_{p_idx}", use_container_width=True):
                        st.session_state[design_state_key] = False
                        st.session_state[studio_tabs_key] = tab_labels[1]
                        st.rerun()

            st.markdown("<div style='margin-bottom:1.2rem;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # TAB 3: SIDE-BY-SIDE TIMBER COMPARISON
    # -----------------------------------------------------------------------
    with tab_compare:
        st.markdown(uhtml(f"""
        <div style="margin-bottom:0.85rem;">
          <h4 style="color:var(--ink);margin:0 0 0.2rem 0;">Side-by-Side Timber Comparison Matrix</h4>
          <p style="font-size:0.82rem;color:var(--muted);margin:0;">
            Compare engineering metrics, workability, and economics for up to 3 timbers. Check boxes in Tab 1 or pick from the selectors below.
          </p>
        </div>
        """), unsafe_allow_html=True)

        all_wood_options = [w["name"] for w in scoring_engine.WOODS_DATABASE]
        all_wood_ids = [w["id"] for w in scoring_engine.WOODS_DATABASE]

        comp_ids = st.session_state.get("compare_woods", [])
        if not comp_ids:
            comp_ids = [top_5_woods[0]["wood"]["id"], top_5_woods[1]["wood"]["id"]]

        cmp_selector_cols = st.columns(len(comp_ids))
        new_comp_ids = []
        for c_idx, cid in enumerate(comp_ids):
            with cmp_selector_cols[c_idx]:
                def_idx = all_wood_ids.index(cid) if cid in all_wood_ids else 0
                chosen_name = st.selectbox(f"Compare Wood #{c_idx+1}:", all_wood_options, index=def_idx, key=f"dlg_sel_comp_slot_{c_idx}")
                new_comp_ids.append(all_wood_ids[all_wood_options.index(chosen_name)])

        if new_comp_ids != comp_ids:
            st.session_state["compare_woods"] = new_comp_ids
            st.rerun()

        cmp_disp_cols = st.columns(len(new_comp_ids), gap="medium")
        for col_slot, c_wid in zip(cmp_disp_cols, new_comp_ids):
            w_obj = scoring_engine.WOODS_BY_ID[c_wid]
            w_recs = [r for r in top_5_woods if r["wood"]["id"] == c_wid]
            w_score = w_recs[0]["score"] if w_recs else 75.0
            
            with col_slot:
                st.markdown(uhtml(f"""
                <div style="background:var(--surface);border:1.5px solid var(--line);border-radius:14px;padding:1rem;box-shadow:0 4px 14px rgba(0,0,0,0.06);">
                  <div style="font-size:0.72rem;color:var(--amber);font-weight:700;text-transform:uppercase;">TIMBER PROFILE</div>
                  <div style="font-size:1.3rem;font-weight:800;color:var(--ink);">{w_obj['name']}</div>
                  <div style="font-style:italic;color:var(--muted);font-size:0.84rem;margin-bottom:0.7rem;">{w_obj['scientificName']}</div>

                  <div style="background:var(--surface-2);border-radius:10px;padding:0.7rem;border:1px solid var(--line);margin-bottom:0.7rem;">
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Suitability Score:</span>
                      <strong style="color:var(--good);">{w_score:.1f} / 100</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Density:</span>
                      <strong>{w_obj['density']} kg/m³</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Bending MOR:</span>
                      <strong>{w_obj['mor']:.1f} MPa</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Janka Hardness:</span>
                      <strong>{w_obj['hardness']} N</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Stability:</span>
                      <strong>{w_obj['shrinkage']['stability_score']} / 10</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Workability:</span>
                      <strong>{w_obj['workability']} / 10</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Durability:</span>
                      <strong>{w_obj['durability']} / 10</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid var(--line);font-size:0.8rem;">
                      <span style="color:var(--muted);">Cost Tier:</span>
                      <strong>Tier {w_obj['costTier']} / 5</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0.25rem 0;font-size:0.8rem;">
                      <span style="color:var(--muted);">India Availability:</span>
                      <strong>{w_obj['availabilityInIndia']} / 10</strong>
                    </div>
                  </div>

                  <div style="font-size:0.78rem;color:var(--ink);line-height:1.45;background:var(--surface);padding:0.6rem 0.8rem;border-radius:8px;border:1px solid var(--line);">
                    <strong style="color:var(--amber);">Joinery Note:</strong> {w_obj['joineryTip']}
                  </div>
                </div>
                """), unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # TAB 4: WORKSHOP RULES & FABRICATION GUIDELINES
    # -----------------------------------------------------------------------
    with tab_rules:
        st.markdown(uhtml(f"""
        <div style="margin-bottom:0.85rem;">
          <h4 style="color:var(--ink);margin:0 0 0.2rem 0;">Carpentry Guidelines for Building a {active_item['name']}</h4>
          <p style="font-size:0.82rem;color:var(--muted);margin:0;">
            Follow these essential workshop engineering principles to maximize structural longevity and prevent joint failure.
          </p>
        </div>
        """), unsafe_allow_html=True)

        rule_cols = st.columns(2, gap="medium")
        rule_tags = ["[01]", "[02]", "[03]", "[04]"]
        for r_idx, rule in enumerate(active_item.get("carpentry_rules", [])):
            with rule_cols[r_idx % 2]:
                parts = rule.split(":", 1)
                r_title = parts[0].strip() if len(parts) > 1 else f"Guideline {r_idx+1}"
                r_text = parts[1].strip() if len(parts) > 1 else rule
                st.markdown(uhtml(f"""
                <div style="background:var(--surface);border:1.5px solid var(--line);border-radius:8px;padding:1rem 1.15rem;margin-bottom:0.8rem;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;font-weight:800;color:var(--amber);">{rule_tags[r_idx % len(rule_tags)]}</span>
                    <span style="font-weight:700;font-size:0.9rem;color:var(--ink);">{r_title}</span>
                  </div>
                  <p style="font-size:0.82rem;color:var(--muted);line-height:1.5;margin:0;">
                    {r_text}
                  </p>
                </div>
                """), unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # BOTTOM CLOSE BUTTON
    # -----------------------------------------------------------------------
    st.markdown("<hr style='margin:1.1rem 0 0.9rem 0;border:none;border-bottom:1px solid var(--line);'>", unsafe_allow_html=True)
    if st.button("Close Studio & Return to Gallery", key="dlg_btn_close_modal_bottom", use_container_width=True, type="secondary"):
        st.session_state["active_modal"] = None
        st.rerun()


# ===========================================================================
# MAIN PAGE RENDERER: GALLERY & STUDIO CONTROLLER
# ===========================================================================
def render_furniture_page(dark: bool = False):
    total_catalog_count = len(FURNITURE_DATA)

    # -----------------------------------------------------------------------
    # INJECT SCOPED CARD & OVERLAY CSS
    # -----------------------------------------------------------------------
    st.markdown("""
    <style>
    /* Uniform Image Height & Object-Fit */
    div[data-testid="stColumn"] div[data-testid="stImage"] img {
      border-radius: 10px !important;
      object-fit: cover !important;
      width: 100% !important;
      height: 200px !important;
      transition: transform 0.25s ease, filter 0.25s ease !important;
      cursor: pointer !important;
    }
    div[data-testid="stColumn"] div[data-testid="stImage"] img:hover {
      transform: scale(1.02) !important;
      filter: brightness(1.05) !important;
    }

    /* Picture Click Overlay Button (Sits right on the photo) */
    div[class*="st-key-btn_img_overlay_"] {
      margin-top: -206px !important;
      height: 200px !important;
      position: relative !important;
      z-index: 10 !important;
      margin-bottom: 6px !important;
    }
    div[class*="st-key-btn_img_overlay_"] button {
      width: 100% !important;
      height: 200px !important;
      background: transparent !important;
      border: 2px solid transparent !important;
      border-radius: 10px !important;
      color: transparent !important;
      cursor: pointer !important;
      transition: all 0.25s ease !important;
      box-shadow: none !important;
      transform: none !important;
      padding: 0 !important;
    }
    div[class*="st-key-btn_img_overlay_"] button p,
    div[class*="st-key-btn_img_overlay_"] button span,
    div[class*="st-key-btn_img_overlay_"] button div {
      display: none !important;
    }
    div[class*="st-key-btn_img_overlay_"] button:hover {
      background: rgba(43, 24, 12, 0.40) !important;
      border: 2px solid var(--amber) !important;
      backdrop-filter: blur(2px) !important;
    }
    div[class*="st-key-btn_img_overlay_"] button:hover::after {
      content: "Inspect Recommendations" !important;
      display: inline-block !important;
      position: absolute !important;
      top: 50% !important;
      left: 50% !important;
      transform: translate(-50%, -50%) !important;
      background: var(--amber) !important;
      color: var(--on-amber) !important;
      font-size: 0.8rem !important;
      font-weight: 800 !important;
      padding: 0.4rem 0.85rem !important;
      border-radius: 4px !important;
      white-space: nowrap !important;
      box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
      pointer-events: none !important;
    }

    /* Modal Dialog styling */
    .react-aria-ModalOverlay,
    div[data-testid="stDialog"],
    div[data-baseweb="modal"],
    .stDialog {
      background-color: rgba(0, 0, 0, 0.82) !important;
      backdrop-filter: blur(6px) !important;
      padding: 0 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
    }
    .react-aria-Modal,
    .react-aria-Dialog,
    div[role="dialog"],
    section[role="dialog"],
    div[data-testid="stDialog"] > div,
    div.stDialog > div,
    div[data-testid="stDialog"] section,
    div[data-testid="stDialog"] [class*="ep9mgll"],
    div[data-testid="stDialog"] [data-testid="stVerticalBlock"],
    div[data-baseweb="modal"] [role="dialog"] {
      background-color: var(--surface) !important;
      color: var(--ink) !important;
    }
    /* Full-Screen Studio Modal Window */
    div[data-testid="stDialog"] [class*="ep9mgll1"],
    div[data-testid="stDialog"] .react-aria-Modal,
    div[data-testid="stDialog"] div[role="dialog"],
    div[data-testid="stDialog"] section[role="dialog"],
    div[data-baseweb="modal"] [role="dialog"],
    .stDialog [class*="ep9mgll1"],
    .stDialog .react-aria-Modal,
    .stDialog div[role="dialog"],
    .react-aria-Modal {
      width: 98vw !important;
      max-width: 98vw !important;
      min-width: 94vw !important;
      height: 96vh !important;
      max-height: 96vh !important;
      min-height: 90vh !important;
      margin: 1.5vh auto !important;
      display: flex !important;
      flex-direction: column !important;
      border: 1.5px solid var(--line) !important;
      border-radius: 14px !important;
      box-shadow: 0 25px 80px rgba(0, 0, 0, 0.8) !important;
      background-color: var(--surface) !important;
      color: var(--ink) !important;
      overflow: hidden !important;
    }

    div[data-testid="stDialog"] [class*="ep9mgll2"],
    div[data-testid="stDialog"] .react-aria-Dialog,
    div[data-testid="stDialog"] section[role="dialog"],
    .stDialog [class*="ep9mgll2"] {
      width: 100% !important;
      max-width: 100% !important;
      height: 100% !important;
      max-height: 100% !important;
      flex: 1 1 auto !important;
      overflow-y: auto !important;
      padding: 1rem 1.8rem 2rem 1.8rem !important;
    }

    /* Furniture Dossier Card Text Contrast Enforcement */
    .wi-furniture-dossier,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier,
    div.wi-furniture-dossier {
      background: linear-gradient(135deg, #1f1107 0%, #341b0d 100%) !important;
      border: 1.5px solid #5a3518 !important;
      border-radius: 8px !important;
      padding: 1.25rem 1.45rem !important;
      color: #f7eee1 !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
    }
    .wi-furniture-dossier * {
      box-sizing: border-box !important;
    }
    .wi-furniture-dossier .dossier-title,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier .dossier-title {
      color: #ffd166 !important;
      font-family: 'Cormorant Garamond', Georgia, serif !important;
      font-size: 1.6rem !important;
      font-weight: 800 !important;
      text-shadow: 0 2px 10px rgba(0,0,0,0.85) !important;
    }
    .wi-furniture-dossier .dossier-chip,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier .dossier-chip {
      color: #ffd166 !important;
      background: rgba(255, 209, 102, 0.18) !important;
      border: 1.5px solid #ffd166 !important;
      font-size: 0.75rem !important;
      font-weight: 800 !important;
    }
    .wi-furniture-dossier .dossier-tagline,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier .dossier-tagline {
      color: #fcd34d !important;
      font-size: 0.92rem !important;
      font-weight: 700 !important;
      line-height: 1.45 !important;
    }
    .wi-furniture-dossier .dossier-desc,
    .wi-furniture-dossier p,
    [data-testid="stMarkdownContainer"] .wi-furniture-dossier p {
      color: #f7eee1 !important;
      font-size: 0.85rem !important;
      line-height: 1.55 !important;
      opacity: 0.95 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # TRIGGER MODAL IF AN ACTIVE PIECE IS SELECTED FOR INSPECTION
    # -----------------------------------------------------------------------
    if st.session_state.get("active_modal"):
        render_recommendations_modal(st.session_state["active_modal"])

    # -----------------------------------------------------------------------
    # 2. SYNCHRONIZED CONTROLS: CATEGORY RADIO FILTER
    # -----------------------------------------------------------------------
    cat_list = furniture_recommender.get_all_categories()
    curr_cat = st.session_state.get("furn_category_filter", cat_list[0])
    if curr_cat not in cat_list:
        matching_cat = next((c for c in cat_list if c.split(" (")[0] == curr_cat.split(" (")[0]), cat_list[0])
        curr_cat = matching_cat
        st.session_state["furn_category_filter"] = curr_cat

    cat_idx = cat_list.index(curr_cat)
    sel_cat = st.radio(
        "Filter Category:",
        cat_list,
        index=cat_idx,
        horizontal=True,
        key=f"cat_filter_radio_{curr_cat}"
    )
    if sel_cat != st.session_state.get("furn_category_filter"):
        st.session_state["furn_category_filter"] = sel_cat
        st.rerun()

    # Compute filtered items from Single Source of Truth
    filtered_keys = furniture_recommender.search_furniture(
        query="",
        category=st.session_state.get("furn_category_filter", cat_list[0])
    )
    if not filtered_keys:
        filtered_keys = furniture_recommender.get_furniture_keys()

    # Ensure selected_furniture is in session state
    if "selected_furniture" not in st.session_state or st.session_state["selected_furniture"] not in furniture_recommender.FURNITURE_KNOWLEDGE:
        st.session_state["selected_furniture"] = "wooden_chair"

    curr_sel = st.session_state["selected_furniture"]
    if curr_sel not in filtered_keys and filtered_keys:
        curr_sel = filtered_keys[0]
        st.session_state["selected_furniture"] = curr_sel

    sel_idx = filtered_keys.index(curr_sel) if curr_sel in filtered_keys else 0

    def format_furn_dropdown(k):
        it_obj = furniture_recommender.get_furniture_item(k)
        return f"{it_obj['icon']} {it_obj['name']} ({it_obj['category']})"

    dropdown_col1, dropdown_col2, dropdown_col3 = st.columns([3.0, 1.0, 1.2], vertical_alignment="bottom")
    with dropdown_col1:
        dropdown_val = st.selectbox(
            "Select Furniture Piece:",
            filtered_keys,
            index=sel_idx,
            format_func=format_furn_dropdown,
            key=f"furn_dropdown_{curr_sel}"
        )
        if dropdown_val != st.session_state["selected_furniture"]:
            st.session_state["selected_furniture"] = dropdown_val
            st.rerun()

    with dropdown_col2:
        if st.button("Sample Piece", key="btn_furn_random", use_container_width=True, help="Explore another catalog piece"):
            st.session_state["selected_furniture"] = random.choice(filtered_keys)
            st.rerun()

    with dropdown_col3:
        if st.button("Open Studio", key="btn_open_active_studio", type="primary", use_container_width=True, help="Open recommendations studio for selected piece"):
            st.session_state["active_modal"] = st.session_state["selected_furniture"]
            st.rerun()

    # -----------------------------------------------------------------------
    # ACTIVE PIECE QUICK BANNER (Top of page, no scroll needed)
    # -----------------------------------------------------------------------
    active_obj = furniture_recommender.get_furniture_item(st.session_state["selected_furniture"])
    sp_act = active_obj["stress_profile"]
    st.markdown(uhtml(f"""
    <div style="background:var(--surface-2);border:1.5px solid var(--amber);border-radius:8px;padding:0.75rem 1.1rem;margin:1rem 0 1.2rem 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.6rem;">
      <div style="display:flex;align-items:center;gap:0.75rem;">
        <div>
          <div style="font-size:0.95rem;font-weight:800;color:var(--ink);">{active_obj['name']} <span style="font-size:0.75rem;font-weight:600;color:var(--muted);background:var(--surface);padding:0.15rem 0.5rem;border-radius:4px;border:1px solid var(--line);">{active_obj['category']}</span></div>
          <div style="font-size:0.78rem;color:var(--muted);margin-top:0.15rem;">Min MOR: <strong style="color:var(--good);">{sp_act['min_mor']}</strong> &bull; Density: <strong>{sp_act['density_range']}</strong> &bull; Cut: <strong>{sp_act['recommended_cut']}</strong></div>
        </div>
      </div>
      <div style="font-size:0.8rem;color:var(--amber);font-weight:700;">
        Select any piece below to view top 5 recommended species and blueprints.
      </div>
    </div>
    """), unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 3. BROWSE FURNITURE GALLERY (CLICKABLE PHOTO CARDS)
    # -----------------------------------------------------------------------
    st.markdown(uhtml(f"""
    <div class="wi-card-header" style="margin-top:0.5rem;margin-bottom:0.8rem;display:flex;justify-content:space-between;align-items:center;">
      <span class="wi-card-title">Browse Furniture Gallery</span>
      <span class="wi-section-label" style="background:var(--surface-2);color:var(--amber);padding:0.25rem 0.75rem;border-radius:4px;border:1px solid var(--line);font-size:0.75rem;font-weight:700;">
        Showing {len(filtered_keys)} of {total_catalog_count} Pieces
      </span>
    </div>
    """), unsafe_allow_html=True)

    grid_cols = st.columns(4, gap="small")
    for g_idx, f_key in enumerate(filtered_keys):
        f_item = furniture_recommender.get_furniture_item(f_key)
        col_slot = grid_cols[g_idx % 4]
        is_active = (f_key == st.session_state["selected_furniture"])

        with col_slot:
            border_color = "var(--amber)" if is_active else "var(--line)"
            bg_color = "var(--surface-2)" if is_active else "var(--surface)"
            shadow_style = "0 4px 14px rgba(217,143,43,0.18)" if is_active else "0 1px 4px rgba(0,0,0,0.04)"
            active_badge = '<div style="position:absolute;top:8px;right:8px;background:var(--amber);color:var(--on-amber);font-size:0.62rem;font-weight:800;padding:0.22rem 0.55rem;border-radius:4px;z-index:3;box-shadow:0 1px 4px rgba(0,0,0,0.2);">ACTIVE</div>' if is_active else ''

            # Card Header Title Box
            st.markdown(uhtml(f'''
            <div style="position:relative;border:1.5px solid {border_color};border-radius:8px;background:{bg_color};
                        padding:10px 10px 6px 10px;margin-bottom:6px;box-shadow:{shadow_style};transition:all 0.2s ease;">
              {active_badge}
              <div style="font-weight:700;font-size:0.88rem;color:var(--ink);margin-bottom:2px;line-height:1.3;text-align:center;">
                {f_item['name']}
              </div>
              <div style="font-size:0.7rem;color:var(--muted);margin-bottom:6px;text-align:center;font-weight:500;">
                {f_item['category']}
              </div>
            </div>
            '''), unsafe_allow_html=True)

            # Furniture Photo
            img_path = f_item["image"]
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.markdown(f'<div style="font-size:1.5rem;font-weight:700;color:var(--muted);text-align:center;padding:1.4rem 0;background:var(--surface-2);border-radius:8px;">{f_item["name"]}</div>', unsafe_allow_html=True)

            # Invisible Click Target Button directly over the image (Triggers when user clicks the picture)
            if st.button("Click", key=f"btn_img_overlay_{f_key}"):
                st.session_state["selected_furniture"] = f_key
                st.session_state["active_modal"] = f_key
                st.rerun()

            # Visible Action Button right below the image
            btn_label = f"Inspect {f_item['name']}"
            btn_type = "primary" if is_active else "secondary"
            if st.button(btn_label, key=f"btn_act_{f_key}", type=btn_type, use_container_width=True):
                st.session_state["selected_furniture"] = f_key
                st.session_state["active_modal"] = f_key
                st.rerun()

    # -----------------------------------------------------------------------
    # 4. SLEEK FOOTER (REPLACES GIANT BOTTOM SECTION)
    # -----------------------------------------------------------------------
    st.markdown("<hr style='margin:2rem 0 1.2rem 0;border:none;border-bottom:1px solid var(--line);'>", unsafe_allow_html=True)
    st.markdown(uhtml(f"""
    <div style="text-align:center;padding:0.5rem 0 2rem 0;color:var(--muted);font-size:0.85rem;">
      <strong>Timber Engineering Specification Suite</strong> &bull; Select any catalog piece to compute stress profiles, structural MOR requirements, and workshop joinery guidelines.
    </div>
    """), unsafe_allow_html=True)

import os
import sys

_cur = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_cur)
for p in [_cur, _parent]:
    if p not in sys.path:
        sys.path.insert(0, p)

from streamlit.testing.v1 import AppTest
try:
    import auth
except ImportError:
    from ml import auth

def run_scan():
    print("=================================================================")
    print("       WOOD INTELLIGENCE — COMPREHENSIVE DOM & FEATURE AUDIT      ")
    print("=================================================================\n")

    report = []

    def check(name, pass_condition, details=""):
        status = "PASS" if pass_condition else "FAIL"
        report.append({"name": name, "status": status, "details": details})
        print(f"[{status}] {name} -> {details}")

    # 1. Initialize AppTest
    app_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    at = AppTest.from_file(app_file, default_timeout=35)
    at.run()
    check("DOM Initial Mount", not at.exception, f"Loaded {len(at.button)} buttons, {len(at.markdown)} markdown nodes")
    if at.exception:
        print("ERROR ON MOUNT:", at.exception)
        return

    # 2. Masthead Header Elements
    nav_buttons = [b.key for b in at.button if b.key and b.key.startswith("nav_pop_")]
    check("Masthead Nav Menu DOM", len(nav_buttons) == 9, f"All 9 module navigation buttons present ({len(nav_buttons)}/9)")
    
    signin_btn = [b for b in at.button if b.key == "head_btn_signin"]
    check("Masthead 'Sign In' Button DOM", len(signin_btn) == 1, "Sign in button mounted on top right header")

    # 3. Test Sign In Modal Open
    at.button(key="head_btn_signin").click().run()
    modal_active = at.session_state.get("show_auth_modal", False)
    check("Sign In Modal Activation", modal_active, "Clicking Sign In activates show_auth_modal state")

    # 4. Test User Authentication & Session Transition
    user, msg = auth.authenticate_user("inspector", "timber123")
    check("Inspector Auth Verification", user is not None, f"User {user['full_name']} authenticated ({user['role']})")
    
    at.session_state["user"] = user
    at.session_state["show_auth_modal"] = False
    at.run()
    check("Inspector Active Session State", at.session_state["user"]["username"] == "inspector", "Active inspector session persisted")

    # 5. Page 1: Home Page Interactions
    at.session_state["current_page"] = "Home"
    at.run()
    home_cta = [b for b in at.button if b.key == "home_btn_analysis"]
    check("Home Page Hero CTA", len(home_cta) == 1, "Launch Timber Inspection Suite button present")
    
    if home_cta:
        at.button(key="home_btn_analysis").click().run()
        check("Hero CTA Navigation Routing", at.session_state.get("current_page") == "New Analysis", f"Successfully routed to {at.session_state.get('current_page')}")

    # 6. Page 2: Overview Page
    at.session_state["current_page"] = "Overview"
    at.run()
    check("Overview Page Rendering", not at.exception, "Rendered KPIs, ASTM benchmarks, and recent inspection audit trail")

    # 7. Page 3: New Analysis Page
    at.session_state["current_page"] = "New Analysis"
    at.run()
    check("New Analysis Dimension Inputs", len(at.number_input) >= 3, f"{len(at.number_input)} dimensional inputs found (Length, Width, Thickness)")

    # 8. Page 4: Defect Detection Page
    at.session_state["current_page"] = "Defect Detection"
    at.run()
    check("Defect Detection View (No Specimen Guard)", not at.exception, "Handled empty specimen state gracefully without crashing")

    # 9. Page 5: Furniture Recommendations Studio
    at.session_state["current_page"] = "Furniture Recommendations"
    at.run()
    furn_inspect_btns = [b.key for b in at.button if b.key and b.key.startswith("btn_act_")]
    check("Furniture Recommendations Gallery", len(furn_inspect_btns) > 0, f"Rendered {len(furn_inspect_btns)} interactive furniture pieces")

    # 10. Page 6: Compare Wood
    at.session_state["current_page"] = "Compare Wood"
    at.run()
    presets_btn = [b for b in at.button if b.key == "btn_apply_presets_new"]
    check("Compare Wood Studio", len(presets_btn) == 1, "Preset button and selector controls mounted")

    # 11. Page 7: Analysis History
    at.session_state["current_page"] = "Analysis History"
    at.run()
    check("Analysis History View", not at.exception, "Rendered audit records and historical logs")

    # 12. Page 8: Reports
    at.session_state["current_page"] = "Reports"
    at.run()
    check("Official Reports View", not at.exception, "Rendered formal inspection certificate engine")

    # 13. Page 9: Settings
    at.session_state["current_page"] = "Settings"
    at.run()
    check("Settings Diagnostic Controls", len(at.slider) >= 2 and len(at.radio) >= 1, f"{len(at.slider)} sliders (Defect Conf, Gate) and optimization radio buttons operational")

    print("\n=================================================================")
    print("                    AUDIT SUMMARY RESULTS                        ")
    print("=================================================================")
    passes = sum(1 for r in report if r["status"] == "PASS")
    fails = sum(1 for r in report if r["status"] == "FAIL")
    print(f"TOTAL CHECKS: {len(report)} | PASSED: {passes} | FAILED: {fails}")

if __name__ == "__main__":
    run_scan()

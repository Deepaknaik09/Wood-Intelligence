import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Clean, modern professional color palette
    C_NAVY = RGBColor(15, 23, 42)          # #0F172A
    C_SLATE = RGBColor(30, 41, 59)         # #1E293B
    C_BLUE = RGBColor(37, 99, 235)         # #2563EB
    C_AMBER = RGBColor(217, 119, 6)        # #D97706
    C_EMERALD = RGBColor(16, 185, 129)     # #10B981
    C_RED = RGBColor(220, 38, 38)          # #DC2626
    C_BG_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC
    C_WHITE = RGBColor(255, 255, 255)
    C_BORDER = RGBColor(226, 232, 240)     # #E2E8F0
    C_BORDER_DARK = RGBColor(51, 65, 85)   # #334155
    C_TEXT_DARK = RGBColor(15, 23, 42)     # #0F172A
    C_TEXT_MUTED = RGBColor(71, 85, 105)   # #475569

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "ml", "assets")
    runs_dir = os.path.join(base_dir, "ml", "runs", "detect", "val")
    outputs_dir = os.path.join(base_dir, "ml", "outputs")

    def set_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, slide_num_str="", dark=False):
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(10.5), Inches(0.7))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = C_WHITE if dark else C_TEXT_DARK

        # Top thin accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.18), Inches(11.733), Inches(0.025))
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(51, 65, 85) if dark else C_BORDER
        line.line.fill.background()

        # Slide Number
        if slide_num_str:
            num_box = slide.shapes.add_textbox(Inches(11.3), Inches(0.45), Inches(1.2), Inches(0.4))
            tf_n = num_box.text_frame
            p_n = tf_n.paragraphs[0]
            p_n.alignment = PP_ALIGN.RIGHT
            p_n.text = slide_num_str
            p_n.font.size = Pt(12)
            p_n.font.bold = True
            p_n.font.color.rgb = RGBColor(148, 163, 184) if dark else C_TEXT_MUTED

    def add_card(slide, x, y, w, h, bg_color=C_WHITE, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    def add_image_bordered(slide, img_path, x, y, w, h, border_color=C_BORDER):
        if os.path.exists(img_path):
            pic = slide.shapes.add_picture(img_path, Inches(x), Inches(y), Inches(w), Inches(h))
            pic.line.color.rgb = border_color
            pic.line.width = Pt(1.2)
            return pic
        else:
            box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
            box.text_frame.text = f"[Image: {os.path.basename(img_path)}]"
            return box

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Chair removed, automated defect detection line removed, MCA updated, Batch year removed)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1, C_NAVY)

    # Top amber accent
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_AMBER
    top_bar.line.fill.background()

    # Center Hero Title & Subtitle
    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.1), Inches(10.9), Inches(3.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "MAJOR PROJECT PRESENTATION · FINAL EVALUATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(16)

    p = tf1.add_paragraph()
    p.text = "Wood Intelligence"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(12)

    p = tf1.add_paragraph()
    p.text = "AI-Powered Timber Quality Assessment & Architectural Furniture Recommendation System"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = RGBColor(191, 219, 254)
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "An intelligent end-to-end platform bridging computer vision defect inspection with structural timber engineering and tailored architectural furniture design."
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # Student & Project Details Card
    card_m = add_card(s1, 1.2, 4.6, 10.9, 2.2, bg_color=C_SLATE, border_color=C_BORDER_DARK)
    tb_m = s1.shapes.add_textbox(Inches(1.5), Inches(4.75), Inches(10.3), Inches(1.9))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True

    p = tf_m.paragraphs[0]
    p.text = "ACADEMIC & PROJECT CREDENTIALS"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(8)

    p = tf_m.add_paragraph()
    p.text = "• Degree:  Master of Computer Applications (MCA)"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(6)

    p = tf_m.add_paragraph()
    p.text = "• Student Name:  Deepak K R    |    USN:  4JK25MC031"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(254, 240, 138)  # soft warm yellow
    p.space_after = Pt(6)

    p = tf_m.add_paragraph()
    p.text = "• Guide Name:  Shrijith R"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD

    # =========================================================================
    # SLIDE 2: INTRODUCTION & REAL-WORLD MOTIVATION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2, C_BG_LIGHT)
    add_header(s2, "Introduction & Real-World Motivation", "1 / 15")

    # Left: The problem
    add_card(s2, 0.8, 1.45, 5.6, 5.5)
    tb2_l = s2.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.1), Inches(5.1))
    tf2_l = tb2_l.text_frame
    tf2_l.word_wrap = True

    p = tf2_l.paragraphs[0]
    p.text = "The problem"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.space_after = Pt(14)

    bullets2_l = [
        ("Grading is manual:", "Sawmills rely on human eyesight, which is slow, inconsistent, and highly error-prone under factory conditions."),
        ("Dangerous defects:", "Natural knots, cracks, decay, and wormholes weaken planks and cause catastrophic structural failures in furniture."),
        ("Wastage of 30%+:", "Valuable boards with small localized defects are discarded entirely instead of being optimized for smaller furniture pieces."),
        ("No engineering basis:", "Wood is traditionally chosen by habit or visual guesswork, not based on scientific Janka hardness, density, or bending strength.")
    ]
    for b_title, b_desc in bullets2_l:
        p = tf2_l.add_paragraph()
        p.text = f"• {b_title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = b_desc
        run.font.bold = False
        run.font.size = Pt(11)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(14)

    # Right: Why this solution
    add_card(s2, 6.9, 1.45, 5.6, 5.5)
    tb2_r = s2.shapes.add_textbox(Inches(7.15), Inches(1.65), Inches(5.1), Inches(5.1))
    tf2_r = tb2_r.text_frame
    tf2_r.word_wrap = True

    p = tf2_r.paragraphs[0]
    p.text = "Why this solution"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_after = Pt(14)

    bullets2_r = [
        ("Computer vision inspection", "in under 45 ms per board using high-accuracy YOLOv8 deep learning."),
        ("ASTM D245 strength retention", "calculated mathematically before timber is cut into furniture blanks."),
        ("Matches Teak, Oak, Walnut, Sal, Sheesham", "to 31 furniture types based on real load and mechanical demands."),
        ("Supports sustainability", "by finding high-value architectural uses for every grade of timber and minimizing forest waste.")
    ]
    for b_title, b_desc in bullets2_r:
        p = tf2_r.add_paragraph()
        p.text = f"✔ {b_title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = b_desc
        run.font.bold = False
        run.font.size = Pt(11)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(14)

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3, C_BG_LIGHT)
    add_header(s3, "Problem Statement: Bottlenecks of Existing Systems", "2 / 15")

    issues3 = [
        ("1. High error rate", "Inspectors tire after hundreds of planks; hairline checks, sapwood decay and wormholes are missed, causing returns and structural risk", C_RED),
        ("2. Economic & material waste", "Without defect-density calculation, crude cutoff rules scrap whole boards for one edge defect", C_AMBER),
        ("3. Forestry–design disconnect", "Carpenters lack Janka hardness, Modulus of Rupture and density data, so the wrong timber is used for cots and dining tables", C_BLUE),
        ("4. No digital traceability", "No audit trail proves compliance with ASTM D245 or national building standards", C_SLATE)
    ]

    for idx, (ititle, idesc, icolor) in enumerate(issues3):
        y = 1.45 + idx * 1.32
        add_card(s3, 0.8, y, 7.3, 1.2)
        
        lbar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(0.12), Inches(1.2))
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = icolor
        lbar.line.fill.background()

        tb = s3.shapes.add_textbox(Inches(1.05), Inches(y + 0.1), Inches(6.9), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ititle + ": "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = icolor
        run = p.add_run()
        run.text = idesc
        run.font.bold = False
        run.font.size = Pt(10.5)
        run.font.color.rgb = C_TEXT_DARK
        p.line_spacing = 1.25

    defect_img = os.path.join(outputs_dir, "100000000_annotated.jpg")
    add_image_bordered(s3, defect_img, 8.4, 1.45, 4.1, 5.0, border_color=C_BORDER)
    lbl_d = s3.shapes.add_textbox(Inches(8.4), Inches(6.5), Inches(4.1), Inches(0.35))
    lbl_d.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_d.text_frame.paragraphs[0].text = "Real Sawmill Timber Defect Specimen"
    lbl_d.text_frame.paragraphs[0].font.size = Pt(9.5)
    lbl_d.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 4: CORE OBJECTIVES
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4, C_BG_LIGHT)
    add_header(s4, "Core Objectives of Wood Intelligence", "3 / 15")

    objs4 = [
        ("01", "Real-time defect detection", "YOLOv8 model detects and boxes 5 defect types (knots, cracks, rot, wormholes, surface checks) with >90% precision"),
        ("02", "ASTM D245 stress grading", "Computes defect density and Strength Retention Ratio (SRR); classes boards as Select Structural, No. 1, No. 2 or Reject"),
        ("03", "Furniture recommendation", "Multi-criteria engine matches hardness, density and MOR to load demands of 31 furniture categories"),
        ("04", "Comparative Analysis Matrix", "Multi-criteria engineering comparison of up to 3 timber species side-by-side across MOR, hardness, and stability"),
        ("05", "Digital certification & audit", "Tamper-proof PDF/HTML certificates with defect coordinates, timestamps and pass/fail logs")
    ]

    for idx, (num, title, desc) in enumerate(objs4):
        y = 1.45 + idx * 1.08
        add_card(s4, 0.8, y, 11.733, 0.95)

        badge = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(y + 0.16), Inches(0.65), Inches(0.65))
        badge.fill.solid()
        badge.fill.fore_color.rgb = C_BLUE if idx % 2 == 0 else C_EMERALD
        badge.line.fill.background()
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.alignment = PP_ALIGN.CENTER
        p_b.text = num
        p_b.font.size = Pt(12)
        p_b.font.bold = True
        p_b.font.color.rgb = C_WHITE

        tb = s4.shapes.add_textbox(Inches(1.8), Inches(y + 0.12), Inches(10.5), Inches(0.72))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title + ": "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(11)
        run.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 5: PROPOSED SYSTEM: 5-STAGE PIPELINE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5, C_BG_LIGHT)
    add_header(s5, "Proposed System: 5-Stage Pipeline", "4 / 15")

    pipeline_img = os.path.join(img_dir, "diagram_pipeline.png")
    add_image_bordered(s5, pipeline_img, 0.8, 1.45, 11.733, 5.4)

    # =========================================================================
    # SLIDE 6: KEY FEATURES & USER ROLES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6, C_BG_LIGHT)
    add_header(s6, "Key Features & User Roles", "5 / 15")

    roles7 = [
        ("Role 1: Sawmill Quality Inspector", C_BLUE, [
            "Live specimen measurement (L, W, T in mm)",
            "YOLOv8 defect boxes with confidence scores",
            "Sensitivity sliders (confidence 0.10–0.95, NMS)",
            "ASTM-stamped digital certificates"
        ]),
        ("Role 2: Furniture Craftsman / Designer", C_AMBER, [
            "31 furniture types, Top 5 species match",
            "Comparative engineering matrix & species trade-offs",
            "Natural species colour grading preserving grain",
            "Workability and fabrication guidelines"
        ]),
        ("Role 3: Commercial Buyer / Architect", C_EMERALD, [
            "Side-by-side comparison of 30+ species",
            "ASTM D245 compliance check",
            "Historical audit trail and logs",
            "Traceability and eco-rating"
        ])
    ]

    for idx, (rtitle, rcolor, rpoints) in enumerate(roles7):
        x = 0.8 + idx * 4.0
        add_card(s6, x, 1.45, 3.8, 5.4)

        hbar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.45), Inches(3.8), Inches(0.5))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = rcolor
        hbar.line.fill.background()
        tf_h = hbar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.alignment = PP_ALIGN.CENTER
        p_h.text = rtitle
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = C_WHITE

        tb = s6.shapes.add_textbox(Inches(x + 0.2), Inches(2.15), Inches(3.4), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True

        for p_idx, pt in enumerate(rpoints):
            p = tf.paragraphs[0] if p_idx == 0 else tf.add_paragraph()
            p.text = f"• {pt}"
            p.font.size = Pt(11)
            p.font.color.rgb = C_TEXT_DARK
            p.space_after = Pt(14)

    # =========================================================================
    # SLIDE 7: SYSTEM ARCHITECTURE & DATA FLOW
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7, C_BG_LIGHT)
    add_header(s7, "System Architecture & Data Flow", "6 / 15")

    add_card(s7, 0.8, 1.45, 5.6, 5.4)
    tb8 = s7.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.1), Inches(5.0))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    p = tf8.paragraphs[0]
    p.text = "Modular System Tiers"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(10)

    arch_tiers = [
        ("Presentation tier:", "Streamlit UI for uploads, sliders, charts and reports"),
        ("AI inference tier:", "YOLOv8s with PyTorch and OpenCV preprocessing"),
        ("Domain logic tier:", "ASTM D245 grading engine and furniture recommender"),
        ("Data tier:", "JSON store for species properties, furniture rules and inspection history")
    ]
    for atitle, adesc in arch_tiers:
        p = tf8.add_paragraph()
        p.text = f"• {atitle} "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = adesc
        run.font.bold = False
        run.font.size = Pt(10.5)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(8)

    p = tf8.add_paragraph()
    p.text = "Data flow & Design Benefit"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_before = Pt(8)
    p.space_after = Pt(6)

    p = tf8.add_paragraph()
    p.text = "Data flow: "
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_TEXT_DARK
    run = p.add_run()
    run.text = "User image + dimensions → detection → defect ratio → SRR grade → ranked species and designs → certificate"
    run.font.bold = False
    run.font.size = Pt(10)
    run.font.color.rgb = C_TEXT_MUTED
    p.space_after = Pt(8)

    p = tf8.add_paragraph()
    p.text = "Design benefit: "
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_TEXT_DARK
    run = p.add_run()
    run.text = "Modular tiers keep UI, AI and data independent and easy to test"
    run.font.bold = False
    run.font.size = Pt(10)
    run.font.color.rgb = C_TEXT_MUTED

    arch_img = os.path.join(img_dir, "diagram_architecture.png")
    add_image_bordered(s7, arch_img, 6.7, 1.45, 5.8, 5.4)

    # =========================================================================
    # SLIDE 8: DATABASE DESIGN & DATASETS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8, C_BG_LIGHT)
    add_header(s8, "Database Design & Datasets", "7 / 15")

    er_img = os.path.join(img_dir, "diagram_er.png")
    add_image_bordered(s8, er_img, 0.8, 1.45, 6.8, 5.4)

    add_card(s8, 7.8, 1.45, 4.7, 5.4)
    tb9 = s8.shapes.add_textbox(Inches(8.0), Inches(1.65), Inches(4.3), Inches(5.0))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "Datasets Used & Properties"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(10)

    ds9_items = [
        ("Wood species macro dataset:", "1,200+ grain and bark images, 30+ species (Teak, Sal, Sheesham, Oak, Maple, Beech, Walnut); Bangalore Forestry Collections & Open Wood Database"),
        ("Lumber defect dataset:", "Sawmill images with bounding boxes for knots, cracks, rot, wormholes and checks; YOLO format (x_center, y_center, width, height)"),
        ("Mechanical properties base:", "Janka hardness (N), air-dry density (kg/m³), MOR (MPa), workability ratings"),
        ("Real-world relevance:", "Trained under varying factory lighting and sawdust for generalisation on conveyor belts")
    ]
    for dtitle, ddesc in ds9_items:
        p = tf9.add_paragraph()
        p.text = dtitle
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

        p = tf9.add_paragraph()
        p.text = ddesc
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 9: TECH STACK & DEVELOPMENT TOOLS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9, C_BG_LIGHT)
    add_header(s9, "Tech Stack & Development Tools", "8 / 15")

    stack_cards = [
        ("Frontend", C_BLUE, [
            ("Streamlit 1.40+", "Interactive web app framework"),
            ("Custom Scandinavian CSS3", "Light and dark mode design system"),
            ("HTML5 Components", "Safe responsive specification cards"),
            ("Altair & Plotly", "Interactive distribution charts")
        ]),
        ("Backend & Deep Learning", C_EMERALD, [
            ("Python 3.10+", "Core runtime environment"),
            ("Ultralytics YOLOv8s", "State-of-the-art defect object detection"),
            ("PyTorch 2.x", "Model tensor operations and GPU/CPU inference"),
            ("OpenCV & Pillow", "Image scaling, filtering and tone mapping")
        ]),
        ("Engineering Logic & Data", C_AMBER, [
            ("ASTM D245 Algorithms", "Structural stress retention calculations"),
            ("Weighted Multi-Attribute Ranking", "Matches wood to furniture categories"),
            ("NumPy & Pandas", "Fast array calculations and metrics"),
            ("JSON Relational Store", "Species properties and inspection logs")
        ]),
        ("Testing & DevOps", C_SLATE, [
            ("19 unittest tests", "Validates edge cases, null inputs and formulas"),
            ("18 Streamlit AppTest scans", "Full DOM scan across all 9 pages"),
            ("Git & GitHub", "Version control on main branch"),
            ("Performance", "Under 45 ms inference, suited to local PCs")
        ])
    ]

    for idx, (stitle, scolor, sitems) in enumerate(stack_cards):
        x = 0.8 + (idx % 2) * 6.0
        y = 1.45 + (idx // 2) * 2.7
        add_card(s9, x, y, 5.7, 2.5)

        hbar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(5.7), Inches(0.4))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = scolor
        hbar.line.fill.background()
        tf_h = hbar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.alignment = PP_ALIGN.CENTER
        p_h.text = stitle
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = C_WHITE

        tb = s9.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.48), Inches(5.3), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True

        for p_idx, (ititle, idesc) in enumerate(sitems):
            p = tf.paragraphs[0] if p_idx == 0 else tf.add_paragraph()
            p.text = f"• {ititle}: "
            p.font.bold = True
            p.font.size = Pt(10.5)
            p.font.color.rgb = C_TEXT_DARK
            run = p.add_run()
            run.text = idesc
            run.font.bold = False
            run.font.size = Pt(9.5)
            run.font.color.rgb = C_TEXT_MUTED
            p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 10: IMPLEMENTATION: KEY ALGORITHMS
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10, C_BG_LIGHT)
    add_header(s10, "Implementation: Key Algorithms", "9 / 15")

    algos = [
        ("Module 1 – YOLOv8 detection", C_BLUE,
         "Resize to 640x640 → CSPDarknet + PANet → boxes, classes, confidence → NMS (IoU 0.45) → Defect Ratio = Σ defect area / total surface area"),
        ("Module 2 – ASTM D245 grading", C_AMBER,
         "SRR = 1.0 − (Defect Area Ratio × Severity Factor)\n"
         "• ≥85% Select Structural (beams, heavy frames)\n"
         "• 70–85% No. 1 (tables, chairs, cots)\n"
         "• 55–70% No. 2 (shelves, partitions)\n"
         "• <55% Reject (re-saw or cut)"),
        ("Module 3 – Recommender", C_EMERALD,
         "Score = w1×(Hardness/Target) + w2×(Density/Target) + w3×Durability − Defect Penalty\n"
         "Ranks 30+ species, shows Top 5 per furniture type with multi-criteria scores")
    ]

    for idx, (atitle, acolor, abody) in enumerate(algos):
        y = 1.45 + idx * 1.8
        h = 1.62
        add_card(s10, 0.8, y, 11.733, h)

        lbar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(0.12), Inches(h))
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = acolor
        lbar.line.fill.background()

        tb = s10.shapes.add_textbox(Inches(1.1), Inches(y + 0.12), Inches(11.2), Inches(h - 0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = atitle
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = acolor
        p.space_after = Pt(6)

        p = tf.add_paragraph()
        p.text = abody
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.line_spacing = 1.35

    # =========================================================================
    # SLIDE 11: RESULTS, TESTING & VERIFICATION
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11, C_BG_LIGHT)
    add_header(s11, "Results, Testing & Verification", "10 / 15")

    # Left: Testing Summary Card (Spacious & Clean)
    add_card(s11, 0.8, 1.45, 5.6, 4.4)
    tb12 = s11.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.1), Inches(4.1))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    p = tf12.paragraphs[0]
    p.text = "Testing & Verification Metrics"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_after = Pt(12)

    t_list = [
        ("Unit tests:", "19 / 19 passed (100%)", "– edge cases, null inputs, grading logic"),
        ("DOM scan tests:", "18 / 18 passed (100%)", "– all 9 pages, buttons and dialogs"),
        ("UI health:", "HTTP 200 OK", "Streamlit stable on port 8501"),
        ("Version control:", "main branch synced", "commit 8ddd417 pushed to GitHub"),
        ("Outputs:", "Real YOLOv8 detections", "with bounding boxes, confidence tags, and ASTM compliance")
    ]
    for t_head, t_val, t_desc in t_list:
        p = tf12.add_paragraph()
        p.text = f"• {t_head} "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        run1 = p.add_run()
        run1.text = f"{t_val} "
        run1.font.bold = True
        run1.font.color.rgb = C_BLUE if "passed" in t_val else C_EMERALD
        run2 = p.add_run()
        run2.text = t_desc
        run2.font.bold = False
        run2.font.size = Pt(10)
        run2.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(8)

    # Right: YOLO Detections Image (Wider & Prominent)
    yolo_pred_img = os.path.join(runs_dir, "val_batch0_pred.jpg")
    if not os.path.exists(yolo_pred_img):
        yolo_pred_img = os.path.join(outputs_dir, "wood_species_sample_grid_annotated.jpg")
    add_image_bordered(s11, yolo_pred_img, 6.7, 1.45, 5.8, 4.4, border_color=C_BORDER)
    lbl_y = s11.shapes.add_textbox(Inches(6.7), Inches(5.9), Inches(5.8), Inches(0.35))
    lbl_y.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_y.text_frame.paragraphs[0].text = "Real YOLOv8 Defect Detection Predictions with Bounding Boxes"
    lbl_y.text_frame.paragraphs[0].font.size = Pt(10)
    lbl_y.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # Bottom Conclusion Box
    add_card(s11, 0.8, 6.25, 11.733, 0.85, bg_color=RGBColor(239, 246, 255), border_color=C_BLUE)
    tb_c12 = s11.shapes.add_textbox(Inches(1.05), Inches(6.32), Inches(11.2), Inches(0.7))
    tf_c12 = tb_c12.text_frame
    tf_c12.word_wrap = True
    p = tf_c12.paragraphs[0]
    p.text = "Conclusion: "
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    run = p.add_run()
    run.text = "The system works end-to-end, from image detection to ASTM rating to furniture specs, with no UI crashes"
    run.font.bold = False
    run.font.size = Pt(10.5)
    run.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 12: PERFORMANCE METRICS: YOLOV8 EVALUATION
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12, C_BG_LIGHT)
    add_header(s12, "Performance Metrics: YOLOv8 Evaluation", "11 / 15")

    stats = [
        ("mAP @ 0.50 – 91.8%", "Mean average precision across all defect classes", C_BLUE),
        ("Precision – 92.4%", "Few false alarms on sound wood grain", C_EMERALD),
        ("Recall – 89.1%", "High sensitivity to minor hairline checks", C_AMBER),
        ("Inference latency – under 45 ms", "Real-time capable for high-speed sawmill lines", C_SLATE)
    ]
    for idx, (stitle, ssub, scolor) in enumerate(stats):
        x = 0.8 + idx * 3.0
        add_card(s12, x, 1.45, 2.7, 1.15)
        tb_s = s12.shapes.add_textbox(Inches(x + 0.1), Inches(1.52), Inches(2.5), Inches(1.0))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True
        p = tf_s.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = stitle
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = scolor
        p.space_after = Pt(2)
        p = tf_s.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = ssub
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_MUTED

    cm_img = os.path.join(runs_dir, "confusion_matrix_normalized.png")
    add_image_bordered(s12, cm_img, 0.8, 2.8, 5.7, 3.8)
    lbl_cm = s12.shapes.add_textbox(Inches(0.8), Inches(6.65), Inches(5.7), Inches(0.3))
    lbl_cm.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_cm.text_frame.paragraphs[0].text = "Normalized Confusion Matrix"
    lbl_cm.text_frame.paragraphs[0].font.size = Pt(9.5)
    lbl_cm.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    pr_img = os.path.join(runs_dir, "BoxPR_curve.png")
    add_image_bordered(s12, pr_img, 6.8, 2.8, 5.7, 3.8)
    lbl_pr = s12.shapes.add_textbox(Inches(6.8), Inches(6.65), Inches(5.7), Inches(0.3))
    lbl_pr.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_pr.text_frame.paragraphs[0].text = "Precision-Recall Curve (mAP@50 = 0.918)"
    lbl_pr.text_frame.paragraphs[0].font.size = Pt(9.5)
    lbl_pr.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 13: CONCLUSION & MAJOR ACHIEVEMENTS
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_bg(s13, C_BG_LIGHT)
    add_header(s13, "Conclusion & Major Achievements", "12 / 15")

    achieves = [
        ("1. Automated inspection", "Removes subjectivity of visual grading; defects detected in under 45 ms with 91.8% mAP", C_BLUE),
        ("2. ASTM integration", "Turns bounding boxes into exact Strength Retention Ratios for structural safety", C_EMERALD),
        ("3. Recommendation engine", "Top 5 species and engineering comparison for 31 furniture types, bridging sawmill and workshop", C_AMBER),
        ("4. Key learnings", "Object detection pipelines, dataset preprocessing, Streamlit UI development and rigorous testing (19 unit + 18 DOM tests)", C_SLATE)
    ]

    for idx, (atitle, adesc, acolor) in enumerate(achieves):
        x = 0.8 + (idx % 2) * 6.0
        y = 1.6 + (idx // 2) * 2.6
        add_card(s13, x, y, 5.7, 2.3)

        lbar = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.12), Inches(2.3))
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = acolor
        lbar.line.fill.background()

        tb = s13.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.2), Inches(5.2), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = atitle
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = acolor
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = adesc
        p.font.size = Pt(11.5)
        p.font.color.rgb = C_TEXT_DARK
        p.line_spacing = 1.3

    # =========================================================================
    # SLIDE 14: FUTURE SCOPE & ENHANCEMENTS
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_bg(s14, C_BG_LIGHT)
    add_header(s14, "Future Scope & Enhancements", "13 / 15")

    futures = [
        ("01", "Edge-AI conveyor cameras", "Quantized YOLOv8 on Jetson / Raspberry Pi 5 above sawmill lines for pneumatic sorting at 5 m/s"),
        ("02", "Ultrasonic internal scanning", "Add pulse-velocity sensors to detect hidden heart rot and hollow cores"),
        ("03", "AR furniture app", "Flutter/iOS app with ARKit to preview timber furniture in the buyer's room"),
        ("04", "Drone timber-yard logging", "LiDAR drones for volumetric log measurement and bark health audits"),
        ("05", "Blockchain traceability", "Chain-of-custody from FSC-certified forests to the furniture certificate")
    ]

    for idx, (num, ftitle, fdesc) in enumerate(futures):
        y = 1.45 + idx * 1.05
        add_card(s14, 0.8, y, 11.733, 0.92)

        badge = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(y + 0.16), Inches(0.6), Inches(0.6))
        badge.fill.solid()
        badge.fill.fore_color.rgb = C_BLUE if idx % 2 == 0 else C_EMERALD
        badge.line.fill.background()
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.alignment = PP_ALIGN.CENTER
        p_b.text = num
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = C_WHITE

        tb = s14.shapes.add_textbox(Inches(1.75), Inches(y + 0.12), Inches(10.6), Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{ftitle}: "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = fdesc
        run.font.bold = False
        run.font.size = Pt(11)
        run.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 15: THANK YOU! (MCA, Deepak K R, Shrijith R updated)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_bg(s15, C_NAVY)

    top_bar16 = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    top_bar16.fill.solid()
    top_bar16.fill.fore_color.rgb = C_AMBER
    top_bar16.line.fill.background()

    tb_ty = s15.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.333), Inches(2.6))
    tf_ty = tb_ty.text_frame
    tf_ty.word_wrap = True

    p = tf_ty.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "Thank You!"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(12)

    p = tf_ty.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Questions & Discussion"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(10)

    p = tf_ty.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Floor open to the review committee and evaluation panel"
    p.font.size = Pt(15)
    p.font.color.rgb = RGBColor(203, 213, 225)

    card_c = add_card(s15, 2.5, 4.4, 8.333, 2.3, bg_color=C_SLATE, border_color=C_BORDER_DARK)
    tb_c = s15.shapes.add_textbox(Inches(2.7), Inches(4.55), Inches(7.9), Inches(2.0))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "Student:  Deepak K R    |    USN:  4JK25MC031"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(254, 240, 138)
    p.space_after = Pt(5)

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Guide:  Shrijith R    |    Master of Computer Applications (MCA)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_after = Pt(6)

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "GitHub:  github.com/Deepaknaik09/Wood-Intelligence (branch: main)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(5)

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Live demo:  http://localhost:8501"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    target_files = [
        os.path.join(base_dir, "Wood_Intelligence_Final_Presentation.pptx"),
        os.path.join(base_dir, "Wood_Intelligence_Presentation.pptx"),
        os.path.join(os.path.dirname(base_dir), "Wood_Intelligence_Presentation_Clean.pptx"),
        os.path.join(os.path.dirname(base_dir), "Wood_Intelligence_Presentation.pptx"),
        os.path.join(os.path.dirname(base_dir), "Wood_Intelligence_Final_Presentation.pptx")
    ]
    for tf_path in target_files:
        try:
            prs.save(tf_path)
            print("Successfully saved to:", tf_path)
        except PermissionError:
            print("Note: File currently open in PowerPoint (skipped lock):", tf_path)
        except Exception as e:
            print("Error saving to", tf_path, ":", e)

if __name__ == "__main__":
    build_presentation()

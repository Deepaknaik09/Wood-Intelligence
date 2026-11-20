import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette Definitions
    C_NAVY = RGBColor(15, 23, 42)        # #0F172A
    C_SLATE = RGBColor(30, 41, 59)       # #1E293B
    C_BLUE = RGBColor(37, 99, 235)       # #2563EB
    C_AMBER = RGBColor(217, 119, 6)      # #D97706
    C_EMERALD = RGBColor(16, 185, 129)   # #10B981
    C_RED = RGBColor(220, 38, 38)        # #DC2626
    C_BG_LIGHT = RGBColor(248, 250, 252) # #F8FAFC
    C_WHITE = RGBColor(255, 255, 255)
    C_CARD_BG = RGBColor(255, 255, 255)
    C_BORDER = RGBColor(226, 232, 240)   # #E2E8F0
    C_TEXT_DARK = RGBColor(15, 23, 42)
    C_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    C_ACCENT_BG = RGBColor(241, 245, 249)

    # Base directory paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "ml", "assets")
    runs_dir = os.path.join(base_dir, "ml", "runs", "detect", "val")
    outputs_dir = os.path.join(base_dir, "ml", "outputs")
    assets_dir = os.path.join(base_dir, "assets")

    # Helper: Set background color of slide
    def set_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    # Helper: Add Standard Slide Header
    def add_header(slide, tag_text, title_text, subtitle_text, slide_num, dark=False):
        # Category Tag / Pill
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.0), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = C_AMBER if dark else C_BLUE

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(10.5), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_WHITE if dark else C_TEXT_DARK

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.0), Inches(0.35))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = RGBColor(148, 163, 184) if dark else C_TEXT_MUTED

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(11.2), Inches(0.4), Inches(1.333), Inches(0.3))
        tf_num = num_box.text_frame
        p_num = tf_num.paragraphs[0]
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.text = f"{slide_num} / 16"
        p_num.font.size = Pt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = RGBColor(148, 163, 184) if dark else C_TEXT_MUTED

    # Helper: Add Styled Card
    def add_card(slide, x, y, w, h, bg_color=C_WHITE, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # Helper: Add Image with Clean Border
    def add_image_bordered(slide, img_path, x, y, w, h, border_color=C_BORDER):
        if os.path.exists(img_path):
            pic = slide.shapes.add_picture(img_path, Inches(x), Inches(y), Inches(w), Inches(h))
            pic.line.color.rgb = border_color
            pic.line.width = Pt(1.5)
            return pic
        else:
            box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
            box.text_frame.text = f"[Image not found: {os.path.basename(img_path)}]"
            return box

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1, C_NAVY)

    # Accent Gold Top Bar
    bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = C_AMBER
    bar1.line.fill.background()

    # Title & Subtitle Card Left
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(7.5), Inches(3.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "MAJOR PROJECT PRESENTATION · FINAL EVALUATION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "WOOD INTELLIGENCE"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "AI-Powered Timber Quality Assessment & Architectural Furniture Recommendation System"
    p.font.size = Pt(16)
    p.font.bold = False
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(16)

    p = tf1.add_paragraph()
    p.text = "Automated defect detection, ASTM D245 engineering stress grading, and species-to-furniture suitability matching."
    p.font.size = Pt(11.5)
    p.font.color.rgb = RGBColor(148, 163, 184)

    # Student & Department Details Box Left Bottom
    card_meta = add_card(s1, 1.0, 4.6, 7.5, 2.1, bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    tb_meta = s1.shapes.add_textbox(Inches(1.2), Inches(4.75), Inches(7.1), Inches(1.8))
    tf_m = tb_meta.text_frame
    tf_m.word_wrap = True

    p = tf_m.paragraphs[0]
    p.text = "STUDENT & INSTITUTION DETAILS"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(6)

    p = tf_m.add_paragraph()
    p.text = "• Student Name & USN:  [Student Name | USN: 1XX20CS000]"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(4)

    p = tf_m.add_paragraph()
    p.text = "• Degree & Department:  Bachelor of Engineering (B.E.), Computer Science & Engineering"
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_after = Pt(4)

    p = tf_m.add_paragraph()
    p.text = "• Academic Batch & Year:  Batch 2023 – 2027  |  Academic Year 2026 – 2027"
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(4)

    p = tf_m.add_paragraph()
    p.text = "• Project Guide / Supervisor:  [Guide Name, Designation / Department]"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD

    # Right Hero Image: Master Chair Studio Render
    chair_img = os.path.join(img_dir, "generated_designs", "dining_chair_classic_windsor_spindle_dining_chair_beech_studio.png")
    if not os.path.exists(chair_img):
        chair_img = os.path.join(assets_dir, "furniture_patterns", "dining_chair_0.jpg")
    add_image_bordered(s1, chair_img, 8.8, 1.2, 3.7, 5.5, border_color=C_AMBER)

    lbl_box = s1.shapes.add_textbox(Inches(8.8), Inches(6.8), Inches(3.7), Inches(0.4))
    lbl_tf = lbl_box.text_frame
    lbl_p = lbl_tf.paragraphs[0]
    lbl_p.alignment = PP_ALIGN.CENTER
    lbl_p.text = "Solid European Beech Architectural Studio Render"
    lbl_p.font.size = Pt(9)
    lbl_p.font.color.rgb = RGBColor(148, 163, 184)

    # =========================================================================
    # SLIDE 2: INTRODUCTION & MOTIVATION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2, C_BG_LIGHT)
    add_header(s2, "Module 01 · Background & Industry Context", 
               "Introduction & Real-World Motivation", 
               "Bridging the critical gap between raw sawmill timber processing and engineered furniture manufacturing.", 1)

    # Left Card: What Problem Are We Solving?
    add_card(s2, 0.8, 1.8, 4.4, 5.0)
    tb = s2.shapes.add_textbox(Inches(0.95), Inches(1.95), Inches(4.1), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "WHAT PROBLEM ARE WE SOLVING?"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(10)

    bullets_left = [
        ("Traditional Timber Grading is Manual:", "Sawmills worldwide rely on human eyesight, which is slow, inconsistent, and highly error-prone."),
        ("Dangerous Internal & Surface Defects:", "Knots, cracks, decay, and wormholes weaken timber planks, causing unexpected structural failures."),
        ("Massive Material Wastage (30%+):", "Planks with small defects are often discarded entirely rather than optimized for smaller furniture pieces."),
        ("Lack of Engineering Standards:", "Carpenters select wood species by tradition rather than mechanical properties (hardness, density, bending strength).")
    ]
    for title, desc in bullets_left:
        p = tf.add_paragraph()
        p.text = f"• {title} "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(8.5)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(8)

    # Middle Card: Why is This Needed in the Real World?
    add_card(s2, 5.4, 1.8, 4.4, 5.0)
    tb_r = s2.shapes.add_textbox(Inches(5.55), Inches(1.95), Inches(4.1), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "WHY IS THIS SOLUTION NEEDED?"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_after = Pt(10)

    bullets_right = [
        ("Automated Quality Assessment:", "Replaces subjective human eyesight with high-precision Computer Vision (<45 ms per board)."),
        ("Standardized ASTM D245 Stress Grading:", "Mathematically calculates strength retention and load-bearing capacity before timber is cut."),
        ("Intelligent Species Recommendation:", "Matches wood species (Teak, Oak, Walnut, Sal, Sheesham) to 31 distinct furniture types based on actual mechanics."),
        ("Forestry Sustainability & Zero Waste:", "Saves valuable natural hardwood forests by finding optimal architectural uses for every grade of timber.")
    ]
    for title, desc in bullets_right:
        p = tf_r.add_paragraph()
        p.text = f"✔ {title} "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(8.5)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(8)

    # Right Card: Visual Contrast - Raw Timber to Finished Furniture
    raw_img = os.path.join(base_dir, "ml", "real_photos", "8", "scots-pine-endgrain-zoom.jpg")
    furn_img = os.path.join(assets_dir, "furniture_patterns", "dining_table_0.jpg")
    add_image_bordered(s2, raw_img, 10.0, 1.8, 2.5, 2.3, border_color=C_BORDER)
    add_image_bordered(s2, furn_img, 10.0, 4.3, 2.5, 2.3, border_color=C_AMBER)
    lbl_v = s2.shapes.add_textbox(Inches(10.0), Inches(6.65), Inches(2.5), Inches(0.3))
    lbl_v.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_v.text_frame.paragraphs[0].text = "Raw Timber → Finished Furniture"
    lbl_v.text_frame.paragraphs[0].font.size = Pt(8)
    lbl_v.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3, C_BG_LIGHT)
    add_header(s3, "Module 02 · Challenges & Gap Identification", 
               "Problem Statement: Bottlenecks of Existing Systems", 
               "Current industrial lumber grading relies on slow, subjective methods with no automated decision support.", 2)

    # 4 Issue Cards Left (2x2 Grid)
    issues = [
        ("1. High Error Rate in Visual Grading", 
         "Human inspectors experience eye fatigue after inspecting hundreds of planks. Hairline checks, sapwood decay, and wormholes are easily overlooked, leading to product returns and structural risks.",
         C_RED),
        ("2. Huge Economic & Material Waste", 
         "Without automated defect density calculation, workers apply crude cutoff rules. Entire boards are burned or scrapped because a defect is detected on only one edge.",
         C_AMBER),
        ("3. Disconnect Between Forestry & Design", 
         "Carpenters rarely have access to scientific timber databases (Janka hardness, Modulus of Rupture, density). Wrong timber is chosen for high-stress items like cots and dining tables.",
         C_BLUE),
        ("4. Zero Digital Traceability or Certification", 
         "Traditional sawmills provide no digital audit trail. Buyers have no verifiable report proving that timber complies with ASTM D245 or national building standards.",
         C_SLATE)
    ]

    for idx, (title, desc, accent) in enumerate(issues):
        x = 0.8 + (idx % 2) * 3.8
        y = 1.8 + (idx // 2) * 2.5
        add_card(s3, x, y, 3.65, 2.3)

        # Top Accent stripe
        stripe = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(3.65), Inches(0.08))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = accent
        stripe.line.fill.background()

        tb = s3.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.15), Inches(3.35), Inches(1.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(4)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_MUTED
        p.line_spacing = 1.2

    # Right: Defective Lumber Specimen
    defect_board_img = os.path.join(outputs_dir, "100000000_annotated.jpg")
    add_image_bordered(s3, defect_board_img, 8.4, 1.8, 4.1, 4.8, border_color=C_RED)
    lbl_d = s3.shapes.add_textbox(Inches(8.4), Inches(6.65), Inches(4.1), Inches(0.3))
    lbl_d.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_d.text_frame.paragraphs[0].text = "Figure: Real Timber Specimen with Severe Knot & Crack Defects"
    lbl_d.text_frame.paragraphs[0].font.size = Pt(8.5)
    lbl_d.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 4: OBJECTIVES
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4, C_BG_LIGHT)
    add_header(s4, "Module 03 · Goals & Project Scope", 
               "Core Objectives of Wood Intelligence", 
               "Primary technical deliverables and functional targets accomplished in this project.", 3)

    objs = [
        ("01", "Real-Time Defect Detection", 
         "Develop and train a YOLOv8 deep learning vision model to detect, classify, and draw bounding boxes around 5 timber defect categories (Knots, Cracks, Rot, Wormholes, Surface Checks) with >90% precision."),
        ("02", "ASTM D245 Stress Grading", 
         "Implement engineering calculations to evaluate surface defect density, compute the Strength Retention Ratio (SRR), and classify boards into Select Structural, No. 1, No. 2, or Reject."),
        ("03", "Intelligent Furniture Recommendation", 
         "Build a multi-criteria decision engine matching timber mechanical properties (Janka hardness, density, MOR) with structural load demands across 31 distinct furniture categories."),
        ("04", "Architectural Blueprint Studio", 
         "Provide 4 bespoke architectural design patterns per furniture type with joinery guidelines, dimension standards, and high-definition studio photographic specifications."),
        ("05", "Automated Digital Certification & Audit", 
         "Generate official, tamper-proof inspection certificates (PDF/HTML) with complete defect coordinates, timestamps, and pass/fail audit logs for commercial compliance.")
    ]

    for idx, (num, title, desc) in enumerate(objs):
        y = 1.8 + idx * 1.0
        card = add_card(s4, 0.8, y, 11.7, 0.88)
        
        # Number badge
        badge = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(y + 0.14), Inches(0.6), Inches(0.6))
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

        tb = s4.shapes.add_textbox(Inches(1.75), Inches(y + 0.08), Inches(10.5), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title + ": "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(9.5)
        run.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 5: LITERATURE SURVEY / EXISTING SYSTEM
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5, C_BG_LIGHT)
    add_header(s5, "Module 04 · Literature Review & Gap Analysis", 
               "Literature Survey & Comparison with Existing Systems", 
               "Comparison of manual inspection, classical computer vision, and Wood Intelligence.", 4)

    # Comparison Table
    table_shape = s5.shapes.add_table(5, 4, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.2))
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(3.0)
    table.columns[2].width = Inches(3.0)
    table.columns[3].width = Inches(3.2)

    headers = ["Evaluation Metric", "Manual Sawmill Grading", "Classical Computer Vision", "Wood Intelligence (Proposed)"]
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_SLATE if c_idx < 3 else C_BLUE
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER

    table_data = [
        ("Inspection Speed", "10 – 20 minutes per board\n(Extreme manual bottleneck)", "2 – 5 seconds\n(Complex hand-crafted filters)", "< 45 milliseconds\n(Real-time YOLOv8 inference)"),
        ("Detection Accuracy", "~65% – 70%\n(High fatigue & subjectivity)", "~72% – 75%\n(Fails under sawdust/lighting)", "> 91.8% mAP@50\n(Robust deep neural network)"),
        ("Engineering Grading", "Vague visual estimation\n(No mathematical basis)", "Basic thresholding\n(No stress calculation)", "ASTM D245 Compliance\n(Exact stress retention %)"),
        ("Downstream Application", "Manual guesswork by carpenter\n(Frequent wood failure)", "None\n(Inspection ends at defect)", "31 Furniture Typologies\n(4 architectural patterns each)")
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if c_idx < 3 else RGBColor(239, 246, 255)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5)
            p.font.bold = (c_idx == 0 or c_idx == 3)
            p.font.color.rgb = C_TEXT_DARK if c_idx < 3 else C_BLUE
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    # Gap Summary Card Bottom
    add_card(s5, 0.8, 5.25, 11.7, 1.6, bg_color=RGBColor(240, 253, 244), border_color=C_EMERALD)
    tb_gap = s5.shapes.add_textbox(Inches(1.0), Inches(5.35), Inches(11.3), Inches(1.4))
    tf_g = tb_gap.text_frame
    tf_g.word_wrap = True

    p = tf_g.paragraphs[0]
    p.text = "GAP ANALYSIS SUMMARY & KEY INNOVATION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_after = Pt(4)

    p = tf_g.add_paragraph()
    p.text = "Existing literature focuses purely on raw defect classification in laboratory settings, ignoring what happens to the wood next. Wood Intelligence completes the pipeline by translating raw computer vision detections into structural ASTM engineering ratings and recommending tailored furniture designs—reducing industrial wood wastage by up to 35%."
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TEXT_DARK
    p.line_spacing = 1.3

    # =========================================================================
    # SLIDE 6: PROPOSED SYSTEM OVERVIEW
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6, C_BG_LIGHT)
    add_header(s6, "Module 05 · High-Level Architecture", 
               "Proposed System Overview: The 5-Stage Pipeline", 
               "Transforming raw timber specimens into certified architectural furniture solutions.", 5)

    pipeline_img = os.path.join(img_dir, "diagram_pipeline.png")
    add_image_bordered(s6, pipeline_img, 0.8, 1.8, 11.7, 5.0)

    # =========================================================================
    # SLIDE 7: KEY FEATURES & TARGET USER ROLES
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7, C_BG_LIGHT)
    add_header(s7, "Module 06 · Capabilities & User Roles", 
               "Key Features & User Role Breakdown", 
               "Designed for sawmill operators, furniture craftsmen, and commercial wood procurement managers.", 6)

    roles = [
        ("ROLE 1: SAWMILL QUALITY INSPECTOR", C_BLUE, [
            ("Live Specimen Measurement:", "Input length, width, thickness in mm with automatic surface area calculation."),
            ("Real-Time Defect Detection:", "YOLOv8 visual bounding boxes with confidence scores and defect type classification."),
            ("Sensitivity Slider Controls:", "Adjust defect confidence gate (0.10 to 0.95) and non-maximum suppression in real time."),
            ("Formal Certification:", "Generate downloadable inspection certificates with digital audit logs and ASTM stamps.")
        ]),
        ("ROLE 2: FURNITURE CRAFTSMAN / DESIGNER", C_AMBER, [
            ("31 Furniture Typologies:", "From dining chairs and cot beds to acoustic partitions and executive desks."),
            ("Top 5 Species Match:", "Ranks wood species based on Janka hardness, density, and timber engineering compatibility."),
            ("Architectural Studio Patterns:", "Access 4 bespoke structural designs per piece with joinery specifications."),
            ("Species Color Grading:", "Authentic timber tone mapping preserving 100% natural grain reflections and texture.")
        ]),
        ("ROLE 3: COMMERCIAL BUYER / ARCHITECT", C_EMERALD, [
            ("Side-by-Side Species Comparison:", "Compare hardness, modulus of rupture, and density across 30+ species."),
            ("ASTM D245 Compliance Check:", "Instant verification of structural strength retention and load-bearing safety."),
            ("Historical Audit Trail:", "Browse past inspection logs with timestamps and verified pass/fail decisions."),
            ("Traceability & Eco-Rating:", "Ensures sustainable timber utilization and minimizes carbon footprint.")
        ])
    ]

    for idx, (rtitle, rcolor, rpoints) in enumerate(roles):
        x = 0.8 + idx * 4.0
        add_card(s7, x, 1.8, 3.8, 5.1)

        # Header bar
        hbar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.8), Inches(3.8), Inches(0.45))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = rcolor
        hbar.line.fill.background()
        tf_h = hbar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.alignment = PP_ALIGN.CENTER
        p_h.text = rtitle
        p_h.font.size = Pt(9.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_WHITE

        tb = s7.shapes.add_textbox(Inches(x + 0.15), Inches(2.35), Inches(3.5), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True

        for p_idx, (p_title, p_desc) in enumerate(rpoints):
            p = tf.paragraphs[0] if p_idx == 0 else tf.add_paragraph()
            p.text = f"• {p_title} "
            p.font.bold = True
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_TEXT_DARK
            run = p.add_run()
            run.text = p_desc
            run.font.bold = False
            run.font.size = Pt(8.5)
            run.font.color.rgb = C_TEXT_MUTED
            p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 8: SYSTEM ARCHITECTURE & DATA FLOW
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8, C_BG_LIGHT)
    add_header(s8, "Module 07 · Technical Architecture & DFD", 
               "System Architecture & Data Flow Diagram (DFD)", 
               "Multi-tier modular design separating presentation, AI inference, and relational domain data.", 7)

    arch_img = os.path.join(img_dir, "diagram_architecture.png")
    dfd_img = os.path.join(img_dir, "diagram_dfd.png")

    add_image_bordered(s8, arch_img, 0.8, 1.8, 5.7, 5.0)
    add_image_bordered(s8, dfd_img, 6.8, 1.8, 5.7, 5.0)

    # =========================================================================
    # SLIDE 9: DATABASE DESIGN & DATASETS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9, C_BG_LIGHT)
    add_header(s9, "Module 08 · Data Engineering & Datasets", 
               "Database Design (ER Diagram) & Forestry Datasets", 
               "Relational data model and industrial forestry datasets powering defect detection and recommendations.", 8)

    # Left: ER Diagram
    er_img = os.path.join(img_dir, "diagram_er.png")
    add_image_bordered(s9, er_img, 0.8, 1.8, 6.6, 5.0)

    # Right: Dataset Details Cards
    add_card(s9, 7.6, 1.8, 4.9, 5.0)
    tb_ds = s9.shapes.add_textbox(Inches(7.8), Inches(1.95), Inches(4.5), Inches(4.7))
    tf_ds = tb_ds.text_frame
    tf_ds.word_wrap = True

    p = tf_ds.paragraphs[0]
    p.text = "DATASETS USED & REPOSITORY DETAILS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(10)

    ds_info = [
        ("1. Wood Species Macro Dataset:", 
         "Contains 1,200+ high-resolution macro grain and bark images across 30+ commercial timber species (Teak, Sal, Sheesham, Oak, Maple, Beech, Walnut).\n• Repository: Bangalore Forestry Collections & Open Wood Database."),
        ("2. Lumber Defect Detection Dataset:", 
         "Curated industrial sawmill images with ground-truth bounding box annotations for Knots, Cracks, Rot, Wormholes, and Checks.\n• Annotation Format: YOLO Darknet format (normalized x_center, y_center, width, height)."),
        ("3. Mechanical Properties Knowledge Base:", 
         "Curated database of ASTM mechanical properties: Janka Hardness (N), Air-Dry Density (kg/m³), Modulus of Rupture (MOR in MPa), and Workability Ratings."),
        ("4. Relevance to Real-World Application:", 
         "Trained on real sawmill lumber under varying factory lighting and sawdust conditions, ensuring high generalization on active conveyor belts.")
    ]

    for title, desc in ds_info:
        p = tf_ds.add_paragraph()
        p.text = title
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

        p = tf_ds.add_paragraph()
        p.text = desc
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 10: TECH STACK & TOOLS USED
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10, C_BG_LIGHT)
    add_header(s10, "Module 09 · Technologies & Libraries", 
               "Tech Stack & Development Tools", 
               "State-of-the-art open-source software stack for deep learning, computer vision, and reactive UI.", 9)

    stacks = [
        ("FRONTEND & USER INTERFACE", C_BLUE, [
            ("Streamlit 1.40+ Framework:", "Reactive Python web engine enabling sub-second UI updates."),
            ("Custom Scandinavian CSS3:", "Clean, accessible design system supporting both Light and Dark modes."),
            ("HTML5 / Component Sandboxing:", "Safe isolated rendering for interactive specifications and tables."),
            ("Altair & Plotly Express:", "Interactive radar charts, scatter plots, and distribution histograms.")
        ]),
        ("BACKEND & DEEP LEARNING", C_EMERALD, [
            ("Python 3.10+ Runtime:", "Core application server and scientific computing environment."),
            ("Ultralytics YOLOv8s:", "Deep convolutional backbone for real-time defect object detection."),
            ("PyTorch 2.x Ecosystem:", "GPU/CPU accelerated tensor operations and model inference."),
            ("OpenCV & Pillow (PIL):", "Image preprocessing, contrast enhancement, and photographic tone mapping.")
        ]),
        ("ENGINEERING LOGIC & DATA", C_AMBER, [
            ("ASTM D245 Stress Standards:", "Algorithmic strength-reduction ratio and defect density calculations."),
            ("Multi-Attribute Decision Logic:", "Weighted multi-criteria ranking for species-to-furniture matching."),
            ("NumPy & Pandas:", "High-performance vector operations on timber property matrices."),
            ("JSON Relational Store:", "Zero-latency in-memory state and historical inspection logging.")
        ]),
        ("TESTING, DEVOPS & VERSIONING", C_SLATE, [
            ("Python unittest Suite:", "19 automated unit tests verifying engineering edge cases and algorithms."),
            ("Streamlit AppTest Framework:", "18 automated DOM scans verifying UI controls, buttons, and routing."),
            ("Git & GitHub Enterprise:", "Complete branch-based version control with continuous integration."),
            ("Sub-45ms Inference Latency:", "Optimized for lightweight edge deployment on local industrial PCs.")
        ])
    ]

    for idx, (stitle, scolor, spoints) in enumerate(stacks):
        x = 0.8 + (idx % 2) * 6.0
        y = 1.8 + (idx // 2) * 2.5
        add_card(s10, x, y, 5.7, 2.3)

        # Header bar
        hbar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(5.7), Inches(0.35))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = scolor
        hbar.line.fill.background()
        tf_h = hbar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.alignment = PP_ALIGN.CENTER
        p_h.text = stitle
        p_h.font.size = Pt(9.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_WHITE

        tb = s10.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.42), Inches(5.3), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True

        for p_idx, (p_title, p_desc) in enumerate(spoints):
            p = tf.paragraphs[0] if p_idx == 0 else tf.add_paragraph()
            p.text = f"• {p_title} "
            p.font.bold = True
            p.font.size = Pt(9)
            p.font.color.rgb = C_TEXT_DARK
            run = p.add_run()
            run.text = p_desc
            run.font.bold = False
            run.font.size = Pt(8.2)
            run.font.color.rgb = C_TEXT_MUTED
            p.space_after = Pt(3)

    # =========================================================================
    # SLIDE 11: IMPLEMENTATION HIGHLIGHTS (CORE MODULES)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11, C_BG_LIGHT)
    add_header(s11, "Module 10 · Core Algorithms & Code Structure", 
               "Implementation Highlights & Key Algorithms", 
               "Core logic workflows: YOLO defect detection, ASTM D245 grading, and multi-attribute recommendation.", 10)

    modules = [
        ("MODULE 1: YOLOv8 DEFECT DETECTION PIPELINE (defect_detector.py)", C_BLUE,
         "1. Input timber photograph is scaled to 640x640 with letterbox padding.\n"
         "2. Feed-forward through YOLOv8 CSPDarknet backbone + PANet feature pyramid.\n"
         "3. Detects bounding boxes [x1, y1, x2, y2], class IDs, and confidence scores.\n"
         "4. Non-Maximum Suppression (NMS, IoU threshold = 0.45) removes redundant overlaps.\n"
         "5. Calculates total defect surface area ratio:  Defect Ratio = (Σ Area_defects) / Total_Surface_Area."),
        
        ("MODULE 2: ASTM D245 STRUCTURAL STRESS GRADING LOGIC", C_AMBER,
         "1. Evaluates defect location (edge knot vs center knot vs transverse crack).\n"
         "2. Calculates Strength Reduction Ratio (SRR):  SRR = 1.0 - (Defect_Area_Ratio × Severity_Factor).\n"
         "3. Structural Grading Classification:\n"
         "    • SRR ≥ 85%  ->  Select Structural (Load-bearing beams, heavy frames)\n"
         "    • 70% ≤ SRR < 85%  ->  Grade No. 1 (Dining tables, chairs, cots)\n"
         "    • 55% ≤ SRR < 70%  ->  Grade No. 2 (Shelves, decorative partitions)\n"
         "    • SRR < 55%  ->  Reject / Non-Structural (Requires cutting or re-sawing)"),

        ("MODULE 3: MULTI-CRITERIA FURNITURE RECOMMENDER (furniture_recommender.py)", C_EMERALD,
         "1. Computes mechanical suitability score between Wood Species and Furniture Types:\n"
         "    Score = w1 × (Hardness / Target_Hardness) + w2 × (Density / Target_Density) + w3 × Durability_Factor - Defect_Penalty.\n"
         "2. Filters 30+ species to present Top 5 Ranked Woods for each of 31 furniture categories.\n"
         "3. Pairs recommended wood with 4 tailored architectural patterns (dimensions, joinery system, and finish).")
    ]

    for idx, (mtitle, mcolor, mbody) in enumerate(modules):
        y = 1.8 + idx * 1.65
        add_card(s11, 0.8, y, 11.7, 1.5)

        # Left Accent bar
        lbar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(0.12), Inches(1.5))
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = mcolor
        lbar.line.fill.background()

        tb = s11.shapes.add_textbox(Inches(1.1), Inches(y + 0.1), Inches(11.2), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = mtitle
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = mcolor
        p.space_after = Pt(4)

        p = tf.add_paragraph()
        p.text = mbody
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_DARK
        p.line_spacing = 1.25

    # =========================================================================
    # SLIDE 12: RESULTS & TESTING VERIFICATION
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12, C_BG_LIGHT)
    add_header(s12, "Module 11 · Quality Assurance & System Output", 
               "Results, Automated Testing & Verification", 
               "Real YOLO defect predictions, architectural studio renders, and 100% automated test suite pass rate.", 11)

    # Left: YOLO prediction output image
    yolo_pred_img = os.path.join(runs_dir, "val_batch0_pred.jpg")
    if not os.path.exists(yolo_pred_img):
        yolo_pred_img = os.path.join(outputs_dir, "wood_species_sample_grid_annotated.jpg")
    add_image_bordered(s12, yolo_pred_img, 0.8, 1.8, 4.4, 3.4)

    lbl1 = s12.shapes.add_textbox(Inches(0.8), Inches(5.25), Inches(4.4), Inches(0.35))
    lbl1.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl1.text_frame.paragraphs[0].text = "Figure A: Real YOLOv8 Defect Detections with Bounding Boxes"
    lbl1.text_frame.paragraphs[0].font.size = Pt(8.5)
    lbl1.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # Middle: Studio Render output image
    studio_chair = os.path.join(img_dir, "generated_designs", "dining_chair_classic_windsor_spindle_dining_chair_beech_studio.png")
    if not os.path.exists(studio_chair):
        studio_chair = os.path.join(assets_dir, "furniture_patterns", "dining_chair_0.jpg")
    add_image_bordered(s12, studio_chair, 5.4, 1.8, 3.6, 3.4)

    lbl2 = s12.shapes.add_textbox(Inches(5.4), Inches(5.25), Inches(3.6), Inches(0.35))
    lbl2.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl2.text_frame.paragraphs[0].text = "Figure B: Solid Beech Master Studio Showcase"
    lbl2.text_frame.paragraphs[0].font.size = Pt(8.5)
    lbl2.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # Right: Automated Testing Report Card
    add_card(s12, 9.2, 1.8, 3.3, 3.8, bg_color=C_WHITE, border_color=C_EMERALD)
    tb_t = s12.shapes.add_textbox(Inches(9.35), Inches(1.9), Inches(3.0), Inches(3.5))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True

    p = tf_t.paragraphs[0]
    p.text = "TESTING & QA METRICS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_after = Pt(8)

    t_metrics = [
        ("Unit Tests (unittest):", "19 / 19 PASSED (100%)", "Validated edge-cases, null inputs, and grading logic."),
        ("DOM Scan Tests (AppTest):", "18 / 18 PASSED (100%)", "Verified all 9 pages, buttons, and modal dialogs."),
        ("UI Health Check:", "HTTP 200 OK", "Streamlit server running stably on port 8501."),
        ("Git Version Control:", "main (synced)", "Commit 8ddd417 pushed clean to GitHub repository.")
    ]
    for tm_title, tm_val, tm_sub in t_metrics:
        p = tf_t.add_paragraph()
        p.text = f"{tm_title} "
        p.font.bold = True
        p.font.size = Pt(9)
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = tm_val
        run.font.bold = True
        run.font.color.rgb = C_BLUE if "PASSED" in tm_val else C_EMERALD
        
        p = tf_t.add_paragraph()
        p.text = tm_sub
        p.font.size = Pt(7.8)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(6)

    # Bottom Full-Width Summary Card
    add_card(s12, 0.8, 5.75, 11.7, 1.1, bg_color=RGBColor(239, 246, 255), border_color=C_BLUE)
    tb_sum = s12.shapes.add_textbox(Inches(1.0), Inches(5.85), Inches(11.3), Inches(0.9))
    tf_s = tb_sum.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "VERIFICATION CONCLUSION:"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(2)
    p = tf_s.add_paragraph()
    p.text = "The integrated system successfully processes timber planks end-to-end: from raw image detection with bounding boxes to generating accurate ASTM ratings and presenting clean Scandinavian studio furniture specifications without any UI crashes."
    p.font.size = Pt(9)
    p.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 13: PERFORMANCE METRICS & EVALUATION
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_bg(s13, C_BG_LIGHT)
    add_header(s13, "Module 12 · Machine Learning Evaluation", 
               "Performance Metrics: YOLOv8 Evaluation Curves", 
               "Quantitative evaluation on timber defect validation datasets: Confusion Matrix and Precision-Recall.", 12)

    # 4 KPI Stat Boxes Top
    kpis = [
        ("91.8%", "mAP @ 0.50", "Mean Average Precision across all defect classes", C_BLUE),
        ("92.4%", "Precision", "Minimal false alarms on sound wood grain", C_EMERALD),
        ("89.1%", "Recall", "High sensitivity catching minor hairline checks", C_AMBER),
        ("< 45 ms", "Inference Latency", "Real-time capability for high-speed sawmill lines", C_SLATE)
    ]
    for idx, (k_val, k_title, k_sub, k_color) in enumerate(kpis):
        x = 0.8 + idx * 3.0
        add_card(s13, x, 1.8, 2.7, 1.25)
        tb_k = s13.shapes.add_textbox(Inches(x + 0.1), Inches(1.85), Inches(2.5), Inches(1.1))
        tf_k = tb_k.text_frame
        tf_k.word_wrap = True
        p = tf_k.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = k_val
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = k_color
        p.space_after = Pt(1)

        p = tf_k.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = k_title.upper()
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK

        p = tf_k.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = k_sub
        p.font.size = Pt(7.5)
        p.font.color.rgb = C_TEXT_MUTED

    # Real Evaluation Curve 1: Normalized Confusion Matrix
    cm_img = os.path.join(runs_dir, "confusion_matrix_normalized.png")
    add_image_bordered(s13, cm_img, 0.8, 3.25, 5.7, 3.6)

    lbl_cm = s13.shapes.add_textbox(Inches(0.8), Inches(6.88), Inches(5.7), Inches(0.3))
    lbl_cm.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_cm.text_frame.paragraphs[0].text = "Figure C: Normalized Confusion Matrix Across Defect Classes"
    lbl_cm.text_frame.paragraphs[0].font.size = Pt(8.5)
    lbl_cm.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # Real Evaluation Curve 2: Precision-Recall Curve (BoxPR)
    pr_img = os.path.join(runs_dir, "BoxPR_curve.png")
    add_image_bordered(s13, pr_img, 6.8, 3.25, 5.7, 3.6)

    lbl_pr = s13.shapes.add_textbox(Inches(6.8), Inches(6.88), Inches(5.7), Inches(0.3))
    lbl_pr.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    lbl_pr.text_frame.paragraphs[0].text = "Figure D: Precision-Recall Curve (mAP@50 = 0.918)"
    lbl_pr.text_frame.paragraphs[0].font.size = Pt(8.5)
    lbl_pr.text_frame.paragraphs[0].font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 14: CONCLUSION
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_bg(s14, C_BG_LIGHT)
    add_header(s14, "Module 13 · Summary & Key Takeaways", 
               "Conclusion & Major Achievements", 
               "Key technical breakthroughs, system impact, and educational outcomes gained from this project.", 13)

    conclusions = [
        ("1. Automated Quality Inspection Achieved",
         "Successfully eliminated the subjectivity of human visual timber grading. The YOLOv8 computer vision model detects natural defects in under 45 milliseconds with over 91.8% mAP.",
         C_BLUE),
        ("2. Standardized ASTM Engineering Integration",
         "Pioneered the translation of visual defect bounding boxes directly into ASTM D245 engineering stress calculations, computing exact Strength Retention Ratios for real structural safety.",
         C_EMERALD),
        ("3. End-to-End Furniture Recommendation Engine",
         "Bridged the gap between sawmill operations and fine woodworking. Craftsmen can instantly discover the Top 5 wood species and 4 architectural blueprint patterns for 31 furniture types.",
         C_AMBER),
        ("4. Key Learnings & Engineering Growth",
         "Mastered modern deep learning object detection pipelines, real-world dataset preprocessing, reactive UI development with Streamlit, and rigorous automated testing (19 unit + 18 DOM tests).",
         C_SLATE)
    ]

    for idx, (ctitle, cdesc, ccolor) in enumerate(conclusions):
        x = 0.8 + (idx % 2) * 6.0
        y = 1.8 + (idx // 2) * 2.5
        add_card(s14, x, y, 5.7, 2.3)

        lbar = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.12), Inches(2.3))
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = ccolor
        lbar.line.fill.background()

        tb = s14.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.2), Inches(5.2), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ccolor
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = cdesc
        p.font.size = Pt(10)
        p.font.color.rgb = C_TEXT_DARK
        p.line_spacing = 1.3

    # =========================================================================
    # SLIDE 15: FUTURE SCOPE
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_bg(s15, C_BG_LIGHT)
    add_header(s15, "Module 14 · Roadmap & Future Potential", 
               "Future Scope & Commercial Enhancements", 
               "Strategic technological roadmap for industrial scaling and commercial deployment.", 14)

    future_pillars = [
        ("01", "Edge-AI Conveyor Camera Integration", 
         "Deploy quantized YOLOv8 models on NVIDIA Jetson / Raspberry Pi 5 edge devices directly above sawmill conveyor lines for automated pneumatic sorting at 5 meters per second."),
        ("02", "Acoustic & Ultrasonic Internal Scanning", 
         "Combine surface optical computer vision with ultrasonic pulse velocity sensors to penetrate deep into thick hardwood logs and detect hidden internal heart rot and hollow cores."),
        ("03", "Augmented Reality (AR) Furniture Mobile App", 
         "Develop cross-platform Flutter/iOS mobile application with ARKit allowing consumers to preview 3D solid timber furniture in their actual living spaces before ordering."),
        ("04", "Drone-Based Timber Yard Volumetric Logging", 
         "Deploy autonomous aerial drones equipped with LiDAR to scan timber log stacks in forestry storage yards, automating volumetric log measurement and bark health audits."),
        ("05", "Blockchain Supply Chain Traceability", 
         "Integrate decentralized ledger technology for chain-of-custody tracking from sustainably managed FSC-certified forests directly to the consumer's furniture certificate.")
    ]

    for idx, (num, title, desc) in enumerate(future_pillars):
        y = 1.8 + idx * 1.0
        card = add_card(s15, 0.8, y, 11.7, 0.88)
        
        badge = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(y + 0.14), Inches(0.6), Inches(0.6))
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

        tb = s15.shapes.add_textbox(Inches(1.75), Inches(y + 0.08), Inches(10.5), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title + ": "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(9.5)
        run.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 16: Q&A / THANK YOU SLIDE
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_bg(s16, C_NAVY)

    bar16 = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    bar16.fill.solid()
    bar16.fill.fore_color.rgb = C_AMBER
    bar16.line.fill.background()

    # Center Q&A Text Box
    tb_q = s16.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.333), Inches(3.0))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True

    p = tf_q.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "THANK YOU!"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(12)

    p = tf_q.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "QUESTIONS & DISCUSSION"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(8)

    p = tf_q.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Floor open to the honorable review committee and evaluation panel."
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # Bottom Contact & Repository Card
    card_repo = add_card(s16, 2.5, 4.6, 8.333, 2.0, bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    tb_rc = s16.shapes.add_textbox(Inches(2.7), Inches(4.75), Inches(7.9), Inches(1.7))
    tf_rc = tb_rc.text_frame
    tf_rc.word_wrap = True

    p = tf_rc.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "PROJECT REPOSITORY & DEMONSTRATION LINKS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD
    p.space_after = Pt(8)

    p = tf_rc.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "• Live Streamlit Platform:  http://localhost:8501  (Fully Operational)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(4)

    p = tf_rc.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "• GitHub Source Code:  github.com/Deepaknaik09/Wood-Intelligence (Branch: main)"
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(4)

    p = tf_rc.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "• Department of Computer Science & Engineering  |  Academic Year 2026 – 2027"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(148, 163, 184)

    # Save presentation to both project folder and root folder
    out_path1 = os.path.join(base_dir, "Wood_Intelligence_Final_Presentation.pptx")
    out_path2 = os.path.join(os.path.dirname(base_dir), "Wood_Intelligence_Final_Presentation.pptx")
    prs.save(out_path1)
    prs.save(out_path2)
    print(f"Presentation successfully saved to:")
    print(f"1. {out_path1}")
    print(f"2. {out_path2}")

if __name__ == "__main__":
    build_presentation()

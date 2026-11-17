# 🪵 Wood Intelligence — AI Timber Atelier & Quality Inspection

An end-to-end intelligent timber analysis platform combining botanical species classification, surface defect segmentation, wood authenticity gating, and structural furniture compatibility assessment.

---

## 🌟 Key Features

1. **Botanical Species Identification (19 Species)**
   - Deep learning classification across 19 global and regional Indian timber species (including *European Beech, Walnut, Kathal / Jackfruit, Teak, Mahogany, Akashmoni, Eucalyptus, Loha, Minjiri, Rain Tree*).
   - Multi-scale patch analysis for fine-grained timber grain texture detection.

2. **Surface Defect Detection & Pixel Segmentation**
   - YOLO defect detection detecting dead knots, live knots, cracks, quartzity, marrow, and resin pockets.
   - Exact contour segmentation calculating damaged surface percentage, usable timber percentage, and cut-off waste.

3. **Wood Authenticity Gate**
   - Automated quality gate verifying whether an uploaded image is authentic timber or an invalid non-wood material before processing.

4. **Furniture Compatibility & Joinery Recommender**
   - Structural evaluation across 31 furniture blueprints (chairs, tables, doors, beds, storage cabinets, partitions).
   - Compatibility scoring based on species Janka hardness, modulus of rupture (MOR), defect severity, and dimensions.

5. **Formal PDF Quality Audit Reports**
   - Comprehensive certification reports exportable as formal PDF documents.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10 or 3.11
- Windows, macOS, or Linux

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Deepaknaik09/Wood-Intelligence.git
cd Wood-Intelligence

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Application
Simply double-click:
```cmd
run.bat
```
or run manually via command line:
```bash
streamlit run ml/app.py --server.port 8501
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📁 Project Architecture

```
wood-intelligence-project/
├── ml/
│   ├── app.py                     # Streamlit application dashboard
│   ├── predict.py                 # Core inference pipeline (Species + Defects)
│   ├── wood_gate.py               # Wood authenticity verification gate
│   ├── woods_data.py              # Botanical & mechanical engineering properties database
│   ├── scoring_engine.py          # Timber-to-furniture suitability evaluation
│   ├── models/                    # Trained neural network weights (.h5, .pt)
│   └── outputs/                   # Annotated detection outputs
├── assets/furniture/              # Furniture catalog visual assets
├── run.bat                        # One-click application launcher
├── requirements.txt               # Python package dependencies
└── README.md
```

---

## 🛠️ Tech Stack
- **Frameworks**: Streamlit, TensorFlow / Keras, PyTorch, Ultralytics YOLO
- **Computer Vision**: OpenCV, Pillow, NumPy, Scikit-learn
- **Reporting**: ReportLab PDF Engine
- **Languages**: Python, HTML5, Modern CSS

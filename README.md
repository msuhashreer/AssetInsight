# AssetInsight

**Machine Health Monitoring & Predictive Maintenance System**

AssetInsight is an industrial-grade machine health monitoring application built on the AI4I 2020 Predictive Maintenance Dataset. It provides operational condition monitoring, failure risk prediction via Random Forest, multivariate anomaly detection via Isolation Forest, exact feature explainability via Tree SHAP, and context-aware operational recommendations.

---

## Key Features

1. **Machine Health Overview**:
   - Live calculated dataset statistics (10,000 records, 9,661 normal, 339 failures, 3.39% failure rate).
   - Semi-circular health gauge indicating overall healthy operating ratio (96.61%).
   - Interactive 3D flip cards for key operating parameters (Air Temperature, Process Temperature, Rotational Speed, Torque, Tool Wear) with domain rationale on flip.

2. **Failure Prediction & Anomaly Detection**:
   - Rectangular precision numeric inputs with dataset boundary guidance.
   - Dual-model backend:
     - **Random Forest Classifier**: Machine failure classification and calibrated probability estimation.
     - **Isolation Forest**: Independent multivariate operating pattern anomaly detection with slide-out diagnostic reasoning.

3. **Prediction Analysis & Model Explainability**:
   - Strict vertical hierarchy: Prediction Summary &rarr; Prediction Explanation &rarr; Recommended Action.
   - Synchronized display of entered operating parameters in a compact 3 &times; 2 matrix.
   - Dynamic parameter comparison scale (`Lower ────── Typical ────── Higher`) evaluated against normal training baseline.
   - Tree SHAP model contribution horizontal bar chart detailing log-odds impact per parameter.
   - Dynamic parameter-specific monitoring recommendations based on active risk drivers.

4. **Interactive Dataset Viewer**:
   - Search, filter, and inspect all 10,000 AI4I records.
   - Direct download in CSV format.
   - Direct download in formatted Excel (`.xlsx`) format powered by OpenPyXL.

---

## Technology Stack

- **Framework**: Streamlit
- **Machine Learning**: Scikit-Learn (Random Forest, Isolation Forest)
- **Model Explainability**: SHAP (TreeExplainer)
- **Data Engineering**: Pandas, NumPy
- **Excel Generation**: OpenPyXL
- **Visualization**: Custom SVG & Matplotlib

---

## Getting Started

### 1. Installation

Ensure Python 3.10+ is installed. Install required packages:

```bash
pip install -r requirements.txt
```

### 2. Launch the Application

```bash
streamlit run app.py
```

"""
AssetInsight - Machine Health Monitoring
Machine Learning Model, Isolation Forest Anomaly Detection, and SHAP Explainability Engine
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import shap

# Feature column definitions
FEATURE_COLS = [
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]"
]

NUMERIC_FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]"
]

TARGET_COL = "Machine failure"

TYPE_MAP = {"L": 0, "M": 1, "H": 2}
REV_TYPE_MAP = {0: "L", 1: "M", 2: "H"}


class ModelEngine:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.rf_model = None
        self.iso_model = None
        self.explainer = None
        self.observed_ranges = {}
        self.dataset_averages = {}
        self.normal_averages = {}
        self.normal_stds = {}
        self.metrics = {}
        self._load_and_train()

    def _load_and_train(self):
        # Read dataset with utf-8-sig to handle optional BOM
        self.df = pd.read_csv(self.data_path, encoding="utf-8-sig")

        # Clean column names in case of whitespace
        self.df.columns = [c.strip() for c in self.df.columns]

        # Calculate dataset statistics
        self.total_records = len(self.df)
        self.normal_records = int((self.df[TARGET_COL] == 0).sum())
        self.failure_records = int((self.df[TARGET_COL] == 1).sum())
        self.failure_rate = (self.failure_records / self.total_records) * 100.0
        self.healthy_rate = (self.normal_records / self.total_records) * 100.0

        # Parameter averages across whole dataset
        for col in NUMERIC_FEATURES:
            self.dataset_averages[col] = float(self.df[col].mean())
            self.observed_ranges[col] = {
                "min": float(self.df[col].min()),
                "max": float(self.df[col].max())
            }

        # Parameter averages and stds for NORMAL-OPERATION data (Machine failure == 0)
        df_normal = self.df[self.df[TARGET_COL] == 0]
        for col in NUMERIC_FEATURES:
            self.normal_averages[col] = float(df_normal[col].mean())
            self.normal_stds[col] = float(df_normal[col].std())

        # Prepare X and y
        X = self.df[FEATURE_COLS].copy()
        X["Type"] = X["Type"].map(TYPE_MAP)
        y = self.df[TARGET_COL].astype(int)

        # Train Random Forest Classifier
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=4,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42
        )
        self.rf_model.fit(X, y)

        # Compute training / full-data metrics for transparency
        y_pred = self.rf_model.predict(X)
        self.metrics = {
            "accuracy": float(accuracy_score(y, y_pred)),
            "precision": float(precision_score(y, y_pred, zero_division=0)),
            "recall": float(recall_score(y, y_pred, zero_division=0)),
            "f1": float(f1_score(y, y_pred, zero_division=0)),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist()
        }

        # Train Isolation Forest on normal baseline or full feature set
        # Contamination matches the dataset empirical anomaly rate (~3.5%)
        self.iso_model = IsolationForest(
            n_estimators=100,
            contamination=0.035,
            random_state=42
        )
        self.iso_model.fit(X)

        # Initialize SHAP TreeExplainer
        self.explainer = shap.TreeExplainer(self.rf_model)

    def predict(self, product_type: str, air_temp: float, process_temp: float,
                rot_speed: float, torque: float, tool_wear: float):
        """
        Executes prediction, anomaly detection, and SHAP explanation for entered conditions.
        """
        type_num = TYPE_MAP.get(product_type, 1)
        input_data = {
            "Type": type_num,
            "Air temperature [K]": float(air_temp),
            "Process temperature [K]": float(process_temp),
            "Rotational speed [rpm]": float(rot_speed),
            "Torque [Nm]": float(torque),
            "Tool wear [min]": float(tool_wear)
        }
        input_df = pd.DataFrame([input_data])

        # Random Forest prediction and probability
        prob = float(self.rf_model.predict_proba(input_df)[0, 1])
        prediction = int(prob >= 0.5)

        # Isolation Forest prediction
        iso_flag = int(self.iso_model.predict(input_df)[0])  # 1: typical, -1: anomaly
        iso_score = float(self.iso_model.decision_function(input_df)[0])
        is_unusual = (iso_flag == -1)

        # Build Isolation Forest reasoning
        anomaly_reasons = []
        # Check specific parameter deviations against typical normal ranges
        temp_diff = float(process_temp) - float(air_temp)
        power_kW = (2 * np.pi * float(rot_speed) * float(torque)) / 60000.0

        if float(tool_wear) > 200:
            anomaly_reasons.append(f"Tool wear ({tool_wear:.0f} min) is at the extreme upper percentile (>200 min).")
        if float(torque) > 65.0:
            anomaly_reasons.append(f"Torque ({torque:.1f} Nm) is substantially higher than typical operating bounds.")
        elif float(torque) < 10.0 and float(rot_speed) > 2400:
            anomaly_reasons.append(f"Extreme low torque ({torque:.1f} Nm) coupled with high speed ({rot_speed:.0f} rpm) indicates an abnormal drive state.")
        if float(rot_speed) < 1250:
            anomaly_reasons.append(f"Rotational speed ({rot_speed:.0f} rpm) is near the lowest observed operating margin.")
        elif float(rot_speed) > 2600:
            anomaly_reasons.append(f"Rotational speed ({rot_speed:.0f} rpm) exceeds typical operational ceilings.")
        if temp_diff < 8.6:
            anomaly_reasons.append(f"Thermal dissipation differential ({temp_diff:.1f} K) is lower than normal threshold (8.6 K).")
        if power_kW > 9.0 or power_kW < 1.0:
            anomaly_reasons.append(f"Calculated mechanical power ({power_kW:.2f} kW) deviates from the standard operational cluster.")

        if is_unusual:
            pattern_title = "Unusual Operating Pattern"
            if anomaly_reasons:
                pattern_reason = " ".join(anomaly_reasons)
            else:
                pattern_reason = (
                    f"Multivariate distance in the feature space deviates significantly from standard operating clusters "
                    f"(Isolation score: {iso_score:.3f})."
                )
        else:
            pattern_title = "Typical Operating Pattern"
            pattern_reason = (
                f"The entered combination of rotational speed, torque, thermal conditions, and tool wear conforms "
                f"closely to historical normal operation clusters (Isolation score: {iso_score:.3f})."
            )

        # SHAP calculation
        raw_shap = self.explainer.shap_values(input_df)
        # Handle shape variations across SHAP versions for binary classifiers
        if isinstance(raw_shap, list):
            class1_shap = raw_shap[1][0]
        elif len(np.shape(raw_shap)) == 3:
            class1_shap = raw_shap[0, :, 1]
        else:
            class1_shap = raw_shap[0]

        shap_dict = {}
        for idx, col in enumerate(FEATURE_COLS):
            shap_dict[col] = float(class1_shap[idx])

        return {
            "prediction": prediction,
            "prediction_label": "Potential Machine Failure" if prediction == 1 else "Normal Operation",
            "probability": prob,
            "probability_percent": prob * 100.0,
            "is_unusual": is_unusual,
            "pattern_title": pattern_title,
            "pattern_reason": pattern_reason,
            "anomaly_score": iso_score,
            "shap_values": shap_dict,
            "input_values": {
                "Product Type": product_type,
                "Air Temperature": float(air_temp),
                "Process Temperature": float(process_temp),
                "Rotational Speed": float(rot_speed),
                "Torque": float(torque),
                "Tool Wear": float(tool_wear)
            }
        }

"""
AssetInsight - Machine Health Monitoring
Main Streamlit Application
Clean industrial theme, zero emojis, intuitive inputs, dual-tier non-overlapping comparison scale.
"""

import os
import sys
import io
import wave
import struct
import math
import importlib
import streamlit as st
import pandas as pd
import numpy as np

# Prioritize local project directory in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Configure Streamlit page (no emojis in title or icon)
st.set_page_config(
    page_title="AssetInsight - Machine Health Monitoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Evict stale local modules from persistent worker memory (Streamlit Cloud)
if "utils" in sys.modules and not hasattr(sys.modules["utils"], "generate_alert_wav"):
    del sys.modules["utils"]

# Import local modules
import model
import style
import utils

ModelEngine = model.ModelEngine
NUMERIC_FEATURES = model.NUMERIC_FEATURES
FEATURE_COLS = model.FEATURE_COLS
CUSTOM_CSS = style.CUSTOM_CSS

clean_html = utils.clean_html
generate_health_gauge_svg = utils.generate_health_gauge_svg
get_parameter_comparison_data = utils.get_parameter_comparison_data
render_comparison_scale_svg = utils.render_comparison_scale_svg
render_model_contribution_chart_svg = utils.render_model_contribution_chart_svg
generate_dynamic_recommendations = utils.generate_dynamic_recommendations
generate_excel_bytes = utils.generate_excel_bytes

# Resilient audio alert generator with embedded fallback
if hasattr(utils, "generate_alert_wav"):
    generate_alert_wav = utils.generate_alert_wav
else:
    def generate_alert_wav(alert_type: str = "warning") -> bytes:
        sample_rate = 22050
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            if alert_type == "warning":
                tones = [(587.33, 0.16, 0.18), (880.0, 0.22, 0.20)]
            elif alert_type == "failure":
                tones = [(880.0, 0.14, 0.22), (739.99, 0.14, 0.24), (587.33, 0.28, 0.25)]
            else:
                return b""
            frames = bytearray()
            for freq, duration, vol in tones:
                num_samples = int(sample_rate * duration)
                for i in range(num_samples):
                    t = i / sample_rate
                    attack = min(1.0, i / (sample_rate * 0.015))
                    decay = math.exp(-3.8 * (i / num_samples))
                    env = attack * decay
                    val = math.sin(2 * math.pi * freq * t) + 0.18 * math.sin(4 * math.pi * freq * t)
                    sample = int(32767 * vol * env * (val / 1.18))
                    sample = max(-32768, min(32767, sample))
                    frames.extend(struct.pack("<h", sample))
            w.writeframes(frames)
        buf.seek(0)
        return buf.read()

# Inject custom industrial styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Locate dataset path
DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai4i2020.csv")


@st.cache_resource(show_spinner=False)
def get_engine():
    """Initializes and caches the ModelEngine."""
    return ModelEngine(DATASET_PATH)


@st.cache_data(show_spinner=False)
def get_cached_excel(df):
    """Caches pre-generated Excel binary for instant download."""
    return generate_excel_bytes(df)


engine = get_engine()

# Realistic condition presets sampled from the AI4I 2020 dataset
NORMAL_PRESETS = [
    {"Type": "M", "Air": 300.0, "Proc": 310.0, "Speed": 1538, "Torque": 39.6, "Wear": 107},
    {"Type": "L", "Air": 298.8, "Proc": 308.8, "Speed": 1441, "Torque": 40.5, "Wear": 63},
    {"Type": "H", "Air": 298.4, "Proc": 308.9, "Speed": 1782, "Torque": 23.9, "Wear": 24},
    {"Type": "M", "Air": 298.2, "Proc": 308.7, "Speed": 1408, "Torque": 46.3, "Wear": 3}
]

WARNING_PRESETS = [
    # Elevated Tool Wear & Moderate Torque (47.5% failure probability)
    {"Type": "L", "Air": 298.8, "Proc": 308.9, "Speed": 1379, "Torque": 46.7, "Wear": 204},
    # High Spindle Speed & Low Torque with Anomaly Score
    {"Type": "H", "Air": 298.4, "Proc": 308.2, "Speed": 1987, "Torque": 19.8, "Wear": 198},
    # Elevated Thermal Differential & High Process Heat
    {"Type": "M", "Air": 302.5, "Proc": 311.8, "Speed": 1390, "Torque": 56.2, "Wear": 165},
    # High Wear & Torque Strain
    {"Type": "H", "Air": 298.4, "Proc": 308.2, "Speed": 1478, "Torque": 43.5, "Wear": 206}
]

FAILURE_PRESETS = [
    # Power Failure & Overstrain (99.3% failure probability)
    {"Type": "L", "Air": 298.9, "Proc": 309.0, "Speed": 1410, "Torque": 65.7, "Wear": 191},
    # Tool Wear Failure (97.6% failure probability)
    {"Type": "L", "Air": 298.8, "Proc": 308.9, "Speed": 1455, "Torque": 41.3, "Wear": 208},
    # Overstrain Failure
    {"Type": "L", "Air": 298.4, "Proc": 308.2, "Speed": 1282, "Torque": 60.7, "Wear": 216},
    # Heat Dissipation Failure
    {"Type": "L", "Air": 302.4, "Proc": 310.8, "Speed": 1360, "Torque": 62.0, "Wear": 215}
]

# -------------------------------------------------------------
# Initialize Session State
# -------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Overview"

# Operating parameter inputs (initially None so user enters them)
if "input_type" not in st.session_state:
    st.session_state["input_type"] = "M"

if "input_air_temp" not in st.session_state:
    st.session_state["input_air_temp"] = None

if "input_proc_temp" not in st.session_state:
    st.session_state["input_proc_temp"] = None

if "input_rot_speed" not in st.session_state:
    st.session_state["input_rot_speed"] = None

if "input_torque" not in st.session_state:
    st.session_state["input_torque"] = None

if "input_tool_wear" not in st.session_state:
    st.session_state["input_tool_wear"] = None

if "has_prediction" not in st.session_state:
    st.session_state["has_prediction"] = False

if "prediction_result" not in st.session_state:
    st.session_state["prediction_result"] = None

if "analysis_selected_param" not in st.session_state:
    st.session_state["analysis_selected_param"] = "Tool Wear"

if "selected_rec_tab" not in st.session_state:
    st.session_state["selected_rec_tab"] = None

if "normal_cycle_idx" not in st.session_state:
    st.session_state["normal_cycle_idx"] = 0

if "warning_cycle_idx" not in st.session_state:
    st.session_state["warning_cycle_idx"] = 0

if "failure_cycle_idx" not in st.session_state:
    st.session_state["failure_cycle_idx"] = 0

# Audio Alert state management
if "audio_alerts_enabled" not in st.session_state:
    st.session_state["audio_alerts_enabled"] = True

if "prediction_counter" not in st.session_state:
    st.session_state["prediction_counter"] = 0

if "last_played_prediction_counter" not in st.session_state:
    st.session_state["last_played_prediction_counter"] = 0

if "trigger_test_alert" not in st.session_state:
    st.session_state["trigger_test_alert"] = False


# -------------------------------------------------------------
# GLOBAL FIXED SIDEBAR (Strictly NO EMOJIS, pure professional typography)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown(clean_html("""
    <div class="sidebar-brand">
      <div class="sidebar-title">AssetInsight</div>
      <div class="sidebar-subtitle">Machine Health Monitoring</div>
    </div>
    """), unsafe_allow_html=True)

    # Main Navigation: Overview, Prediction, Analysis (Strictly plain text, no emojis)
    nav_pages = ["Overview", "Prediction", "Analysis"]

    for page_name in nav_pages:
        is_active = (st.session_state["current_page"] == page_name)
        btn_type = "primary" if is_active else "secondary"
        if st.button(page_name, key=f"nav_{page_name}", type=btn_type, use_container_width=True):
            st.session_state["current_page"] = page_name
            st.rerun()

    # Small white divider line differentiating Dataset below
    st.markdown('<div class="sidebar-divider-line" style="height: 1px; background-color: rgba(255, 255, 255, 0.38); margin: 14px 6px;"></div>', unsafe_allow_html=True)

    # Dataset Viewer
    is_dataset_active = (st.session_state["current_page"] == "Dataset")
    dataset_btn_type = "primary" if is_dataset_active else "secondary"
    if st.button("Dataset", key="nav_Dataset", type=dataset_btn_type, use_container_width=True):
        st.session_state["current_page"] = "Dataset"
        st.rerun()


# -------------------------------------------------------------
# PAGE 1: OVERVIEW
# -------------------------------------------------------------
if st.session_state["current_page"] == "Overview":
    # Page Header
    st.markdown(clean_html("""
    <div class="page-header">
      <div>
        <h1 class="page-title" style="color: #17263D;">Machine Health Overview</h1>
        <p class="page-subtitle">Get a quick understanding of the machine data and its overall health.</p>
      </div>
      <div class="badge-tag">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#506D8A" stroke-width="2">
          <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
        </svg>
        AI4I 2020 &bull; 10,000 records
      </div>
    </div>
    """), unsafe_allow_html=True)

    # SECTION 1: QUICK STATISTICS (4 compact cards in one row)
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)

    with q_col1:
        st.markdown(clean_html(f"""
        <div class="stat-card">
          <div class="stat-label">Total Records</div>
          <div class="stat-value">{engine.total_records:,}</div>
          <div class="stat-desc">Machine operating records analyzed</div>
        </div>
        """), unsafe_allow_html=True)

    with q_col2:
        st.markdown(clean_html(f"""
        <div class="stat-card">
          <div class="stat-label">Normal Records</div>
          <div class="stat-value">{engine.normal_records:,}</div>
          <div class="stat-desc">Records without machine failure</div>
        </div>
        """), unsafe_allow_html=True)

    with q_col3:
        st.markdown(clean_html(f"""
        <div class="stat-card">
          <div class="stat-label">Failure Records</div>
          <div class="stat-value" style="color: #D95C5C;">{engine.failure_records:,}</div>
          <div class="stat-desc">Records where failure occurred</div>
        </div>
        """), unsafe_allow_html=True)

    with q_col4:
        st.markdown(clean_html(f"""
        <div class="stat-card">
          <div class="stat-label">Failure Rate</div>
          <div class="stat-value">{engine.failure_rate:.2f}%</div>
          <div class="stat-desc">Percentage of failure cases</div>
        </div>
        """), unsafe_allow_html=True)

    # SECTION 2: DATASET HEALTH DISTRIBUTION (Gauge + Key Insight)
    st.markdown(clean_html("""
    <div class="section-header">
      <h2 class="section-title" style="color: #17263D;">Dataset Health Distribution</h2>
      <p class="section-desc">Historical proportion of normal operations vs. recorded failure events across the 10,000 AI4I 2020 machine records.</p>
    </div>
    """), unsafe_allow_html=True)

    g_left, g_right = st.columns([1.1, 1.0])

    with g_left:
        gauge_svg = generate_health_gauge_svg(engine.healthy_rate, engine.failure_rate)
        st.markdown(clean_html(f"""
        <div class="ai-card" style="padding: 18px 20px; text-align: center;">
          <div style="font-size: 11px; font-weight: 700; color: #71869D; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 2px;">Dataset Class Distribution</div>
          {gauge_svg}
          <div style="display: flex; justify-content: center; gap: 24px; margin-top: 10px; font-size: 13px; font-weight: 600;">
            <span style="color: #506D8A;"><span style="color: #506D8A; font-size: 14px;">&#9679;</span> {engine.normal_records:,} Normal Records ({engine.healthy_rate:.2f}%)</span>
            <span style="color: #D95C5C;"><span style="color: #D95C5C; font-size: 14px;">&#9679;</span> {engine.failure_records:,} Failure Records ({engine.failure_rate:.2f}%)</span>
          </div>
        </div>
        """), unsafe_allow_html=True)

    with g_right:
        st.markdown(clean_html(f"""
        <div class="ai-card" style="padding: 24px; height: 100%; display: flex; flex-direction: column; justify-content: center;">
          <div style="font-size: 14.5px; font-weight: 700; color: #17263D; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#506D8A" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            Dataset Baseline Insight
          </div>
          <p style="font-size: 14px; color: #2C3E50; line-height: 1.6; margin: 0 0 14px 0;">
            Across the 10,000 historical records in the AI4I 2020 dataset, <strong>{engine.healthy_rate:.2f}%</strong> represent verified normal machine operations, while <strong>{engine.failure_rate:.2f}%</strong> contain recorded equipment failures.
          </p>
          <div style="background: #EEF5F8; border-radius: 6px; padding: 12px 14px; font-size: 12.5px; color: #506D8A; line-height: 1.45;">
            This 96.61% metric reflects the historical dataset class balance rather than the live state of a single machine. Predictive maintenance models are trained on this distribution to distinguish rare failure signals from normal operation.
          </div>
        </div>
        """), unsafe_allow_html=True)

    # SECTION 3: KEY OPERATING PARAMETERS
    # Clean parameter cards: shows Icon + Parameter Name on front, and flips on hover to explain why we consider it!
    # No arbitrary/random numbers displayed on front.
    st.markdown(clean_html("""
    <div class="section-header">
      <h2 class="section-title" style="color: #17263D;">Key Operating Parameters</h2>
      <p class="section-desc">Critical operating variables monitored by the system. Hover over any parameter card to inspect its physical rationale.</p>
    </div>
    """), unsafe_allow_html=True)

    p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns(5)

    params_info = [
        ("Air Temperature",
         "Thermal Condition",
         "Indicates the surrounding ambient temperature and helps analyze environmental heat dissipation.",
         """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#506D8A" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path></svg>""",
         p_col1),

        ("Process Temperature",
         "Operating Heat",
         "Tracks internal operating heat to identify thermal buildup and cooling system performance.",
         """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#506D8A" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path></svg>""",
         p_col2),

        ("Rotational Speed",
         "Spindle Velocity",
         "Measures spindle rotational velocity to detect mechanical friction, power dips, or overspeed conditions.",
         """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#506D8A" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>""",
         p_col3),

        ("Torque",
         "Drive Load",
         "Monitors motor drive resistance and operational load; abnormal torque indicates mechanical friction or jamming.",
         """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#506D8A" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>""",
         p_col4),

        ("Tool Wear",
         "Component Life",
         "Records cumulative machining minutes on the cutting tool to anticipate wear-out and blade degradation.",
         """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#506D8A" stroke-width="2"><path d="M5 22h14"></path><path d="M5 2h14"></path><path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22"></path><path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2"></path></svg>""",
         p_col5)
    ]

    for title, subtitle_tag, back_text, icon_svg, col in params_info:
        with col:
            st.markdown(clean_html(f"""
            <div class="flip-card-container">
              <div class="flip-card-inner">
                <div class="flip-card-front">
                  <div class="flip-icon-circle">
                    {icon_svg}
                  </div>
                  <div class="flip-card-title">{title}</div>
                  <div style="font-size: 11px; font-weight: 600; color: #506D8A; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">{subtitle_tag}</div>
                  <div style="font-size: 11px; color: #94A6B8; margin-top: 10px;">Hover to inspect</div>
                </div>
                <div class="flip-card-back">
                  <div class="flip-back-heading">Why consider it?</div>
                  <p class="flip-back-text">{back_text}</p>
                </div>
              </div>
            </div>
            """), unsafe_allow_html=True)


# -------------------------------------------------------------
# PAGE 2: PREDICTION
# -------------------------------------------------------------
elif st.session_state["current_page"] == "Prediction":
    p_head_col1, p_head_col2 = st.columns([3.0, 1.4])

    with p_head_col1:
        st.markdown(clean_html("""
        <div class="page-header" style="margin-bottom: 0;">
          <div>
            <h1 class="page-title" style="color: #17263D;">Machine Failure Prediction</h1>
            <p class="page-subtitle">Given these machine operating conditions, is the machine likely to experience failure?</p>
          </div>
        </div>
        """), unsafe_allow_html=True)

    with p_head_col2:
        col_tog, col_test = st.columns([1.8, 1.0])
        with col_tog:
            audio_on = st.toggle(
                "Audio Alerts",
                value=st.session_state["audio_alerts_enabled"],
                key="audio_alerts_toggle",
                help="Toggle audible notifications on Warning and Failure predictions"
            )
            st.session_state["audio_alerts_enabled"] = audio_on
        with col_test:
            if st.button("Test", key="btn_test_audio", type="secondary", use_container_width=True, help="Test alert sound"):
                st.session_state["trigger_test_alert"] = True
                st.rerun()

    # Play test chime if test was triggered and no prediction result handles it
    if st.session_state.get("trigger_test_alert") and not st.session_state.get("has_prediction"):
        st.session_state["trigger_test_alert"] = False
        test_audio_bytes = generate_alert_wav("warning")
        st.audio(test_audio_bytes, format="audio/wav", autoplay=True)

    # SECTION 1: MACHINE INPUT
    st.markdown(clean_html("""
    <div class="section-header" style="margin-top: 0.3rem;">
      <h2 class="section-title" style="color: #17263D;">Machine Operating Inputs</h2>
      <p class="section-desc">Enter observed machine operational parameters below. You can enter values manually or select a condition preset to populate representative dataset values.</p>
    </div>
    """), unsafe_allow_html=True)

    # 4 Condition Action Buttons: Normal, Warning, Failure, and Clear
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        if st.button("Normal Condition", key="btn_normal_cond", type="secondary", use_container_width=True):
            idx = st.session_state["normal_cycle_idx"] % len(NORMAL_PRESETS)
            st.session_state["normal_cycle_idx"] += 1
            preset = NORMAL_PRESETS[idx]
            st.session_state["input_type"] = preset["Type"]
            st.session_state["input_air_temp"] = preset["Air"]
            st.session_state["input_proc_temp"] = preset["Proc"]
            st.session_state["input_rot_speed"] = preset["Speed"]
            st.session_state["input_torque"] = preset["Torque"]
            st.session_state["input_tool_wear"] = preset["Wear"]
            st.session_state["has_prediction"] = False
            st.session_state["prediction_result"] = None
            st.rerun()

    with b_col2:
        if st.button("Warning Condition", key="btn_warning_cond", type="secondary", use_container_width=True):
            idx = st.session_state["warning_cycle_idx"] % len(WARNING_PRESETS)
            st.session_state["warning_cycle_idx"] += 1
            preset = WARNING_PRESETS[idx]
            st.session_state["input_type"] = preset["Type"]
            st.session_state["input_air_temp"] = preset["Air"]
            st.session_state["input_proc_temp"] = preset["Proc"]
            st.session_state["input_rot_speed"] = preset["Speed"]
            st.session_state["input_torque"] = preset["Torque"]
            st.session_state["input_tool_wear"] = preset["Wear"]
            st.session_state["has_prediction"] = False
            st.session_state["prediction_result"] = None
            st.rerun()

    with b_col3:
        if st.button("Failure Condition", key="btn_failure_cond", type="secondary", use_container_width=True):
            idx = st.session_state["failure_cycle_idx"] % len(FAILURE_PRESETS)
            st.session_state["failure_cycle_idx"] += 1
            preset = FAILURE_PRESETS[idx]
            st.session_state["input_type"] = preset["Type"]
            st.session_state["input_air_temp"] = preset["Air"]
            st.session_state["input_proc_temp"] = preset["Proc"]
            st.session_state["input_rot_speed"] = preset["Speed"]
            st.session_state["input_torque"] = preset["Torque"]
            st.session_state["input_tool_wear"] = preset["Wear"]
            st.session_state["has_prediction"] = False
            st.session_state["prediction_result"] = None
            st.rerun()

    with b_col4:
        if st.button("Clear Inputs", key="btn_clear_inputs", type="secondary", use_container_width=True):
            st.session_state["input_air_temp"] = None
            st.session_state["input_proc_temp"] = None
            st.session_state["input_rot_speed"] = None
            st.session_state["input_torque"] = None
            st.session_state["input_tool_wear"] = None
            st.session_state["input_type"] = "M"
            st.session_state["has_prediction"] = False
            st.session_state["prediction_result"] = None
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 6 inputs arranged in 3x2 grid - NO SLIDERS, rectangular input boxes
    in_r1_c1, in_r1_c2, in_r1_c3 = st.columns(3)
    in_r2_c1, in_r2_c2, in_r2_c3 = st.columns(3)

    air_min = engine.observed_ranges["Air temperature [K]"]["min"]
    air_max = engine.observed_ranges["Air temperature [K]"]["max"]
    proc_min = engine.observed_ranges["Process temperature [K]"]["min"]
    proc_max = engine.observed_ranges["Process temperature [K]"]["max"]
    speed_min = int(engine.observed_ranges["Rotational speed [rpm]"]["min"])
    speed_max = int(engine.observed_ranges["Rotational speed [rpm]"]["max"])
    torque_min = engine.observed_ranges["Torque [Nm]"]["min"]
    torque_max = engine.observed_ranges["Torque [Nm]"]["max"]
    wear_min = int(engine.observed_ranges["Tool wear [min]"]["min"])
    wear_max = int(engine.observed_ranges["Tool wear [min]"]["max"])

    with in_r1_c1:
        type_options = ["L", "M", "H"]
        type_idx = type_options.index(st.session_state["input_type"]) if st.session_state["input_type"] in type_options else 1
        st.session_state["input_type"] = st.selectbox(
            "Product Type",
            options=type_options,
            index=type_idx,
            help="Quality variant: L (Low, 50%), M (Medium, 30%), H (High, 20%)"
        )
        st.caption("Variant: L (Low), M (Medium), H (High)")

    with in_r1_c2:
        val_air = st.session_state["input_air_temp"]
        new_air = st.number_input(
            "Air Temperature [K]",
            value=val_air,
            placeholder=f"{air_min:.1f} – {air_max:.1f} K",
            step=0.1,
            format="%.1f",
            help=f"Observed dataset range: {air_min:.1f} – {air_max:.1f} K"
        )
        st.session_state["input_air_temp"] = new_air
        if new_air is not None and (new_air < air_min or new_air > air_max):
            st.markdown('<span style="color: #D49A3A; font-size: 12px; font-weight: 600;">Value outside observed dataset range.</span>', unsafe_allow_html=True)
        else:
            st.caption(f"Range: {air_min:.1f} – {air_max:.1f} K")

    with in_r1_c3:
        val_proc = st.session_state["input_proc_temp"]
        new_proc = st.number_input(
            "Process Temperature [K]",
            value=val_proc,
            placeholder=f"{proc_min:.1f} – {proc_max:.1f} K",
            step=0.1,
            format="%.1f",
            help=f"Observed dataset range: {proc_min:.1f} – {proc_max:.1f} K"
        )
        st.session_state["input_proc_temp"] = new_proc
        if new_proc is not None and (new_proc < proc_min or new_proc > proc_max):
            st.markdown('<span style="color: #D49A3A; font-size: 12px; font-weight: 600;">Value outside observed dataset range.</span>', unsafe_allow_html=True)
        else:
            st.caption(f"Range: {proc_min:.1f} – {proc_max:.1f} K")

    with in_r2_c1:
        val_speed = st.session_state["input_rot_speed"]
        new_speed = st.number_input(
            "Rotational Speed [rpm]",
            value=val_speed,
            placeholder=f"{speed_min:,} – {speed_max:,} rpm",
            step=10,
            format="%d",
            help=f"Observed dataset range: {speed_min:,} – {speed_max:,} rpm"
        )
        st.session_state["input_rot_speed"] = new_speed
        if new_speed is not None and (new_speed < speed_min or new_speed > speed_max):
            st.markdown('<span style="color: #D49A3A; font-size: 12px; font-weight: 600;">Value outside observed dataset range.</span>', unsafe_allow_html=True)
        else:
            st.caption(f"Range: {speed_min:,} – {speed_max:,} rpm")

    with in_r2_c2:
        val_torque = st.session_state["input_torque"]
        new_torque = st.number_input(
            "Torque [Nm]",
            value=val_torque,
            placeholder=f"{torque_min:.1f} – {torque_max:.1f} Nm",
            step=0.5,
            format="%.1f",
            help=f"Observed dataset range: {torque_min:.1f} – {torque_max:.1f} Nm"
        )
        st.session_state["input_torque"] = new_torque
        if new_torque is not None and (new_torque < torque_min or new_torque > torque_max):
            st.markdown('<span style="color: #D49A3A; font-size: 12px; font-weight: 600;">Value outside observed dataset range.</span>', unsafe_allow_html=True)
        else:
            st.caption(f"Range: {torque_min:.1f} – {torque_max:.1f} Nm")

    with in_r2_c3:
        val_wear = st.session_state["input_tool_wear"]
        new_wear = st.number_input(
            "Tool Wear [min]",
            value=val_wear,
            placeholder=f"{wear_min} – {wear_max} min",
            step=1,
            format="%d",
            help=f"Observed dataset range: {wear_min} – {wear_max} min"
        )
        st.session_state["input_tool_wear"] = new_wear
        if new_wear is not None and (new_wear < wear_min or new_wear > wear_max):
            st.markdown('<span style="color: #D49A3A; font-size: 12px; font-weight: 600;">Value outside observed dataset range.</span>', unsafe_allow_html=True)
        else:
            st.caption(f"Range: {wear_min} – {wear_max} min")

    # Count entered parameters
    entered_inputs = [
        st.session_state["input_type"],
        st.session_state["input_air_temp"],
        st.session_state["input_proc_temp"],
        st.session_state["input_rot_speed"],
        st.session_state["input_torque"],
        st.session_state["input_tool_wear"]
    ]
    entered_count = sum(1 for v in entered_inputs if v is not None)

    # Parameter completion counter
    if entered_count == 6:
        st.markdown(clean_html("""
        <div style="margin: 10px 0 16px 0; font-size: 13.5px; font-weight: 600; color: #56806B; display: flex; align-items: center; gap: 6px;">
          <span>&#10003; All 6 parameters entered</span>
        </div>
        """), unsafe_allow_html=True)
    else:
        st.markdown(clean_html(f"""
        <div style="margin: 10px 0 16px 0; font-size: 13.5px; font-weight: 500; color: #71869D; display: flex; align-items: center; gap: 6px;">
          <span>{entered_count} / 6 parameters entered</span>
        </div>
        """), unsafe_allow_html=True)

    # SECTION 2: PREDICTION ACTION
    st.markdown(clean_html("""
    <div class="ai-card" style="padding: 18px 24px; margin: 14px 0 22px 0; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div style="font-size: 15px; font-weight: 700; color: #17263D;">Ready to Analyze</div>
        <div style="font-size: 13px; color: #71869D;">All 6 operating conditions must be entered before analysis.</div>
      </div>
      <div>
    """), unsafe_allow_html=True)

    can_predict = (entered_count == 6)
    if st.button("Predict Machine Condition", type="primary", key="btn_run_prediction", disabled=not can_predict):
        if can_predict:
            st.session_state["prediction_result"] = engine.predict(
                st.session_state["input_type"],
                st.session_state["input_air_temp"],
                st.session_state["input_proc_temp"],
                st.session_state["input_rot_speed"],
                st.session_state["input_torque"],
                st.session_state["input_tool_wear"]
            )
            st.session_state["has_prediction"] = True
            st.session_state["prediction_counter"] = st.session_state.get("prediction_counter", 0) + 1
            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

    # SECTIONS 3 & 4: ONLY DISPLAYED ONCE PREDICTION IS RUN
    if st.session_state.get("has_prediction") and st.session_state["prediction_result"] is not None:
        pred_res = st.session_state["prediction_result"]
        is_fail = (pred_res["prediction"] == 1)
        status_label = pred_res["prediction_label"]
        fail_prob = pred_res["probability_percent"]

        # Check for specifically elevated parameters to dynamically alert the user
        recs_dict, flagged = generate_dynamic_recommendations(
            pred_res["prediction"],
            pred_res["probability"],
            pred_res["shap_values"],
            pred_res["input_values"],
            engine.normal_averages,
            pred_res["is_unusual"]
        )

        # Classify operational state: Failure, Warning, or Normal
        if is_fail:
            pred_state = "failure"
        elif pred_res["is_unusual"] or len(flagged) > 0 or fail_prob >= 20.0:
            pred_state = "warning"
        else:
            pred_state = "normal"

        result_accent = "#D95C5C" if is_fail else "#56806B"
        result_bg = "#FDEDED" if is_fail else "#EEF5F8"

        # Audio alert dispatch logic (one-shot per new prediction or manual test)
        sound_to_play = None
        if st.session_state.get("trigger_test_alert"):
            st.session_state["trigger_test_alert"] = False
            sound_to_play = "warning"
        elif st.session_state.get("audio_alerts_enabled", True):
            curr_counter = st.session_state.get("prediction_counter", 0)
            if curr_counter > 0 and curr_counter != st.session_state.get("last_played_prediction_counter", 0):
                st.session_state["last_played_prediction_counter"] = curr_counter
                if pred_state in ["warning", "failure"]:
                    sound_to_play = pred_state
        else:
            # When alerts disabled, keep counter synchronized so enabling later won't trigger stale alert
            st.session_state["last_played_prediction_counter"] = st.session_state.get("prediction_counter", 0)

        if sound_to_play:
            alert_audio_bytes = generate_alert_wav(sound_to_play)
            st.audio(alert_audio_bytes, format="audio/wav", autoplay=True)

        # Visual indicator badge inside Prediction Result card
        audio_pill_html = ""
        if st.session_state.get("audio_alerts_enabled", True):
            if pred_state == "failure":
                audio_pill_html = clean_html("""<span class="audio-alert-indicator failure" title="Audible alert dispatched for potential machine failure">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#D95C5C" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
                  Alert Sounded
                </span>""")
            elif pred_state == "warning":
                audio_pill_html = clean_html("""<span class="audio-alert-indicator warning" title="Audible warning chime dispatched for elevated parameters">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#D49A3A" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
                  Warning Chime Sounded
                </span>""")
        else:
            if pred_state in ["warning", "failure"]:
                audio_pill_html = clean_html("""<span class="audio-alert-indicator muted" title="Audio alerts are muted in header settings">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#71869D" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>
                  Alert Muted
                </span>""")

        alert_banner_html = ""
        if flagged:
            flagged_str = " and ".join(flagged)
            alert_banner_html = f"""<div style="background: #FFF5E8; border-left: 4px solid #D49A3A; padding: 10px 16px; border-radius: 6px; margin-top: 12px; font-size: 13.5px; color: #17263D;">
              <strong>Action Focus:</strong> Elevated operating parameters detected in <strong>{flagged_str}</strong>. Detailed diagnostic recommendations are available on the Analysis page.
            </div>"""

        # SECTION 3: PREDICTION RESULT (Large rectangular card)
        st.markdown(clean_html(f"""
        <div class="ai-card" style="border-left: 5px solid {result_accent}; padding: 22px 26px; margin-bottom: 22px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="display: flex; align-items: center;">
                <span style="font-size: 11.5px; font-weight: 700; color: #71869D; text-transform: uppercase; letter-spacing: 0.6px;">Prediction Result</span>
                {audio_pill_html}
              </div>
              <div style="font-size: 24px; font-weight: 700; color: {result_accent}; margin-top: 3px;">
                {status_label}
              </div>
            </div>
            <div style="text-align: right; background: {result_bg}; padding: 10px 18px; border-radius: 8px; border: 1px solid {result_accent}33;">
              <span style="font-size: 12px; font-weight: 600; color: #71869D;">Failure Probability</span>
              <div style="font-size: 22px; font-weight: 700; color: {result_accent};">
                {fail_prob:.1f}%
              </div>
            </div>
          </div>
          {alert_banner_html}
          <div style="font-size: 12.5px; color: #71869D; margin-top: 10px; border-top: 1px solid #E8F1F5; padding-top: 10px;">
            Probability calculated via Random Forest Classifier on AI4I 2020 operational data.
          </div>
        </div>
        """), unsafe_allow_html=True)

        # SECTION 4: OPERATING PATTERN (Isolation Forest with slide-out Reason card)
        st.markdown(clean_html("""
        <div class="section-header">
          <h2 class="section-title" style="color: #17263D;">Operating Pattern</h2>
          <p class="section-desc">Multivariate anomaly detection via Isolation Forest to determine whether the combination looks unusual compared with observed data.</p>
        </div>
        """), unsafe_allow_html=True)

        is_unusual = pred_res["is_unusual"]
        pat_title = pred_res["pattern_title"]
        pat_accent = "#D49A3A" if is_unusual else "#506D8A"
        pat_badge_bg = "#FFF5E6" if is_unusual else "#EEF5F8"

        st.markdown(clean_html(f"""
        <div class="pattern-card-group">
          <div class="pattern-primary-card" style="border-left: 5px solid {pat_accent};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <div style="font-size: 11.5px; font-weight: 700; color: #71869D; text-transform: uppercase; letter-spacing: 0.6px;">Evaluated Operating Pattern</div>
                <div style="font-size: 20px; font-weight: 700; color: #17263D; margin-top: 3px;">
                  {pat_title}
                </div>
              </div>
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 12px; font-weight: 600; color: {pat_accent}; background: {pat_badge_bg}; padding: 6px 14px; border-radius: 6px; border: 1px solid {pat_accent}33;">
                  Anomaly Score: {pred_res['anomaly_score']:.3f}
                </div>
                <div class="reason-indicator">
                  <span style="font-size: 12px; font-weight: 600; color: #506D8A;">Reason &darr;</span>
                </div>
              </div>
            </div>
          </div>
          <div class="pattern-drawer-card">
            <div style="font-size: 11px; font-weight: 700; color: #506D8A; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">
              Diagnostic Rationale
            </div>
            <div style="font-size: 13.5px; color: #17263D; line-height: 1.55;">
              {pred_res['pattern_reason']}
            </div>
          </div>
        </div>
        """), unsafe_allow_html=True)

    else:
        st.markdown(clean_html("""
        <div class="ai-card" style="padding: 24px; text-align: center; color: #71869D; background: #F8FBFC; border: 1px dashed #C8D8E4;">
          <div style="font-size: 15px; font-weight: 600; color: #506D8A; margin-bottom: 4px;">Awaiting Input</div>
          <div style="font-size: 13px;">Please enter the operating parameters above and click <strong>Predict Machine Condition</strong> to view model predictions and anomaly diagnostics.</div>
        </div>
        """), unsafe_allow_html=True)


# -------------------------------------------------------------
# PAGE 3: ANALYSIS
# -------------------------------------------------------------
elif st.session_state["current_page"] == "Analysis":
    st.markdown(clean_html("""
    <div class="page-header">
      <div>
        <h1 class="page-title" style="color: #17263D;">Prediction Explanation & Recommendations</h1>
        <p class="page-subtitle">Why did the model make this prediction, and what should I monitor?</p>
      </div>
    </div>
    """), unsafe_allow_html=True)

    # Check if a prediction has already been generated
    if not st.session_state.get("has_prediction") or st.session_state.get("prediction_result") is None:
        st.markdown(clean_html("""
        <div class="ai-card" style="padding: 32px 24px; text-align: center; margin-bottom: 24px; border: 1px dashed #C8D8E4; background: #F8FBFC;">
          <div style="font-size: 16px; font-weight: 700; color: #17263D; margin-bottom: 6px;">No Prediction Generated Yet</div>
          <p style="font-size: 13.5px; color: #71869D; max-width: 580px; margin: 0 auto;">
            Analysis explains a machine prediction that was already generated on the Prediction page.
            Please enter operating conditions on the <strong>Prediction</strong> page and click <strong>Predict Machine Condition</strong> to view the detailed explanation and recommendations.
          </p>
        </div>
        """), unsafe_allow_html=True)

    else:
        # Retrieve existing prediction generated on Page 2
        pred_res = st.session_state["prediction_result"]
        is_fail = (pred_res["prediction"] == 1)
        status_label = pred_res["prediction_label"]
        fail_prob = pred_res["probability_percent"]
        inp = pred_res["input_values"]
        shap_dict = pred_res["shap_values"]

        # =========================================================
        # SECTION 1: PREDICTION SUMMARY (Strict vertical flow - Section 1)
        # =========================================================
        st.markdown(clean_html("""
        <div class="section-header" style="margin-top: 0.3rem;">
          <h2 class="section-title" style="color: #17263D;">Prediction Summary</h2>
          <p class="section-desc">Machine condition evaluated from the exact parameters entered on the Prediction page.</p>
        </div>
        """), unsafe_allow_html=True)

        result_accent = "#D95C5C" if is_fail else "#56806B"
        result_bg = "#FDEDED" if is_fail else "#EEF5F8"

        # ONE large rectangular prediction-result card
        st.markdown(clean_html(f"""
        <div class="ai-card" style="border-left: 5px solid {result_accent}; padding: 22px 26px; margin-bottom: 18px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <span style="font-size: 11.5px; font-weight: 700; color: #71869D; text-transform: uppercase; letter-spacing: 0.6px;">Prediction</span>
              <div style="font-size: 24px; font-weight: 700; color: {result_accent}; margin-top: 2px;">
                {status_label}
              </div>
            </div>
            <div style="text-align: right; background: {result_bg}; padding: 10px 18px; border-radius: 8px; border: 1px solid {result_accent}33;">
              <span style="font-size: 12px; font-weight: 600; color: #71869D;">Failure Probability</span>
              <div style="font-size: 22px; font-weight: 700; color: {result_accent};">
                {fail_prob:.1f}%
              </div>
            </div>
          </div>
        </div>
        """), unsafe_allow_html=True)

        # Below that: Operating Conditions (SIX compact cards arranged 3 x 2)
        st.markdown(clean_html("""
        <div style="font-size: 13.5px; font-weight: 700; color: #71869D; text-transform: uppercase; letter-spacing: 0.5px; margin: 12px 0 10px 0;">
          Operating Conditions
        </div>
        """), unsafe_allow_html=True)

        c_r1_1, c_r1_2, c_r1_3 = st.columns(3)
        c_r2_1, c_r2_2, c_r2_3 = st.columns(3)

        with c_r1_1:
            st.markdown(clean_html(f"""
            <div class="ai-card" style="padding: 14px 18px;">
              <div style="font-size: 12px; font-weight: 600; color: #71869D;">Air Temperature</div>
              <div style="font-size: 18px; font-weight: 700; color: #17263D; margin-top: 3px;">{inp['Air Temperature']:.1f} K</div>
            </div>
            """), unsafe_allow_html=True)

        with c_r1_2:
            st.markdown(clean_html(f"""
            <div class="ai-card" style="padding: 14px 18px;">
              <div style="font-size: 12px; font-weight: 600; color: #71869D;">Process Temperature</div>
              <div style="font-size: 18px; font-weight: 700; color: #17263D; margin-top: 3px;">{inp['Process Temperature']:.1f} K</div>
            </div>
            """), unsafe_allow_html=True)

        with c_r1_3:
            st.markdown(clean_html(f"""
            <div class="ai-card" style="padding: 14px 18px;">
              <div style="font-size: 12px; font-weight: 600; color: #71869D;">Rotational Speed</div>
              <div style="font-size: 18px; font-weight: 700; color: #17263D; margin-top: 3px;">{inp['Rotational Speed']:,.0f} rpm</div>
            </div>
            """), unsafe_allow_html=True)

        with c_r2_1:
            st.markdown(clean_html(f"""
            <div class="ai-card" style="padding: 14px 18px; margin-top: 10px;">
              <div style="font-size: 12px; font-weight: 600; color: #71869D;">Torque</div>
              <div style="font-size: 18px; font-weight: 700; color: #17263D; margin-top: 3px;">{inp['Torque']:.1f} Nm</div>
            </div>
            """), unsafe_allow_html=True)

        with c_r2_2:
            st.markdown(clean_html(f"""
            <div class="ai-card" style="padding: 14px 18px; margin-top: 10px;">
              <div style="font-size: 12px; font-weight: 600; color: #71869D;">Tool Wear</div>
              <div style="font-size: 18px; font-weight: 700; color: #17263D; margin-top: 3px;">{inp['Tool Wear']:.0f} min</div>
            </div>
            """), unsafe_allow_html=True)

        with c_r2_3:
            st.markdown(clean_html(f"""
            <div class="ai-card" style="padding: 14px 18px; margin-top: 10px;">
              <div style="font-size: 12px; font-weight: 600; color: #71869D;">Product Type</div>
              <div style="font-size: 18px; font-weight: 700; color: #17263D; margin-top: 3px;">{inp['Product Type']}</div>
            </div>
            """), unsafe_allow_html=True)

        # =========================================================
        # SECTION 2: PREDICTION EXPLANATION (Strict vertical flow - Section 2)
        # =========================================================
        st.markdown(clean_html("""
        <div class="section-header" style="margin-top: 2rem;">
          <h2 class="section-title" style="color: #17263D;">Prediction Explanation</h2>
          <p class="section-desc">Explain how the operating conditions relate to the model prediction.</p>
        </div>
        """), unsafe_allow_html=True)

        # Selectable parameter tabs
        param_options = [
            ("Tool Wear", "Tool wear [min]", "min"),
            ("Torque", "Torque [Nm]", "Nm"),
            ("Rotational Speed", "Rotational speed [rpm]", "rpm"),
            ("Process Temperature", "Process temperature [K]", "K"),
            ("Air Temperature", "Air temperature [K]", "K")
        ]

        p_names = [p[0] for p in param_options]
        tab_cols = st.columns(len(param_options))
        for idx, (label, col_key, unit) in enumerate(param_options):
            with tab_cols[idx]:
                is_tab_active = (st.session_state["analysis_selected_param"] == label)
                btn_style = "primary" if is_tab_active else "secondary"
                if st.button(label, key=f"tab_param_{label}", type=btn_style, use_container_width=True):
                    st.session_state["analysis_selected_param"] = label
                    st.rerun()

        # Selected Parameter details
        sel_label = st.session_state["analysis_selected_param"]
        col_key = next(p[1] for p in param_options if p[0] == sel_label)
        unit = next(p[2] for p in param_options if p[0] == sel_label)

        entered_val = float(inp[sel_label])
        normal_avg = engine.normal_averages[col_key]
        normal_std = engine.normal_stds[col_key]

        comp_data = get_parameter_comparison_data(sel_label, entered_val, normal_avg, normal_std)
        scale_html = render_comparison_scale_svg(comp_data, unit)
        st.markdown(scale_html, unsafe_allow_html=True)

        # MODEL CONTRIBUTION (MUST appear BELOW the comparison, NOT beside it!)
        st.markdown(clean_html("""
        <div style="margin-top: 1.2rem;">
          <h3 style="font-size: 16px; font-weight: 700; color: #17263D; margin-bottom: 2px;">Model Contribution</h3>
          <p style="font-size: 12.5px; color: #71869D; margin: 0 0 10px 0;">Tree SHAP feature importance for the current operating prediction.</p>
        </div>
        """), unsafe_allow_html=True)

        chart_html = render_model_contribution_chart_svg(shap_dict, sel_label)
        st.markdown(chart_html, unsafe_allow_html=True)

        # Factual explanation text
        if is_fail:
            top_contribs = sorted(
                [(k, v) for k, v in shap_dict.items() if k != "Type"],
                key=lambda x: x[1],
                reverse=True
            )
            significant_pos = [k for k, v in top_contribs if v > 0.05]
            if significant_pos:
                param_names_clean = [p.split(" [")[0] for p in significant_pos[:2]]
                contrib_text = f"<strong>{' and '.join(param_names_clean)}</strong> contributed strongly to the model's prediction."
            else:
                contrib_text = "The model's failure prediction is influenced by the joint interaction of operating conditions."
        else:
            contrib_text = "The entered operating conditions remain within patterns associated with normal operation."

        st.markdown(clean_html(f"""
        <div style="background: #FFFFFF; border: 1px solid #D8E4EC; border-radius: 8px; padding: 12px 18px; font-size: 13.5px; color: #17263D; margin-bottom: 18px;">
          {contrib_text}
        </div>
        """), unsafe_allow_html=True)

        # =========================================================
        # SECTION 3: RECOMMENDED ACTION (Strict vertical flow - Section 3)
        # =========================================================
        st.markdown(clean_html("""
        <div class="section-header" style="margin-top: 2rem;">
          <h2 class="section-title" style="color: #17263D;">Recommended Action</h2>
          <p class="section-desc">What should I watch?</p>
        </div>
        """), unsafe_allow_html=True)

        recs, flagged_params = generate_dynamic_recommendations(
            pred_res["prediction"],
            pred_res["probability"],
            shap_dict,
            inp,
            engine.normal_averages,
            pred_res["is_unusual"]
        )

        rec_keys = list(recs.keys())
        if not st.session_state["selected_rec_tab"] or st.session_state["selected_rec_tab"] not in rec_keys:
            st.session_state["selected_rec_tab"] = rec_keys[0]

        # Multi-parameter alert banner if specific elevated parameters were detected
        if flagged_params:
            flagged_str = " and ".join(flagged_params)
            st.markdown(clean_html(f"""
            <div style="background: #FFF5E8; border-left: 4px solid #D49A3A; padding: 12px 18px; border-radius: 6px; margin-bottom: 14px; font-size: 14px; color: #17263D;">
              <strong>Parameter Warning:</strong> Operating values for <strong>{flagged_str}</strong> are significantly elevated above typical baseline values. Immediate inspection is recommended.
            </div>
            """), unsafe_allow_html=True)

        # Selectable parameter buttons if multiple parameters are relevant
        if len(rec_keys) > 1:
            rec_cols = st.columns(len(rec_keys))
            for idx, r_key in enumerate(rec_keys):
                with rec_cols[idx]:
                    is_r_active = (st.session_state["selected_rec_tab"] == r_key)
                    r_btn_type = "primary" if is_r_active else "secondary"
                    if st.button(r_key, key=f"rec_tab_{r_key}", type=r_btn_type, use_container_width=True):
                        st.session_state["selected_rec_tab"] = r_key
                        st.rerun()

        active_rec = recs[st.session_state["selected_rec_tab"]]
        rec_level = active_rec["level"]
        rec_border_color = "#D95C5C" if rec_level == "Critical" else ("#D49A3A" if rec_level == "Warning" else "#56806B")

        st.markdown(clean_html(f"""
        <div class="ai-card" style="border-left: 4.5px solid {rec_border_color}; padding: 22px 26px; margin-top: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 16px; font-weight: 700; color: #17263D;">{active_rec['title']}</span>
            <span style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; color: {rec_border_color}; background: #EEF5F8; padding: 4px 10px; border-radius: 4px;">
              {rec_level} Guidance
            </span>
          </div>
          <p style="font-size: 14px; color: #17263D; line-height: 1.6; margin: 0;">
            {active_rec['recommendation']}
          </p>
        </div>
        """), unsafe_allow_html=True)


# -------------------------------------------------------------
# PAGE 4: DATASET (Viewer below divider)
# -------------------------------------------------------------
elif st.session_state["current_page"] == "Dataset":
    st.markdown(clean_html("""
    <div class="page-header">
      <div>
        <h1 class="page-title" style="color: #17263D;">AI4I 2020 Predictive Maintenance Dataset</h1>
        <p class="page-subtitle">Inspect the complete dataset used for predictive maintenance modeling.</p>
      </div>
      <div class="badge-tag">
        10,000 records &bull; 14 columns
      </div>
    </div>
    """), unsafe_allow_html=True)

    # Filter controls in a clean bar
    f_c1, f_c2, f_c3 = st.columns([1.5, 1.5, 3])

    with f_c1:
        failure_filter = st.selectbox(
            "Condition Filter",
            options=["All Records", "Normal Only (0)", "Failure Only (1)"],
            index=0
        )

    with f_c2:
        type_filter = st.selectbox(
            "Product Type Filter",
            options=["All Types", "L", "M", "H"],
            index=0
        )

    with f_c3:
        search_query = st.text_input(
            "Search Product ID or UDI",
            value="",
            placeholder="e.g. M14860 or 47181"
        )

    # Apply filters
    display_df = engine.df.copy()

    if failure_filter == "Normal Only (0)":
        display_df = display_df[display_df["Machine failure"] == 0]
    elif failure_filter == "Failure Only (1)":
        display_df = display_df[display_df["Machine failure"] == 1]

    if type_filter != "All Types":
        display_df = display_df[display_df["Type"] == type_filter]

    if search_query.strip():
        q = search_query.strip()
        display_df = display_df[
            display_df["Product ID"].astype(str).str.contains(q, case=False) |
            display_df["UDI"].astype(str).str.contains(q)
        ]

    st.markdown(clean_html(f"""
    <div style="font-size: 13px; font-weight: 600; color: #71869D; margin: 10px 0 14px 0;">
      Displaying {len(display_df):,} of {len(engine.df):,} records
    </div>
    """), unsafe_allow_html=True)

    # Display clean table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=460,
        hide_index=True
    )

    # Download action buttons (CSV and Excel)
    d_c1, d_c2, _ = st.columns([1.3, 1.3, 4])

    with d_c1:
        csv_data = engine.df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="ai4i2020.csv",
            mime="text/csv",
            use_container_width=True
        )

    with d_c2:
        excel_data = get_cached_excel(engine.df)
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name="ai4i2020.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

"""
AssetInsight - Machine Health Monitoring
CSS Stylesheet and Custom UI Component Renderers
Theme directly aligned with the official reference mockup.
"""

CUSTOM_CSS = """
<style>
/* =======================================================
   AssetInsight Global Industrial Design System
   ======================================================= */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #17263D;
    -webkit-font-smoothing: antialiased;
}

/* App Background: Soft Clean Light Blue-Gray */
[data-testid="stAppViewContainer"],
.stApp {
    background-color: #E8F1F5 !important;
}

/* Main Container Spacing */
.main .block-container {
    max-width: 1160px;
    padding-top: 1.5rem;
    padding-bottom: 3.5rem;
    padding-left: 2.2rem;
    padding-right: 2.2rem;
}

/* Hide default streamlit header decoration and collapse buttons */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 1rem !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

/* CRITICAL: SIDEBAR IS ALWAYS VISIBLE - NO COLLAPSE BUTTON */
[data-testid="stSidebarCollapseButton"],
button[kind="header"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Sidebar: Deep Industrial Navy */
section[data-testid="stSidebar"] {
    display: block !important;
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    background-color: #101D31 !important;
    border-right: 1px solid #182B46 !important;
    box-shadow: 2px 0 14px rgba(10, 19, 33, 0.3) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Sidebar Brand Block */
.sidebar-brand {
    padding: 0.2rem 0.6rem 1.4rem 0.6rem;
}

.sidebar-title {
    font-size: 23px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.4px;
    margin: 0;
    line-height: 1.2;
}

.sidebar-subtitle {
    font-size: 12.5px;
    font-weight: 500;
    color: #7B94B2;
    margin-top: 4px;
    letter-spacing: 0.1px;
}

.sidebar-divider-line {
    height: 1px !important;
    background-color: rgba(255, 255, 255, 0.38) !important;
    margin: 14px 6px 14px 6px !important;
    border: none !important;
    display: block !important;
    width: auto !important;
}

/* SLEEK SIDEBAR NAVIGATION (Overriding Streamlit buttons to match reference mockup) */
section[data-testid="stSidebar"] div.stButton > button {
    width: 100% !important;
    text-align: left !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    background-color: transparent !important;
    color: #8C9FB5 !important;
    box-shadow: none !important;
    margin-bottom: 5px !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #1A2D48 !important;
    color: #FFFFFF !important;
    border-color: #273E60 !important;
    transform: none !important;
}

/* Active Navigation Item (Pill style from reference screenshot) */
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background-color: #243B5C !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: 1px solid #365377 !important;
    box-shadow: 0 2px 8px rgba(10, 20, 35, 0.4) !important;
}

/* Global Cards */
.ai-card {
    background: #FFFFFF;
    border: 1px solid #D8E4EC;
    border-radius: 12px;
    padding: 22px 24px;
    box-shadow: 0 2px 10px rgba(16, 29, 49, 0.04);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
}

.ai-card:hover {
    border-color: #506D8A;
    box-shadow: 0 4px 20px rgba(80, 109, 138, 0.18);
    transform: translateY(-2px);
}

/* Quick Statistics Card (Page 1 row of 4) */
.stat-card {
    background: #FFFFFF;
    border: 1px solid #D8E4EC;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(16, 29, 49, 0.03);
    transition: all 0.25s ease;
    height: 100%;
}

.stat-card:hover {
    border-color: #8BA6C1;
    box-shadow: 0 4px 18px rgba(80, 109, 138, 0.16);
    transform: translateY(-2px);
}

.stat-label {
    font-size: 11px;
    font-weight: 700;
    color: #71869D;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
}

.stat-value {
    font-size: 26px;
    font-weight: 700;
    color: #17263D;
    line-height: 1.1;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
}

.stat-desc {
    font-size: 12px;
    font-weight: 400;
    color: #71869D;
    line-height: 1.35;
}

/* Top Page Header */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.4rem;
}

.page-title {
    font-size: 26px;
    font-weight: 700;
    color: #17263D;
    letter-spacing: -0.4px;
    margin: 0 0 5px 0;
}

.page-subtitle {
    font-size: 13.5px;
    font-weight: 400;
    color: #71869D;
    margin: 0;
}

.badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: #FFFFFF;
    border: 1px solid #D8E4EC;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: #506D8A;
    box-shadow: 0 1px 3px rgba(16, 29, 49, 0.03);
}

/* Section Header */
.section-header {
    margin-top: 1.6rem;
    margin-bottom: 0.85rem;
}

.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #17263D;
    margin: 0 0 3px 0;
    letter-spacing: -0.2px;
}

.section-desc {
    font-size: 13px;
    color: #71869D;
    margin: 0;
}

/* =======================================================
   3D FLIP CARDS (PAGE 1 OVERVIEW)
   ======================================================= */
.flip-card-container {
    perspective: 1000px;
    width: 100%;
    height: 165px;
    cursor: pointer;
}

.flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    transition: transform 0.55s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
    border-radius: 12px;
}

.flip-card-container:hover .flip-card-inner {
    transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    border-radius: 12px;
    border: 1px solid #D8E4EC;
    box-shadow: 0 2px 8px rgba(16, 29, 49, 0.04);
}

.flip-card-front {
    background: #FFFFFF;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 16px 14px;
    transition: all 0.25s ease;
}

.flip-card-container:hover .flip-card-front {
    border-color: #5B8AC2;
    box-shadow: 0 4px 18px rgba(91, 138, 194, 0.22);
}

.flip-card-back {
    background: #F4F8FA;
    color: #17263D;
    transform: rotateY(180deg);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 14px 14px;
    border-color: #506D8A;
    box-shadow: 0 4px 18px rgba(80, 109, 138, 0.18);
}

.flip-icon-circle {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #EEF5F8;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    color: #506D8A;
}

.flip-card-title {
    font-size: 12.5px;
    font-weight: 600;
    color: #71869D;
    margin-bottom: 4px;
}

.flip-card-value {
    font-size: 20px;
    font-weight: 700;
    color: #17263D;
}

.flip-back-heading {
    font-size: 11px;
    font-weight: 700;
    color: #506D8A;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.flip-back-text {
    font-size: 11.5px;
    color: #17263D;
    line-height: 1.45;
    margin: 0;
    font-weight: 400;
}

/* =======================================================
   OPERATING PATTERN SLIDE-OUT CARD (PAGE 2 PREDICTION)
   ======================================================= */
.pattern-card-group {
    position: relative;
    margin-bottom: 22px;
}

.pattern-primary-card {
    background: #FFFFFF;
    border: 1px solid #D8E4EC;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(16, 29, 49, 0.04);
    position: relative;
    z-index: 2;
    transition: all 0.25s ease;
}

.pattern-card-group:hover .pattern-primary-card {
    border-color: #506D8A;
    box-shadow: 0 4px 16px rgba(80, 109, 138, 0.16);
}

.pattern-drawer-card {
    position: relative;
    z-index: 1;
    background: #F4F8FA;
    border: 1px solid #D8E4EC;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 16px 22px;
    margin-top: -6px;
    transform: translateY(-8px);
    opacity: 0.88;
    transition: all 0.32s cubic-bezier(0.16, 1, 0.3, 1);
}

.pattern-card-group:hover .pattern-drawer-card {
    transform: translateY(0);
    opacity: 1;
    background: #EEF5F8;
    box-shadow: 0 6px 16px rgba(80, 109, 138, 0.12);
}

.reason-indicator {
    padding: 4px 10px;
    background: #F4F8FA;
    border-radius: 5px;
    border: 1px solid #D8E4EC;
    transition: all 0.2s ease;
}

.pattern-card-group:hover .reason-indicator {
    background: #E0EBF2;
    border-color: #506D8A;
}

/* =======================================================
   STREAMLIT FORM, INPUTS & SELECTBOX FIX
   Ensures Product Type selectbox has clean white background and dark readable text
   ======================================================= */
/* SELECTBOX BACKGROUND & TEXT (Fixes dark/black column issue) */
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] div[aria-expanded],
div[data-baseweb="select"] * {
    background-color: #FFFFFF !important;
    color: #17263D !important;
}

div[data-baseweb="select"] > div {
    border: 1px solid #D8E4EC !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    box-shadow: 0 1px 3px rgba(16, 29, 49, 0.02) !important;
}

div[data-baseweb="select"] > div:hover,
div[data-baseweb="select"] > div:focus-within {
    border-color: #506D8A !important;
    box-shadow: 0 0 0 2px rgba(80, 109, 138, 0.18) !important;
}

/* Dropdown Popup Menu */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"] {
    background-color: #FFFFFF !important;
    color: #17263D !important;
}

li[role="option"]:hover,
li[aria-selected="true"] {
    background-color: #EEF5F8 !important;
    color: #17263D !important;
}

/* Number Input Box */
div[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    border: 1px solid #D8E4EC !important;
    border-radius: 8px !important;
    color: #17263D !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    min-height: 42px !important;
    box-shadow: 0 1px 3px rgba(16, 29, 49, 0.02) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stNumberInput"] input:focus {
    border-color: #506D8A !important;
    box-shadow: 0 0 0 2px rgba(80, 109, 138, 0.18) !important;
}

/* Fix Stepper Buttons (+ / -) in number inputs so they are soft light buttons */
div[data-testid="stNumberInput"] button {
    background-color: #F4F8FA !important;
    color: #506D8A !important;
    border-color: #D8E4EC !important;
    border-radius: 6px !important;
}

div[data-testid="stNumberInput"] button:hover {
    background-color: #E2ECF2 !important;
    color: #17263D !important;
}

div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #17263D !important;
    margin-bottom: 5px !important;
}

/* Main Content Primary Action Button */
div.main .stButton > button[kind="primary"] {
    background-color: #101D31 !important;
    color: #FFFFFF !important;
    border: 1px solid #101D31 !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 2px 6px rgba(16, 29, 49, 0.15) !important;
    transition: all 0.2s ease !important;
}

div.main .stButton > button[kind="primary"]:hover {
    background-color: #1E3456 !important;
    border-color: #1E3456 !important;
    box-shadow: 0 4px 14px rgba(16, 29, 49, 0.25) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Button */
div.main .stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #17263D !important;
    border: 1px solid #D8E4EC !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    transition: all 0.2s ease !important;
}

div.main .stButton > button[kind="secondary"]:hover {
    background-color: #EEF5F8 !important;
    border-color: #8BA6C1 !important;
    color: #101D31 !important;
}

/* Dataframe Container */
div[data-testid="stDataFrame"] {
    border: 1px solid #D8E4EC !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
}
</style>
"""

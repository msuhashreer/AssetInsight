"""
AssetInsight - Machine Health Monitoring
CSS Stylesheet and Custom UI Component Renderers
Theme directly aligned with the official reference mockup.
Cross-device compatibility: locked light theme, high-contrast headings, responsive sidebar support.
"""

CUSTOM_CSS = """
<style>
/* =======================================================
   AssetInsight Global Industrial Design System
   Enforced Light Theme & Cross-Device Compatibility
   ======================================================= */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    color-scheme: light !important;
    --text-color: #17263D !important;
    --background-color: #E8F1F5 !important;
    --secondary-background-color: #FFFFFF !important;
}

html, body, [class*="css"], .stApp {
    color-scheme: light !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    color: #17263D !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}

/* App Background: Soft Clean Light Blue-Gray */
[data-testid="stAppViewContainer"],
.stApp {
    background-color: #E8F1F5 !important;
    color: #17263D !important;
}

/* Main Container Spacing */
.main .block-container {
    max-width: 1160px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2.2rem !important;
    padding-right: 2.2rem !important;
}

/* =======================================================
   HEADER, TOOLBAR & SIDEBAR TOGGLE
   ======================================================= */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: auto !important;
    min-height: 2.5rem !important;
    z-index: 100 !important;
}

/* Keep stToolbar active so the expand button can function, but hide deploy/extra actions */
[data-testid="stToolbar"] {
    display: flex !important;
    background: transparent !important;
    visibility: visible !important;
}

[data-testid="stToolbarActions"],
#MainMenu,
footer {
    display: none !important;
}

/* Streamlit Sidebar Expand button (visible when sidebar is collapsed) */
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background-color: #101D31 !important;
    border: 1px solid #243B5C !important;
    border-radius: 8px !important;
    padding: 6px 8px !important;
    box-shadow: 0 2px 10px rgba(10, 19, 33, 0.3) !important;
    cursor: pointer !important;
    z-index: 999999 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stExpandSidebarButton"] svg,
[data-testid="collapsedControl"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}

[data-testid="stExpandSidebarButton"]:hover,
[data-testid="collapsedControl"]:hover {
    background-color: #1A2D48 !important;
    border-color: #365377 !important;
}

/* =======================================================
   SIDEBAR: Deep Industrial Navy
   ======================================================= */
section[data-testid="stSidebar"],
.stSidebar {
    background-color: #101D31 !important;
    border-right: 1px solid #182B46 !important;
    box-shadow: 2px 0 14px rgba(10, 19, 33, 0.3) !important;
    z-index: 99999 !important;
}

/* Ensure sidebar stays visible and docked on screens >= 768px (laptops, desktops) */
@media (min-width: 768px) {
    section[data-testid="stSidebar"],
    .stSidebar {
        display: block !important;
        visibility: visible !important;
        transform: none !important;
        margin-left: 0 !important;
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }

    /* Hide redundant expand toggle when sidebar is forced open on desktop */
    [data-testid="stExpandSidebarButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Hide internal collapse button on desktop to keep sidebar consistently pinned */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Sidebar Brand Block */
.sidebar-brand {
    padding: 0.2rem 0.6rem 1.4rem 0.6rem !important;
}

.sidebar-title {
    font-size: 23px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    letter-spacing: -0.4px !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}

.sidebar-subtitle {
    font-size: 12.5px !important;
    font-weight: 500 !important;
    color: #7B94B2 !important;
    -webkit-text-fill-color: #7B94B2 !important;
    margin-top: 4px !important;
    letter-spacing: 0.1px !important;
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
    -webkit-text-fill-color: #8C9FB5 !important;
    box-shadow: none !important;
    margin-bottom: 5px !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #1A2D48 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border-color: #273E60 !important;
    transform: none !important;
}

/* Active Navigation Item (Pill style from reference screenshot) */
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background-color: #243B5C !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 600 !important;
    border: 1px solid #365377 !important;
    box-shadow: 0 2px 8px rgba(10, 20, 35, 0.4) !important;
}

/* =======================================================
   TYPOGRAPHY & HEADINGS (Strict Light Enforced)
   ======================================================= */
h1, h2, h3, h4, h5, h6,
h1.page-title, h2.section-title,
.page-title, .section-title,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.4rem;
}

.page-title {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    letter-spacing: -0.4px !important;
    margin: 0 0 5px 0 !important;
}

.page-subtitle {
    font-size: 13.5px !important;
    font-weight: 400 !important;
    color: #71869D !important;
    -webkit-text-fill-color: #71869D !important;
    margin: 0 !important;
}

.badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: #FFFFFF !important;
    border: 1px solid #D8E4EC !important;
    border-radius: 6px;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #506D8A !important;
    -webkit-text-fill-color: #506D8A !important;
    box-shadow: 0 1px 3px rgba(16, 29, 49, 0.03);
}

/* Section Header */
.section-header {
    margin-top: 1.6rem;
    margin-bottom: 0.85rem;
}

.section-title {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    margin: 0 0 3px 0 !important;
    letter-spacing: -0.2px !important;
}

.section-desc {
    font-size: 13px !important;
    color: #71869D !important;
    -webkit-text-fill-color: #71869D !important;
    margin: 0 !important;
}

/* =======================================================
   CARDS & STAT CONTAINERS
   ======================================================= */
.ai-card {
    background: #FFFFFF !important;
    border: 1px solid #D8E4EC !important;
    border-radius: 12px;
    padding: 22px 24px;
    box-shadow: 0 2px 10px rgba(16, 29, 49, 0.04);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    color: #17263D !important;
}

.ai-card:hover {
    border-color: #506D8A !important;
    box-shadow: 0 4px 20px rgba(80, 109, 138, 0.18);
    transform: translateY(-2px);
}

/* Quick Statistics Card (Page 1 row of 4) */
.stat-card {
    background: #FFFFFF !important;
    border: 1px solid #D8E4EC !important;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(16, 29, 49, 0.03);
    transition: all 0.25s ease;
    height: 100%;
    color: #17263D !important;
}

.stat-card:hover {
    border-color: #8BA6C1 !important;
    box-shadow: 0 4px 18px rgba(80, 109, 138, 0.16);
    transform: translateY(-2px);
}

.stat-label {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #71869D !important;
    -webkit-text-fill-color: #71869D !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    margin-bottom: 6px !important;
}

.stat-value {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    line-height: 1.1 !important;
    margin-bottom: 6px !important;
    letter-spacing: -0.3px !important;
}

.stat-desc {
    font-size: 12px !important;
    font-weight: 400 !important;
    color: #71869D !important;
    -webkit-text-fill-color: #71869D !important;
    line-height: 1.35 !important;
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
    border: 1px solid #D8E4EC !important;
    box-shadow: 0 2px 8px rgba(16, 29, 49, 0.04);
}

.flip-card-front {
    background: #FFFFFF !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 16px 14px;
    transition: all 0.25s ease;
    color: #17263D !important;
}

.flip-card-container:hover .flip-card-front {
    border-color: #5B8AC2 !important;
    box-shadow: 0 4px 18px rgba(91, 138, 194, 0.22);
}

.flip-card-back {
    background: #F4F8FA !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    transform: rotateY(180deg);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 14px 14px;
    border-color: #506D8A !important;
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
    font-size: 12.5px !important;
    font-weight: 600 !important;
    color: #71869D !important;
    -webkit-text-fill-color: #71869D !important;
    margin-bottom: 4px !important;
}

.flip-card-value {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
}

.flip-back-heading {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #506D8A !important;
    -webkit-text-fill-color: #506D8A !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 6px !important;
}

.flip-back-text {
    font-size: 11.5px !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    line-height: 1.45 !important;
    margin: 0 !important;
    font-weight: 400 !important;
}

/* =======================================================
   OPERATING PATTERN SLIDE-OUT CARD (PAGE 2 PREDICTION)
   ======================================================= */
.pattern-card-group {
    position: relative;
    margin-bottom: 22px;
}

.pattern-primary-card {
    background: #FFFFFF !important;
    border: 1px solid #D8E4EC !important;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(16, 29, 49, 0.04);
    position: relative;
    z-index: 2;
    transition: all 0.25s ease;
    color: #17263D !important;
}

.pattern-card-group:hover .pattern-primary-card {
    border-color: #506D8A !important;
    box-shadow: 0 4px 16px rgba(80, 109, 138, 0.16);
}

.pattern-drawer-card {
    position: relative;
    z-index: 1;
    background: #F4F8FA !important;
    border: 1px solid #D8E4EC !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px;
    padding: 16px 22px;
    margin-top: -6px;
    transform: translateY(-8px);
    opacity: 0.88;
    transition: all 0.32s cubic-bezier(0.16, 1, 0.3, 1);
    color: #17263D !important;
}

.pattern-card-group:hover .pattern-drawer-card {
    transform: translateY(0);
    opacity: 1;
    background: #EEF5F8 !important;
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
   ======================================================= */
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] div[aria-expanded],
div[data-baseweb="select"] * {
    background-color: #FFFFFF !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
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
    -webkit-text-fill-color: #17263D !important;
}

li[role="option"]:hover,
li[aria-selected="true"] {
    background-color: #EEF5F8 !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
}

/* Number Input & Text Input Boxes */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    border: 1px solid #D8E4EC !important;
    border-radius: 8px !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    min-height: 42px !important;
    box-shadow: 0 1px 3px rgba(16, 29, 49, 0.02) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #506D8A !important;
    box-shadow: 0 0 0 2px rgba(80, 109, 138, 0.18) !important;
}

/* Stepper Buttons (+ / -) in number inputs */
div[data-testid="stNumberInput"] button {
    background-color: #F4F8FA !important;
    color: #506D8A !important;
    -webkit-text-fill-color: #506D8A !important;
    border-color: #D8E4EC !important;
    border-radius: 6px !important;
}

div[data-testid="stNumberInput"] button:hover {
    background-color: #E2ECF2 !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
}

/* Input Labels & Captions */
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
label[data-testid="stWidgetLabel"] {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #17263D !important;
    -webkit-text-fill-color: #17263D !important;
    margin-bottom: 5px !important;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: #71869D !important;
    -webkit-text-fill-color: #71869D !important;
    font-size: 12px !important;
}

/* Main Content Primary Action Button */
div.main .stButton > button[kind="primary"] {
    background-color: #101D31 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
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
    -webkit-text-fill-color: #17263D !important;
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
    -webkit-text-fill-color: #101D31 !important;
}

/* Dataframe Container */
div[data-testid="stDataFrame"] {
    border: 1px solid #D8E4EC !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
}
</style>
"""

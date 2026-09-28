"""
AssetInsight - Machine Health Monitoring
Utility functions for Gauges, Comparisons, Dynamic Recommendations, and OpenPyXL Excel generation.
Dual-tier non-overlapping scale ensures Typical (above) and Current (below) never collide.
"""

import io
import os
import wave
import struct
import math
import pandas as pd
import numpy as np

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# Ensure matplotlib cache is in a writable location
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"


def generate_alert_wav(alert_type: str = "warning") -> bytes:
    """
    Generates a pure, subtle industrial alert tone in-memory as WAV audio bytes.
    - warning: Soft, warm ascending two-tone chime (D5: 587.33 Hz -> A5: 880.0 Hz).
    - failure: Distinct three-tone alert chime (A5: 880 Hz -> F#5: 740 Hz -> D5: 587.33 Hz).
    Uses pure Python standard library (wave, struct, math) with zero external dependencies.
    """
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


def clean_html(html_str: str) -> str:
    """
    Strips leading and trailing whitespace from every line of the HTML string.
    Streamlit markdown interprets lines with 4 or more leading spaces as
    markdown code blocks (<pre><code>). This function guarantees proper HTML rendering.
    """
    lines = [line.strip() for line in html_str.splitlines()]
    return "".join(lines)


def generate_health_gauge_svg(healthy_pct: float = 96.61, failure_pct: float = 3.39) -> str:
    """
    Generates a clean, modern SVG semi-circular arc gauge matching the industrial visual style.
    Visualizes the historical dataset baseline distribution (normal vs. failure records).
    Healthy: Muted Slate Blue (#506D8A)
    Failure: Muted Red (#D95C5C)
    """
    r = 100
    cx, cy = 160, 135
    stroke_w = 22
    total_arc = np.pi * r  # ~314.16

    healthy_fraction = max(0.0, min(1.0, healthy_pct / 100.0))
    healthy_dash = healthy_fraction * total_arc
    failure_dash = total_arc - healthy_dash

    healthy_color = "#506D8A"
    failure_color = "#D95C5C"
    bg_track_color = "#DDE7ED"

    svg = f"""<svg viewBox="0 0 320 170" width="100%" height="170" style="display: block; margin: 0 auto; max-width: 320px;" xmlns="http://www.w3.org/2000/svg">
<path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}" fill="none" stroke="{bg_track_color}" stroke-width="{stroke_w}" stroke-linecap="round" />
<path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}" fill="none" stroke="{healthy_color}" stroke-width="{stroke_w}" stroke-linecap="round" stroke-dasharray="{healthy_dash:.2f} {total_arc:.2f}" stroke-dashoffset="0" />
<path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}" fill="none" stroke="{failure_color}" stroke-width="{stroke_w}" stroke-linecap="round" stroke-dasharray="{failure_dash:.2f} {total_arc:.2f}" stroke-dashoffset="-{healthy_dash:.2f}" />
<text x="{cx}" y="{cy - 18}" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="28" fill="#17263D">{healthy_pct:.2f}%</text>
<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="500" font-size="12.5" fill="#71869D">Normal Operation Baseline</text>
</svg>"""
    return clean_html(svg)


def get_parameter_comparison_data(param_name: str, entered_val: float, normal_avg: float, normal_std: float):
    """
    Computes comparative position and factual interpretation.
    Scale: Lower ─────── Typical ─────── Higher
    """
    threshold = max(normal_std * 0.5, abs(normal_avg) * 0.04) if normal_std > 0 else 5.0
    diff = entered_val - normal_avg

    if diff > threshold:
        interpretation = "Higher than typical operating level"
        status_color = "#D95C5C" if diff > 2 * threshold else "#D49A3A"
    elif diff < -threshold:
        interpretation = "Lower than typical operating level"
        status_color = "#D95C5C" if diff < -2 * threshold else "#D49A3A"
    else:
        interpretation = "Within typical operating level"
        status_color = "#56806B"

    # Normalize position for visual scale: 0% (low), 50% (typical), 100% (high)
    span = max(normal_std * 3.0, abs(normal_avg) * 0.25) if normal_std > 0 else 20.0
    relative_pos = 50.0 + ((diff / span) * 45.0)
    relative_pos = max(5.0, min(95.0, relative_pos))

    return {
        "param_name": param_name,
        "entered_val": entered_val,
        "normal_avg": normal_avg,
        "diff": diff,
        "interpretation": interpretation,
        "status_color": status_color,
        "entered_pct": relative_pos,
        "typical_pct": 50.0
    }


def render_comparison_scale_svg(comp_data: dict, unit: str) -> str:
    """
    Renders the custom industrial dual-marker comparison scale.
    FIXED DUAL-TIER DESIGN (Pure Vector SVG):
    - Typical Baseline is positioned strictly in the UPPER TIER above the track.
    - Current Value is positioned strictly in the LOWER TIER below the track.
    - Mathematical vertical separation guarantees they NEVER collide or overlap!
    """
    entered_pct = max(6.0, min(94.0, float(comp_data["entered_pct"])))
    typical_pct = 50.0
    entered_val = comp_data["entered_val"]
    normal_avg = comp_data["normal_avg"]
    status_color = comp_data["status_color"]

    if unit == "rpm":
        entered_str = f"{entered_val:,.0f} {unit}"
        typical_str = f"{normal_avg:,.0f} {unit}"
    elif unit == "min":
        entered_str = f"{entered_val:.0f} {unit}"
        typical_str = f"{normal_avg:.0f} {unit}"
    else:
        entered_str = f"{entered_val:.1f} {unit}"
        typical_str = f"{normal_avg:.1f} {unit}"

    # Calculate exact SVG X-coordinates across viewBox width of 700
    track_width = 700.0
    entered_x = (entered_pct / 100.0) * track_width
    typical_x = (typical_pct / 100.0) * track_width

    # Badges clamped safely within 15px margins
    typ_badge_w = 152
    typ_badge_x = max(15, min(track_width - typ_badge_w - 15, typical_x - typ_badge_w / 2.0))

    cur_badge_w = 138
    cur_badge_x = max(15, min(track_width - cur_badge_w - 15, entered_x - cur_badge_w / 2.0))

    html = f"""<div style="background: #FFFFFF; border: 1px solid #D8E4EC; border-radius: 12px; padding: 22px 26px; margin: 14px 0 20px 0; box-shadow: 0 2px 8px rgba(16, 29, 49, 0.04);">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px;">
<div>
<span style="font-size: 12px; font-weight: 700; color: #71869D; text-transform: uppercase; letter-spacing: 0.6px;">Entered Value</span>
<div style="font-size: 26px; font-weight: 700; color: #17263D; margin-top: 2px;">{entered_str}</div>
</div>
<div style="text-align: right;">
<span style="font-size: 12px; font-weight: 700; color: #71869D; text-transform: uppercase; letter-spacing: 0.6px;">Typical Baseline</span>
<div style="font-size: 20px; font-weight: 600; color: #506D8A; margin-top: 2px;">{typical_str}</div>
</div>
</div>
<!-- Dual-Tier High-Precision SVG Scale (Upper: Typical, Lower: Current) -->
<svg viewBox="0 0 700 120" width="100%" height="120" style="display: block; margin: 6px 0 14px 0;" xmlns="http://www.w3.org/2000/svg">
<!-- Track Background -->
<rect x="20" y="47" width="660" height="8" rx="4" fill="#E2ECF2" />
<!-- Typical Operating Range (Nominal Core) -->
<rect x="230" y="47" width="240" height="8" rx="4" fill="#C5D8E4" />

<!-- UPPER TIER: Typical Baseline Marker & Badge (y=6 to y=47) -->
<line x1="{typical_x:.1f}" y1="28" x2="{typical_x:.1f}" y2="55" stroke="#506D8A" stroke-width="2.5" />
<rect x="{typ_badge_x:.1f}" y="6" width="{typ_badge_w}" height="22" rx="4" fill="#F0F5F8" stroke="#CADBE6" stroke-width="1.2" />
<text x="{typ_badge_x + typ_badge_w / 2:.1f}" y="21" fill="#43607E" font-size="11.5" font-family="system-ui, -apple-system, sans-serif" font-weight="700" text-anchor="middle">Typical Baseline: {typical_str}</text>

<!-- LOWER TIER: Current Entered Value Pin & Badge (y=47 to y=102) -->
<circle cx="{entered_x:.1f}" cy="51" r="7.5" fill="{status_color}" stroke="#FFFFFF" stroke-width="2.5" />
<line x1="{entered_x:.1f}" y1="59" x2="{entered_x:.1f}" y2="75" stroke="{status_color}" stroke-width="2" />
<rect x="{cur_badge_x:.1f}" y="75" width="{cur_badge_w}" height="25" rx="5" fill="{status_color}" />
<text x="{cur_badge_x + cur_badge_w / 2:.1f}" y="92" fill="#FFFFFF" font-size="12" font-family="system-ui, -apple-system, sans-serif" font-weight="700" text-anchor="middle">Current: {entered_str}</text>

<!-- Sub-track Zone Identifiers -->
<text x="24" y="115" fill="#8C9EAF" font-size="10.5" font-family="system-ui, -apple-system, sans-serif" font-weight="600">LOWER ZONE</text>
<text x="350" y="115" fill="#71869D" font-size="10.5" font-family="system-ui, -apple-system, sans-serif" font-weight="600" text-anchor="middle">TYPICAL OPERATING RANGE</text>
<text x="676" y="115" fill="#8C9EAF" font-size="10.5" font-family="system-ui, -apple-system, sans-serif" font-weight="600" text-anchor="end">HIGHER ZONE</text>
</svg>
<!-- Factual Interpretation Status Bar -->
<div style="margin-top: 14px; padding: 12px 16px; background: #EEF5F8; border-left: 4px solid {status_color}; border-radius: 6px; display: flex; align-items: center; justify-content: space-between;">
<span style="font-size: 13.5px; font-weight: 600; color: #17263D;">Evaluation: {comp_data['interpretation']}</span>
<span style="font-size: 12.5px; font-weight: 600; color: #506D8A;">Baseline Delta: {comp_data['diff']:+.1f} {unit}</span>
</div>
</div>"""
    return clean_html(html)


def render_model_contribution_chart_svg(shap_dict: dict, selected_param: str = None) -> str:
    """
    Generates a clean horizontal bar chart for Model Contribution using actual SHAP values.
    Zero indentation on every line prevents markdown code-block bugs.
    """
    display_params = [
        ("Tool wear [min]", "Tool Wear"),
        ("Torque [Nm]", "Torque"),
        ("Rotational speed [rpm]", "Rotational Speed"),
        ("Process temperature [K]", "Process Temperature"),
        ("Air temperature [K]", "Air Temperature")
    ]

    values = [shap_dict.get(col, 0.0) for col, label in display_params]
    max_abs = max(max([abs(v) for v in values]), 0.01)

    chart_rows_html = ""
    for (col, label), val in zip(display_params, values):
        pct = (abs(val) / max_abs) * 100.0
        pct = max(3.0, min(100.0, pct))

        is_selected = (selected_param and (selected_param.lower() in label.lower() or label.lower() in selected_param.lower()))
        bar_color = "#3A5574" if is_selected else "#506D8A"
        bg_highlight = "background: #F4F8FA; border-radius: 6px;" if is_selected else ""
        border_indicator = "border-left: 3px solid #3A5574;" if is_selected else "border-left: 3px solid transparent;"
        font_wt = "700" if is_selected else "500"
        txt_clr = "#17263D" if is_selected else "#506D8A"
        sign_str = f"{val:+.3f}"

        chart_rows_html += f"""<div style="display: flex; align-items: center; margin: 8px 0; padding: 7px 10px; {bg_highlight} {border_indicator} transition: all 0.2s ease;">
<div style="width: 170px; font-size: 13.5px; font-weight: {font_wt}; color: #17263D;">{label}</div>
<div style="flex: 1; margin: 0 14px; position: relative;">
<div style="height: 12px; background: #DDE7ED; border-radius: 6px; overflow: hidden;">
<div style="width: {pct:.1f}%; height: 100%; background: {bar_color}; border-radius: 6px; transition: width 0.4s ease;"></div>
</div>
</div>
<div style="width: 75px; text-align: right; font-size: 12.5px; font-weight: 600; font-family: 'SF Mono', Consolas, monospace; color: {txt_clr};">{sign_str}</div>
</div>"""

    card = f"""<div style="background: #FFFFFF; border: 1px solid #D8E4EC; border-radius: 12px; padding: 22px 24px; margin: 14px 0 20px 0; box-shadow: 0 2px 8px rgba(16, 29, 49, 0.04);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #E8F1F5; padding-bottom: 10px;">
<span style="font-size: 14px; font-weight: 600; color: #17263D;">Parameter Contribution (SHAP Values)</span>
<span style="font-size: 12px; color: #71869D; font-weight: 500;">Directional Impact on Failure Risk</span>
</div>
<div style="display: flex; flex-direction: column;">
{chart_rows_html}
</div>
<div style="display: flex; justify-content: space-between; font-size: 11.5px; color: #71869D; margin-top: 14px; padding-top: 8px; border-top: 1px dashed #E2ECF2;">
<span>Lower Contribution</span>
<span>Calculated via Tree SHAP Explainer (Log-Odds Domain)</span>
<span>Higher Contribution</span>
</div>
</div>"""
    return clean_html(card)


def generate_dynamic_recommendations(prediction: int, prob: float, shap_dict: dict,
                                     input_values: dict, normal_averages: dict, is_unusual: bool):
    """
    Produces dynamic, context-specific monitoring recommendations.
    Directly flags specific parameters that are elevated (e.g. Torque and Temperature)
    and provides detailed actionable guidance for each.
    """
    tool_wear = input_values.get("Tool Wear", 0.0)
    torque = input_values.get("Torque", 0.0)
    speed = input_values.get("Rotational Speed", 0.0)
    air_temp = input_values.get("Air Temperature", 0.0)
    proc_temp = input_values.get("Process Temperature", 0.0)
    temp_diff = proc_temp - air_temp

    recs = {}
    flagged_params = []

    # 1. Torque check
    tq_norm = normal_averages.get("Torque [Nm]", 39.6)
    if torque > 52.0 or shap_dict.get("Torque [Nm]", 0.0) > 0.05:
        delta = torque - tq_norm
        flagged_params.append("Torque")
        recs["Torque"] = {
            "title": "Torque",
            "param_key": "torque",
            "level": "Critical" if torque > 62.0 else "Warning",
            "recommendation": (
                f"Action Required: Check torque and motor drive loading. Current torque is {torque:.1f} Nm "
                f"(+{delta:.1f} Nm above typical baseline of {tq_norm:.1f} Nm). "
                f"Monitor operating load if torque continues to increase beyond the typical operating level. "
                f"Inspect spindle bearings, mechanical alignment, and transmission gearing to prevent overstrain."
            )
        }
    elif torque < 16.0 and speed > 2200:
        flagged_params.append("Torque")
        recs["Torque"] = {
            "title": "Torque",
            "param_key": "torque",
            "level": "Critical",
            "recommendation": (
                f"Action Required: Torque is abnormally low ({torque:.1f} Nm) relative to high spindle speed ({speed:,.0f} rpm). "
                f"Inspect for cutter disengagement, broken tool tip, or transmission belt slippage."
            )
        }

    # 2. Temperature check
    pt_norm = normal_averages.get("Process temperature [K]", 310.0)
    at_norm = normal_averages.get("Air temperature [K]", 300.0)
    if proc_temp > 311.5 or temp_diff < 8.6 or shap_dict.get("Process temperature [K]", 0.0) > 0.04 or shap_dict.get("Air temperature [K]", 0.0) > 0.04:
        flagged_params.append("Process Temperature")
        delta_p = proc_temp - pt_norm
        recs["Process Temperature"] = {
            "title": "Process Temperature",
            "param_key": "proc_temp",
            "level": "Warning",
            "recommendation": (
                f"Action Required: Check machine thermal dissipation. Process temperature is currently {proc_temp:.1f} K "
                f"(+{delta_p:.1f} K above normal baseline of {pt_norm:.1f} K), with an air-to-process differential of {temp_diff:.1f} K. "
                f"Verify cutting fluid circulation, clean thermal heat sinks, and check environmental cooling."
            )
        }

    # 3. Tool Wear check
    tw_norm = normal_averages.get("Tool wear [min]", 106.7)
    if tool_wear > 150.0 or shap_dict.get("Tool wear [min]", 0.0) > 0.05:
        flagged_params.append("Tool Wear")
        recs["Tool Wear"] = {
            "title": "Tool Wear",
            "param_key": "tool_wear",
            "level": "Critical" if tool_wear > 200.0 else "Warning",
            "recommendation": (
                f"Action Required: Continue monitoring tool wear as operating conditions change. Tool wear is currently at "
                f"{tool_wear:.0f} min (typical baseline is {tw_norm:.0f} min). "
                f"Consider inspection and tool insert replacement if wear accumulation continues."
            )
        }

    # 4. Rotational Speed check
    spd_norm = normal_averages.get("Rotational speed [rpm]", 1540)
    if speed > 2100 or speed < 1320 or shap_dict.get("Rotational speed [rpm]", 0.0) > 0.06:
        flagged_params.append("Rotational Speed")
        recs["Rotational Speed"] = {
            "title": "Rotational Speed",
            "param_key": "rot_speed",
            "level": "Critical" if (speed > 2500 or speed < 1250) else "Warning",
            "recommendation": (
                f"Action Required: Monitor rotational speed if it continues to move outside the typical operating range. "
                f"Current speed is {speed:,.0f} rpm (typical baseline is {spd_norm:,.0f} rpm). "
                f"Check inverter drive stability, frequency oscillation, and spindle encoder feedback."
            )
        }

    # If prediction is failure or high probability, but no specific threshold was tripped
    if (prediction == 1 or prob >= 0.40) and not recs:
        recs["Critical Monitoring"] = {
            "title": "Elevated Risk Monitoring",
            "param_key": "elevated_risk",
            "level": "Warning",
            "recommendation": (
                "The model detected high multivariate sensitivity across the combination of operating conditions. "
                "Closely monitor spindle drive load and cutting tool wear rate over subsequent operating cycles."
            )
        }

    # If completely Normal Operation with no elevated values
    if not recs and prediction == 0:
        recs["Standard Monitoring"] = {
            "title": "Operating Conditions",
            "param_key": "normal_routine",
            "level": "Normal",
            "recommendation": (
                "Operating conditions are within typical patterns. Continue monitoring the parameters as they change. "
                "All mechanical and thermal variables are currently operating within historical reliability envelopes."
            )
        }

    return recs, flagged_params


def generate_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    Creates an Excel spreadsheet in memory using OpenPyXL with professional styling.
    Falls back gracefully if openpyxl is not available in the runtime.
    """
    if not HAS_OPENPYXL:
        buf = io.BytesIO()
        try:
            with pd.ExcelWriter(buf, engine=None) as writer:
                df.to_excel(writer, index=False)
        except Exception:
            # Direct CSV bytes fallback
            return df.to_csv(index=False).encode("utf-8")
        return buf.getvalue()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AI4I 2020 Dataset"

    header_fill = PatternFill(start_color="101D31", end_color="101D31", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=10, color="17263D")
    border_thin = Border(
        left=Side(style='thin', color="D4E0E7"),
        right=Side(style='thin', color="D4E0E7"),
        top=Side(style='thin', color="D4E0E7"),
        bottom=Side(style='thin', color="D4E0E7")
    )
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")

    headers = list(df.columns)
    ws.append(headers)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align

    for row in df.itertuples(index=False):
        ws.append(list(row))

    for row in ws.iter_rows(min_row=2, max_row=len(df)+1):
        for cell in row:
            cell.font = data_font
            cell.border = border_thin
            if isinstance(cell.value, (int, float)):
                cell.alignment = right_align
            else:
                cell.alignment = left_align

    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col[:40])
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

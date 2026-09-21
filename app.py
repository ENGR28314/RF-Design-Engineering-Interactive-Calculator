import streamlit as st
import numpy as np
import plotly.graph_objects as go

# App title and description
st.set_page_config(page_title="RF Design Engineering Suite", layout="wide")
st.title("📡 RF Design Engineering Interactive Calculator")
st.markdown("Based on the *RF Design Engineering Master Guide* formulas.")

# Sidebar navigation
tool_choice = st.sidebar.radio(
    "Select an RF Analysis Module",
    ["Free-Space Path Loss (FSPL)", "Impedance Mismatch & VSWR"]
)

# ----------------------------------------------------
# MODULE 1: FREE-SPACE PATH LOSS (FSPL)
# ----------------------------------------------------
if tool_choice == "Free-Space Path Loss (FSPL)":
    st.header("📉 Free-Space Path Loss (FSPL) Visualizer")
    st.markdown(
        r"Formula: $FSPL(dB) = 20\log_{10}(d) + 20\log_{10}(f) + 32.45$  "
        "\n*(where $d$ is distance in km, and $f$ is frequency in MHz)*"
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Inputs")
        freq = st.number_input("Frequency (MHz)", min_value=1.0, max_value=100000.0, value=1800.0, step=100.0)
        max_dist = st.slider("Maximum Distance Plot Range (km)", min_value=1.0, max_value=100.0, value=20.0)
        target_dist = st.number_input("Specific Evaluation Distance (km)", min_value=0.1, max_value=float(max_dist), value=5.0)
        
        # Calculate specific result
        specific_fspl = 20 * np.log10(target_dist) + 20 * np.log10(freq) + 32.45
        st.metric(label=f"FSPL at {target_dist} km", value=f"{specific_fspl:.2f} dB")
        
    with col2:
        st.subheader("FSPL vs. Distance Curve")
        distances = np.linspace(0.1, max_dist, 500)
        fspl_values = 20 * np.log10(distances) + 20 * np.log10(freq) + 32.45
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=distances, y=fspl_values, mode='lines', name='FSPL (dB)', line=dict(color='#FF4B4B', width=3)))
        fig.add_trace(go.Scatter(x=[target_dist], y=[specific_fspl], mode='markers+text', 
                                 text=[f"{specific_fspl:.1f} dB"], textposition="top left",
                                 marker=dict(size=12, color='blue'), name='Your Selection'))
        
        fig.update_layout(xaxis_title="Distance (km)", yaxis_title="Path Loss (dB)", 
                          margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        
    st.info(f"💡 **Interpretation:** At **{freq} MHz**, signal attenuation increases logarithmically. "
            f"If you double the distance, your path loss increases by approximately **6 dB**.")

# ----------------------------------------------------
# MODULE 2: IMPEDANCE MISMATCH & VSWR
# ----------------------------------------------------
elif tool_choice == "Impedance Mismatch & VSWR":
    st.header("⚡ Impedance Mismatch & VSWR Analyzer")
    st.markdown(
        r"Formulas: $\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0} \quad \text{and} \quad VSWR = \frac{1 + |\Gamma|}{1 - |\Gamma|}$"
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Inputs")
        z0 = st.number_input("System Characteristic Impedance Z₀ (Ω)", min_value=1.0, max_value=300.0, value=50.0)
        zl = st.number_input("Actual Load Impedance Z_L (Ω)", min_value=1.0, max_value=500.0, value=75.0)
        
        # Calculations
        gamma = (zl - z0) / (zl + z0)
        vswr = (1 + abs(gamma)) / (1 - abs(gamma))
        return_loss = -20 * np.log10(abs(gamma)) if gamma != 0 else float('inf')
        
        st.subheader("Results")
        st.metric(label="Reflection Coefficient (Γ)", value=f"{gamma:.3f}")
        st.metric(label="VSWR", value=f"{vswr:.2f} : 1")
        st.metric(label="Return Loss (RL)", value=f"{return_loss:.2f} dB" if return_loss != float('inf') else "∞ dB")
        
    with col2:
        st.subheader("VSWR Sensitivity Curve")
        zl_range = np.linspace(1, 200, 500)
        gamma_range = (zl_range - z0) / (zl_range + z0)
        vswr_range = (1 + np.abs(gamma_range)) / (1 - np.abs(gamma_range))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=zl_range, y=vswr_range, mode='lines', name='VSWR', line=dict(color='#0068C9')))
        fig.add_trace(go.Scatter(x=[zl], y=[vswr], mode='markers+text', 
                                 text=[f"{vswr:.2f}:1"], textposition="top center",
                                 marker=dict(size=12, color='red'), name='Current Load'))
        
        fig.update_layout(xaxis_title="Load Impedance Z_L (Ω)", yaxis_title="VSWR", 
                          yaxis=dict(maxallowed=10, range=[1, 10]), margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    # Interpretations based on the guide's standards
    if vswr <= 1.5:
        st.success("✅ **Interpretation:** VSWR is **excellent** (< 1.5:1). This matches typical industrial radio acceptance criteria.")
    elif vswr <= 2.0:
        st.warning("⚠️ **Interpretation:** VSWR is **acceptable** but sub-optimal. Minor reflections are present.")
    else:
        st.error("🚨 **Interpretation:** High mismatch! Excessive signal energy is reflecting back to the source, which can damage transmission components.")

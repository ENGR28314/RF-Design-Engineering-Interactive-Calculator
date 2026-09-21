 import streamlit as st
import numpy as np
import plotly.graph_objects as go

# App configuration
st.set_page_config(page_title="Advanced RF Design Engineering Suite", layout="wide")
st.title("📡 Master RF Design Engineering Suite")
st.markdown("A interactive playground implementing core formulas from the *RF Design Engineering Master Guide*.")

# Sidebar navigation
tool_choice = st.sidebar.radio(
    "Select an RF Analysis Module",
    [
        "Free-Space Path Loss (FSPL)", 
        "Impedance Mismatch & VSWR",
        "Cascaded Noise Figure (Friis Formula)",
        "End-to-End Link Budget Calculator",
        "IQ Constellation Mismatch Visualizer",
        "Beamwidth & Sector Array Gain"
    ]
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Inputs")
        freq = st.number_input("Frequency (MHz)", min_value=1.0, max_value=100000.0, value=1800.0, step=100.0)
        max_dist = st.slider("Maximum Distance Plot Range (km)", min_value=1.0, max_value=100.0, value=20.0)
        target_dist = st.number_input("Specific Evaluation Distance (km)", min_value=0.1, max_value=float(max_dist), value=5.0)
        
        specific_fspl = 20 * np.log10(target_dist) + 20 * np.log10(freq) + 32.45
        st.metric(label=f"FSPL at {target_dist} km", value=f"{specific_fspl:.2f} dB")
        
    with col2:
        st.subheader("FSPL vs. Distance Curve")
        distances = np.linspace(0.1, max_dist, 500)
        fspl_values = 20 * np.log10(distances) + 20 * np.log10(freq) + 32.45
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=distances, y=fspl_values, mode='lines', name='FSPL (dB)', line=dict(color='#FF4B4B', width=3)))
        fig.add_trace(go.Scatter(x=[target_dist], y=[specific_fspl], mode='markers+text', 
                                 text=[f"  {specific_fspl:.1f} dB"], textposition="top left",
                                 marker=dict(size=12, color='blue'), name='Your Selection'))
        
        fig.update_layout(xaxis_title="Distance (km)", yaxis_title="Path Loss (dB)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    st.info(f"💡 **Interpretation:** At **{freq} MHz**, signal attenuation increases logarithmically. "
            f"Doubling your operating distance adds roughly **6 dB** of attenuation.")

# ----------------------------------------------------
# MODULE 2: IMPEDANCE MISMATCH & VSWR
# ----------------------------------------------------
elif tool_choice == "Impedance Mismatch & VSWR":
    st.header("⚡ Impedance Mismatch & VSWR Analyzer")
    st.markdown(
        r"Formulas: $\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0} \quad \text{and} \quad VSWR = \frac{1 + |\Gamma|}{1 - |\Gamma|}$"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Inputs")
        z0 = st.number_input("System Characteristic Impedance Z₀ (Ω)", min_value=1.0, max_value=300.0, value=50.0)
        zl = st.number_input("Actual Load Impedance Z_L (Ω)", min_value=1.0, max_value=500.0, value=75.0)
        
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
                                 text=[f"  {vswr:.2f}:1"], textposition="top center",
                                 marker=dict(size=12, color='red'), name='Current Load'))
        
        fig.update_layout(xaxis_title="Load Impedance Z_L (Ω)", yaxis_title="VSWR", yaxis=dict(range=[1, 10]), margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    if vswr <= 1.5:
        st.success("✅ **Interpretation:** VSWR is **excellent** (< 1.5:1). This targets standard cellular RAN acceptance parameters.")
    elif vswr <= 2.0:
        st.warning("⚠️ **Interpretation:** VSWR is **marginal**. Minor reflections exist. Watch out for transmission heat build-up.")
    else:
        st.error("🚨 **Interpretation:** Critical mismatch! Severe reflected energy can stress or permanently damage the PA.")

# ----------------------------------------------------
# MODULE 3: CASCAEDED NOISE FIGURE (FRIIS FORMULA)
# ----------------------------------------------------
elif tool_choice == "Cascaded Noise Figure (Friis Formula)":
    st.header("🎛️ Cascaded Noise Figure (Friis Formula)")
    st.markdown(
        r"Formula: $F_{\text{total}} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2}$ *(Note: Calculations use linear power ratios, not dBs)*"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stage 1 (e.g., LNA)")
        nf1 = st.number_input("Stage 1 Noise Figure (dB)", min_value=0.0, max_value=20.0, value=1.5, step=0.1)
        g1 = st.number_input("Stage 1 Gain (dB)", min_value=0.0, max_value=40.0, value=15.0, step=1.0)
        
        st.subheader("Stage 2 (e.g., Mixer)")
        nf2 = st.number_input("Stage 2 Noise Figure (dB)", min_value=0.0, max_value=20.0, value=6.0, step=0.1)
        g2 = st.number_input("Stage 2 Gain (dB)", min_value=-20.0, max_value=40.0, value=10.0, step=1.0)
        
        st.subheader("Stage 3 (e.g., IF Amplifier)")
        nf3 = st.number_input("Stage 3 Noise Figure (dB)", min_value=0.0, max_value=20.0, value=4.0, step=0.1)
        
        f1_lin, g1_lin = 10**(nf1/10), 10**(g1/10)
        f2_lin, g2_lin = 10**(nf2/10), 10**(g2/10)
        f3_lin = 10**(nf3/10)
        
        f_total_2 = f1_lin + (f2_lin - 1) / g1_lin
        f_total_3 = f_total_2 + (f3_lin - 1) / (g1_lin * g2_lin)
        
        nf_total = 10 * np.log10(f_total_3)
        st.subheader("System Result")
        st.metric(label="Total Cascaded Noise Figure (NF)", value=f"{nf_total:.2f} dB")
        
    with col2:
        st.subheader("Noise Figure Accumulation Analysis")
        stages_labels = ['Stage 1 Only', 'Stage 1 + 2', 'Complete Cascade (1+2+3)']
        nf_steps = [nf1, 10 * np.log10(f_total_2), nf_total]
        
        fig = go.Figure(go.Bar(
            x=stages_labels, y=nf_steps,
            text=[f"{x:.2f} dB" for x in nf_steps], textposition='auto',
            marker_color=['#4C78A8', '#F58518', '#E45756']
        ))
        fig.update_layout(yaxis_title="Running Noise Figure (dB)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    st.info("💡 **Friis Rule Interpretation:** Notice how little the Noise Figure increases after Stage 1. "
            "High gain ($G_1$) in your low-noise amplifier suppresses noise additions from all down-chain components.")

# ----------------------------------------------------
# MODULE 4: END-TO-END LINK BUDGET CALCULATOR
# ----------------------------------------------------
elif tool_choice == "End-to-End Link Budget Calculator":
    st.header("🚀 End-to-End Link Budget Analyzer")
    st.markdown(
        r"Formulas: $EIRP = P_{\text{tx}} + G_{\text{tx}} - \text{Loss}_{\text{tx}} \quad \text{and} \quad P_{\text{rx}} = EIRP - FSPL + G_{\text{rx}} - \text{Loss}_{\text{rx}}$"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Transmitter Parameters")
        ptx = st.number_input("Tx Output Power (dBm)", min_value=-30.0, max_value=60.0, value=43.0, step=1.0)
        gtx = st.number_input("Tx Antenna Gain (dBi)", min_value=0.0, max_value=30.0, value=18.0, step=0.5)
        ltx = st.number_input("Tx Cable & Connector Loss (dB)", min_value=0.0, max_value=10.0, value=2.0, step=0.5)
        
        eirp = ptx + gtx - ltx
        st.metric(label="Calculated EIRP", value=f"{eirp:.2f} dBm")
        
        st.subheader("Channel & Receiver Parameters")
        link_dist = st.number_input("Link Distance (km)", min_value=0.1, max_value=200.0, value=10.0)
        link_freq = st.number_input("Operating Frequency (MHz)", min_value=1.0, max_value=100000.0, value=2100.0, step=100.0)
        grx = st.number_input("Rx Antenna Gain (dBi)", min_value=0.0, max_value=30.0, value=15.0, step=0.5)
        lrx = st.number_input("Rx Cable & Connector Loss (dB)", min_value=0.0, max_value=10.0, value=1.5, step=0.5)
        sensitivity = st.number_input("Receiver Sensitivity Floor (dBm)", min_value=-130.0, max_value=-50.0, value=-95.0, step=1.0)
        
        fspl_mid = 20 * np.log10(link_dist) + 20 * np.log10(link_freq) + 32.45
        prx = eirp - fspl_mid + grx - lrx
        margin = prx - sensitivity
        
    with col2:
        st.subheader("Link Budget Power Level Progression")
        stages = ['Tx Power', 'EIRP', 'After FSPL', 'Received Power (Prx)', 'Rx Sensitivity']
        levels = [ptx, eirp, eirp - fspl_mid, prx, sensitivity]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stages, y=levels, mode='lines+markers+text',

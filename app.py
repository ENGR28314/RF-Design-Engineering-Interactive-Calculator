 import streamlit as st
import numpy as np
import plotly.graph_objects as go

# App layout setup
st.set_page_config(page_title="Master RF Design Engineering Suite", layout="wide")
st.title("📡 Master RF Design Engineering Dashboard")
st.markdown("An interactive simulation toolkit built on verified engineering models.")

# Navigation Sidebar
tool_choice = st.sidebar.radio(
    "Select an RF Analysis Module",
    [
        "Free-Space Path Loss (FSPL)", 
        "Impedance Mismatch & VSWR",
        "Cascaded Noise Figure (Friis Formula)",
        "End-to-End Link Budget Calculator",
        "IQ Constellation Mismatch Visualizer",
        "Beamwidth & Sector Array Gain",
        "dB / dBm Quick Conversion Matrix",
        "Quarter-Wave Transformer Designer"
    ]
)

# ----------------------------------------------------
# MODULE 1: FREE-SPACE PATH LOSS (FSPL)
# ----------------------------------------------------
if tool_choice == "Free-Space Path Loss (FSPL)":
    st.header("📉 Free-Space Path Loss (FSPL) Visualizer")
    st.markdown(r"Formula: $FSPL(dB) = 20\log_{10}(d) + 20\log_{10}(f) + 32.45$")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Parameters")
        freq = st.number_input("Frequency (MHz)", min_value=1.0, max_value=100000.0, value=1800.0)
        max_dist = st.slider("Plot Distance Max Boundary (km)", min_value=1.0, max_value=100.0, value=20.0)
        target_dist = st.number_input("Target Evaluation Distance (km)", min_value=0.1, max_value=float(max_dist), value=5.0)
        
        specific_fspl = 20 * np.log10(target_dist) + 20 * np.log10(freq) + 32.45
        st.metric(label=f"FSPL Attenuation at {target_dist} km", value=f"{specific_fspl:.2f} dB")
    with col2:
        distances = np.linspace(0.1, max_dist, 500)
        fspl_values = 20 * np.log10(distances) + 20 * np.log10(freq) + 32.45
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=distances, y=fspl_values, mode='lines', name='FSPL Curve', line=dict(color='#FF4B4B', width=3)))
        fig.add_trace(go.Scatter(x=[target_dist], y=[specific_fspl], mode='markers', marker=dict(size=12, color='blue'), name='Target Selection'))
        fig.update_layout(xaxis_title="Distance (km)", yaxis_title="Loss (dB)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# MODULE 2: IMPEDANCE MISMATCH & VSWR
# ----------------------------------------------------
elif tool_choice == "Impedance Mismatch & VSWR":
    st.header("⚡ Impedance Mismatch & VSWR Analyzer")
    st.markdown(r"Formulas: $\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0} \quad VSWR = \frac{1 + |\Gamma|}{1 - |\Gamma|}$")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("System Topology")
        z0 = st.number_input("System Reference Impedance Z₀ (Ω)", min_value=1.0, max_value=300.0, value=50.0)
        zl = st.number_input("Complex Load Real Impedance Z_L (Ω)", min_value=1.0, max_value=500.0, value=75.0)
        
        gamma = (zl - z0) / (zl + z0)
        vswr = (1 + abs(gamma)) / (1 - abs(gamma)) if (1 - abs(gamma)) != 0 else 999.0
        return_loss = -20 * np.log10(abs(gamma)) if gamma != 0 else float('inf')
        
        st.metric(label="VSWR Level", value=f"{vswr:.2f} : 1")
        st.metric(label="Return Loss (RL)", value=f"{return_loss:.2f} dB" if return_loss != float('inf') else "∞ dB")
    with col2:
        zl_range = np.linspace(1, 200, 500)
        vswr_range = (1 + np.abs((zl_range - z0) / (zl_range + z0))) / (1 - np.abs((zl_range - z0) / (zl_range + z0)))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=zl_range, y=vswr_range, mode='lines', name='VSWR Slope', line=dict(color='#0068C9')))
        fig.add_trace(go.Scatter(x=[zl], y=[vswr], mode='markers', marker=dict(size=12, color='red'), name='Current Operating Load'))
        fig.update_layout(xaxis_title="Load Impedance Z_L (Ω)", yaxis_title="VSWR", yaxis=dict(range=[1, 10]), margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# MODULE 3: CASCADED NOISE FIGURE (FRIIS FORMULA)
# ----------------------------------------------------
elif tool_choice == "Cascaded Noise Figure (Friis Formula)":
    st.header("🎛️ Cascaded Noise Figure (Friis Formula)")
    st.markdown(r"Formula: $F_{\text{total}} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2}$")
    col1, col2 = st.columns(2)
    with col1:
        nf1 = st.number_input("Stage 1 (LNA) NF (dB)", min_value=0.0, max_value=20.0, value=1.5)
        g1 = st.number_input("Stage 1 (LNA) Gain (dB)", min_value=0.0, max_value=40.0, value=15.0)
        nf2 = st.number_input("Stage 2 (Mixer) NF (dB)", min_value=0.0, max_value=20.0, value=6.0)
        g2 = st.number_input("Stage 2 (Mixer) Gain (dB)", min_value=-20.0, max_value=40.0, value=10.0)
        nf3 = st.number_input("Stage 3 (IF Amp) NF (dB)", min_value=0.0, max_value=20.0, value=4.0)
        
        f1, g1_l = 10**(nf1/10), 10**(g1/10)
        f2, g2_l = 10**(nf2/10), 10**(g2/10)
        f3 = 10**(nf3/10)
        
        f_tot_2 = f1 + (f2 - 1) / g1_l
        f_tot_3 = f_tot_2 + (f3 - 1) / (g1_l * g2_l)
        nf_total = 10 * np.log10(f_tot_3)
        st.metric(label="Total Cascade System Noise Figure", value=f"{nf_total:.2f} dB")
    with col2:
        steps = ['LNA Output', 'Post-Mixer Stage', 'Full Receiver Cascade']
        vals = [nf1, 10 * np.log10(f_tot_2), nf_total]
        fig = go.Figure(go.Bar(x=steps, y=vals, marker_color=['#4C78A8', '#F58518', '#E45756']))
        fig.update_layout(yaxis_title="System Running Noise Figure (dB)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# MODULE 4: END-TO-END LINK BUDGET CALCULATOR
# ----------------------------------------------------
elif tool_choice == "End-to-End Link Budget Calculator":
    st.header("🚀 End-to-End Link Budget Analyzer")
    col1, col2 = st.columns(2)
    with col1:
        ptx = st.number_input("Tx Transmit Power (dBm)", min_value=-30.0, max_value=60.0, value=43.0)
        gtx = st.number_input("Tx Element Gain (dBi)", min_value=0.0, max_value=30.0, value=18.0)
        ltx = st.number_input("Tx Component Feeder Losses (dB)", min_value=0.0, max_value=10.0, value=2.0)
        dist = st.number_input("Channel Physical Path Range (km)", min_value=0.1, max_value=200.0, value=10.0)
        freq_lb = st.number_input("Link Channel Carrier Frequency (MHz)", min_value=1.0, max_value=100000.0, value=2100.0)
        grx = st.number_input("Rx Base Element Gain (dBi)", min_value=0.0, max_value=30.0, value=15.0)
        lrx = st.number_input("Rx Component Feeder Losses (dB)", min_value=0.0, max_value=10.0, value=1.5)
        sens = st.number_input("Target Receiver Demodulation Threshold (dBm)", min_value=-130.0, max_value=-50.0, value=-95.0)
        
        eirp = ptx + gtx - ltx
        fspl = 20 * np.log10(dist) + 20 * np.log10(freq_lb) + 32.45
        prx = eirp - fspl + grx - lrx
        fade_margin = prx - sens
        st.metric(label="Available Channel Operating Fade Margin", value=f"{fade_margin:.2f} dB")
    with col2:
        stages = ['Tx Engine Output', 'EIRP Footprint', 'Free-Space Cut', 'Rx Antenna Capture', 'Sensitivity Floor']
        levels = [ptx, eirp, eirp - fspl, prx, sens]
        fig = go.Figure(go.Scatter(x=stages, y=levels, mode='lines+markers+text', text=[f"{x:.1f}" for x in levels], textposition="top center"))
        fig.update_layout(yaxis_title="Calculated Signal Level (dBm)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# MODULE 5: IQ CONSTELLATION MISMATCH VISUALIZER
# ----------------------------------------------------
elif tool_choice == "IQ Constellation Mismatch Visualizer":
    st.header("🎨 IQ Constellation Mismatch Visualizer")
    col1, col2 = st.columns(2)
    with col1:
        amp_imb = st.slider("Gain Cross-Imbalance Delta (dB)", min_value=-3.0, max_value=3.0, value=0.8, step=0.1)
        phase_err = st.slider("Phase Orthogonality Displacement Angle (°)", min_value=-20.0, max_value=20.0, value=8.0, step=0.5)
        
        a = 10**(amp_imb / 20)
        p = np.radians(phase_err)
        ii, qq = np.array([1, -1, -1, 1]), np.array([1, 1, -1, -1])
        
        di = ii * a * np.cos(p/2) - qq * np.sin(p/2)
        dq = qq * (1/a) * np.cos(p/2) - ii * np.sin(p/2)
        evm = (np.mean(np.sqrt((di-ii)**2 + (dq-qq)**2)) / np.sqrt(2)) * 100
        st.metric(label="System Error Vector Magnitude (EVM Ratio)", value=f"{evm:.2f} %")
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ii, y=qq, mode='markers', name='Reference Ideal states', marker=dict(size=14, color='rgba(0,0,0,0)', line=dict(width=2, color='green'))))
        fig.add_trace(go.Scatter(x=di, y=dq, mode='markers', name='Impaired Stream Nodes', marker=dict(size=12, color='red', symbol='x')))
        fig.update_layout(xaxis=dict(range=[-2, 2], title="In-Phase Axis"), yaxis=dict(range=[-2, 2], title="Quadrature Axis"), width=400, height=400)
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# MODULE 6: BEAMWIDTH & SECTOR ARRAY GAIN
# ----------------------------------------------------
elif tool_choice == "Beamwidth & Sector Array Gain":
    st.header("📐 Spatial Structural Array Gain Estimator")
    st.markdown(r"Formula: $G(dBi) \approx 10\cdot\log_{10}\left(\frac{41253}{\theta_H \cdot \theta_V}\right)$")
    col1, col2 = st.columns(2)
    with col1:
        th_h = st.slider("Horizontal Half-Power -3dB Contour Aperture (°)", min_value=5.0, max_value=120.0, value=65.0)

import streamlit as st
import numpy as np
import librosa
import plotly.graph_objects as go
from src.audio_utils import load_and_clean_audio, apply_highpass_filter, get_3d_coordinates
from src.viz_utils import render_3d_video
import os

st.set_page_config(page_title="NamY Lab - Bioacoustics", layout="wide")

st.title("🔬 NamY Advanced Bioacoustics Research")

uploaded_file = st.file_uploader("Tải dữ liệu âm thanh Chào mào", type=["mp3", "wav"])

if uploaded_file:
    y, sr = load_and_clean_audio(uploaded_file)
    
    # --- SIDEBAR: ĐIỀU KHIỂN NÂNG CAO ---
    st.sidebar.header("⚙️ Thông số nghiên cứu")
    speed = st.sidebar.select_slider("Tốc độ phân tích (Speed)", options=[0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 4.0], value=1.0)
    
    freq_min, freq_max = st.sidebar.slider("Dải tần số quan tâm (Hz)", 0, 10000, (1500, 8000))
    show_axes = st.sidebar.checkbox("Hiển thị hệ trục 3D trong video", value=True)
    color_theme = st.sidebar.selectbox("Dãy màu sắc (Colorscale)", ["Turbo", "Viridis", "Magma", "Plasma"])

    # Lọc tần số theo yêu cầu người dùng
    y_filtered = apply_highpass_filter(y, sr, cutoff=freq_min)
    
    # --- HIỂN THỊ BIỂU ĐỒ 2D ---
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 📈 Waveform")
        st.audio(y_filtered, sample_rate=sr)
    
    # --- RENDER VIDEO ---
    st.markdown("---")
    if st.button("🎬 Bắt đầu Render Video Nghiên cứu"):
        with st.status(f"Đang xử lý ở tốc độ x{speed}...") as status:
            temp_audio = "temp_input.wav"
            with open(temp_audio, "wb") as f: f.write(uploaded_file.getbuffer())
            
            x, y_c, z = get_3d_coordinates(y_filtered, sr)
            output = "research_output.mp4"
            render_3d_video(x, y_c, z, temp_audio, output, speed=speed, show_axes=show_axes)
            
            st.video(output)
            st.success(f"Video đã đồng bộ ở tốc độ x{speed}")

    # --- GIAO DIỆN 3D TƯƠNG TÁC (Dành cho nghiên cứu đồ thị) ---
    st.markdown("---")
    st.write("### 🧊 Đồ thị 3D Tương tác (Interactive Research Plot)")
    st.info("Bạn có thể xoay, thu phóng và di chuột để xem thông số cụ thể từng âm tiết.")
    
    x_coords, y_coords, z_coords = get_3d_coordinates(y_filtered, sr)
    
    fig_3d = go.Figure(data=[go.Scatter3d(
        x=x_coords, y=y_coords, z=z_coords,
        mode='markers+lines',
        marker=dict(
            size=z_coords*20 + 2,
            color=x_coords,
            colorscale=color_theme,
            opacity=0.8
        ),
        line=dict(color='rgba(100,100,100,0.2)', width=1)
    )])
    
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='Tần số (Centroid)',
            yaxis_title='Độ trải phổ (Rolloff)',
            zaxis_title='Cường độ (RMS)',
            xaxis=dict(backgroundcolor="rgb(255, 255, 255)", gridcolor="lightgray"),
            yaxis=dict(backgroundcolor="rgb(255, 255, 255)", gridcolor="lightgray"),
            zaxis=dict(backgroundcolor="rgb(255, 255, 255)", gridcolor="lightgray"),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        template="plotly_white"
    )
    st.plotly_chart(fig_3d, use_container_width=True)
import streamlit as st
import os
import numpy as np
import librosa
import plotly.graph_objects as go
from src.audio_utils import load_and_clean_audio, apply_highpass_filter, get_3d_coordinates
from src.viz_utils import render_3d_video

st.set_page_config(page_title="NamY Bioacoustics", page_icon="🕊️", layout="wide")

# Theme sáng cho Sidebar
st.sidebar.title("🕊️ NamY Bioacoustics")
st.sidebar.info("Dự án giải mã ngôn ngữ chim Chào Mào")

st.title("📊 Phân tích cấu trúc âm tiết & Quang phổ")
st.markdown("---")

uploaded_file = st.file_uploader("Tải lên file âm thanh", type=["mp3", "wav"])

if uploaded_file:
    y, sr = load_and_clean_audio(uploaded_file)
    y_clean = apply_highpass_filter(y, sr)

    # --- BIỂU ĐỒ DẠNG SÓNG (WAVEFORM) ---
    st.write("### 📈 Biểu đồ dạng sóng (Waveform)")
    step = 10
    time_axis = np.linspace(0, len(y_clean)/sr, len(y_clean))[::step]
    fig_wave = go.Figure()
    fig_wave.add_trace(go.Scatter(x=time_axis, y=y_clean[::step], line=dict(color='#0284c7')))
    fig_wave.update_layout(template="plotly_white", height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_wave, use_container_width=True)

    # --- BIỂU ĐỒ QUANG PHỔ (SPECTROGRAM) ---
    st.write("### 🌌 Biểu đồ quang phổ (Spectrogram)")
    # Tính toán phổ ký
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y_clean)), ref=np.max)
    
    fig_spec = go.Figure(data=go.Heatmap(
        z=D,
        x=np.linspace(0, len(y_clean)/sr, D.shape[1]),
        y=librosa.fft_frequencies(sr=sr),
        colorscale='Turbo' # Màu sắc rực rỡ theo tần số
    ))
    fig_spec.update_layout(
        template="plotly_white", 
        height=400, 
        yaxis_title="Tần số (Hz)",
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_spec, use_container_width=True)

    st.markdown("---")

    # --- RENDER VIDEO ---
    if st.button("🚀 Render Video 3D lung linh"):
        with st.status("Đang render video nền sáng...") as status:
            temp_audio = f"temp_{uploaded_file.name}"
            with open(temp_audio, "wb") as f: f.write(uploaded_file.getbuffer())
            
            x, y_coord, z = get_3d_coordinates(y_clean, sr)
            output = "namy_3d_pro.mp4"
            render_3d_video(x, y_coord, z, temp_audio, output)
            
            st.video(output)
            os.remove(temp_audio)
            status.update(label="✅ Đã xong!", state="complete")
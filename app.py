# app.py
import streamlit as st
import plotly.graph_objects as go
from src.audio_utils import load_and_clean_audio, apply_highpass_filter
import librosa
import numpy as np

# Cấu hình thương hiệu NamY
st.set_page_config(page_title="NamY Bioacoustics - Chào Mào Project", layout="wide")

st.sidebar.title("🕊️ NamY Bioacoustics")
st.sidebar.info("Dự án phân tích ngôn ngữ chim Chào Mào (Red-whiskered Bulbul)")

st.title("Phân tích Âm thanh Chim Bản địa")
st.markdown("---")

# Khu vực Upload
uploaded_file = st.file_uploader("Chọn file âm thanh Chào mào (mp3, wav)", type=["mp3", "wav"])

if uploaded_file:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔊 Dữ liệu gốc")
        st.audio(uploaded_file)
        y, sr = load_and_clean_audio(uploaded_file)
        st.write(f"Sample Rate: {sr} Hz | Độ dài: {len(y)/sr:.2f} s")

    with col2:
        st.subheader("✨ Dữ liệu đã qua lọc nhiễu")
        y_clean = apply_highpass_filter(y, sr)
        # Lưu tạm file đã lọc để nghe thử (option)
        st.audio(y_clean, sample_rate=sr)

    # Vẽ biểu đồ tương tác bằng Plotly (để có thể zoom vào từng âm tiết)
    st.subheader("📊 Phân tích cấu trúc âm tiết (Syllables)")
    
    time = np.linspace(0, len(y_clean)/sr, len(y_clean))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time[::10], y=y_clean[::10], name="Waveform", line=dict(color='#1f77b4')))
    fig.update_layout(
        title="Biểu đồ dạng sóng (đã giảm mật độ điểm để tăng tốc độ load)",
        xaxis_title="Thời gian (giây)",
        yaxis_title="Biên độ",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("© 2026 NamY - Phát triển dựa trên niềm đam mê thiên nhiên và công nghệ.")
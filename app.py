import streamlit as st
import os
import numpy as np
import plotly.graph_objects as go
from src.audio_utils import load_and_clean_audio, apply_highpass_filter, get_3d_coordinates
from src.viz_utils import render_3d_video

# 1. Cấu hình giao diện NamY Bioacoustics
st.set_page_config(
    page_title="NamY Bioacoustics - Bird Sound Geometry",
    page_icon="🕊️",
    layout="wide"
)

# Sidebar thương hiệu
st.sidebar.title("🕊️ NamY Bioacoustics")
st.sidebar.markdown("""
Dự án giải mã ngôn ngữ loài chim thông qua hình học âm thanh 3D.
**Đối tượng:** Chim Chào Mào (*Red-whiskered Bulbul*)
""")
st.sidebar.divider()
st.sidebar.caption("© 2026 NamY Engine")

# Tiêu đề chính
st.title("📊 Phân tích cấu trúc âm tiết (Syllables)")
st.markdown("---")

# 2. Khu vực tải lên dữ liệu
uploaded_file = st.file_uploader("Tải lên file âm thanh Chào mào từ YouTube (mp3, wav)", type=["mp3", "wav"])

if uploaded_file:
    # Tạo các cột hiển thị âm thanh
    col1, col2 = st.columns(2)
    
    with st.spinner('Đang xử lý âm thanh...'):
        # Load và làm sạch
        y, sr = load_and_clean_audio(uploaded_file)
        y_clean = apply_highpass_filter(y, sr)
        
        with col1:
            st.write("🔊 **Âm thanh gốc**")
            st.audio(uploaded_file)
            
        with col2:
            st.write("✨ **Đã lọc nhiễu (High-pass > 1500Hz)**")
            st.audio(y_clean, sample_rate=sr)

    # 3. Vẽ biểu đồ Waveform 2D
    st.write("### Biểu đồ dạng sóng (đã giảm mật độ điểm để tăng tốc độ load)")
    
    # Giảm mật độ điểm để biểu đồ Plotly chạy mượt
    step = 10
    time_axis = np.linspace(0, len(y_clean)/sr, len(y_clean))[::step]
    amplitude = y_clean[::step]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_axis, 
        y=amplitude, 
        name="Waveform", 
        line=dict(color='#1f77b4', width=1)
    ))
    fig.update_layout(
        xaxis_title="Thời gian (giây)",
        yaxis_title="Biên độ",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 4. Tính năng Render Video 3D (Có tích hợp âm thanh)
    st.write("### 🎬 Xuất mô phỏng hình học 3D")
    st.info("Hệ thống sẽ trích xuất đặc trưng vật lý và ghép âm thanh gốc vào video quỹ đạo không gian.")

    if st.button("🚀 Render Video 3D (NamY Engine)"):
        with st.status("Đang chuẩn bị dữ liệu và render...", expanded=True) as status:
            # Tạo đường dẫn tạm cho file audio đầu vào để ffmpeg có thể đọc được
            temp_audio_path = f"temp_input_{uploaded_file.name}"
            with open(temp_audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # Bước A: Lấy tọa độ x, y, z
                x_coords, y_coords, z_coords = get_3d_coordinates(y_clean, sr)
                
                # Bước B: Định nghĩa file đầu ra
                output_video = "namy_bird_3d_with_audio.mp4"
                
                # Bước C: Gọi hàm render từ viz_utils (đã bao gồm audio_path để ghép nhạc)
                render_3d_video(x_coords, y_coords, z_coords, temp_audio_path, output_video)
                
                status.update(label="✅ Render hoàn tất!", state="complete", expanded=False)
                
                # Hiển thị video và nút tải về
                st.video(output_video)
                
                with open(output_video, "rb") as file:
                    st.download_button(
                        label="📥 Tải video 3D về máy",
                        data=file,
                        file_name="NamY_ChaoMao_3D.mp4",
                        mime="video/mp4"
                    )
                
                # Dọn dẹp file video sau khi hiển thị
                if os.path.exists(output_video):
                    os.remove(output_video)
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra trong quá trình render: {e}")
                status.update(label="❌ Lỗi render", state="error")
            finally:
                # Dọn dẹp file audio tạm thời
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

else:
    st.write("👆 Hãy tải lên một file âm thanh để bắt đầu hành trình giải mã.")
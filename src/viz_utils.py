import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np
import os
import subprocess

def render_3d_video(x, y, z, audio_path, output_path="namy_final_video.mp4"):
    """
    Vẽ quỹ đạo âm thanh 3D, sau đó ghép âm thanh gốc vào video.
    """
    # 1. Tên file video tạm (không có âm thanh)
    temp_video = "temp_silent_video.mp4"

    # --- PHẦN VẼ 3D (GIỮ NGUYÊN HOẶC TINH CHỈNH LUNG LINH) ---
    fig = plt.figure(figsize=(10, 10), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    ax.set_axis_off()

    line, = ax.plot([], [], [], color='#4ade80', alpha=0.2, lw=0.8)
    scatter = ax.scatter([], [], [], s=[], c=[], cmap='magma', edgecolors='white', linewidth=0.1, alpha=0.9)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)

    def update(frame):
        current_x = x[:frame]
        current_y = y[:frame]
        current_z = z[:frame]
        
        line.set_data(current_x, current_y)
        line.set_3d_properties(current_z)
        
        scatter._offsets3d = (current_x, current_y, current_z)
        sizes = np.linspace(1, 120, frame) * current_z 
        scatter.set_sizes(sizes)
        scatter.set_array(current_x)
        
        ax.view_init(elev=20 + np.sin(frame*0.05)*5, azim=frame * 0.8)
        return line, scatter

    # 2. Render video không âm thanh
    fps = 30
    ani = FuncAnimation(fig, update, frames=len(x), interval=1000/fps, blit=False)
    writer = FFMpegWriter(fps=fps, bitrate=3000)
    ani.save(temp_video, writer=writer)
    plt.close(fig)

    # 3. GHÉP ÂM THANH VÀO VIDEO (SỬ DỤNG FFMPEG)
    # Câu lệnh này sẽ lấy hình ảnh từ temp_video và âm thanh từ audio_path
    try:
        # Nếu audio_path là đối tượng file của Streamlit, ta cần lưu nó ra file tạm trước
        # Nhưng ở bước app.py ta sẽ xử lý việc truyền đường dẫn file thực
        cmd = [
            'ffmpeg', '-y', 
            '-i', temp_video, 
            '-i', audio_path, 
            '-map', '0:v', '-map', '1:a', 
            '-c:v', 'copy', '-c:a', 'aac', 
            '-shortest', # Cắt video/audio theo cái nào ngắn hơn để đồng bộ
            output_path
        ]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Lỗi khi ghép âm thanh: {e}")
        # Nếu lỗi ghép âm thanh, trả về video không tiếng để tránh crash app
        return temp_video
    finally:
        # Xóa video tạm không tiếng
        if os.path.exists(temp_video):
            os.remove(temp_video)

    return output_path
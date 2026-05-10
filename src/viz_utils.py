import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np
import os
import subprocess

def render_3d_video(x, y, z, audio_path, output_path="namy_final_video.mp4"):
    temp_video = "temp_silent_video.mp4"

    # 1. Thiết lập nền sáng (Light Theme)
    fig = plt.figure(figsize=(10, 10), facecolor='white')
    ax = fig.add_subplot(111, projection='3d', facecolor='white')
    ax.set_axis_off()

    # Đường nối mờ tạo hiệu ứng quỹ đạo
    line, = ax.plot([], [], [], color='#059669', alpha=0.2, lw=0.8)
    
    # Hạt năng lượng dùng cmap 'turbo' (giống video gốc) và viền mảnh
    scatter = ax.scatter([], [], [], s=[], c=[], cmap='turbo', edgecolors='black', linewidth=0.1, alpha=0.8)

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
        
        # Hiệu ứng lung linh: các điểm mới nhất to hơn các điểm cũ
        # np.linspace tạo mảng kích thước tăng dần từ 5 đến 150
        base_sizes = np.linspace(5, 150, frame) 
        sizes = base_sizes * current_z # Nhân với biên độ RMS để "nhảy" theo nhạc
        
        scatter.set_sizes(sizes)
        scatter.set_array(current_x) # Đổi màu theo trục X (Tần số trọng tâm)
        
        # Xoay camera linh hoạt
        ax.view_init(elev=25, azim=frame * 0.6)
        return line, scatter

    fps = 30
    ani = FuncAnimation(fig, update, frames=len(x), interval=1000/fps, blit=False)
    writer = FFMpegWriter(fps=fps, bitrate=3000)
    ani.save(temp_video, writer=writer)
    plt.close(fig)

    # Ghép âm thanh vào video
    try:
        cmd = [
            'ffmpeg', '-y', '-i', temp_video, '-i', audio_path, 
            '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', 
            '-shortest', output_path
        ]
        subprocess.run(cmd, check=True)
    except:
        return temp_video
    finally:
        if os.path.exists(temp_video): os.remove(temp_video)

    return output_path
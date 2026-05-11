import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np
import os
import subprocess

def render_3d_video(x, y, z, audio_path, output_path, speed=1.0, show_axes=True):
    temp_video = "temp_silent.mp4"
    fig = plt.figure(figsize=(10, 10), facecolor='white')
    ax = fig.add_subplot(111, projection='3d', facecolor='white')
    
    if not show_axes:
        ax.set_axis_off()
    else:
        ax.set_xlabel('Tần số (Centroid)')
        ax.set_ylabel('Phổ (Rolloff)')
        ax.set_zlabel('Cường độ (RMS)')

    # Sử dụng màu sắc theo dãy Turbo
    cmap = plt.get_cmap('turbo')
    
    # Khởi tạo điểm và đường
    scatter = ax.scatter([], [], [], s=[], c=[], cmap='turbo', alpha=0.8, edgecolors='none')
    
    # Để vẽ đường đa sắc, chúng ta sẽ dùng tập hợp các đoạn thẳng (LineCollection) 
    # nhưng để đơn giản và hiệu quả trên Cloud, ta dùng plot cập nhật liên tục
    line, = ax.plot([], [], [], color='gray', alpha=0.3, lw=0.5)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)

    def update(frame):
        curr_x = x[:frame]
        curr_y = y[:frame]
        curr_z = z[:frame]
        
        line.set_data(curr_x, curr_y)
        line.set_3d_properties(curr_z)
        
        scatter._offsets3d = (curr_x, curr_y, curr_z)
        # Kích thước theo cường độ (RMS)
        sizes = (curr_z * 400) + 2
        scatter.set_sizes(sizes)
        scatter.set_array(curr_x) # Màu theo tần số
        
        ax.view_init(elev=20, azim=frame * 0.5)
        return line, scatter

    # Tính toán FPS để khớp với tốc độ yêu cầu
    # Độ dài audio gốc / speed = Độ dài video mong muốn
    # FPS = Tổng số frame / Độ dài video mong muốn
    base_fps = 30
    actual_fps = base_fps * speed
    
    ani = FuncAnimation(fig, update, frames=len(x), interval=1000/actual_fps, blit=False)
    writer = FFMpegWriter(fps=actual_fps, bitrate=4000)
    ani.save(temp_video, writer=writer)
    plt.close(fig)

    # Ghép audio và điều chỉnh tốc độ audio bằng ffmpeg (atempo)
    # atempo chỉ hỗ trợ từ 0.5 đến 2.0, nên cần lặp lại nếu ngoài khoảng này
    audio_filter = f"atempo={speed}"
    if speed < 0.5: audio_filter = "atempo=0.5,atempo=" + str(speed/0.5)
    if speed > 2.0: audio_filter = "atempo=2.0,atempo=" + str(speed/2.0)

    try:
        cmd = [
            'ffmpeg', '-y', '-i', temp_video, '-i', audio_path,
            '-filter_complex', f'[1:a]{audio_filter}[s_audio]',
            '-map', '0:v', '-map', '[s_audio]',
            '-c:v', 'copy', '-c:a', 'aac', '-shortest', output_path
        ]
        subprocess.run(cmd, check=True)
    except:
        os.rename(temp_video, output_path)
    finally:
        if os.path.exists(temp_video): os.remove(temp_video)
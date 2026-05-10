import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np
import os

def render_3d_video(x, y, z, output_path="namy_output.mp4"):
    """
    Vẽ quỹ đạo âm thanh 3D và xuất thành file video MP4.
    """
    # 1. Khởi tạo khung hình với nền đen huyền ảo
    fig = plt.figure(figsize=(12, 9), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    
    # Ẩn các trục tọa độ để tập trung vào hình khối âm thanh
    ax.set_axis_off()

    # Khởi tạo đường vẽ (line) và điểm sáng hiện tại (point)
    # Màu #10b981 là màu xanh thương hiệu Emerald
    line, = ax.plot([], [], [], color='#10b981', alpha=0.5, lw=1.2)
    point = ax.scatter([], [], [], color='white', s=40, edgecolors='#10b981', linewidth=1)

    # Giới hạn không gian hiển thị (vì dữ liệu đã chuẩn hóa 0-1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)

    def init():
        line.set_data([], [])
        line.set_3d_properties([])
        return line, point

    def update(frame):
        # Vẽ "quá khứ" của tiếng hót (đường nối)
        line.set_data(x[:frame], y[:frame])
        line.set_3d_properties(z[:frame])
        
        # Cập nhật "hiện tại" (điểm đang phát sáng)
        # Lưu ý: scatter dùng mảng cho offsets3d
        point._offsets3d = ([x[frame]], [y[frame]], [z[frame]])
        
        # Hiệu ứng xoay camera chậm xung quanh trục Z
        # Tạo cảm giác không gian 3D thực thụ
        ax.view_init(elev=20, azim=frame * 0.7) 
        
        return line, point

    # 2. Tạo Animation
    # frames: tổng số khung hình dựa trên độ dài dữ liệu
    # interval: tốc độ chuyển cảnh (ms)
    ani = FuncAnimation(
        fig, update, frames=len(x), 
        init_func=init, blit=False, interval=30
    )

    # 3. Xuất Video bằng FFMpeg
    # fps=30 cho chuyển động mượt mà như video mẫu
    writer = FFMpegWriter(fps=30, metadata=dict(artist='NamY Bioacoustics'), bitrate=2500)
    
    try:
        ani.save(output_path, writer=writer)
    finally:
        plt.close(fig) # Giải phóng bộ nhớ RAM sau khi render
        
    return output_path
import librosa
import numpy as np
from scipy.signal import butter, lfilter

def load_and_clean_audio(audio_path):
    # 1. Load âm thanh
    y, sr = librosa.load(audio_path, sr=None)
    
    # 2. Cắt bỏ các đoạn tĩnh lặng ở đầu và cuối
    # Sử dụng librosa.effects.trim thay vì librosa.trim
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)
    
    return y_trimmed, sr

def apply_highpass_filter(y, sr, cutoff=1500):
    nyquist = 0.5 * sr
    normal_cutoff = cutoff / nyquist
    b, a = butter(5, normal_cutoff, btype='high', analog=False)
    y_filtered = lfilter(b, a, y)
    return y_filtered
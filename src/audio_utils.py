# src/audio_utils.py
import librosa
import numpy as np
from scipy.signal import butter, lfilter

def load_and_clean_audio(audio_path):
    # 1. Load âm thanh (giữ nguyên sample rate gốc)
    y, sr = librosa.load(audio_path, sr=None)
    
    # 2. Cắt bỏ các đoạn tĩnh lặng ở đầu và cuối (Trimming)
    # top_db=20 nghĩa là coi những đoạn dưới 20db là im lặng
    y_trimmed, _ = librosa.trim(y, top_db=20)
    
    return y_trimmed, sr

def apply_highpass_filter(y, sr, cutoff=1500):
    # Bộ lọc để loại bỏ tiếng ù, tiếng xe cộ (thường < 1000Hz)
    nyquist = 0.5 * sr
    normal_cutoff = cutoff / nyquist
    b, a = butter(5, normal_cutoff, btype='high', analog=False)
    y_filtered = lfilter(b, a, y)
    return y_filtered
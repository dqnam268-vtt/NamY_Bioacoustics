import librosa
import numpy as np
from scipy.signal import butter, lfilter

def load_and_clean_audio(audio_path):
    """Load âm thanh và cắt bỏ các khoảng lặng ở hai đầu."""
    # 1. Load âm thanh (giữ nguyên sample rate gốc)
    y, sr = librosa.load(audio_path, sr=None)
    
    # 2. Cắt bỏ các đoạn tĩnh lặng ở đầu và cuối (top_db=20)
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)
    
    return y_trimmed, sr

def apply_highpass_filter(y, sr, cutoff=1500):
    """Loại bỏ tiếng ồn tần số thấp (tiếng gió, xe cộ)."""
    nyquist = 0.5 * sr
    normal_cutoff = cutoff / nyquist
    b, a = butter(5, normal_cutoff, btype='high', analog=False)
    y_filtered = lfilter(b, a, y)
    return y_filtered

def get_3d_coordinates(y, sr, hop_length=512):
    """
    Tính toán tọa độ x, y, z từ các đặc trưng vật lý của âm thanh.
    X: Spectral Centroid (Độ sáng âm thanh/Tần số trọng tâm)
    Y: Spectral Rolloff (Hình dáng phổ âm)
    Z: RMS Energy (Cường độ/Âm lượng)
    """
    # 1. Trích xuất đặc trưng
    x_raw = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    y_raw = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop_length)[0]
    z_raw = librosa.feature.rms(y=y, hop_length=hop_length)[0]

    # 2. Hàm chuẩn hóa dữ liệu về khoảng [0, 1]
    def normalize(data):
        if np.max(data) == np.min(data):
            return np.zeros_like(data)
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    return normalize(x_raw), normalize(y_raw), normalize(z_raw)

def extract_features(y, sr, n_mfcc=13):
    """
    Trích xuất MFCCs và Centroid phục vụ cho việc phân cụm (Clustering)
    hoặc gán màu sắc cho các điểm 3D.
    """
    # Trích xuất 13 hệ số MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    
    # Trích xuất Centroid để làm dữ liệu màu sắc
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    
    return mfcc.T, centroid.T
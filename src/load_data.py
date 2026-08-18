import pandas as pd
from scipy.signal import butter, filtfilt

def load_ecg_data(filepath, skip_seconds=3, sampling_rate=200):
    df = pd.read_csv(filepath, comment="#")

    df.columns = [col.strip().replace('"', '') for col in df.columns]

    if "ECG" not in df.columns:
        raise ValueError(f"Kolumna 'ECG' nie znaleziona w pliku: {filepath}\nZnalezione kolumny: {df.columns.tolist()}")

    start_index = int(skip_seconds * sampling_rate)
    df = df.iloc[start_index:]

    time = df["Elapsed time"].values
    ecg = df["ECG"].values

    return time, ecg



def bandpass_filter(signal, lowcut=0.5, highcut=40, fs=200, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    return filtfilt(b, a, signal)

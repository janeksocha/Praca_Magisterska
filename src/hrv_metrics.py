import numpy as np
import neurokit2 as nk

def compute_rmssd(rr_intervals):
    diff_rr = np.diff(rr_intervals)
    return np.sqrt(np.mean(diff_rr ** 2))

def compute_sdnn(rr_intervals):
    return np.std(rr_intervals, ddof=1)

def compute_mean_hr(rr_intervals):
    mean_rr = np.mean(rr_intervals)
    return 60000 / mean_rr

def extract_rr_from_ecg(ecg_signal, sampling_rate=200):

    try:
        processed = nk.ecg_process(ecg_signal, sampling_rate=sampling_rate)

        if "ECG_RR_Intervals" not in processed[1]:
            print("Brak 'ECG_RR_Intervals' – możliwe problemy z jakością sygnału.")
            return []

        rr_intervals = processed[1]["ECG_RR_Intervals"].dropna().values

        if len(rr_intervals) == 0:
            print("Wykryto 0 odstępów RR – możliwe problemy z detekcją R.")
            return []

        return rr_intervals
    except Exception as e:
        print(f"Błąd przy przetwarzaniu EKG: {e}")
        return []

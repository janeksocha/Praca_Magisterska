import pandas as pd
import neurokit2 as nk
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "pomiary"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)

SAMPLING_RATE = 200
LAST_3MIN = 3 * 60 * SAMPLING_RATE

OUTPUT_FILE = RESULTS_DIR / "HRV_master.xlsx"
ERROR_LOG = RESULTS_DIR / "hrv_errors.txt"

# FOLDERY DO ANALIZY

DATASETS = [
    {
        "group_type": "badawcza",
        "sex": "kobieta",
        "path": DATA_DIR / "badawcza" / "kobiety"
    },

    {
        "group_type": "badawcza",
        "sex": "mężczyzna",
        "path": DATA_DIR / "badawcza" / "mężczyźni"
    },

    {
        "group_type": "kontrolna",
        "sex": "kobieta",
        "path": DATA_DIR / "kontrolna" / "kobiety_k"
    },

    {
        "group_type": "kontrolna",
        "sex": "mężczyzna",
        "path": DATA_DIR / "kontrolna" / "mężczyźni_k"
    }
]

# WCZYTYWANIE CSV

def load_csv(filepath):

    df = pd.read_csv(
        filepath,
        comment="#",
        sep=",",
        engine="python"
    )

    df.columns = [
        c.strip().replace('"', '')
        for c in df.columns
    ]

    ecg_col = None

    for col in df.columns:

        if "ECG" in col.upper():
            ecg_col = col
            break

    if ecg_col is None:
        raise ValueError("Brak kolumny ECG")

    df = df.rename(columns={ecg_col: "ECG"})

    return df


# ANALIZA HRV

def analyze_hrv(ecg_signal):

    # FAZA WALKI

    if len(ecg_signal) > LAST_3MIN:
        fight_signal = ecg_signal[:-LAST_3MIN]
        recovery_signal = ecg_signal[-LAST_3MIN:]
    else:
        fight_signal = ecg_signal
        recovery_signal = ecg_signal

    cleaned_fight = nk.ecg_clean(
        fight_signal,
        sampling_rate=SAMPLING_RATE
    )

    cleaned_recovery = nk.ecg_clean(
        recovery_signal,
        sampling_rate=SAMPLING_RATE
    )

    _, info_fight = nk.ecg_process(
        cleaned_fight,
        sampling_rate=SAMPLING_RATE
    )

    _, info_recovery = nk.ecg_process(
        cleaned_recovery,
        sampling_rate=SAMPLING_RATE
    )

    rpeaks_fight = info_fight["ECG_R_Peaks"]
    rpeaks_recovery = info_recovery["ECG_R_Peaks"]

    if len(rpeaks_fight) < 10:
        raise ValueError("Za mało R-peaków - fight")

    if len(rpeaks_recovery) < 10:
        raise ValueError("Za mało R-peaków - recovery")

    # HRV FIGHT
    hrv_time_f = nk.hrv_time(
        rpeaks_fight,
        sampling_rate=SAMPLING_RATE
    )

    hrv_freq_f = nk.hrv_frequency(
        rpeaks_fight,
        sampling_rate=SAMPLING_RATE
    )

    # HRV RECOVERY

    hrv_time_r = nk.hrv_time(
        rpeaks_recovery,
        sampling_rate=SAMPLING_RATE
    )

    hrv_freq_r = nk.hrv_frequency(
        rpeaks_recovery,
        sampling_rate=SAMPLING_RATE
    )

    # ZWROT WYNIKÓW
    return {

        "RMSSD": float(hrv_time_f["HRV_RMSSD"].iloc[0]),
        "SDNN": float(hrv_time_f["HRV_SDNN"].iloc[0]),
        "MeanNN": float(hrv_time_f["HRV_MeanNN"].iloc[0]),
        "HF": float(hrv_freq_f["HRV_HFn"].iloc[0]),
        "LF": float(hrv_freq_f["HRV_LFn"].iloc[0]),
        "LF_HF": float(hrv_freq_f["HRV_LFHF"].iloc[0]),

        "RMSSD_recovery": float(hrv_time_r["HRV_RMSSD"].iloc[0]),
        "SDNN_recovery": float(hrv_time_r["HRV_SDNN"].iloc[0]),
        "MeanNN_recovery": float(hrv_time_r["HRV_MeanNN"].iloc[0]),
        "HF_recovery": float(hrv_freq_r["HRV_HFn"].iloc[0]),
        "LF_recovery": float(hrv_freq_r["HRV_LFn"].iloc[0]),
        "LF_HF_recovery": float(hrv_freq_r["HRV_LFHF"].iloc[0])
    }

def main():

    all_results = []
    quality_results = []
    errors = []

    for dataset in DATASETS:

        group_type = dataset["group_type"]
        sex = dataset["sex"]
        folder = dataset["path"]

        print(f"\nGrupa: {group_type} | {sex}")

        if not folder.exists():

            print("Folder nie istnieje")
            continue

        files = sorted([
            f for f in folder.iterdir()
            if f.is_file()
               and f.suffix.lower() in [".csv", ".txt"]
        ])

        print(f"Liczba plików: {len(files)}")

        for file in files:

            print(f"→ {file.name}")

            try:

                df = load_csv(file)

                ecg = df["ECG"].values

                result = analyze_hrv(ecg)

                result["file"] = file.name
                result["group_type"] = group_type
                result["sex"] = sex

                all_results.append(result)

                print("   ✓ OK")

                ARTIFACT_THRESHOLD = 5

                artifact_count = np.sum(
                    np.abs(df["ECG"]) > ARTIFACT_THRESHOLD
                )

                artifact_percent = (
                                           artifact_count / len(df)
                                   ) * 100

                quality_row = {

                    "file": file.stem,
                    "group_type": group_type,
                    "sex": sex,

                    "samples": len(df),

                    "ecg_mean": float(df["ECG"].mean()),
                    "ecg_std": float(df["ECG"].std()),
                    "ecg_min": float(df["ECG"].min()),
                    "ecg_max": float(df["ECG"].max()),

                    "artifact_count": int(artifact_count),
                    "artifact_percent": float(artifact_percent),

                    "status": "OK"
                }

                quality_results.append(quality_row)

            except Exception as e:

                error_msg = f"{file.name} | {str(e)}"

                errors.append(error_msg)

                quality_results.append({

                    "file": file.stem,
                    "group_type": group_type,
                    "sex": sex,
                    "status": f"ERROR: {e}"

                })

                print(f"   ✗ {e}")

    # ZAPIS WYNIKÓW

    if len(all_results) > 0:

        results_df = pd.DataFrame(all_results)

        columns_order = [
            "file",
            "group_type",
            "sex",

            "RMSSD",
            "SDNN",
            "MeanNN",
            "HF",
            "LF",
            "LF_HF",

            "RMSSD_recovery",
            "SDNN_recovery",
            "MeanNN_recovery",
            "HF_recovery",
            "LF_recovery",
            "LF_HF_recovery"
        ]

        results_df = results_df[columns_order]

        results_df.to_excel(
            OUTPUT_FILE,
            index=False
        )

        print("ZAPISANO HRV")

        print(f"\nPlik:")
        print(OUTPUT_FILE)

        print(f"\nLiczba analiz:")
        print(len(results_df))

    else:

        print("\nBrak poprawnych wyników")

    quality_df = pd.DataFrame(quality_results)

    quality_df.to_excel(
        RESULTS_DIR / "quality_report.xlsx",
        index=False
    )

    print("\nZapisano raport jakości:")
    print(RESULTS_DIR / "quality_report.xlsx")

    with open(ERROR_LOG, "w", encoding="utf-8") as f:

        for err in errors:
            f.write(err + "\n")

    print(f"\nLiczba błędów: {len(errors)}")
    print(f"Log błędów: {ERROR_LOG}")


if __name__ == "__main__":
    main()
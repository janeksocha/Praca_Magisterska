import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "pomiary"
RESULTS_DIR = BASE_DIR / "results"
QUALITY_DIR = RESULTS_DIR / "quality"

QUALITY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


SAMPLING_RATE = 200

# fragment do wizualizacji
START_SECOND = 300      # np. 300 s = 5 minuta
WINDOW_SECONDS = 10     # długość fragmentu


FILE_TO_PLOT = (
    DATA_DIR
    / "badawcza"
    / "mężczyźni"
    / "PU1011.csv"
)


def load_csv(filepath):

    df = pd.read_csv(
        filepath,
        comment="#",
        sep=",",
        engine="python"
    )

    df.columns = [
        c.strip().replace('"', "")
        for c in df.columns
    ]

    ecg_col = None

    for col in df.columns:

        if "ECG" in col.upper():
            ecg_col = col
            break

    if ecg_col is None:
        raise ValueError("Brak kolumny ECG")

    df = df.rename(
        columns={ecg_col: "ECG"}
    )

    return df


def plot_fragment(ecg, file_name):

    start = START_SECOND * SAMPLING_RATE
    end = start + WINDOW_SECONDS * SAMPLING_RATE

    fragment = ecg[start:end]

    plt.figure(figsize=(12, 4))

    plt.plot(fragment)

    plt.title(
        f"Fragment sygnału EKG "
        f"({START_SECOND}-{START_SECOND + WINDOW_SECONDS} s)"
    )

    plt.xlabel("Próbka")
    plt.ylabel("Amplituda")

    plt.tight_layout()

    plt.savefig(
        QUALITY_DIR / f"ecg_fragment_{file_name}.png",
        dpi=300
    )

    plt.close()


def plot_full_signal(ecg, file_name):

    plt.figure(figsize=(14, 4))

    plt.plot(ecg)

    plt.title("Pełny zapis sygnału EKG")

    plt.xlabel("Próbka")
    plt.ylabel("Amplituda")

    plt.tight_layout()

    plt.savefig(
        QUALITY_DIR / f"ecg_full_signal_{file_name}.png",
        dpi=300
    )

    plt.close()


def plot_r_peaks(ecg, file_name):

    cleaned = nk.ecg_clean(
        ecg,
        sampling_rate=SAMPLING_RATE
    )

    _, info = nk.ecg_process(
        cleaned,
        sampling_rate=SAMPLING_RATE
    )

    r_peaks = info["ECG_R_Peaks"]

    start = START_SECOND * SAMPLING_RATE
    end = start + WINDOW_SECONDS * SAMPLING_RATE

    fragment = cleaned[start:end]

    r_peaks_fragment = [
        p - start
        for p in r_peaks
        if start <= p < end
    ]

    plt.figure(figsize=(12, 4))

    plt.plot(fragment)

    plt.scatter(
        r_peaks_fragment,
        fragment[r_peaks_fragment],
        s=60
    )

    plt.title(
        f"Detekcja załamków R "
        f"({START_SECOND}-{START_SECOND + WINDOW_SECONDS} s)"
    )

    plt.xlabel("Próbka")
    plt.ylabel("Amplituda")

    plt.tight_layout()

    plt.savefig(
        QUALITY_DIR / f"ecg_r_peaks_{file_name}.png",
        dpi=300
    )

    plt.close()


def main():

    print("Generowanie wizualizacji EKG...")

    if not FILE_TO_PLOT.exists():

        print(
            f"Nie znaleziono pliku:\n{FILE_TO_PLOT}"
        )

        return

    df = load_csv(FILE_TO_PLOT)

    ecg = df["ECG"].values

    print(
        f"Liczba próbek: {len(ecg)}"
    )

    print(
        f"Wyświetlany fragment: "
        f"{START_SECOND}-{START_SECOND + WINDOW_SECONDS} s"
    )

    file_name = FILE_TO_PLOT.stem

    plot_fragment(ecg, file_name)
    plot_full_signal(ecg, file_name)
    plot_r_peaks(ecg, file_name)

    print("\nZapisano:")

    print(
        RESULTS_DIR / "ecg_fragment.png"
    )

    print(
        RESULTS_DIR / "ecg_full_signal.png"
    )

    print(
        RESULTS_DIR / "ecg_r_peaks.png"
    )


if __name__ == "__main__":
    main()
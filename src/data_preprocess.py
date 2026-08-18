import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# ŚCIEŻKI

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "pomiary"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)

SURVEY_RESEARCH = DATA_DIR / "Ankieta grupa badawcza.xlsx"
SURVEY_CONTROL = DATA_DIR / "Ankieta grupa kontrolna.xlsx"

# Wynik końcowy
OUTPUT_FILE = RESULTS_DIR / "master_dataset.xlsx"

# MAPOWANIE

scale_5 = {
    "Bardzo niska": 1,
    "Niska": 2,
    "Średnia": 3,
    "Wysoka": 4,
    "Bardzo wysoka": 5,

    "Bardzo słaba": 1,
    "Słaba": 2,
    "Średnia": 3,
    "Dobra": 4,
    "Bardzo dobra": 5,

    "Bardzo źle": 1,
    "Źle": 2,
    "Średnio": 3,
    "Dobrze": 4,
    "Bardzo dobrze": 5,

    "Bardzo niski": 1,
    "Niski": 2,
    "Średni": 3,
    "Wysoki": 4,
    "Bardzo wysoki": 5,

    "Tak": 1,
    "Nie": 0,
    "Zła": 2
}

experience_map = {
    "mniej niż rok": 1,
    "1-3 lata": 2,
    "4-6 lat": 3,
    "powyżej 6 lat": 4
}

def clean_columns(df):

    # Upraszcza nazwy kolumn

    rename_dict = {}

    for col in df.columns:

        col_lower = str(col).lower().strip()

        if "plik" in col_lower or "indeks" in col_lower:
            rename_dict[col] = "file"

        elif "płeć" in col_lower:
            rename_dict[col] = "sex"

        elif "energii" in col_lower:
            rename_dict[col] = "energy"


        elif "regeneracji" in col_lower:
            rename_dict[col] = "recovery"

        elif "snu" in col_lower:
            rename_dict[col] = "sleep"

        elif "dolegliwości" in col_lower:
            rename_dict[col] = "pain"

        elif "motywacj" in col_lower:
            rename_dict[col] = "motivation"

        elif "intensywność" in col_lower:
            rename_dict[col] = "intensity"

        elif "jednostek treningowych" in col_lower:
            rename_dict[col] = "trainings"

        elif "stresu" in col_lower:
            rename_dict[col] = "stress"

        elif "koncentracji" in col_lower:
            rename_dict[col] = "concentration"

        elif "jak długo trenujesz" in col_lower:
            rename_dict[col] = "experience"

        elif "jak często" in col_lower:
            rename_dict[col] = "weekly_frequency"

    df = df.rename(columns=rename_dict)

    return df


def map_answers(df):

    for col in df.columns:

        if df[col].dtype == object:

            df[col] = df[col].replace(scale_5)

            df[col] = df[col].replace(experience_map)

    return df


def prepare_survey(filepath, group_name):

    print(f"Wczytywanie ankiety: {filepath.name}")

    df = pd.read_excel(filepath)

    df.columns = df.columns.str.strip()
    df = clean_columns(df)
    df = map_answers(df)

    if "file" in df.columns:

        df["file"] = (
            df["file"]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(".csv", "", regex=False)
        )
    return df


def load_hrv():

    hrv_df = pd.read_excel(
        RESULTS_DIR / "HRV_master.xlsx"
    )

    hrv_df["file"] = (
        hrv_df["file"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(".csv", "", regex=False)
    )

    return hrv_df



def main():

    # Ankiety
    research_df = prepare_survey(
        SURVEY_RESEARCH,
        "badawcza"
    )

    control_df = prepare_survey(
        SURVEY_CONTROL,
        "kontrolna"
    )

    # Połączenie ankiet
    survey_df = pd.concat(
        [research_df, control_df],
        ignore_index=True
    )

    print(f"\nŁączna liczba ankiet: {len(survey_df)}")

    hrv_df = load_hrv()

    print(f"Liczba rekordów HRV: {len(hrv_df)}")

    master_df = hrv_df.merge(
        survey_df,
        on="file",
        how="inner"
    )

    print(f"Liczba rekordów po merge: {len(master_df)}")

    master_df["readiness_index"] = (
    master_df["energy"] +
    master_df["recovery"]) / 2

    master_df["fatigue_index"] = (
            6 - master_df["readiness_index"]
    )

    master_df = master_df.drop_duplicates()

    # Zapis
    master_df.to_excel(
        OUTPUT_FILE,
        index=False
    )


if __name__ == "__main__":
    main()

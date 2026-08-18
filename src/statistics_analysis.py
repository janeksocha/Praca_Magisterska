import pandas as pd
import numpy as np
from pathlib import Path

from scipy.stats import (
    shapiro,
    ttest_ind,
    mannwhitneyu,
    spearmanr,
    ttest_rel,
    wilcoxon
)

import matplotlib.pyplot as plt
import seaborn as sns


# ŚCIEŻKI


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
DATA_FILE = RESULTS_DIR / "master_dataset.xlsx"
OUTPUT_STATS = RESULTS_DIR / "statistics_results.xlsx"

PLOTS_DIR = RESULTS_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

HRV_PARAMS = [
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

# WCZYTANIE DANYCH

def load_data():

    df = pd.read_excel(DATA_FILE)

    return df

# OPIS STATYSTYCZNY

def descriptive_statistics(df):

    rows = []

    for param in HRV_PARAMS:

        if param not in df.columns:
            continue

        values = df[param].dropna()

        rows.append({

            "parameter": param,
            "mean": np.mean(values),
            "std": np.std(values),
            "median": np.median(values),
            "min": np.min(values),
            "max": np.max(values)

        })

    return pd.DataFrame(rows)

# TEST NORMALNOŚCI

def normality_test(df):

    rows = []

    for param in HRV_PARAMS:

        if param not in df.columns:
            continue

        values = df[param].dropna()

        if len(values) < 3:
            continue

        stat, p = shapiro(values)

        rows.append({

            "parameter": param,
            "shapiro_stat": stat,
            "p_value": p,
            "normal_distribution": p > 0.05

        })

    return pd.DataFrame(rows)

# PORÓWNANIE GRUP

def compare_groups(df):

    rows = []

    research = df[df["group_type"] == "badawcza"]
    control = df[df["group_type"] == "kontrolna"]

    for param in HRV_PARAMS:

        if param not in df.columns:
            continue

        g1 = research[param].dropna()
        g2 = control[param].dropna()

        if len(g1) < 3 or len(g2) < 3:
            continue

        # Test normalności
        p1 = shapiro(g1)[1]
        p2 = shapiro(g2)[1]

        # Jeśli normalne t-test
        if p1 > 0.05 and p2 > 0.05:

            stat, p = ttest_ind(
                g1,
                g2,
                equal_var=False
            )

            test_name = "t-test"

        # Jeśli nienormalne Mann-Whitney
        else:

            stat, p = mannwhitneyu(
                g1,
                g2,
                alternative="two-sided"
            )

            test_name = "Mann-Whitney"

        rows.append({

            "parameter": param,
            "test": test_name,
            "statistic": stat,
            "p_value": p,
            "significant": p < 0.05

        })

    return pd.DataFrame(rows)

# KORELACJE

def correlations(df):

    questionnaire_cols = [
        "energy",
        "recovery",
        "sleep",
        "pain",
        "motivation",
        "intensity",
        "trainings",
        "stress",
        "concentration",
        "age"
    ]

    rows = []

    for hrv in HRV_PARAMS:

        if hrv not in df.columns:
            continue

        for q in questionnaire_cols:

            if q not in df.columns:
                continue

            temp = df[[hrv, q]].dropna()

            if len(temp) < 5:
                continue

            corr, p = spearmanr(
                temp[hrv],
                temp[q]
            )

            rows.append({

                "HRV_parameter": hrv,
                "questionnaire_parameter": q,
                "correlation": corr,
                "p_value": p,
                "significant": p < 0.05

            })

    return pd.DataFrame(rows)

# WYKRESY

def generate_boxplots(df):

    for param in HRV_PARAMS:

        if param not in df.columns:
            continue

        plt.figure(figsize=(8, 5))

        sns.boxplot(
            data=df,
            x="group_type",
            y=param
        )

        plt.title(f"{param} - comparison")

        plt.tight_layout()

        plt.savefig(
            PLOTS_DIR / f"{param}_boxplot.png"
        )

        plt.close()

# HEATMAP

def generate_heatmap(df):

    heatmap_cols = [

        # HRV - walka
        "RMSSD",
        "SDNN",
        "MeanNN",
        "HF",
        "LF",
        "LF_HF",

        # HRV - regeneracja
        "RMSSD_recovery",
        "SDNN_recovery",
        "MeanNN_recovery",
        "HF_recovery",
        "LF_recovery",
        "LF_HF_recovery",

        # Ankieta
        "energy",
        "recovery",
        "sleep",
        "pain",
        "motivation",
        "intensity",
        "trainings",
        "stress",
        "concentration",
        "age"
    ]

    heatmap_cols = [
        col for col in heatmap_cols
        if col in df.columns
    ]

    numeric_df = df[heatmap_cols]

    corr_matrix = numeric_df.corr(
        method="spearman"
    )

    plt.figure(figsize=(18, 14))

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
    )

    plt.title(
        "Macierz korelacji Spearmana"
    )

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "correlation_heatmap.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# WALKA VS REGENERACJA

def compare_fight_vs_recovery(df):

    parameter_pairs = [

        ("RMSSD", "RMSSD_recovery"),
        ("SDNN", "SDNN_recovery"),
        ("MeanNN", "MeanNN_recovery"),
        ("HF", "HF_recovery"),
        ("LF", "LF_recovery"),
        ("LF_HF", "LF_HF_recovery")

    ]

    rows = []

    for fight_col, recovery_col in parameter_pairs:

        if (
            fight_col not in df.columns
            or recovery_col not in df.columns
        ):
            continue

        temp = df[
            [fight_col, recovery_col]
        ].dropna()

        if len(temp) < 5:
            continue

        differences = (
            temp[recovery_col]
            - temp[fight_col]
        )

        shapiro_stat, shapiro_p = shapiro(
            differences
        )

        if shapiro_p > 0.05:

            stat, p = ttest_rel(
                temp[fight_col],
                temp[recovery_col]
            )

            test_name = "paired_t_test"

        else:

            stat, p = wilcoxon(
                temp[fight_col],
                temp[recovery_col]
            )

            test_name = "wilcoxon"

        rows.append({

            "parameter": fight_col,

            "fight_mean":
                temp[fight_col].mean(),

            "recovery_mean":
                temp[recovery_col].mean(),

            "difference_mean":
                differences.mean(),

            "test":
                test_name,

            "statistic":
                stat,

            "p_value":
                p,

            "significant":
                p < 0.05

        })

    return pd.DataFrame(rows)

def main():

    df = load_data()

    print(f"\nLiczba rekordów: {len(df)}")

    desc_df = descriptive_statistics(df)
    normality_df = normality_test(df)
    compare_df = compare_groups(df)
    fight_recovery_df = compare_fight_vs_recovery(df)
    corr_df = correlations(df)
    generate_boxplots(df)
    generate_heatmap(df)

    with pd.ExcelWriter(
        OUTPUT_STATS,
        engine="openpyxl"
    ) as writer:

        desc_df.to_excel(
            writer,
            sheet_name="descriptive_statistics",
            index=False
        )

        normality_df.to_excel(
            writer,
            sheet_name="normality_tests",
            index=False
        )

        compare_df.to_excel(
            writer,
            sheet_name="group_comparison",
            index=False
        )

        corr_df.to_excel(
            writer,
            sheet_name="correlations",
            index=False
        )

        fight_recovery_df.to_excel(
            writer,
            sheet_name="fight_vs_recovery",
            index=False
        )

    print("ANALIZA ZAKOŃCZONA")

    print(f"\nWyniki:")
    print(OUTPUT_STATS)

    print(f"\nWykresy:")
    print(PLOTS_DIR)


if __name__ == "__main__":
    main()
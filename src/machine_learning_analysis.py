import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import (
    LeaveOneOut,
    cross_val_predict
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import plot_tree

warnings.filterwarnings("ignore")


BASE_DIR = Path(__file__).resolve().parent.parent

RESULTS_DIR = BASE_DIR / "results"

DATA_FILE = RESULTS_DIR / "master_dataset.xlsx"

OUTPUT_FILE = (
    RESULTS_DIR
    / "machine_learning_results.xlsx"
)


FEATURES = [

    # walka
    "RMSSD",
    "SDNN",
    "MeanNN",
    "HF",
    "LF",
    "LF_HF",

    # regeneracja
   # "RMSSD_recovery",
   # "SDNN_recovery",
   # "MeanNN_recovery",
   # "HF_recovery",
   # "LF_recovery",
   # "LF_HF_recovery",

    # dane podstawowe
    "Wiek"

]

TARGET = "recovery"


def load_data():

    df = pd.read_excel(DATA_FILE)

    columns = FEATURES + [TARGET]

    df = df[columns].dropna()

    return df


def evaluate_model(model, X, y):

    loo = LeaveOneOut()

    predictions = cross_val_predict(
        model,
        X,
        y,
        cv=loo
    )

    plt.figure(figsize=(6, 6))

    plt.scatter(
        y,
        predictions
    )

    plt.xlabel("Rzeczywista wartość")
    plt.ylabel("Przewidywana wartość")

    plt.plot(
        [y.min(), y.max()],
        [y.min(), y.max()]
    )

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "predicted_vs_actual.png",
        dpi=300
    )

    plt.close()

    mae = mean_absolute_error(
        y,
        predictions
    )

    rmse = float(np.sqrt(
        mean_squared_error(
            y,
            predictions)
        )
    )

    r2 = r2_score(
        y,
        predictions
    )

    return {

        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "predictions": predictions

    }


def build_models():

    models = {}

    models["LinearRegression"] = Pipeline([

        ("scaler", StandardScaler()),
        ("model", LinearRegression())

    ])

    models["FastFrugalTree"] = DecisionTreeRegressor(
        max_depth=3,
        random_state=42
    )

    plt.figure(figsize=(14, 8))

    models["RandomForest"] = RandomForestRegressor(

        n_estimators=200,
        random_state=42

    )

    models["SVM"] = Pipeline([

        ("scaler", StandardScaler()),

        ("model", SVR(
            kernel="rbf",
            C=1.0
        ))

    ])

    return models


def main():

    df = load_data()

    print(
        f"\nLiczba próbek: {len(df)}    Target: {TARGET}"
    )

    X = df[FEATURES]

    y = df[TARGET]

    models = build_models()

    results = []

    for name, model in models.items():

        print(f"\n{name}")

        metrics = evaluate_model(
            model,
            X,
            y
        )

        print(metrics)

        results.append({

            "Model": name,

            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "R2": metrics["R2"]

        })

    results_df = pd.DataFrame(
        results
    )

    results_df.to_excel(
        OUTPUT_FILE,
        index=False
    )

    print(OUTPUT_FILE)

    rf = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    rf.fit(X, y)

    importance = pd.DataFrame({
        "feature": X.columns,
        "importance": rf.feature_importances_
    })

    importance = importance.sort_values(
        by="importance",
        ascending=False
    )

    print(importance)

    plt.figure(figsize=(8, 5))

    plt.barh(
        importance["feature"],
        importance["importance"]
    )

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "feature_importance.png",
        dpi=300
    )

    plt.close()

    rf_metrics = evaluate_model(
        rf,
        X,
        y
    )

    predictions = rf_metrics["predictions"]

    plt.figure(figsize=(6, 6))

    plt.scatter(
        y,
        predictions
    )

    plt.xlabel("Rzeczywista regeneracja")
    plt.ylabel("Przewidywana regeneracja")

    plt.plot(
        [y.min(), y.max()],
        [y.min(), y.max()]
    )

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "predicted_vs_actual.png",
        dpi=300
    )

    plt.close()

    fft = DecisionTreeRegressor(
        max_depth=3,
        random_state=42
    )

    fft.fit(X, y)

    plt.figure(figsize=(14, 8))

    plot_tree(
        fft,
        feature_names=X.columns,
        filled=True
    )

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "fft_tree.png",
        dpi=300
    )

    plt.close()

# =========================================

if __name__ == "__main__":
    main()

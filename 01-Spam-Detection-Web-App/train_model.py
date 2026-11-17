
from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "spam.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "spam_pipeline.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"


def main():
    print("Loading spam dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Download and prepare spam.csv first."
        )

    df = pd.read_csv(DATA_PATH)

    if not {"label", "message"}.issubset(df.columns):
        raise ValueError(
            "CSV must contain 'label' and 'message' columns."
        )

    df = df[["label", "message"]].dropna()
    df["label"] = df["label"].str.lower().str.strip()
    df["message"] = df["message"].astype(str).str.strip()

    df = df[
        df["label"].isin(["ham", "spam"])
        & df["message"].ne("")
    ]

    # Remove duplicate messages before splitting.
    df = df.drop_duplicates(subset="message")

    print(f"Valid messages: {len(df)}")
    print(df["label"].value_counts())

    X = df["message"]
    y = df["label"].map({"ham": 0, "spam": 1})

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # Keep vectorization inside the pipeline so it is
    # fitted only on training data.
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=10000,
        )),
        ("classifier", MultinomialNB()),
    ])

    print("\nTraining model...")
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    metrics = {
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, predictions, zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(
            y_test, predictions
        ).tolist(),
        "training_samples": len(X_train),
        "testing_samples": len(X_test),
    }

    print("\nMODEL RESULTS")
    print("-" * 40)

    for name in ("accuracy", "precision", "recall", "f1_score"):
        print(f"{name}: {metrics[name]:.4f}")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        target_names=["Not Spam", "Spam"],
        zero_division=0,
    ))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, MODEL_PATH)

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    main()

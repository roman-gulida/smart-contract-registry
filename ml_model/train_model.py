"""
Trains all 5 models across 3 versions with different train/test splits.
Saves each as a separate .pkl and updates model_registry.json.

Version strategy:
  v1.0 - 80/20 split, seed=42  (400 train, 100 test)
  v2.0 - 80/20 split, seed=7   (400 train, 100 test, different shuffle)
  v3.0 - 60/40 split, seed=99  (300 train, 200 test, harder split)
"""

import os
import pickle
import hashlib
import json
import warnings
import PyPDF2
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import joblib

warnings.filterwarnings("ignore")

DOCUMENTS_DIR = "data"
MODELS_DIR = "ml_model"
CLASSES = ["logistics", "salary", "hr", "finance", "legal"]

MODEL_CONFIGS = {
    "SVM": SVC(kernel="linear", C=1.0, random_state=42),
    "SGD": SGDClassifier(
        loss="hinge", penalty="l2", alpha=1e-3, random_state=42, max_iter=1000
    ),
    "NaiveBayes": MultinomialNB(alpha=1.0),
    "RandomForest": RandomForestClassifier(
        n_estimators=100, random_state=42, max_depth=50
    ),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42, C=1.0),
}

# Version definitions: (version_label, test_size, random_seed)
VERSIONS = [
    ("1.0", 0.20, 42),  # 80/20, baseline seed
    ("2.0", 0.20, 7),  # 80/20, different shuffle - different model weights
    ("3.0", 0.40, 99),  # 60/40, harder split - lower data for training
]


# Load all documents
def extract_text(pdf_path: str) -> str:
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return " ".join(page.extract_text() for page in reader.pages).strip()
    except Exception as e:
        print(f"  Error reading {pdf_path}: {e}")
        return ""


print("Loading documents...")
data, labels = [], []
for doc_class in CLASSES:
    class_dir = os.path.join(DOCUMENTS_DIR, doc_class)
    files = [f for f in os.listdir(class_dir) if f.endswith(".pdf")]
    for pdf_file in files:
        text = extract_text(os.path.join(class_dir, pdf_file))
        if text:
            data.append(text)
            labels.append(doc_class)

print(f"Loaded {len(data)} documents across {len(CLASSES)} classes")
os.makedirs(MODELS_DIR, exist_ok=True)

# Load existing registry if present
registry_path = os.path.join(MODELS_DIR, "model_registry.json")
if os.path.exists(registry_path):
    with open(registry_path) as f:
        registry = json.load(f)
else:
    registry = {}

# Train each version
for version, test_size, seed in VERSIONS:
    train_count = int(len(data) * (1 - test_size))
    test_count = len(data) - train_count
    print(f"\nVersion {version} | test_size={test_size}  seed={seed}")
    print(f"Train: {train_count} docs   Test: {test_count} docs")

    X_train, X_test, y_train, y_test = train_test_split(
        data,
        labels,
        test_size=test_size,
        random_state=seed,
        stratify=labels,
    )

    # Each version gets its own vectorizer fitted on its own training split
    vectorizer = TfidfVectorizer(
        max_features=5000,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 2),
        stop_words="english",
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    for model_name, base_model in MODEL_CONFIGS.items():
        import sklearn.base

        model = sklearn.base.clone(base_model)

        print(f"\n  Training {model_name} v{version}...")
        model.fit(X_train_tfidf, y_train)

        y_pred = model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        print(f"    Accuracy: {accuracy:.4f}   F1: {f1:.4f}")

        model_data = {
            "model": model,
            "vectorizer": vectorizer,
            "classes": CLASSES,
            "model_name": model_name,
            "version": version,
            "test_size": test_size,
            "random_seed": seed,
            "train_docs": train_count,
            "test_docs": test_count,
            "accuracy": accuracy,
            "f1_score": f1,
            "timestamp": pd.Timestamp.now().isoformat(),
        }

        model_hash = hashlib.sha256(pickle.dumps(model_data)).hexdigest()
        model_data["model_hash"] = model_hash

        filename = f"{model_name}_v{version}.pkl"
        save_path = os.path.join(MODELS_DIR, filename)
        joblib.dump(model_data, save_path)
        print(f"    Hash = {model_hash[:32]}...")

        # Update registry
        if model_name not in registry:
            registry[model_name] = {}

        registry[model_name][version] = {
            "file": filename,
            "hash": model_hash,
            "accuracy": round(accuracy, 4),
            "f1_score": round(f1, 4),
            "test_size": test_size,
            "random_seed": seed,
            "train_docs": train_count,
            "test_docs": test_count,
        }

# Save registry

with open(registry_path, "w") as f:
    json.dump(registry, f, indent=2)

print(f"\n\nRegistry saved -> {registry_path}")
print("\nSummary:")
for model_name, versions in registry.items():
    print(f"  {model_name}:")
    for v, meta in versions.items():
        print(
            f"    v{v}  acc={meta['accuracy']:.4f}  f1={meta['f1_score']:.4f}  "
            f"train={meta['train_docs']}  test={meta['test_docs']}"
        )

print("\nAll models trained and saved.")

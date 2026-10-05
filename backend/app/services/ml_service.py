"""
ML Model Service
Loads the trained models dynamically based on model_name + version.
"""

import hashlib
import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import Optional
import io

import joblib
import PyPDF2

from app.core.config import settings

logger = logging.getLogger(__name__)

DECISION_MAP: dict[str, int] = {
    "logistics": 0,
    "salary": 1,
    "finance": 2,
    "legal": 3,
    "hr": 4,
}

# model_name => version => loaded model_data dict
_model_cache: dict[str, dict] = {}


def _load_registry() -> dict:
    registry_path = Path(settings.MODELS_DIR) / "model_registry.json"
    if not registry_path.exists():
        logger.warning("model_registry.json not found at %s", registry_path)
        return {}
    with open(registry_path) as f:
        return json.load(f)


def get_available_models() -> dict:
    """Returns {model_name: {version: {file, hash, accuracy}}}"""
    return _load_registry()


def load_model(model_name: str, version: str) -> dict:
    """Load and cache a specific model by name + version."""
    cache_key = f"{model_name}_{version}"
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    registry = _load_registry()
    if model_name not in registry or version not in registry[model_name]:
        raise ValueError(
            f"Model '{model_name}' version '{version}' not found in registry."
        )

    filename = registry[model_name][version]["file"]
    model_path = Path(settings.MODELS_DIR) / filename

    if not model_path.exists():
        raise RuntimeError(f"Model file not found: {model_path}")

    logger.info("Loading model %s v%s from %s", model_name, version, model_path)
    model_data = joblib.load(model_path)
    _model_cache[cache_key] = model_data
    return model_data


class MLService:
    def __init__(self):
        self._default_model: Optional[dict] = None
        self._try_load_default()

    def _try_load_default(self):
        try:
            registry = _load_registry()
            if registry:
                first_model = next(iter(registry))
                first_version = next(iter(registry[first_model]))
                self._default_model = load_model(first_model, first_version)
                logger.info("Default model loaded: %s v%s", first_model, first_version)
        except Exception as e:
            logger.warning("Could not load default model: %s", e)

    @property
    def is_loaded(self) -> bool:
        return self._default_model is not None

    def extract_text(self, pdf_bytes: bytes) -> str:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        return " ".join(page.extract_text() for page in reader.pages).strip()

    def classify(
        self, pdf_bytes: bytes, model_name: str = "SVM", version: str = "1.0"
    ) -> dict:
        """
        Classify a PDF using the specified model and version.

        Returns:
            {
                "label": "finance",
                "decision_index": 2,
                "doc_hash": "0x...",
                "model_hash": "0x...",
                "model_name": "SVM",
                "version": "1.0",
            }
        """
        model_data = load_model(model_name, version)

        doc_hash_hex = "0x" + hashlib.sha256(pdf_bytes).hexdigest()

        text = self.extract_text(pdf_bytes)
        if not text.strip():
            raise ValueError("Could not extract text from PDF.")

        features = model_data["vectorizer"].transform([text])
        label: str = model_data["model"].predict(features)[0]

        model_hash = model_data.get("model_hash", "")
        if not model_hash.startswith("0x"):
            model_hash = "0x" + model_hash

        return {
            "label": label,
            "decision_index": DECISION_MAP[label],
            "doc_hash": doc_hash_hex,
            "model_hash": model_hash,
            "model_name": model_name,
            "version": version,
        }


@lru_cache(maxsize=1)
def get_ml_service() -> MLService:
    return MLService()

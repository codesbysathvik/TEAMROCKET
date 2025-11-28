# backend/models.py — loads ML artifacts from ml/models/ and exposes predict_prob()
import os, pickle, numpy as np
from typing import Optional

# Paths (repo-root/ml/models/)
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models"))
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

class SmallModelFromFiles:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.scaler = None
        # load model.pkl (expected: (model, vectorizer) OR model)
        if os.path.exists(MODEL_PATH):
            try:
                loaded = pickle.load(open(MODEL_PATH, "rb"))
                if isinstance(loaded, tuple) and len(loaded) >= 2:
                    self.model = loaded[0]
                    self.vectorizer = loaded[1]
                else:
                    self.model = loaded
            except Exception:
                self.model = None
        # load scaler
        if os.path.exists(SCALER_PATH):
            try:
                self.scaler = pickle.load(open(SCALER_PATH, "rb"))
            except Exception:
                self.scaler = None

    def predict_prob(self, payload: dict) -> Optional[float]:
        """
        payload should include:
          - 'clean_url' or 'url' (text)
          - 'feature1' and 'feature2' numeric fields (trainer used these)
        Returns probability between 0..1, or None when model missing or failure.
        """
        if self.model is None or self.vectorizer is None:
            return None
        try:
            text = payload.get("clean_url", payload.get("url", ""))
            X_text = self.vectorizer.transform([text])
            f1 = float(payload.get("feature1", 0.0))
            f2 = float(payload.get("feature2", 0.0))
            # scaler transforms numeric features if available
            if self.scaler is not None:
                X_num = self.scaler.transform([[f1, f2]])
            else:
                X_num = np.array([[f1, f2]])
            # combine sparse + dense
            from scipy.sparse import hstack
            X = hstack([X_text, X_num])
            prob = self.model.predict_proba(X)[0][1]
            return float(prob)
        except Exception:
            return None

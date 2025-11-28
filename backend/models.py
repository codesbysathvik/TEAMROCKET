# backend/models.py
import os
import joblib
import numpy as np

MODEL_FILENAME = os.path.join(os.path.dirname(__file__), "phish_model.joblib")

class SmallModel:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_FILENAME):
            try:
                self.model = joblib.load(MODEL_FILENAME)
            except Exception:
                self.model = None

    def predict_malicious_prob(self, features: dict):
        if self.model is None:
            return None
        keys = ["url_length","host_length","host_entropy","has_ip","has_at_symbol",
                "dot_count","suspicious_word_count","is_https","uses_shortener",
                "path_token_count"]
        x = [float(features.get(k,0.0)) for k in keys]
        x_arr = np.array(x).reshape(1,-1)
        try:
            return float(self.model.predict_proba(x_arr)[0][1])
        except Exception:
            return None

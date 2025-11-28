import os
import pickle
from scipy.sparse import hstack
from utils.preprocessing import clean_text

def load_model():
    base = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base, "models", "model.pkl")
    scaler_path = os.path.join(base, "models", "scaler.pkl")

    model, vectorizer = pickle.load(open(model_path, "rb"))
    scaler = pickle.load(open(scaler_path, "rb"))

    return model, vectorizer, scaler

model, vectorizer, scaler = load_model()

def predict_url(url, feature1, feature2):
    clean = clean_text(url)
    X_text = vectorizer.transform([clean])
    X_num = scaler.transform([[feature1, feature2]])
    X = hstack([X_text, X_num])

    prob = model.predict_proba(X)[0][1]
    score = int(prob * 100)

    return score

if __name__ == "__main__":
    print(predict_url("http://example55.com", 0.5, 0.9))


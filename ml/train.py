import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack
from utils.preprocessing import clean_text
from utils.csv_sql_sync import merge_sql_to_dataset

print("🔄 Loading and merging CSV files...")
df = merge_sql_to_dataset()

required = ["url", "feature1", "feature2", "label"]
for col in required:
    if col not in df.columns:
        raise Exception(f"Missing required column: {col}")

df["clean_text"] = df["url"].astype(str).apply(clean_text)

# Vectorization
vectorizer = TfidfVectorizer(max_features=5000)
X_text = vectorizer.fit_transform(df["clean_text"])

# Numeric features
scaler = StandardScaler()
X_num = scaler.fit_transform(df[["feature1", "feature2"]])

# Combine
X = hstack([X_text, X_num])
y = df["label"]

# Train model
print("🤖 Training model...")
model = RandomForestClassifier(n_estimators=300, random_state=42)
model.fit(X, y)

# Save artifacts
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, "models")
os.makedirs(models_dir, exist_ok=True)

pickle.dump((model, vectorizer), open(os.path.join(models_dir, "model.pkl"), "wb"))
pickle.dump(scaler, open(os.path.join(models_dir, "scaler.pkl"), "wb"))

print("✔ Training complete!")
print("✔ Saved: models/model.pkl")
print("✔ Saved: models/scaler.pkl")
import os
import pandas as pd
import numpy as np

def get_path(filename):
    """Return absolute path inside ML/data folder."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ML/
    return os.path.join(base_dir, "data", filename)

def create_csv_if_missing():
    """Auto-create dataset.csv and sql_dump.csv if missing."""
    dataset_path = get_path("dataset.csv")
    sql_path = get_path("sql_dump.csv")

    # dataset.csv missing → create synthetic version
    if not os.path.exists(dataset_path):
        print("⚠ dataset.csv not found. Creating a sample dataset...")
        urls = [f"http://example{i}.com" for i in range(1, 101)]
        df = pd.DataFrame({
            "url": urls,
            "feature1": np.random.rand(100),
            "feature2": np.random.rand(100),
            "label": np.random.randint(0, 2, 100)
        })
        df.to_csv(dataset_path, index=False)
        print("✔ dataset.csv created")

    # sql_dump.csv missing → create synthetic version
    if not os.path.exists(sql_path):
        print("⚠ sql_dump.csv not found. Creating a sample SQL dump...")
        urls = [f"http://example{i}.com" for i in range(1, 101)]
        df_sql = pd.DataFrame({
            "url": urls,
            "heuristic_score": np.random.randint(0, 101, 100),
            "additional_signal": np.random.choice(
                ["low-risk", "medium-risk", "high-risk", "critical"],
                100
            )
        })
        df_sql.to_csv(sql_path, index=False)
        print("✔ sql_dump.csv created")

def merge_sql_to_dataset():
    """Load dataset and SQL dump safely (absolute paths)."""
    create_csv_if_missing()

    dataset_path = get_path("dataset.csv")
    sql_path = get_path("sql_dump.csv")

    df_data = pd.read_csv(dataset_path)
    df_sql = pd.read_csv(sql_path)

    # Merge on URL
    df = df_data.merge(df_sql, on="url", how="left")

    return df

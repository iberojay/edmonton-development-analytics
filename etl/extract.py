import pandas as pd

# Reads raw CSV into a pandas DataFrame and returns it
def extract_permits(csv_path):
    df = pd.read_csv(csv_path, dtype="string", encoding="utf-8")
    return df
  
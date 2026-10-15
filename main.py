'''Coordinates the pipeline'''
# Calls extraction, calls transformation, then exports the cleaned CSV
from pathlib import Path

from etl.extract import extract_permits
from etl.transform import transform_permits

# Find the folder containing main.py: project root 
project_root = Path(__file__).resolve().parent

# Choose the raw CSV to read
csv_path = project_root / "data" / "raw" / "Development_Permits_20261010.csv"

# Read the CSV, then clean the returned DataFrame
df = extract_permits(csv_path)
clean_df = transform_permits(df)

# Choose where to save the cleaned CSV
output_path = project_root / "data" / "processed" / "development_permits_clean.csv"

# Create the output folder if it doesn't exists
output_path.parent.mkdir(parents=True, exist_ok=True)

# Write the cleaned DataFrame to CSV
clean_df.to_csv(output_path, index=False)

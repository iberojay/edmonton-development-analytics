from pathlib import Path
import pandas as pd

from etl.extract import extract_permits
from etl.transform import transform_permits

project_root = Path(__file__).resolve().parent.parent
csv_path = project_root / "data" / "raw" / "Development_Permits_20261010.csv"

df = extract_permits(csv_path)

clean_df = transform_permits(df)

# Validate date and numeric conversions
conversion_columns = {
    "Permit Date": "permit_date",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Land Parcel Count": "land_parcel_count",
}

print("\nConversion failures:")
# Loop through key value 
for raw_column, clean_column in conversion_columns.items():
    # Select orginal column and remove whitespace and blank strings 
    original_values = df[raw_column].str.strip().replace("", pd.NA)

    # True/False result for each row
    failed_conversion = (
        original_values.notna()
        & clean_df[clean_column].isna()
    )

    print(f"{clean_column}: {failed_conversion.sum()}")

    if failed_conversion.any():
        print(original_values[failed_conversion].head())

# print("\nRaw and cleaned row counts:")
# print(len(df), len(clean_df))

# print("\nCleaned column types:")
# print(clean_df.dtypes) # shows data type of every column in df

# print("\nRaw neighbourhood classification:")
# print(df["Neighbourhood Classification"].value_counts(dropna=False))

# print("\nCleaned neighbourhood classification:")
# print(clean_df["neighbourhood_classification"].value_counts(dropna=False))

'''Checking rows columns and missing Values'''
# print("Rows:", df.shape[0])
# print("Columns:", df.shape[1])

# print("\nColumn names:")
# print(df.columns.tolist())

# print("\nMissing values per column:")
# print(df.isna().sum())


'''Checking Ids and Categories'''
# print("\nDuplicate Row IDs:")
# print(df["Row ID"].duplicated().sum())  # Count repeated IDs after first occurence

# print("\nPermit types:")
# print(df["Permit Type"].value_counts(dropna=False))

# print("\nStatuses:")
# print(df["Status"].value_counts(dropna=False))

# print("\nNeighbourhood classifications:")
# print(df["Neighbourhood Classification"].value_counts(dropna=False))


'''Converting and Checking Dates'''

'''Missing Permit Dates by Status'''
# print("\nMissing Permit Dates by Status:")
# print(
#     df.loc[df["Permit Date"].isna(), "Status"] # identifies rows with missing oermit dates and returns the corresponding status values
#     .value_counts(dropna=False) # Counts how amny belong to eachs status
# )

'''Data Conversion and Failed Conversion Check'''
# print("\nPermit Date Conversion Check:")
permit_dates = pd.to_datetime(
    df["Permit Date"],
    format = "%b %d, %Y",  # Month name, day of month, year
    errors = "coerce"  # if value cannot be converted to datetime, return NaT (Not a Time) instead of raising an error
)

invalid_dates = df["Permit Date"].notna() & permit_dates.isna()

# print("\nDates present but unable to parse:")
# print(invalid_dates.sum())

'''Date Examples and Range'''
# print("\nExamples of orginal date values:")
# print(df["Permit Date"].dropna().head())

# print("\nEarliest permit date:", permit_dates.min())  # January 2, 2015
# print("Latest permit date:", permit_dates.max())  # October 9, 2026


'''Exploring Annual Approval Counts '''
approved_with_dates = (
    (df["Status"] == "Approved") & (permit_dates.notna())
)

# print("\nTotal approved permits:", df["Status"].eq("Approved").sum())
# print("Approved permits with valid dates:", approved_with_dates.sum())

# print(
#     permit_dates[approved_with_dates]
#     .dt.year  # only get the year part of the datetime object
#     .value_counts()  # Count how many permits were approved in EACH YEAR
#     .sort_index()  # Sorts resuls by their labels (years) in ascending order
# )

'''Comparing Permit Types in 2018 and 2019 '''
# print("\nDated approved permits by year and type:")
annual_counts_by_type = pd.crosstab(
    permit_dates[approved_with_dates].dt.year,  # rows: years of approved permits
    df.loc[approved_with_dates, "Permit Type"],  # columns: types of approved permits
    
)

# print(annual_counts_by_type.loc[[2018,2019]].T.to_string())  # Display only the rows for 2018 and 2019
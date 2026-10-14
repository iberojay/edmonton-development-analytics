from pathlib import Path
import pandas as pd

from etl.extract import extract_permits
from etl.transform import transform_permits

def profile_raw_data(df):
    '''Summarize the source data before transformation'''
    print("\nRAW DATA PROFILE")

    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nMissing values per column:")
    print(df.isna().sum())

    print("\nDuplicate Row IDs:")
    print(df["Row ID"].duplicated().sum())  # Count repeated IDs after first occurence

    for column in ["Permit Type", "Status", "Neighbourhood Classification"]:
        print(f"\n{column}:")
        print(df[column].value_counts(dropna=False))

    print("\nExamples of orginal date values:")
    print(df["Permit Date"].dropna().head())

    print("\nMissing Permit Dates by Status:")
    print(
        df.loc[df["Permit Date"].isna(), "Status"] # identifies rows with missing oermit dates and returns the corresponding status values
        .value_counts(dropna=False) # Counts how amny belong to eachs status
    )


def validate_transformation(df, clean_df):
    '''Report row preservation, data types, and conversion failures'''
    print("\nTransfomration Validation")
    print("Raw rows:", len(df))
    print("Cleaned rows:", len(clean_df))
    print("Row counts match:", len(df) == len(clean_df))

    print("\nCleaned column types:")
    print(clean_df.dtypes)  # shows data type of every column in df

    # Validate date and numeric conversions
    conversion_columns = {
        "Permit Date": "permit_date",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Land Parcel Count": "land_parcel_count",
    }

    print("Conversion failures:")
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

    print("\nRaw neighbourhood classification:")
    print(df["Neighbourhood Classification"].value_counts(dropna=False))

    print("\nCleaned neighbourhood classification:")
    print(clean_df["neighbourhood_classification"].value_counts(dropna=False))


def explore_approvals(clean_df):
    '''Explore approval trends using the transformed data'''
    print("\nApproval Exploreation")
    print("\nEarliest permit date:", clean_df["permit_date"].min())  
    print("Latest permit date:", clean_df["permit_date"].max()) 

    # Exploring Annual Approval Counts
    approved = clean_df.loc[
        clean_df["status"].eq("Approved") & clean_df["permit_date"].notna()
    ]

    print("\nAnnaual dated approval counts:")
    print(
        approved["permit_date"]
        .dt.year  # only get the year part of the datetime object
        .value_counts()  # Count how many permits were approved in EACH YEAR
        .sort_index()  # Sorts resuls by their labels (years) in ascending order
    )

    annual_counts_by_type = pd.crosstab(
        approved["permit_date"].dt.year,
        approved["permit_type"],
    )

    print("\nApproved permit types in 2018 and 2019:")
    print(
        annual_counts_by_type
        .reindex([2018, 2019], fill_value=0)
        .T.to_string()
    )


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "raw" / "Development_Permits_20261010.csv" 

    df = extract_permits(csv_path)
    clean_df = transform_permits(df)  

    profile_raw_data(df)
    validate_transformation(df, clean_df)
    explore_approvals(clean_df)

if __name__ == "__main__":
    main()


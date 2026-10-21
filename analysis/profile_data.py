from pathlib import Path
import pandas as pd

from etl.extract import extract_permits
from etl.transform import transform_permits, build_permit_neighbourhoods
from analysis.validate_data import validate_transformation, validate_permit_neighbourhoods

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

    reference_path = (project_root / "data" / "reference" / "neighbourhood_overrides.csv")
    neighbourhood_overrides = pd.read_csv(reference_path, dtype="string")

    df = extract_permits(csv_path)
    clean_df = transform_permits(df)  

    #profile_raw_data(df)
    validate_transformation(df, clean_df, neighbourhood_overrides)
    #explore_approvals(clean_df)

    permit_neighbourhoods = build_permit_neighbourhoods(clean_df)
    validate_permit_neighbourhoods(clean_df, permit_neighbourhoods)


if __name__ == "__main__":
    main()


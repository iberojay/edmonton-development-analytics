import pandas as pd

def validate_rows(clean_df):
    '''Check missing and duplacte permit identifiers.'''
    print("\nROW ID VALIDATION")
    print("Missing Row IDs:", clean_df["row_id"].isna().sum())
    print("Duplicate Row IDs:", clean_df["row_id"].duplicated().sum())


def validate_conversions(df, clean_df):
    '''Find nonempty values that becmae missing during conversion.'''
    # Validate date and numeric conversions
    conversion_columns = {
        "Permit Date": "permit_date",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Land Parcel Count": "land_parcel_count",
    }

    print("\nCONVERSION VALIDATION")
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


def validate_classifications(df, clean_df):
    '''Display classifcaiton counts before and after cleaning'''
    print("\nRaw neighbourhood classification:")
    print(df["Neighbourhood Classification"].value_counts(dropna=False))

    print("\nCleaned neighbourhood classification:")
    print(clean_df["neighbourhood_classification"].value_counts(dropna=False))


def validate_neighbourhood_mappings(clean_df):
    '''Inspect inconsistent names for ID strings and individual IDs.'''
    # Neighbourhood Id and Names Check
    names_per_id = (
        clean_df.groupby("neighbourhood_id")["neighbourhood"]  # groups records sharing neighbourhood ID
        .nunique()  # Counts distinct nonmissing neighbourhood names
    )
    conflicting_ids = names_per_id[names_per_id > 1]  # Identify IDs associated with multiple names

    print("\nNeighbourhood IDs with multiple names:")
    print(conflicting_ids)

    print("\nAssociated ID-and-name combinations:")
    print(
        clean_df.loc[
            clean_df["neighbourhood_id"].isin(conflicting_ids.index),
            ["neighbourhood_id", "neighbourhood"],
        ]
        .drop_duplicates()
        .to_string(index=False)
    )

    single_id_records = clean_df.loc[
        clean_df["neighbourhood_id"].notna() &
        ~clean_df["neighbourhood_id"].str.contains(",", na=False)  # exclude ID cells containing commas
    ]

    names_per_single_id = (
        single_id_records
        .groupby("neighbourhood_id")["neighbourhood"]
        .nunique()
    )
    conflicting_single_ids = names_per_single_id[
        names_per_single_id > 1
    ]
    print("\nSingle neighbourhood IDs with multiple names:")
    print(conflicting_single_ids)

    print("\nAssociated single-ID name combinations:")
    print(
        single_id_records.loc[
            single_id_records["neighbourhood_id"].isin(
                conflicting_single_ids.index
            ),
            ["neighbourhood_id", "neighbourhood"],
        ]
        .drop_duplicates()
        .sort_values(["neighbourhood_id", "neighbourhood"])
        .to_string(index=False)
    )

def validate_missing_neighbourhoods(clean_df):
    '''Count and display missing neighbourhood information.'''
    print("\nMISSING NEIGHBOURHOOD VALUES")
    print(
        clean_df[["neighbourhood_id", "neighbourhood"]]
        .isna().sum()
    )

    missing_neighbourhood = (
        clean_df["neighbourhood_id"].isna()
        | clean_df["neighbourhood"].isna()
    )

    print("\nRecords with missing neighbourhood information:")
    print(
        clean_df.loc[
            missing_neighbourhood,
            ["row_id", "neighbourhood_id", "neighbourhood"],
        ].to_string(index=False)
    )


def validate_neighbourhood_name_recovery(clean_df):
    '''Check availble names for IDs whose names are missing.'''
    # Build loockup candidates from single IDs with single names
    #  - existing ID and name pair 
    known_names = clean_df.loc[
        clean_df["neighbourhood_id"].notna()
        & clean_df["neighbourhood"].notna()
        & ~clean_df["neighbourhood_id"].str.contains(",", na=False)
        & ~clean_df["neighbourhood"].str.contains(",", na=False),
        ["neighbourhood_id", "neighbourhood"],
    ].drop_duplicates()

    # Find IDs needing a name (neighbourhood_ID with MISSING name)
    missing_neighbourhood_name_ids = clean_df.loc[
        clean_df["neighbourhood_id"].notna() & clean_df["neighbourhood"].isna(),  #id with no name
        ["neighbourhood_id"]
    ].drop_duplicates()

    # .merge()
    #  - matches missing name Ids to known names using neighbourhood_id
    recovery_check = missing_neighbourhood_name_ids.merge(
        known_names,
        on="neighbourhood_id",
        how="left",
        validate="one_to_one"
    )
    print("\nPossible names for missing neighbourhood values:")
    print(recovery_check.to_string(index=False))


# For every individual ID inside a multiple-ID cell, find its name elsewhere in the dataset
def validate_multi_id_coverage(clean_df, neighbourhood_overrides):
    '''Check lookup coverage for IDs appearing in multi-ID cells.'''
    # Lookup where: ID and name both exists AND neither contains commas, so each cell contains a single entry 
    known_name = clean_df.loc[
        clean_df["neighbourhood_id"].notna()
        & clean_df["neighbourhood"].notna()
        & ~clean_df["neighbourhood_id"].str.contains(",", na=False)
        & ~clean_df["neighbourhood"].str.contains(",", na=False),
        ["neighbourhood_id", "neighbourhood"],
    ].drop_duplicates()

    # Combines mappings from permit records with the three confirmed mappings from reference CSV
    known_name = pd.concat(
        [known_name, neighbourhood_overrides],
        ignore_index=True,
    ).drop_duplicates()

    # Select cells with multiple IDs
    multi_id_values = clean_df.loc[
        clean_df["neighbourhood_id"].str.contains(",", na=False),
        "neighbourhood_id",
    ]


    # Turn those cells into a table of individual IDs
    individual_ids = (
        multi_id_values
        .str.split(",")  # string becomes list
        .explode()  # Each item in list becomes a separate row
        .str.strip()
        .drop_duplicates()  # keeps each indivudal ID once
        .rename("neighbourhood_id")
        .to_frame() # Converts the Series into a one-column DataFrame 
    )

    # Look up a name for each ID 
    coverage = individual_ids.merge(
        known_name,
        on="neighbourhood_id",
        how="left",
        validate="one_to_one"
    )

    print("Table merge:",coverage.to_string(index=False))

    # Select IDs lookup couldn't name, from the merged table, select IDs whose name is missing 
    #   - 6212, 3381, 5456, 4451
    unmatched_ids = coverage.loc[
        coverage["neighbourhood"].isna(),
        "neighbourhood_id",
    ]

    # loop through each missing one
    for neighbourhood_id in unmatched_ids:
        contains_id = clean_df["neighbourhood_id"].apply(
            lambda value: (
                neighbourhood_id in [
                    item.strip() for item in value.split(",")
                ]
                if pd.notna(value)
                else False
            )   
        )

        print(f"\nSource combinations containing ID {neighbourhood_id}:")
        print(
            clean_df.loc[
                contains_id,
                ["neighbourhood_id", "neighbourhood"],
            ]
            .drop_duplicates()
            .to_string(index=False)
        )


def split_neighbourhood_ids(value):
    '''Takes one cell and returns its individual IDs  as  a set'''
    # Check whether the cell is missing
    if pd.isna(value):
        return set()

    # Create a empty collection
    neighbourhood_ids = set()

    #Split by commas and loop through the pieces
    for item in value.split(","):
        neighbourhood_ids.add(item.strip())

    return neighbourhood_ids


def validate_permit_neighbourhoods(clean_df, permit_neighbourhoods):
    '''Check that relationshups match the original permit records.'''
    # Does each permit have the same neighbourhood IDs before and after we split them into relationship rows?

    print("\nPERMIT-NEIGHBOURHOOD VALIDATION")

    # Expected neighbourhood IDs from each original permit record 
    # row_id index, selects neighbourhood ID column and run helper function on each cell
    # Represents the IDs each permit should have 
    expected = (
        clean_df
        .set_index("row_id")["neighbourhood_id"]
        .apply(split_neighbourhood_ids)
    )

    # Collect actual IDs from the relationshup table 
    actual = (
        permit_neighbourhoods
        .groupby("row_id")["neighbourhood_id"] # Gather rows belonging to the same permit
        .agg(set)  # Collects their neighbourhood IDs into a set
    )

    # Compare expected and actual sets, list to collect problems 
    mismatched_permits = []

    for row_id, expected_ids in expected.items():  #.item give index and value together on each iteration 
        actual_ids = actual.get(row_id, set())

        if expected_ids != actual_ids:
            mismatched_permits.append(row_id)

    unknown_permits = ~permit_neighbourhoods["row_id"].isin(
        clean_df["row_id"]
    )

    # Same permit linked to the same neighbourhood twice
    print(
        "Duplicate permit–neighbourhood pairs:",
        permit_neighbourhoods.duplicated(
            subset=["row_id", "neighbourhood_id"]
        ).sum(),
    )

    # A relationship missing either ID
    print(
        "Missing values in relationship columns:",
        permit_neighbourhoods[["row_id", "neighbourhood_id"]]
        .isna().sum().sum(),
    )

    # A link whose permit doesn't exist in clean_df
    print("Links to unknown permits:", unknown_permits.sum())

    # A permit whose actual neighbourhood IDs differ from its original IDds
    print(
        "Permits with mismatched neighbourhood links:",
        len(mismatched_permits),
    )
    
    if mismatched_permits:
        print("Example mismatched permit IDs:", mismatched_permits[:5])


def validate_transformation(df, clean_df, neighbourhood_overrides):
    '''Report row preservation, data types, and conversion failures'''
    # print("\nTransfomration Validation")
    # print("Raw rows:", len(df))
    # print("Cleaned rows:", len(clean_df))
    # print("Row counts match:", len(df) == len(clean_df))

    # print("\nCleaned column types:")
    # print(clean_df.dtypes)  # shows data type of every column in df

    # validate_rows(clean_df)
    # validate_conversions(df, clean_df)
    # validate_classifications(df, clean_df)
    # validate_neighbourhood_mappings(clean_df)

    # validate_missing_neighbourhoods(clean_df)
    # validate_neighbourhood_name_recovery(clean_df)

    validate_multi_id_coverage(clean_df, neighbourhood_overrides)
import pandas as pd

def transform_permits(df):
    '''Create a cleaned copy of the development permits DataFrame.'''
    clean_df = df.copy()

    # Standardize column names
    clean_df.columns = (
        clean_df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ","_", regex=False)
    )
    
    # Remove whitespace and replace empty strings with missing values
    for column in clean_df.columns:
        clean_df[column] = clean_df[column].str.strip().replace("", pd.NA)

    clean_df["permit_date"] = pd.to_datetime(
        clean_df["permit_date"],
        format = "%b %d, %Y",
        errors = "coerce"
    )

    # Convert numerical column values from strings to numbers 
    numerical_columns = ["latitude", "longitude", "land_parcel_count"]

    for column in numerical_columns:
        clean_df[column] = pd.to_numeric(
            clean_df[column],
            errors="coerce"
        )

    clean_df["land_parcel_count"] = clean_df["land_parcel_count"].astype("Int64")

    clean_df["neighbourhood_classification"] = (
        clean_df["neighbourhood_classification"].apply(clean_classifcation)
    )


    '''Fill in missing neighbourhood names that have a neighbourhood ID'''
    # Build a lookup from a single IDs with single, nonmissing names
    known_names = clean_df.loc[
        clean_df["neighbourhood_id"].notna()
        & clean_df["neighbourhood"].notna()
        & ~clean_df["neighbourhood_id"].str.contains(",", na=False)
        & ~clean_df["neighbourhood"].str.contains(",", na=False),
        ["neighbourhood_id", "neighbourhood"],
    ].drop_duplicates()

    # Prevent ambigious ID-to-name mappings
    if known_names["neighbourhood_id"].duplicated().any():
        raise ValueError("Conflicting neighbourhood names in lookup")

    # .set_index(): makes neughbourhood IDs the lookup keys
    name_lookup = known_names.set_index("neighbourhood_id")["neighbourhood"]

    # Fill in missing names using their IDs
    clean_df["neighbourhood"] = clean_df["neighbourhood"].fillna(
        clean_df["neighbourhood_id"].map(name_lookup)  # map(): finds corresponding name for each ID
    )

    return clean_df


def clean_classifcation(value):
    '''Remove repeated classifications inside Neighbourhood Classifcation'''
    # If no value exists return <NA> inside the record 
    if pd.isna(value):
        return pd.NA
    
    classications = value.split(",")

    cleaned_classifcation = []

    for classifcation in classications:
        cleaned_classifcation.append(classifcation.strip())

    # Uses each classifcation as a key, with None as its value 
    unique_classifcations = dict.fromkeys(cleaned_classifcation)
    
    return ", ".join(unique_classifcations)

def build_permit_neighbourhoods(clean_df):
    '''Create one row per permit-neighbourhood relationship. (No multiple neighbourhood_id in one cell)'''
    relationships = clean_df[
        ["row_id", "neighbourhood_id"]
    ].dropna(subset=["neighbourhood_id"]).copy()

    # Convert each neighbourhood_id string into a list
    relationships["neighbourhood_id"] = (
        relationships["neighbourhood_id"].str.split(",")
    )

    # Each record becomes a separate row, Pandas repeats the corresponding row_id automatically
    relationships = relationships.explode("neighbourhood_id")

    # Remove surronding whitespace
    relationships["neighbourhood_id"] = (
        relationships["neighbourhood_id"].str.strip()
    )

    # Removes repeat permit-neihgbourhood pairs,, gives result a fresh numbered index and returns it 
    return relationships.drop_duplicates().reset_index(drop=True)
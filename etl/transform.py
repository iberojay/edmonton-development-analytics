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

    return clean_df


def  clean_classifcation(value):
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

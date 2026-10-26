CREATE TABLE IF NOT EXISTS staging_permits (
    row_id TEXT PRIMARY KEY,
    permit_type TEXT NOT NULL,
    permit_class TEXT,
    permit_date DATE,
    status TEXT NOT NULL,
    description_of_development TEXT,
    address TEXT,
    legal_description TEXT,
    neighbourhood_id TEXT,
    neighbourhood TEXT,
    neighbourhood_classification TEXT,
    ward TEXT,
    bia TEXT,
    zoning TEXT,
    land_parcel_count INTEGER,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location TEXT,
    geometry_point TEXT
);


CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS dim_permit_type (
    permit_type_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    permit_type TEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS dim_neighbourhood (
    neighbourhood_id TEXT PRIMARY KEY,
    neighbourhood TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS fact_permits (
    row_id TEXT PRIMARY KEY,
    date_key INTEGER REFERENCES dim_date(date_key),
    permit_type_key INTEGER NOT NULL
        REFERENCES dim_permit_type(permit_type_key),
    permit_class TEXT,
    status TEXT NOT NULL,
    description_of_development TEXT,
    address TEXT,
    legal_description TEXT,
    neighbourhood_classification TEXT,
    ward TEXT,
    bia TEXT,
    zoning TEXT,
    land_parcel_count INTEGER,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location TEXT,
    geometry_point TEXT
);

CREATE TABLE IF NOT EXISTS bridge_permit_neighbourhood (
    row_id TEXT NOT NULL REFERENCES fact_permits(row_id),
    neighbourhood_id TEXT NOT NULL
        REFERENCES dim_neighbourhood(neighbourhood_id),
    PRIMARY KEY (row_id, neighbourhood_id)
);
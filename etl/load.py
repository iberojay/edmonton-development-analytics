import psycopg
from psycopg import sql

def check_database_connection():
    """Connect to PostgreSQL and display the database and user."""
    with psycopg.connect(dbname="edmonton_development") as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user;")
            database_name, user_name = cursor.fetchone()

            print("Connected to database:", database_name)
            print("Connected as:", user_name)


def load_staging_permits(clean_df):
    """Replace staging contents with the cleaned permit data."""
    copy_command = sql.SQL(
        "COPY staging_permits ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
    ).format(
        sql.SQL(", ").join(
            sql.Identifier(column) for column in clean_df.columns
        )
    )

    with psycopg.connect(dbname="edmonton_development") as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM staging_permits;")

            with cursor.copy(copy_command) as copy:
                copy.write(clean_df.to_csv(index=False))

            cursor.execute("SELECT COUNT(*) FROM staging_permits;")
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(clean_df):
                raise ValueError(
                    f"Expected {len(clean_df)} rows, loaded {loaded_rows}"
                )

    print(f"Loaded {loaded_rows:,} rows into staging_permits.")


def populate_dimensions(neighbourhoods):
    """Populate the date, permit type, and neighbourhood dimensions."""
    with psycopg.connect(dbname="edmonton_development") as connection:
        with connection.cursor() as cursor:

            # Create every calendar date between the earliest and latest permit
            cursor.execute("""
                INSERT INTO dim_date (
                    date_key, full_date, year, quarter, month, day
                )
                SELECT
                    TO_CHAR(calendar_date, 'YYYYMMDD')::INTEGER,
                    calendar_date::DATE,
                    EXTRACT(YEAR FROM calendar_date)::INTEGER,
                    EXTRACT(QUARTER FROM calendar_date)::INTEGER,
                    EXTRACT(MONTH FROM calendar_date)::INTEGER,
                    EXTRACT(DAY FROM calendar_date)::INTEGER
                FROM GENERATE_SERIES(
                    (SELECT MIN(permit_date) FROM staging_permits)::TIMESTAMP,
                    (SELECT MAX(permit_date) FROM staging_permits)::TIMESTAMP,
                    INTERVAL '1 day'
                ) AS dates(calendar_date)
                ON CONFLICT (date_key) DO NOTHING;
            """)

            # Insert each permit type once
            cursor.execute("""
                INSERT INTO dim_permit_type (permit_type)
                SELECT DISTINCT permit_type
                FROM staging_permits
                ORDER BY permit_type
                ON CONFLICT (permit_type) DO NOTHING;
            """)

            # Insert neighbourhood mappings, updating names for existing IDs
            cursor.executemany(
                """
                INSERT INTO dim_neighbourhood (
                    neighbourhood_id, neighbourhood
                )
                VALUES (%s, %s)
                ON CONFLICT (neighbourhood_id)
                DO UPDATE SET neighbourhood = EXCLUDED.neighbourhood;
                """,
                neighbourhoods[
                    ["neighbourhood_id", "neighbourhood"]
                ].itertuples(index=False, name=None),
            )

    print("Populated date, permit type, and neighbourhood dimensions.")


def populate_fact_permits():
    """Load permit records from staging with their dimension keys."""
    with psycopg.connect(dbname="edmonton_development") as connection:
        with connection.cursor() as cursor:

            # Check that all populated dates have a dimension match
            cursor.execute("""
                SELECT COUNT(*)
                FROM staging_permits AS s
                LEFT JOIN dim_date AS d
                    ON s.permit_date = d.full_date
                WHERE s.permit_date IS NOT NULL
                  AND d.date_key IS NULL;
            """)

            if cursor.fetchone()[0] > 0:
                raise ValueError("Some permit dates have no dimension match")

            # Insert permits and update existing records on reruns
            cursor.execute("""
                INSERT INTO fact_permits (
                    row_id,
                    date_key,
                    permit_type_key,
                    permit_class,
                    status,
                    description_of_development,
                    address,
                    legal_description,
                    neighbourhood_classification,
                    ward,
                    bia,
                    zoning,
                    land_parcel_count,
                    latitude,
                    longitude,
                    location,
                    geometry_point
                )
                SELECT
                    s.row_id,
                    d.date_key,
                    t.permit_type_key,
                    s.permit_class,
                    s.status,
                    s.description_of_development,
                    s.address,
                    s.legal_description,
                    s.neighbourhood_classification,
                    s.ward,
                    s.bia,
                    s.zoning,
                    s.land_parcel_count,
                    s.latitude,
                    s.longitude,
                    s.location,
                    s.geometry_point
                FROM staging_permits AS s
                LEFT JOIN dim_date AS d
                    ON s.permit_date = d.full_date
                LEFT JOIN dim_permit_type AS t
                    ON s.permit_type = t.permit_type
                ON CONFLICT (row_id) DO UPDATE SET
                    date_key = EXCLUDED.date_key,
                    permit_type_key = EXCLUDED.permit_type_key,
                    permit_class = EXCLUDED.permit_class,
                    status = EXCLUDED.status,
                    description_of_development =
                        EXCLUDED.description_of_development,
                    address = EXCLUDED.address,
                    legal_description = EXCLUDED.legal_description,
                    neighbourhood_classification =
                        EXCLUDED.neighbourhood_classification,
                    ward = EXCLUDED.ward,
                    bia = EXCLUDED.bia,
                    zoning = EXCLUDED.zoning,
                    land_parcel_count = EXCLUDED.land_parcel_count,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    location = EXCLUDED.location,
                    geometry_point = EXCLUDED.geometry_point;
            """)

            cursor.execute("SELECT COUNT(*) FROM staging_permits;")
            expected_rows = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM fact_permits;")
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != expected_rows:
                raise ValueError(
                    f"Expected {expected_rows} permits, found {loaded_rows}"
                )

    print(f"Populated fact_permits with {loaded_rows:,} records.")

if __name__ == "__main__":
    check_database_connection()
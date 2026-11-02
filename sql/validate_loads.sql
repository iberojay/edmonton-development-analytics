-- Check for missing permits in fact table
SELECT sp.row_id
FROM staging_permits sp 
LEFT JOIN fact_permits fp ON sp.row_id = fp.row_id
WHERE fp.row_id IS NULL
;

-- Fact permits missing from staging 
SELECT fp.row_id
FROM fact_permits fp
LEFT JOIN staging_permits sp on fp.row_id = sp.row_id
WHERE sp.row_id IS NULL
;

SELECT fp.row_id, sp.permit_date, dd.full_date
FROM staging_permits sp
LEFT JOIN fact_permits fp ON sp.row_id = fp.row_id
LEFT JOIN dim_date dd ON fp.date_key = dd.date_key
WHERE sp.permit_date IS DISTINCT FROM dd.full_date
;


-- Did each permit get the correct type key when we loaded it 
SELECT fp.row_id, sp.permit_type, dt.permit_type

FROM staging_permits sp
LEFT JOIN fact_permits fp ON sp.row_id = fp.row_id
LEFT JOIN dim_permit_type dt ON fp.permit_type_key = dt.permit_type_key

WHERE sp.permit_type IS DISTINCT FROM dt.permit_type
;


-- Find permit-neighbourhood links expected from staging but missing from the bridge.
-- Split comma-sepearted staging IDs into individual rows, then match both ids.
WITH expected_links AS (
    -- Removes duplicate pairs
    SELECT DISTINCT sp.row_id, TRIM(ids.neighbourhood_id) AS neighbourhood_id
    FROM staging_permits sp
    -- Split each ID cell
    -- Turns array into separate rows, TRIM removes white space
    CROSS JOIN LATERAL
        UNNEST(STRING_TO_ARRAY(sp.neighbourhood_id, ',')) AS ids(neighbourhood_id)
)

SELECT e.row_id, e.neighbourhood_id
-- Compare expected links with the bridge
FROM expected_links e
LEFT JOIN bridge_permit_neighbourhood bn 
    ON e.row_id = bn.row_id
    AND e.neighbourhood_id = bn.neighbourhood_id

WHERE bn.row_id IS NULL;


WITH expected_links AS (
    -- Removes duplicate pairs
    SELECT DISTINCT sp.row_id, TRIM(ids.neighbourhood_id) AS neighbourhood_id
    FROM staging_permits sp 
    -- Split each ID cell
    -- Turns array into separate rows, TRIM removes white space
    CROSS JOIN LATERAL
        UNNEST(STRING_TO_ARRAY(sp.neighbourhood_id, ',')) AS ids(neighbourhood_id)
)

SELECT bn.row_id, bn.neighbourhood_id

FROM bridge_permit_neighbourhood bn
LEFT JOIN expected_links e ON bn.row_id = e.row_id 
AND bn.neighbourhood_id = e.neighbourhood_id

WHERE e.row_id IS NULL;


-- How many permit records are in each status?
SELECT status, COUNT(*) as permit_count
FROM fact_permits 
GROUP BY status
ORDER BY permit_count ASC
;


-- How many permit records belong to each permit type 
SELECT dt.permit_type, COUNT(*) AS permit_count

FROM fact_permits fp
INNER JOIN dim_permit_type dt ON fp.permit_type_key = dt.permit_type_key
GROUP BY dt.permit_type
ORDER BY permit_count DESC
;


-- How many approved permits with valid dates are recorded in each year
SELECT dd.year, COUNT(*) AS permit_count
FROM fact_permits fp
INNER JOIN dim_date dd ON fp.date_key = dd.date_key

WHERE fp.status = 'Approved'

GROUP BY dd.year
ORDER BY dd.year ASC
;


-- How many approved permits with valid dates are recorded in each uear and month 
SELECT dd.year, dd.month, COUNT(*) AS permit_count
FROM fact_permits fp
INNER JOIN dim_date dd ON fp.date_key = dd.date_key

WHERE fp.status = 'Approved'

GROUP BY dd.year, dd.month
ORDER BY dd.year ASC
;


-- How many approved permits with valid dates are recorded in each month of 2025?
SELECT dd.year, dd.month, COUNT(*) AS permit_count
FROM fact_permits fp
INNER JOIN dim_date dd ON fp.date_key = dd.date_key

WHERE fp.status = 'Approved' AND dd.year = 2025

GROUP BY dd.year, dd.month
ORDER BY dd.year ASC
;


-- Whcih permit types contributed most to the decline in approved permits between 2018 and 2019?
SELECT pt.permit_type, COUNT(*) FILTER (WHERE dd.year = 2018) AS approved_2018, COUNT(*) FILTER (WHERE dd.year = 2019) AS approved_2019, 
( (COUNT(*) FILTER (WHERE dd.year = 2018)) - (COUNT(*) FILTER (WHERE dd.year = 2019)) ) AS approval_decrease 

FROM fact_permits fp
INNER JOIN dim_date dd ON fp.date_key = dd.date_key 
INNER JOIN dim_permit_type pt ON fp.permit_type_key = pt.permit_type_key

WHERE fp.status = 'Approved' AND dd.year IN (2018, 2019)

GROUP BY pt.permit_type
ORDER BY approval_decrease DESC
;


-- Which 10 neighbourhoods had the most approved permits in 2025
SELECT dn.neighbourhood_id, dn.neighbourhood, COUNT(DISTINCT fp.row_id) AS approved_permits

FROM fact_permits fp 
INNER JOIN dim_date dd ON fp.date_key = dd.date_key
INNER JOIN bridge_permit_neighbourhood bp ON fp.row_id = bp.row_id
INNER JOIN dim_neighbourhood dn ON bp.neighbourhood_id = dn.neighbourhood_id

WHERE fp.status = 'Approved' AND dd.year = 2025

GROUP BY dn.neighbourhood_id, dn.neighbourhood
ORDER BY approved_permits DESC, dn.neighbourhood_id
LIMIT 10
;


-- Which permit types made up approved activity in Alces, Keswick, and Edgemont in 2025?
SELECT dn.neighbourhood_id, dn.neighbourhood, pt.permit_type, COUNT(DISTINCT fp.row_id) AS approved_permits

FROM fact_permits fp 
INNER JOIN dim_date dd ON fp.date_key = dd.date_key
INNER JOIN bridge_permit_neighbourhood bp ON fp.row_id = bp.row_id
INNER JOIN dim_neighbourhood dn ON bp.neighbourhood_id = dn.neighbourhood_id
INNER JOIN dim_permit_type pt ON fp.permit_type_key = pt.permit_type_key

WHERE fp.status = 'Approved' AND dd.year = 2025 AND dn.neighbourhood_id IN ('6669', '5574', '4462')

GROUP BY dn.neighbourhood_id, dn.neighbourhood, pt.permit_type
ORDER BY dn.neighbourhood, approved_permits DESC
;


--  Which neighbourhoods had the largest increases in approved permit counts between 2024 and 2025
SELECT dn.neighbourhood_id, dn.neighbourhood, COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2024) AS approved_2024, 
    COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2025) AS approved_2025, 
    (COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2025)) - (COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2024)) AS approval_change

FROM fact_permits fp 
INNER JOIN dim_date dd ON fp.date_key = dd.date_key
INNER JOIN bridge_permit_neighbourhood bp ON fp.row_id = bp.row_id
INNER JOIN dim_neighbourhood dn ON bp.neighbourhood_id = dn.neighbourhood_id

WHERE fp.status = 'Approved' AND dd.year IN (2024,2025)

GROUP BY dn.neighbourhood_id, dn.neighbourhood
ORDER BY approval_change DESC, dn.neighbourhood_id
LIMIT 10
;

-- Which neighbourhoods had the largest decreaes in approved permit counts between 2024 and 2025
SELECT dn.neighbourhood_id, dn.neighbourhood, COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2024) AS approved_2024, 
    COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2025) AS approved_2025, 
    (COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2025)) - (COUNT(DISTINCT fp.row_id) FILTER (WHERE dd.year = 2024)) AS approval_change

FROM fact_permits fp 
INNER JOIN dim_date dd ON fp.date_key = dd.date_key
INNER JOIN bridge_permit_neighbourhood bp ON fp.row_id = bp.row_id
INNER JOIN dim_neighbourhood dn ON bp.neighbourhood_id = dn.neighbourhood_id

WHERE fp.status = 'Approved' AND dd.year IN (2024,2025)

GROUP BY dn.neighbourhood_id, dn.neighbourhood
ORDER BY approval_change ASC, dn.neighbourhood_id
LIMIT 10
;
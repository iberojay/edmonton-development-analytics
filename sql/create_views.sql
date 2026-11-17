CREATE OR REPLACE VIEW vw_monthly_permit_activity AS
SELECT dd.year, dd.month, fp.status, pt.permit_type, COUNT(DISTINCT fp.row_id) AS permit_count 

FROM fact_permits fp
INNER JOIN dim_date dd ON fp.date_key = dd.date_key
INNER JOIN dim_permit_type pt ON fp.permit_type_key = pt.permit_type_key

GROUP BY dd.year, dd.month, fp.status, pt.permit_type
;

CREATE OR REPLACE VIEW vw_neighbourhood_permit_activity AS 
SELECT dd.year, dn.neighbourhood_id, dn.neighbourhood, fp.status, pt.permit_type, COUNT(DISTINCT fp.row_id) AS permit_count

FROM fact_permits fp
INNER JOIN dim_date dd ON fp.date_key = dd.date_key
INNER JOIN bridge_permit_neighbourhood bp ON fp.row_id = bp.row_id
INNER JOIN dim_neighbourhood dn ON bp.neighbourhood_id = dn.neighbourhood_id
INNER JOIN dim_permit_type pt ON fp.permit_type_key = pt.permit_type_key

GROUP BY dd.year, dn.neighbourhood_id, dn.neighbourhood, fp.status, pt.permit_type
;
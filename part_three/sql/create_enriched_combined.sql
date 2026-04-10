-- Create enriched combined table with NCES enrollment data


CREATE TABLE enriched_combined AS
SELECT
    c.*,
    n.fipst as nces_fips_code,
    n.state_name as nces_state_name,
    n.nces_enrollment_2122 as nces_state_enrollment_2122,
    n.nces_join_method
FROM combined_chronic_absenteeism c
LEFT JOIN nces_sea_enrollment n
    ON c.state = n.state
    AND c.reporting_category = n.reporting_category


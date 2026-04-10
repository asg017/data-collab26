-- Join NCES SEA enrollment to state-level chronic absenteeism
-- NCES data: 2021-22 | Absenteeism data: 2023-24


CREATE TABLE state_absenteeism_with_nces AS
SELECT
    c.state,
    c.academic_year as absenteeism_year,
    n.state_name as nces_state_name,
    n.fipst as nces_fips_code,
    '2021-22' as nces_enrollment_year,
    c.reporting_category,
    c.category_description,
    c.chronic_absent_rate,
    c.eligible_enrollment as state_eligible_enrollment_2324,
    n.nces_enrollment_2122,
    n.nces_join_method,
    CASE
        WHEN c.eligible_enrollment IS NOT NULL AND n.nces_enrollment_2122 IS NOT NULL
        THEN ROUND((c.eligible_enrollment - n.nces_enrollment_2122) * 100.0
                    / n.nces_enrollment_2122, 2)
        ELSE NULL
    END as enrollment_change_pct
FROM combined_chronic_absenteeism c
LEFT JOIN nces_sea_enrollment n
    ON c.state = n.state
    AND c.reporting_category = n.reporting_category
WHERE c.entity_level = 'State'
ORDER BY c.state, c.reporting_category


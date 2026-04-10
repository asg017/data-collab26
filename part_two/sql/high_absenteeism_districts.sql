-- Find districts with highest chronic absenteeism rates (Total All Students)
-- Useful for cross-state comparison of most-impacted areas

SELECT
    state,
    county,
    district,
    chronic_absent_rate,
    eligible_enrollment
FROM combined_chronic_absenteeism
WHERE entity_level = 'District'
  AND reporting_category = 'TA'
  AND chronic_absent_rate IS NOT NULL
ORDER BY chronic_absent_rate DESC
LIMIT 50;

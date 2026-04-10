-- District-level chronic absenteeism comparison between CA and IL
-- Shows distribution of rates by state for the "Total All Students" category

SELECT
    state,
    COUNT(*) as num_districts,
    ROUND(AVG(chronic_absent_rate), 2) as avg_rate,
    ROUND(MEDIAN(chronic_absent_rate), 2) as median_rate,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY chronic_absent_rate), 2) as p25,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY chronic_absent_rate), 2) as p75,
    ROUND(MIN(chronic_absent_rate), 2) as min_rate,
    ROUND(MAX(chronic_absent_rate), 2) as max_rate
FROM combined_chronic_absenteeism
WHERE entity_level = 'District'
  AND reporting_category = 'TA'
  AND chronic_absent_rate IS NOT NULL
GROUP BY state;

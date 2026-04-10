-- Analyze join match quality between NCES and absenteeism data


SELECT
    c.state,
    COUNT(*) as total_state_rows,
    COUNT(n.nces_enrollment_2122) as nces_matched,
    COUNT(*) - COUNT(n.nces_enrollment_2122) as nces_unmatched,
    ROUND(COUNT(n.nces_enrollment_2122) * 100.0 / COUNT(*), 1) as match_pct,
    STRING_AGG(
        CASE WHEN n.nces_enrollment_2122 IS NULL THEN c.reporting_category END,
        ', '
    ) as unmatched_categories
FROM combined_chronic_absenteeism c
LEFT JOIN nces_sea_enrollment n
    ON c.state = n.state
    AND c.reporting_category = n.reporting_category
WHERE c.entity_level = 'State'
GROUP BY c.state


-- State-level chronic absenteeism comparison between CA and IL
-- Uses the combined table where entity_level is already normalized

SELECT
    reporting_category,
    category_description,
    ROUND(MAX(CASE WHEN state = 'CA' THEN chronic_absent_rate END), 2) as ca_rate,
    ROUND(MAX(CASE WHEN state = 'IL' THEN chronic_absent_rate END), 2) as il_rate,
    ROUND(MAX(CASE WHEN state = 'CA' THEN chronic_absent_rate END) -
          MAX(CASE WHEN state = 'IL' THEN chronic_absent_rate END), 2) as difference
FROM combined_chronic_absenteeism
WHERE entity_level = 'State'
GROUP BY reporting_category, category_description
ORDER BY reporting_category;

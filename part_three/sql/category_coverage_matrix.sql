-- Category coverage across all three data sources


WITH categories AS (
    SELECT DISTINCT reporting_category, category_description
    FROM combined_chronic_absenteeism
),
ca_cats AS (
    SELECT DISTINCT reporting_category FROM combined_chronic_absenteeism WHERE state = 'CA'
),
il_cats AS (
    SELECT DISTINCT reporting_category FROM combined_chronic_absenteeism WHERE state = 'IL'
),
nces_cats AS (
    SELECT DISTINCT reporting_category FROM nces_sea_enrollment
)
SELECT
    c.reporting_category,
    c.category_description,
    CASE WHEN ca.reporting_category IS NOT NULL THEN 'Y' ELSE '' END as in_ca_absenteeism,
    CASE WHEN il.reporting_category IS NOT NULL THEN 'Y' ELSE '' END as in_il_absenteeism,
    CASE WHEN n.reporting_category IS NOT NULL THEN 'Y' ELSE '' END as in_nces_enrollment,
    CASE
        WHEN ca.reporting_category IS NOT NULL
         AND il.reporting_category IS NOT NULL
         AND n.reporting_category IS NOT NULL
        THEN 'FULL 3-WAY'
        WHEN ca.reporting_category IS NOT NULL AND il.reporting_category IS NOT NULL
        THEN 'CA+IL only'
        WHEN n.reporting_category IS NOT NULL
        THEN 'NCES only'
        ELSE 'PARTIAL'
    END as join_status
FROM categories c
LEFT JOIN ca_cats ca ON c.reporting_category = ca.reporting_category
LEFT JOIN il_cats il ON c.reporting_category = il.reporting_category
LEFT JOIN nces_cats n ON c.reporting_category = n.reporting_category
ORDER BY c.reporting_category


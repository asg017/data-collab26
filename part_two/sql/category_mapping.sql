-- category_mapping
-- Full outer join of reporting categories


    WITH ca_cats AS (
        SELECT DISTINCT "Reporting Category" as cat FROM ca_chronic_absenteeism
    ),
    il_cats AS (
        SELECT DISTINCT "Reporting Category" as cat FROM il_chronic_absenteeism_long
    )
    SELECT
        COALESCE(c.cat, '') as ca_category,
        COALESCE(i.cat, '') as il_category,
        CASE
            WHEN c.cat IS NOT NULL AND i.cat IS NOT NULL THEN 'BOTH'
            WHEN c.cat IS NOT NULL THEN 'CA only'
            ELSE 'IL only'
        END as presence
    FROM ca_cats c
    FULL OUTER JOIN il_cats i ON c.cat = i.cat
    ORDER BY COALESCE(c.cat, i.cat)


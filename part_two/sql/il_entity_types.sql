-- il_entity_types
-- Illinois: rows by entity type


    SELECT
        "Type",
        COUNT(*) as row_count,
        COUNT(DISTINCT "Reporting Category") as distinct_categories
    FROM il_chronic_absenteeism_long
    GROUP BY "Type"
    ORDER BY row_count DESC


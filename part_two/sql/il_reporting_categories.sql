-- il_reporting_categories
-- Illinois distinct reporting categories


    SELECT
        "Reporting Category",
        COUNT(*) as row_count,
        ROUND(AVG("ChronicAbsenteeismRate"), 2) as avg_rate
    FROM il_chronic_absenteeism_long
    GROUP BY "Reporting Category"
    ORDER BY "Reporting Category"


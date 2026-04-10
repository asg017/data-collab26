-- ca_reporting_categories
-- California distinct reporting categories


    SELECT
        "Reporting Category",
        COUNT(*) as row_count,
        ROUND(AVG("ChronicAbsenteeismRate"), 2) as avg_rate
    FROM ca_chronic_absenteeism
    GROUP BY "Reporting Category"
    ORDER BY "Reporting Category"


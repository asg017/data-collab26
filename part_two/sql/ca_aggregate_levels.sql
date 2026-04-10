-- ca_aggregate_levels
-- California: rows by aggregate level


    SELECT
        "Aggregate Level",
        CASE "Aggregate Level"
            WHEN 'T' THEN 'State Total'
            WHEN 'C' THEN 'County'
            WHEN 'D' THEN 'District'
            WHEN 'S' THEN 'School'
        END as level_meaning,
        COUNT(*) as row_count,
        COUNT(DISTINCT "Reporting Category") as distinct_categories
    FROM ca_chronic_absenteeism
    GROUP BY "Aggregate Level"
    ORDER BY row_count DESC


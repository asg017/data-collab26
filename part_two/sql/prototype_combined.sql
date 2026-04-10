-- prototype_combined
-- Prototype combined dataset summary


    WITH combined AS (
    -- Prototype combined chronic absenteeism dataset
    WITH ca_normalized AS (
        SELECT
            'CA' as state,
            '2023-24' as academic_year,
            "Aggregate Level" as entity_level,
            "County Name" as county,
            "District Name" as district,
            "School Name" as school,
            "Charter School" as charter_school,
            "Reporting Category" as reporting_category,
            "ChronicAbsenteeismEligibleCumulativeEnrollment" as enrollment,
            "ChronicAbsenteeismCount" as chronic_absent_count,
            "ChronicAbsenteeismRate" as chronic_absent_rate
        FROM ca_chronic_absenteeism
        WHERE "Charter School" = 'All' AND "DASS" = 'All'
    ),
    il_normalized AS (
        SELECT
            'IL' as state,
            '2023-24' as academic_year,
            CASE "Type"
                WHEN 'State' THEN 'T'
                WHEN 'District' THEN 'D'
                WHEN 'School' THEN 'S'
                ELSE "Type"
            END as entity_level,
            "County" as county,
            "District" as district,
            "School Name" as school,
            NULL as charter_school,
            "Reporting Category" as reporting_category,
            NULL::DOUBLE as enrollment,
            NULL::DOUBLE as chronic_absent_count,
            "ChronicAbsenteeismRate" as chronic_absent_rate
        FROM il_chronic_absenteeism_long
    )
    SELECT * FROM ca_normalized
    UNION ALL
    SELECT * FROM il_normalized
)
    SELECT
        state,
        entity_level,
        COUNT(*) as rows,
        COUNT(chronic_absent_rate) as non_null_rates,
        ROUND(AVG(chronic_absent_rate), 2) as avg_rate
    FROM combined
    GROUP BY state, entity_level
    ORDER BY state, entity_level


-- il_data_quality
-- Illinois data quality summary


    SELECT
        COUNT(*) as total_rows,
        COUNT("ChronicAbsenteeismRate") as non_null_rate,
        ROUND(COUNT("ChronicAbsenteeismRate") * 100.0 / COUNT(*), 1) as pct_non_null,
        ROUND(MIN("ChronicAbsenteeismRate"), 2) as min_rate,
        ROUND(MAX("ChronicAbsenteeismRate"), 2) as max_rate,
        ROUND(AVG("ChronicAbsenteeismRate"), 2) as avg_rate,
        ROUND(MEDIAN("ChronicAbsenteeismRate"), 2) as median_rate
    FROM il_chronic_absenteeism_long


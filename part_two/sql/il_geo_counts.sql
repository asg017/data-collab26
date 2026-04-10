-- il_geo_counts
-- Illinois geographic entity counts


    SELECT
        COUNT(DISTINCT "County") as counties,
        COUNT(DISTINCT "District") as districts,
        COUNT(DISTINCT "School Name") as schools
    FROM il_chronic_absenteeism_long
    WHERE "Type" = 'School'


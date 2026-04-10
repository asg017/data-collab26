-- ca_geo_counts
-- California geographic entity counts


    SELECT
        COUNT(DISTINCT "County Name") as counties,
        COUNT(DISTINCT "District Name") as districts,
        COUNT(DISTINCT "School Name") as schools
    FROM ca_chronic_absenteeism
    WHERE "Aggregate Level" = 'S'


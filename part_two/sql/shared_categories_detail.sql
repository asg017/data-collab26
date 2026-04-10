-- shared_categories_detail
-- Categories that exist in BOTH datasets


    WITH ca_cats AS (
        SELECT DISTINCT "Reporting Category" as cat FROM ca_chronic_absenteeism
    ),
    il_cats AS (
        SELECT DISTINCT "Reporting Category" as cat FROM il_chronic_absenteeism_long
    ),
    shared AS (
        SELECT c.cat FROM ca_cats c INNER JOIN il_cats i ON c.cat = i.cat
    )
    SELECT
        s.cat as shared_category,
        CASE s.cat
            WHEN 'GF' THEN 'Gender: Female'
            WHEN 'GM' THEN 'Gender: Male'
            WHEN 'GR1' THEN 'Grade 1'
            WHEN 'GR10' THEN 'Grade 10'
            WHEN 'GR11' THEN 'Grade 11'
            WHEN 'GR12' THEN 'Grade 12'
            WHEN 'GR2' THEN 'Grade 2'
            WHEN 'GR3' THEN 'Grade 3'
            WHEN 'GR4' THEN 'Grade 4'
            WHEN 'GR5' THEN 'Grade 5'
            WHEN 'GR6' THEN 'Grade 6'
            WHEN 'GR7' THEN 'Grade 7'
            WHEN 'GR8' THEN 'Grade 8'
            WHEN 'GR9' THEN 'Grade 9'
            WHEN 'GRK' THEN 'Grade K'
            WHEN 'RA' THEN 'Race: Asian'
            WHEN 'RB' THEN 'Race: Black/African American'
            WHEN 'RH' THEN 'Race: Hispanic/Latino'
            WHEN 'RI' THEN 'Race: American Indian/Alaska Native'
            WHEN 'RP' THEN 'Race: Native Hawaiian/Pacific Islander'
            WHEN 'RT' THEN 'Race: Two or More'
            WHEN 'RW' THEN 'Race: White'
            WHEN 'SD' THEN 'Students with Disabilities'
            WHEN 'SEL' THEN 'English Learners'
            WHEN 'SIEP' THEN 'IEP Students'
            WHEN 'SLI' THEN 'Low Income'
            WHEN 'TA' THEN 'Total (All Students)'
            ELSE s.cat
        END as meaning
    FROM shared s
    ORDER BY s.cat


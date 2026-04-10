-- Create combined chronic absenteeism table (IL + CA)
-- Only includes the 11 shared reporting categories


CREATE OR REPLACE TABLE combined_chronic_absenteeism AS

WITH ca_normalized AS (
    SELECT
        'CA' as state,
        '2023-24' as academic_year,
        CASE "Aggregate Level"
            WHEN 'T' THEN 'State'
            WHEN 'C' THEN 'County'
            WHEN 'D' THEN 'District'
            WHEN 'S' THEN 'School'
        END as entity_level,
        "County Name" as county,
        "District Name" as district,
        "School Name" as school,
        "Reporting Category" as reporting_category,
        CASE "Reporting Category"
            WHEN 'GF' THEN 'Gender: Female'
            WHEN 'GM' THEN 'Gender: Male'
            WHEN 'RA' THEN 'Race: Asian'
            WHEN 'RB' THEN 'Race: Black/African American'
            WHEN 'RH' THEN 'Race: Hispanic/Latino'
            WHEN 'RI' THEN 'Race: American Indian/Alaska Native'
            WHEN 'RP' THEN 'Race: Native Hawaiian/Pacific Islander'
            WHEN 'RT' THEN 'Race: Two or More Races'
            WHEN 'RW' THEN 'Race: White'
            WHEN 'SD' THEN 'Students with Disabilities'
            WHEN 'TA' THEN 'Total (All Students)'
        END as category_description,
        "ChronicAbsenteeismEligibleCumulativeEnrollment" as eligible_enrollment,
        "ChronicAbsenteeismCount" as chronic_absent_count,
        "ChronicAbsenteeismRate" as chronic_absent_rate
    FROM ca_chronic_absenteeism
    WHERE "Charter School" = 'All'
      AND "DASS" = 'All'
      AND "Reporting Category" IN ('GF', 'GM', 'RA', 'RB', 'RH', 'RI', 'RP', 'RT', 'RW', 'SD', 'TA')
),

il_normalized AS (
    SELECT
        'IL' as state,
        '2023-24' as academic_year,
        CASE "Type"
            WHEN 'Statewide' THEN 'State'
            WHEN 'District' THEN 'District'
            WHEN 'School' THEN 'School'
            ELSE "Type"
        END as entity_level,
        "County" as county,
        "District" as district,
        "School Name" as school,
        "Reporting Category" as reporting_category,
        CASE "Reporting Category"
            WHEN 'GF' THEN 'Gender: Female'
            WHEN 'GM' THEN 'Gender: Male'
            WHEN 'RA' THEN 'Race: Asian'
            WHEN 'RB' THEN 'Race: Black/African American'
            WHEN 'RH' THEN 'Race: Hispanic/Latino'
            WHEN 'RI' THEN 'Race: American Indian/Alaska Native'
            WHEN 'RP' THEN 'Race: Native Hawaiian/Pacific Islander'
            WHEN 'RT' THEN 'Race: Two or More Races'
            WHEN 'RW' THEN 'Race: White'
            WHEN 'SD' THEN 'Students with Disabilities'
            WHEN 'TA' THEN 'Total (All Students)'
        END as category_description,
        NULL::DOUBLE as eligible_enrollment,
        NULL::DOUBLE as chronic_absent_count,
        "ChronicAbsenteeismRate" as chronic_absent_rate
    FROM il_chronic_absenteeism_long
    WHERE "Reporting Category" IN ('GF', 'GM', 'RA', 'RB', 'RH', 'RI', 'RP', 'RT', 'RW', 'SD', 'TA')
)

SELECT * FROM ca_normalized
UNION ALL
SELECT * FROM il_normalized


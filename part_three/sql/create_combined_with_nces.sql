-- Combined CA+IL chronic absenteeism with NCES school/district IDs

CREATE TABLE combined_with_nces AS

SELECT
    'CA' as state,
    '06' as fips_code,
    '2023-24' as academic_year,
    'School' as entity_level,
    "County Name" as county,
    "District Name" as district,
    "School Name" as school,
    "Reporting Category" as reporting_category,
    "ChronicAbsenteeismEligibleCumulativeEnrollment" as eligible_enrollment,
    "ChronicAbsenteeismCount" as chronic_absent_count,
    "ChronicAbsenteeismRate" as chronic_absent_rate,
    nces_school_id,
    nces_district_id,
    nces_school_type,
    nces_charter,
    nces_level,
    nces_city,
    nces_zip
FROM ca_with_nces
WHERE "Charter School" = 'All' AND "DASS" = 'All'

UNION ALL

SELECT
    'IL' as state,
    '17' as fips_code,
    '2023-24' as academic_year,
    CASE "Type"
        WHEN 'Statewide' THEN 'State'
        ELSE "Type"
    END as entity_level,
    "County" as county,
    "District" as district,
    "School Name" as school,
    "Reporting Category" as reporting_category,
    NULL::DOUBLE as eligible_enrollment,
    NULL::DOUBLE as chronic_absent_count,
    "ChronicAbsenteeismRate" as chronic_absent_rate,
    nces_school_id,
    nces_district_id,
    nces_school_type,
    nces_charter,
    nces_level,
    nces_city,
    nces_zip
FROM il_with_nces;

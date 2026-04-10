-- ============================================================
-- Crosswalk Queries: Harmonizing CA & OR into comparable form
-- REVISED: Accounts for data dictionary definitions and
-- Oregon website documentation (OAR 411-020-0002)
--
-- Key corrections from initial analysis:
-- 1. Use CA's explicit LTC field instead of guessing from FAC_TYPE_CODE
-- 2. CA "Abuse/Facility Not Self Reported" = failure to report, NOT abuse findings
-- 3. OR Allegation is a fixed dropdown (~90 options), not free text
-- 4. CA records enforcement actions; OR records substantiated findings
-- 5. Abuse categories should NOT be compared across states
-- ============================================================

-- ============================================================
-- Step 1: Source views
-- ============================================================

CREATE OR REPLACE VIEW california_raw AS
SELECT * FROM read_csv('/home/sprite/california.csv',
    header=true, ignore_errors=true, auto_detect=true, strict_mode=false);

CREATE OR REPLACE VIEW oregon_raw AS
SELECT * FROM read_csv('/home/sprite/oregon.csv', header=true, auto_detect=true);

-- ============================================================
-- Step 2: California harmonized
-- Uses the LTC field explicitly (per data dictionary)
-- Excludes Failure to Report and Breach categories (no OR equivalent)
-- Excludes Adverse Event categories (no OR equivalent)
-- ============================================================

CREATE OR REPLACE VIEW california_harmonized AS
SELECT
    'CA' AS state,
    FACID AS facility_id,
    FACILITY_NAME AS facility_name,
    FAC_TYPE_CODE AS facility_type_original,

    -- Facility type crosswalk
    CASE
        WHEN FAC_TYPE_CODE = 'SNF' THEN 'Nursing Facility'
        WHEN FAC_TYPE_CODE IN ('ICF', 'ICFDDH', 'ICFDDN', 'ICFDD') THEN 'Intermediate Care'
        WHEN FAC_TYPE_CODE = 'CLHF' THEN 'Congregate Living'
        WHEN FAC_TYPE_CODE = 'PDHRCF' THEN 'Other LTC'
        ELSE FAC_TYPE_CODE
    END AS facility_type_harmonized,

    VIOLATION_FROM_DATE::DATE AS violation_date,
    extract(year FROM VIOLATION_FROM_DATE)::INT AS violation_year,

    -- Enforcement action type (CA-specific)
    PENALTY_TYPE AS enforcement_type,
    PENALTY_DETAIL AS enforcement_detail,

    -- Severity (CA-specific)
    CLASS_ASSESSED_INITIAL AS severity_class,
    CLASS_ASSESSED_FINAL AS severity_class_final,

    -- Violation category crosswalk (comparable categories only)
    CASE
        WHEN PENALTY_CATEGORY = 'Patient Care' THEN 'Care Quality'
        WHEN PENALTY_CATEGORY = 'Patient Rights' THEN 'Resident Rights'
        WHEN PENALTY_CATEGORY = 'Medication' THEN 'Medication'
        WHEN PENALTY_CATEGORY = 'Staffing' THEN 'Staffing'
        WHEN PENALTY_CATEGORY LIKE 'DHPPD%' THEN 'Staffing (Hours)'
        WHEN PENALTY_CATEGORY = 'Physical Environment' THEN 'Environment/Safety'
        WHEN PENALTY_CATEGORY = 'Dietary' THEN 'Dietary'
        WHEN PENALTY_CATEGORY IN ('Administration', 'Patient Record') THEN 'Administration/Records'
        WHEN PENALTY_CATEGORY = 'Willful Material Falsification'
          OR PENALTY_CATEGORY = 'Willful Material Omission' THEN 'Falsification/Records'
        -- Categories with NO Oregon equivalent:
        WHEN PENALTY_CATEGORY = 'Abuse/Facility Not Self Reported' THEN 'Failure to Self-Report (CA only)'
        WHEN PENALTY_CATEGORY LIKE 'AE%' THEN 'Adverse Event (CA only)'
        WHEN PENALTY_CATEGORY LIKE 'Breach%'
          OR PENALTY_CATEGORY LIKE 'Deliberate breach%' THEN 'Privacy Breach (CA only)'
        WHEN PENALTY_CATEGORY = 'Financial Occurrence/Fac Not Self Reported' THEN 'Failure to Self-Report (CA only)'
        WHEN PENALTY_CATEGORY = 'Problem Transfer' THEN 'Transfer/Discharge'
        WHEN PENALTY_CATEGORY = 'Refusal to Readmit' THEN 'Transfer/Discharge'
        ELSE 'Other'
    END AS violation_category_harmonized,
    PENALTY_CATEGORY AS violation_category_original,

    -- Whether this category has an OR equivalent
    CASE
        WHEN PENALTY_CATEGORY IN (
            'Patient Care', 'Patient Rights', 'Medication', 'Staffing',
            'Physical Environment', 'Dietary', 'Administration', 'Patient Record',
            'Problem Transfer', 'Refusal to Readmit',
            'Willful Material Falsification', 'Willful Material Omission'
        ) OR PENALTY_CATEGORY LIKE 'DHPPD%' THEN true
        ELSE false
    END AS has_or_equivalent,

    -- Financial data (CA-specific)
    TOTAL_AMOUNT_INITIAL AS penalty_amount_initial,
    TOTAL_AMOUNT_DUE_FINAL AS penalty_amount_final,

    -- Other CA-specific
    DEATH_RELATED AS death_related,
    DISPOSITION AS disposition,
    APPEALED AS appealed

FROM california_raw
WHERE LTC = 'LTC'  -- Use explicit LTC field per data dictionary
  AND VIOLATION_FROM_DATE >= '2010-01-01'
  AND VIOLATION_FROM_DATE < '2024-07-01';


-- ============================================================
-- Step 3: Oregon harmonized
-- Allegation is a fixed dropdown (~90 options per OR website)
-- Abuse findings are flagged but kept separate from licensing violations
-- ============================================================

CREATE OR REPLACE VIEW oregon_harmonized AS
SELECT
    'OR' AS state,
    "Provider ID" AS facility_id,
    "Name" AS facility_name,
    "Provider type" AS facility_type_original,

    -- Facility type crosswalk
    CASE
        WHEN "Provider type" = 'NF' THEN 'Nursing Facility'
        WHEN "Provider type" IN ('ALF', 'RCF') THEN 'Residential Care'
        WHEN "Provider type" = 'AFH' THEN 'Adult Foster Home'
        ELSE 'Other'
    END AS facility_type_harmonized,

    "Date" AS violation_date,
    extract(year FROM "Date")::INT AS violation_year,

    -- OR has no enforcement action type -- these are all substantiated findings
    'Substantiated Finding' AS enforcement_type,
    "Report number" AS enforcement_detail,

    -- OR has no severity classification
    NULL AS severity_class,
    NULL AS severity_class_final,

    -- Violation category crosswalk (from fixed dropdown allegations)
    CASE
        -- Medication-related (multiple allegation variants)
        WHEN "Allegation" IN (
            'Failed to provide a safe medication administration system',
            'Failed to administer medication as ordered',
            'Failed to administer ordered medication',
            'Failed to have medication available',
            'Failed to keep medication record current or accurate',
            'Failed to properly secure or store medication',
            'Failed to obtain medication order',
            'Failure to provide a system that prevents theft or misuse of medication'
        ) THEN 'Medication'

        -- Care quality
        WHEN "Allegation" IN (
            'Failed to follow care plan',
            'Failed to properly plan care',
            'Failed to provide service',
            'Failed to intervene when resident''s condition changed',
            'Failed to provide oversight and monitoring of change of condition',
            'Failed to care plan in accordance with assessment',
            'Failed to perform adequate screening or assessment',
            'Failed to provide medical treatment as ordered',
            'Failed to assure timely medical treatment',
            'Failed to assure physician services',
            'Failed to obtain medical order',
            'Failed to obtain appropriate consultation',
            'Failed to provide appropriate pain control',
            'Failed to provide appropriate skin care',
            'Failed to provide peri care',
            'Failed to provide or assist with hygiene',
            'Failed to assist with toileting',
            'Failed to assist with eating',
            'Failed to assist with dressing or grooming',
            'Failed to assist with transfer',
            'Failed to assist with ambulation or mobility',
            'Failed to provide assistive devices',
            'Failed to provide or maintain resident care equipment',
            'Failed to answer call light in a timely manner',
            'Failed to meet the scheduled and unscheduled needs of residents',
            'Failed to provide rehabilitative services',
            'Failed to provide infection control',
            'Failed to provide appropriate activities',
            'Failed to provide social services',
            'Failed to assure dental treatment',
            'Failed to provide inservice',
            'Failed to comply with nursing delegation requirement',
            'Failed to assure resident was safe',
            'Failed to address resident''s behavior'
        ) THEN 'Care Quality'

        -- Resident rights
        WHEN "Allegation" IN (
            'Failed to assure resident rights',
            'Retaliated against resident/complainant'
        ) THEN 'Resident Rights'

        -- Staffing
        WHEN "Allegation" IN (
            'Failed to provide appropriate staffing',
            'Failed to assure a qualified caregiver was present',
            'Failed to assure that a qualified caregiver was present',
            'Failed to hire according to administrative rules',
            'Failed to submit timely or adequate staffing documentation',
            'Failed to properly post and maintain daily staffing documentation',
            'Failed to staff as indicated by ABST',
            'Failed to use an ABST',
            'Failed to update staffing plan based on ABST'
        ) THEN 'Staffing'

        -- Environment/Safety
        WHEN "Allegation" IN (
            'Failed to provide safe environment',
            'Failed to maintain a safe physical environment',
            'Failed to provide a homelike environment',
            'Failed to maintain functional door alarm or call system',
            'Failed to control pests',
            'Failed to provide appropriate housekeeping services',
            'Failed to assure adequate supply or equipment'
        ) THEN 'Environment/Safety'

        -- Dietary
        WHEN "Allegation" IN (
            'Failed to provide a therapeutic diet',
            'Failed to provide proper food/nutrition',
            'Failed to assure proper hydration',
            'Failed to assure food safety',
            'Failed to provide sanitary food service conditions',
            'Failed to assure adequate food supply'
        ) THEN 'Dietary'

        -- Administration/Records
        WHEN "Allegation" IN (
            'Failed to keep resident record current or accurate',
            'Failed to make facility or resident records accessible',
            'Falsified records',
            'Failed to communicate necessary information',
            'Failed to cooperate with an investigation',
            'Failed to obtain a facility license',
            'Failed to obtain an exception or waiver',
            'Failed to demonstrate financial solvency',
            'Failed to report vaccination status',
            'Exceeded license capacity'
        ) THEN 'Administration/Records'

        -- Falls
        WHEN "Allegation" = 'Failed to adequately care plan related to falls' THEN 'Falls'

        -- Transfer/Discharge
        WHEN "Allegation" IN (
            'Failed to comply with move-out, transfer or discharge requirements',
            'Failed to adequately plan discharge',
            'Failed to properly admit or re-admit'
        ) THEN 'Transfer/Discharge'

        -- Reporting
        WHEN "Allegation" IN (
            'Failed to report potential or suspected abuse',
            'Failed to notify family',
            'Failed to notify family of suspected abuse',
            'Failed to investigate injury of unknown origin to rule out abuse'
        ) THEN 'Reporting/Notification'

        -- Abuse-specific allegations (protection failures)
        WHEN "Allegation" IN (
            'Failed to protect resident from financial exploitation',
            'Failed to protect resident from physical abuse',
            'Failed to protect resident from verbal abuse',
            'Failed to protect resident from mental or emotional abuse',
            'Failed to protect resident from inappropriate sexual contact',
            'Failed to protect resident from involuntary seclusion',
            'Failed to protect resident from rough treatment',
            'Failed to protect resident from corporal punishment',
            'Failed to protect resident from rape',
            'Failed to properly use restraint',
            'Failed to use restraint properly'
        ) THEN 'Abuse Protection (OR only)'

        -- Transport
        WHEN "Allegation" = 'Failed to provide transportation for medical or social purposes' THEN 'Care Quality'

        -- Final order compliance
        WHEN "Allegation" = 'Failed to comply with a final order' THEN 'Administration/Records'

        ELSE 'Other'
    END AS violation_category_harmonized,
    "Allegation" AS violation_category_original,

    -- Whether this is an abuse finding (OR-specific concept)
    CASE WHEN "Type" LIKE 'Abuse:%' THEN true ELSE false END AS is_abuse_finding,

    -- Abuse subtype (OR-specific)
    CASE WHEN "Type" LIKE 'Abuse:%' THEN "Type" ELSE NULL END AS abuse_subtype,

    -- Whether this category has a CA equivalent
    CASE
        WHEN "Allegation" IN (
            'Failed to protect resident from financial exploitation',
            'Failed to protect resident from physical abuse',
            'Failed to protect resident from verbal abuse',
            'Failed to protect resident from mental or emotional abuse',
            'Failed to protect resident from inappropriate sexual contact',
            'Failed to protect resident from involuntary seclusion',
            'Failed to protect resident from rough treatment',
            'Failed to protect resident from corporal punishment',
            'Failed to protect resident from rape',
            'Failed to properly use restraint',
            'Failed to use restraint properly'
        ) THEN false
        ELSE true
    END AS has_ca_equivalent,

    -- Financial data not available in OR violations
    NULL::DOUBLE AS penalty_amount_initial,
    NULL::DOUBLE AS penalty_amount_final,

    -- Other (not available)
    NULL AS death_related,
    'Substantiated' AS disposition,
    NULL AS appealed

FROM oregon_raw
WHERE "Date" >= '2010-01-01'
  AND "Date" < '2024-07-01';


-- ============================================================
-- Step 4: Comparison queries (COMPARABLE CATEGORIES ONLY)
-- ============================================================

-- 4a. Annual volume by state (all records, for context)
SELECT state, violation_year, count(*) AS total_records
FROM (SELECT state, violation_year FROM california_harmonized
      UNION ALL
      SELECT state, violation_year FROM oregon_harmonized)
GROUP BY 1, 2
ORDER BY 2, 1;

-- 4b. Annual volume: Nursing Facilities only (best comparison)
SELECT state, violation_year, count(*) AS nf_records
FROM (SELECT state, violation_year FROM california_harmonized
      WHERE facility_type_harmonized = 'Nursing Facility'
      UNION ALL
      SELECT state, violation_year FROM oregon_harmonized
      WHERE facility_type_harmonized = 'Nursing Facility'
      -- Exclude abuse findings for fair comparison
      AND "is_abuse_finding" = false)
GROUP BY 1, 2
ORDER BY 2, 1;

-- 4c. Violation category distribution (COMPARABLE categories only)
--     Excludes CA-only and OR-only categories
SELECT state, violation_category_harmonized,
       count(*) AS violations,
       round(100.0 * count(*) / sum(count(*)) OVER (PARTITION BY state), 1) AS pct
FROM (
    SELECT state, violation_category_harmonized FROM california_harmonized
    WHERE has_or_equivalent = true
    UNION ALL
    SELECT state, violation_category_harmonized FROM oregon_harmonized
    WHERE has_ca_equivalent = true
    AND is_abuse_finding = false  -- exclude abuse findings (no CA equivalent)
)
GROUP BY 1, 2
ORDER BY 1, 4 DESC;

-- 4d. Facility type distribution
SELECT state, facility_type_harmonized,
       count(*) AS violations,
       round(100.0 * count(*) / sum(count(*)) OVER (PARTITION BY state), 1) AS pct
FROM (SELECT state, facility_type_harmonized FROM california_harmonized
      UNION ALL
      SELECT state, facility_type_harmonized FROM oregon_harmonized)
GROUP BY 1, 2
ORDER BY 1, 4 DESC;

-- 4e. Nursing Facility category comparison (cleanest analysis)
SELECT state, violation_category_harmonized,
       count(*) AS violations,
       round(100.0 * count(*) / sum(count(*)) OVER (PARTITION BY state), 1) AS pct
FROM (
    SELECT state, violation_category_harmonized FROM california_harmonized
    WHERE facility_type_harmonized = 'Nursing Facility'
    AND has_or_equivalent = true
    UNION ALL
    SELECT state, violation_category_harmonized FROM oregon_harmonized
    WHERE facility_type_harmonized = 'Nursing Facility'
    AND has_ca_equivalent = true
    AND is_abuse_finding = false
)
GROUP BY 1, 2
ORDER BY 1, 4 DESC;

-- 4f. Top repeat-offender facilities (within each state)
SELECT state, facility_id, facility_name,
       facility_type_harmonized, count(*) AS violations
FROM (SELECT state, facility_id, facility_name, facility_type_harmonized
      FROM california_harmonized
      UNION ALL
      SELECT state, facility_id, facility_name, facility_type_harmonized
      FROM oregon_harmonized)
GROUP BY 1, 2, 3, 4
ORDER BY violations DESC
LIMIT 25;

-- 4g. Oregon: abuse vs licensing violation breakdown by year
SELECT violation_year,
       sum(CASE WHEN is_abuse_finding THEN 1 ELSE 0 END) AS abuse_findings,
       sum(CASE WHEN NOT is_abuse_finding THEN 1 ELSE 0 END) AS licensing_violations,
       round(100.0 * sum(CASE WHEN is_abuse_finding THEN 1 ELSE 0 END) / count(*), 1) AS abuse_pct
FROM oregon_harmonized
GROUP BY 1
ORDER BY 1;

-- 4h. CA-only: enforcement severity and penalty amounts by category
SELECT violation_category_harmonized,
       severity_class,
       count(*) AS cnt,
       round(avg(penalty_amount_final), 0) AS avg_penalty,
       round(sum(penalty_amount_final), 0) AS total_penalties
FROM california_harmonized
WHERE has_or_equivalent = true
GROUP BY 1, 2
ORDER BY 1, 2;

-- 4i. Records with no cross-state equivalent (what gets excluded)
SELECT state, violation_category_harmonized, count(*) AS excluded_records
FROM (
    SELECT state, violation_category_harmonized FROM california_harmonized
    WHERE has_or_equivalent = false
    UNION ALL
    SELECT state, violation_category_harmonized FROM oregon_harmonized
    WHERE has_ca_equivalent = false
)
GROUP BY 1, 2
ORDER BY 1, 3 DESC;

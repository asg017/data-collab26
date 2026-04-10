-- ============================================================
-- Exploration Queries: California & Oregon Violation Datasets
-- REVISED with data dictionary and Oregon website definitions
--
-- Run with: python3 -c "import duckdb; print(duckdb.connect().execute(open('02_exploration_queries.sql').read()).fetchall())"
-- Or load into DuckDB CLI
-- ============================================================

CREATE OR REPLACE VIEW california AS
SELECT * FROM read_csv('/home/sprite/california.csv',
    header=true, ignore_errors=true, auto_detect=true, strict_mode=false);

CREATE OR REPLACE VIEW oregon AS
SELECT * FROM read_csv('/home/sprite/oregon.csv', header=true, auto_detect=true);

-- ============================================================
-- 1. Basic stats
-- ============================================================

SELECT 'California' AS state, count(*) AS total_rows,
       count(DISTINCT FACID) AS distinct_facilities,
       min(VIOLATION_FROM_DATE)::DATE AS earliest,
       max(VIOLATION_FROM_DATE)::DATE AS latest,
       count(CASE WHEN LTC = 'LTC' THEN 1 END) AS ltc_rows,
       count(CASE WHEN LTC = 'Non-LTC' THEN 1 END) AS non_ltc_rows
FROM california;

SELECT 'Oregon' AS state, count(*) AS total_rows,
       count(DISTINCT "Provider ID") AS distinct_providers,
       min("Date") AS earliest,
       max("Date") AS latest,
       count(CASE WHEN "Type" = 'Licensing Violation' THEN 1 END) AS licensing_violations,
       count(CASE WHEN "Type" LIKE 'Abuse:%' THEN 1 END) AS abuse_findings
FROM oregon;

-- ============================================================
-- 2. CA: Enforcement action types with HSC references
--    (per data dictionary: PENALTY_DETAIL has HSC codes)
-- ============================================================

SELECT PENALTY_TYPE, PENALTY_DETAIL, CLASS_ASSESSED_INITIAL,
       count(*) AS cnt,
       round(avg(TOTAL_AMOUNT_DUE_FINAL), 0) AS avg_penalty,
       round(sum(TOTAL_AMOUNT_DUE_FINAL), 0) AS total_penalties
FROM california
WHERE LTC = 'LTC'
GROUP BY 1, 2, 3
ORDER BY 1, cnt DESC;

-- ============================================================
-- 3. CA: LTC violations by category and year (2010+)
-- ============================================================

SELECT extract(year FROM VIOLATION_FROM_DATE)::INT AS year,
       PENALTY_CATEGORY,
       count(*) AS violations
FROM california
WHERE LTC = 'LTC'
  AND VIOLATION_FROM_DATE >= '2010-01-01'
  AND VIOLATION_FROM_DATE < '2024-07-01'
GROUP BY 1, 2
ORDER BY 1, 3 DESC;

-- ============================================================
-- 4. OR: All substantiated findings by Type and Allegation
--    (Allegation is a fixed dropdown per OR website, not free text)
-- ============================================================

SELECT "Type", "Allegation", count(*) AS cnt
FROM oregon
GROUP BY 1, 2
ORDER BY 1, 3 DESC;

-- ============================================================
-- 5. OR: Abuse findings by subtype and year
--    (Abuse defined under OAR 411-020-0002)
-- ============================================================

SELECT extract(year FROM "Date")::INT AS year,
       "Type" AS abuse_subtype,
       count(*) AS findings
FROM oregon
WHERE "Type" LIKE 'Abuse:%'
GROUP BY 1, 2
ORDER BY 1, 3 DESC;

-- ============================================================
-- 6. CA: Top LTC facilities by enforcement actions (2010+)
--    (FACID links to other CDPH open data files per dictionary)
-- ============================================================

SELECT FACID, FACILITY_NAME, FAC_TYPE_CODE,
       count(*) AS enforcement_actions,
       count(CASE WHEN CLASS_ASSESSED_INITIAL IN ('A', 'AA') THEN 1 END) AS serious_actions,
       round(sum(TOTAL_AMOUNT_DUE_FINAL), 0) AS total_penalties
FROM california
WHERE LTC = 'LTC'
  AND VIOLATION_FROM_DATE >= '2010-01-01'
GROUP BY 1, 2, 3
ORDER BY enforcement_actions DESC
LIMIT 25;

-- ============================================================
-- 7. OR: Top providers by violation count
-- ============================================================

SELECT "Provider ID", "Name", "Provider type",
       count(*) AS total_findings,
       count(CASE WHEN "Type" = 'Licensing Violation' THEN 1 END) AS licensing,
       count(CASE WHEN "Type" LIKE 'Abuse:%' THEN 1 END) AS abuse
FROM oregon
GROUP BY 1, 2, 3
ORDER BY total_findings DESC
LIMIT 25;

-- ============================================================
-- 8. CA: Death-related investigations (per dictionary:
--    "related to the death of at least one patient")
-- ============================================================

SELECT extract(year FROM VIOLATION_FROM_DATE)::INT AS year,
       PENALTY_CATEGORY,
       count(*) AS death_related_actions
FROM california
WHERE DEATH_RELATED = 'Y'
  AND LTC = 'LTC'
  AND VIOLATION_FROM_DATE >= '2010-01-01'
GROUP BY 1, 2
ORDER BY 1, 3 DESC;

-- ============================================================
-- 9. CA: Appeal outcomes (per dictionary: enforcement actions
--    may be appealed to court or administrative hearing)
-- ============================================================

SELECT CLASS_ASSESSED_INITIAL, CLASS_ASSESSED_FINAL,
       count(*) AS cnt,
       round(avg(TOTAL_AMOUNT_INITIAL), 0) AS avg_initial,
       round(avg(TOTAL_AMOUNT_DUE_FINAL), 0) AS avg_final
FROM california
WHERE LTC = 'LTC'
  AND APPEALED = true
GROUP BY 1, 2
ORDER BY cnt DESC;

-- ============================================================
-- 10. CA: Complaint-driven vs survey-driven enforcement
--     (per dictionary: blank INTAKEID_ALL = relicensure/recert visit)
-- ============================================================

SELECT
    CASE WHEN INTAKEID_ALL IS NOT NULL AND INTAKEID_ALL != ''
         THEN 'Complaint-driven'
         ELSE 'Survey/Relicensure'
    END AS source,
    count(*) AS cnt,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM california
WHERE LTC = 'LTC'
  AND VIOLATION_FROM_DATE >= '2010-01-01'
GROUP BY 1;

-- ============================================================
-- 11. OR: Provider type breakdown with abuse rates
--     (NF is federally regulated; ALF/RCF/AFH are state-licensed
--      per Oregon website; AFH has Class 1/2/3 system)
-- ============================================================

SELECT "Provider type",
       count(*) AS total,
       count(CASE WHEN "Type" = 'Licensing Violation' THEN 1 END) AS licensing,
       count(CASE WHEN "Type" LIKE 'Abuse:%' THEN 1 END) AS abuse,
       round(100.0 * count(CASE WHEN "Type" LIKE 'Abuse:%' THEN 1 END) / count(*), 1) AS abuse_pct
FROM oregon
GROUP BY 1
ORDER BY total DESC;

"""
03_create_combined_dataset.py
Creates the actual combined chronic absenteeism dataset from IL + CA,
using only the categories that exist in both states.

Exports to both DuckDB table and CSV.
"""

import duckdb
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SQL_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')
DB_PATH = os.path.join(DATA_DIR, 'education.duckdb')

con = duckdb.connect(DB_PATH)

# ============================================================================
# Create the combined table with only shared reporting categories
# ============================================================================

# These 11 categories exist in both datasets
SHARED_CATEGORIES = [
    'GF',   # Gender: Female
    'GM',   # Gender: Male
    'RA',   # Race: Asian
    'RB',   # Race: Black/African American
    'RH',   # Race: Hispanic/Latino
    'RI',   # Race: American Indian/Alaska Native
    'RP',   # Race: Native Hawaiian/Pacific Islander
    'RT',   # Race: Two or More Races
    'RW',   # Race: White
    'SD',   # Students with Disabilities
    'TA',   # Total (All Students)
]

shared_list = "', '".join(SHARED_CATEGORIES)

sql = f"""
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
      AND "Reporting Category" IN ('{shared_list}')
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
    WHERE "Reporting Category" IN ('{shared_list}')
)

SELECT * FROM ca_normalized
UNION ALL
SELECT * FROM il_normalized
"""

print("Creating combined table...")
con.execute(sql)

# Save the SQL
with open(os.path.join(SQL_DIR, 'create_combined_table.sql'), 'w') as f:
    f.write(f"-- Create combined chronic absenteeism table (IL + CA)\n-- Only includes the 11 shared reporting categories\n\n{sql}\n")

# Summary stats
print("\n=== Combined Table Summary ===")
result = con.execute("""
    SELECT
        state,
        entity_level,
        COUNT(*) as rows,
        COUNT(chronic_absent_rate) as with_rate,
        ROUND(AVG(chronic_absent_rate), 2) as avg_rate,
        ROUND(MEDIAN(chronic_absent_rate), 2) as median_rate
    FROM combined_chronic_absenteeism
    GROUP BY state, entity_level
    ORDER BY state, entity_level
""").fetchdf()
print(result.to_string())

# State-level comparison
print("\n=== State-Level Comparison by Category ===")
comparison = con.execute("""
    SELECT
        reporting_category,
        category_description,
        ROUND(MAX(CASE WHEN state = 'CA' THEN chronic_absent_rate END), 2) as ca_rate,
        ROUND(MAX(CASE WHEN state = 'IL' THEN chronic_absent_rate END), 2) as il_rate,
        ROUND(MAX(CASE WHEN state = 'CA' THEN chronic_absent_rate END) -
              MAX(CASE WHEN state = 'IL' THEN chronic_absent_rate END), 2) as difference
    FROM combined_chronic_absenteeism
    WHERE entity_level = 'State'
    GROUP BY reporting_category, category_description
    ORDER BY reporting_category
""").fetchdf()
print(comparison.to_string())

# Export to CSV
export_path = os.path.join(DATA_DIR, 'combined_chronic_absenteeism.csv')
con.execute(f"COPY combined_chronic_absenteeism TO '{export_path}' (HEADER, DELIMITER ',')")
total = con.execute("SELECT COUNT(*) FROM combined_chronic_absenteeism").fetchone()[0]
print(f"\nExported {total:,} rows to {export_path}")

con.close()
print("Done!")

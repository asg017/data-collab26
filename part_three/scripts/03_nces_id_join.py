"""
03_nces_id_join.py

Join the NCES CCD School Directory to CA and IL chronic absenteeism data,
adding NCESSCH (school) and LEAID (district) federal IDs.

Join keys discovered:
  CA Schools:  CA School Code (7-digit) = CCD ccd_school_id (from ST_SCHID)
  CA Districts: County(2)+District(5) = CCD ccd_district_id (from ST_SCHID)
  IL Schools:  RCDTS (15-char) = CCD numeric tail of ST_SCHID
  IL Districts: RCDTS (15-char) = CCD school numeric_tail[:11] + '0000'
"""

import duckdb
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PART_TWO_DB = os.path.join(os.path.dirname(__file__), '..', '..', 'part_two', 'data', 'education.duckdb')
DB_PATH = os.path.join(DATA_DIR, 'part_three.duckdb')
SQL_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')

# ============================================================================
# 1. Load CCD Directory
# ============================================================================
print("Loading CCD Directory...")
ccd = pd.read_csv(
    os.path.join(DATA_DIR, 'ccd_directory.csv'), dtype=str,
    usecols=['SCHOOL_YEAR', 'ST', 'FIPST', 'SCH_NAME', 'LEA_NAME',
             'ST_LEAID', 'LEAID', 'ST_SCHID', 'NCESSCH', 'SCHID',
             'MCITY', 'MSTATE', 'MZIP', 'SCH_TYPE_TEXT', 'CHARTER_TEXT',
             'LEVEL', 'SY_STATUS_TEXT', 'GSLO', 'GSHI']
)
print(f"  Total CCD schools: {len(ccd):,}")

# ============================================================================
# 2. Prepare CA join table
# ============================================================================
print("\nPreparing CA join keys...")
ca_ccd = ccd[ccd['ST'] == 'CA'].copy()
ca_ccd['ccd_district_id'] = ca_ccd['ST_SCHID'].str.replace('CA-', '').str.split('-').str[0]
ca_ccd['ccd_school_id'] = ca_ccd['ST_SCHID'].str.replace('CA-', '').str.split('-').str[1]

# Build full CDS key: district_7 + school_7 (= county2 + district5 + school7 = 14 chars)
ca_ccd['cds_14'] = ca_ccd['ccd_district_id'] + ca_ccd['ccd_school_id']

# School-level lookup (deduplicated on full CDS, not just school code)
ca_school_lookup = ca_ccd[['cds_14', 'ccd_school_id', 'ccd_district_id', 'NCESSCH', 'LEAID',
                            'SCH_NAME', 'LEA_NAME', 'SCH_TYPE_TEXT', 'CHARTER_TEXT',
                            'LEVEL', 'SY_STATUS_TEXT', 'MCITY', 'MZIP']].copy()
ca_school_lookup = ca_school_lookup.drop_duplicates(subset='cds_14')

# District-level lookup
ca_district_lookup = ca_ccd[['ccd_district_id', 'LEAID', 'LEA_NAME']].drop_duplicates(subset='ccd_district_id')

print(f"  CA school lookup: {len(ca_school_lookup):,} entries")
print(f"  CA district lookup: {len(ca_district_lookup):,} entries")

# ============================================================================
# 3. Prepare IL join table
# ============================================================================
print("\nPreparing IL join keys...")
il_ccd = ccd[ccd['ST'] == 'IL'].copy()
il_ccd['rcdts'] = il_ccd['ST_SCHID'].str.split('-').str[-1]

# School-level lookup
il_school_lookup = il_ccd[['rcdts', 'NCESSCH', 'LEAID',
                            'SCH_NAME', 'LEA_NAME', 'SCH_TYPE_TEXT', 'CHARTER_TEXT',
                            'LEVEL', 'SY_STATUS_TEXT', 'MCITY', 'MZIP']].copy()
il_school_lookup = il_school_lookup.drop_duplicates(subset='rcdts')

# District-level lookup: district RCDTS = school RCDTS[:11] + '0000'
il_ccd['district_rcdts'] = il_ccd['rcdts'].str[:11] + '0000'
il_district_lookup = il_ccd[['district_rcdts', 'LEAID', 'LEA_NAME']].drop_duplicates(subset='district_rcdts')

print(f"  IL school lookup: {len(il_school_lookup):,} entries")
print(f"  IL district lookup: {len(il_district_lookup):,} entries")

# ============================================================================
# 4. Load into DuckDB and perform joins
# ============================================================================
print(f"\nLoading into DuckDB...")
con = duckdb.connect(DB_PATH)

# Drop old tables if re-running
for t in ['ccd_directory', 'ca_school_lookup', 'ca_district_lookup',
          'il_school_lookup', 'il_district_lookup',
          'ca_with_nces', 'il_with_nces', 'combined_with_nces']:
    con.execute(f"DROP TABLE IF EXISTS {t}")

# Load lookups
con.execute("CREATE TABLE ca_school_lookup AS SELECT * FROM ca_school_lookup")
con.execute("CREATE TABLE ca_district_lookup AS SELECT * FROM ca_district_lookup")
con.execute("CREATE TABLE il_school_lookup AS SELECT * FROM il_school_lookup")
con.execute("CREATE TABLE il_district_lookup AS SELECT * FROM il_district_lookup")

# Make sure we have the absenteeism tables
tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
if 'ca_chronic_absenteeism' not in tables:
    con.execute(f"ATTACH '{PART_TWO_DB}' AS part_two (READ_ONLY)")
    con.execute("CREATE TABLE ca_chronic_absenteeism AS SELECT * FROM part_two.ca_chronic_absenteeism")
    con.execute("CREATE TABLE il_chronic_absenteeism_long AS SELECT * FROM part_two.il_chronic_absenteeism_long")
    con.execute("DETACH part_two")

# ============================================================================
# 5. Join CA absenteeism → NCES IDs
# ============================================================================
print("\n=== Joining CA schools to NCES IDs ===")

ca_join_sql = """
CREATE TABLE ca_with_nces AS
SELECT
    a.*,
    s.NCESSCH as nces_school_id,
    s.LEAID as nces_district_id,
    s.SCH_TYPE_TEXT as nces_school_type,
    s.CHARTER_TEXT as nces_charter,
    s.LEVEL as nces_level,
    s.SY_STATUS_TEXT as nces_status,
    s.MCITY as nces_city,
    s.MZIP as nces_zip
FROM ca_chronic_absenteeism a
LEFT JOIN ca_school_lookup s
    ON (a."County Code" || a."District Code" || a."School Code") = s.cds_14
WHERE a."Aggregate Level" = 'S'
"""
con.execute(ca_join_sql)

ca_total = con.execute("SELECT COUNT(*) FROM ca_with_nces").fetchone()[0]
ca_matched = con.execute("SELECT COUNT(*) FROM ca_with_nces WHERE nces_school_id IS NOT NULL").fetchone()[0]
ca_schools_total = con.execute("""SELECT COUNT(DISTINCT "County Code" || "District Code" || "School Code") FROM ca_with_nces""").fetchone()[0]
ca_schools_matched = con.execute("""SELECT COUNT(DISTINCT "County Code" || "District Code" || "School Code") FROM ca_with_nces WHERE nces_school_id IS NOT NULL""").fetchone()[0]
ca_schools_unmatched = ca_schools_total - ca_schools_matched

print(f"  Total rows: {ca_total:,}")
print(f"  Rows with NCES match: {ca_matched:,} ({ca_matched*100/ca_total:.1f}%)")
print(f"  Unique schools (by full CDS): {ca_schools_total:,}")
print(f"  Schools with NCES ID: {ca_schools_matched:,} ({ca_schools_matched*100/ca_schools_total:.1f}%)")
print(f"  Schools without NCES ID: {ca_schools_unmatched:,}")

# ============================================================================
# 6. Join IL absenteeism → NCES IDs
# ============================================================================
print("\n=== Joining IL schools to NCES IDs ===")

il_school_join_sql = """
CREATE TABLE il_with_nces AS
SELECT
    a.*,
    CASE
        WHEN a."Type" = 'School' THEN s.NCESSCH
        ELSE NULL
    END as nces_school_id,
    CASE
        WHEN a."Type" = 'School' THEN s.LEAID
        WHEN a."Type" = 'District' THEN d.LEAID
        ELSE NULL
    END as nces_district_id,
    s.SCH_TYPE_TEXT as nces_school_type,
    s.CHARTER_TEXT as nces_charter,
    s.LEVEL as nces_level,
    s.SY_STATUS_TEXT as nces_status,
    s.MCITY as nces_city,
    s.MZIP as nces_zip
FROM il_chronic_absenteeism_long a
LEFT JOIN il_school_lookup s
    ON a."RCDTS" = s.rcdts AND a."Type" = 'School'
LEFT JOIN il_district_lookup d
    ON a."RCDTS" = d.district_rcdts AND a."Type" = 'District'
"""
con.execute(il_school_join_sql)

il_total = con.execute("SELECT COUNT(*) FROM il_with_nces WHERE \"Type\" = 'School'").fetchone()[0]
il_matched = con.execute("SELECT COUNT(*) FROM il_with_nces WHERE \"Type\" = 'School' AND nces_school_id IS NOT NULL").fetchone()[0]
il_schools_total = con.execute("SELECT COUNT(DISTINCT \"RCDTS\") FROM il_with_nces WHERE \"Type\" = 'School'").fetchone()[0]
il_schools_matched = con.execute("SELECT COUNT(DISTINCT \"RCDTS\") FROM il_with_nces WHERE \"Type\" = 'School' AND nces_school_id IS NOT NULL").fetchone()[0]

print(f"  School rows: {il_total:,}")
print(f"  Rows with NCES match: {il_matched:,} ({il_matched*100/il_total:.1f}%)")
print(f"  Unique schools: {il_schools_total:,}")
print(f"  Schools with NCES ID: {il_schools_matched:,} ({il_schools_matched*100/il_schools_total:.1f}%)")

il_d_total = con.execute("SELECT COUNT(DISTINCT \"RCDTS\") FROM il_with_nces WHERE \"Type\" = 'District'").fetchone()[0]
il_d_matched = con.execute("SELECT COUNT(DISTINCT \"RCDTS\") FROM il_with_nces WHERE \"Type\" = 'District' AND nces_district_id IS NOT NULL").fetchone()[0]
print(f"  Districts: {il_d_total:,}, with LEAID: {il_d_matched:,} ({il_d_matched*100/il_d_total:.1f}%)")

# ============================================================================
# 7. Build unified combined table with NCES IDs
# ============================================================================
print("\n=== Building combined table with NCES IDs ===")

combined_sql = """
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
FROM il_with_nces
"""
con.execute(combined_sql)

total = con.execute("SELECT COUNT(*) FROM combined_with_nces").fetchone()[0]
with_nces = con.execute("SELECT COUNT(*) FROM combined_with_nces WHERE nces_school_id IS NOT NULL OR nces_district_id IS NOT NULL").fetchone()[0]
print(f"  Total rows: {total:,}")
print(f"  With any NCES ID: {with_nces:,} ({with_nces*100/total:.1f}%)")

# Summary by state
print("\n=== Summary by state and entity level ===")
summary = con.execute("""
    SELECT
        state, entity_level,
        COUNT(*) as total_rows,
        COUNT(nces_school_id) as with_school_id,
        COUNT(nces_district_id) as with_district_id,
        ROUND(COUNT(nces_school_id) * 100.0 / COUNT(*), 1) as school_match_pct,
        ROUND(COUNT(nces_district_id) * 100.0 / COUNT(*), 1) as district_match_pct
    FROM combined_with_nces
    GROUP BY state, entity_level
    ORDER BY state, entity_level
""").fetchdf()
print(summary.to_string())

# ============================================================================
# 8. Unmatched analysis
# ============================================================================
print("\n=== CA unmatched schools (sample) ===")
unmatched_ca = con.execute("""
    SELECT DISTINCT "School Name", "District Name", "County Code", "District Code", "School Code",
           "County Code" || "District Code" || "School Code" as full_cds
    FROM ca_with_nces
    WHERE nces_school_id IS NULL
    LIMIT 20
""").fetchdf()
print(unmatched_ca.to_string())
print(f"\nTotal unmatched CDS codes: {ca_schools_unmatched}")

print(f"\n=== IL unmatched schools (sample) ===")
unmatched_il = con.execute("""
    SELECT DISTINCT "School Name", "District", "RCDTS"
    FROM il_with_nces
    WHERE "Type" = 'School' AND nces_school_id IS NULL
    LIMIT 15
""").fetchdf()
print(unmatched_il.to_string())

# ============================================================================
# 9. Export
# ============================================================================
export_path = os.path.join(DATA_DIR, 'combined_with_nces_ids.csv')
con.execute(f"COPY combined_with_nces TO '{export_path}' (HEADER, DELIMITER ',')")
print(f"\nExported to {export_path}")

# Save SQL
with open(os.path.join(SQL_DIR, 'create_combined_with_nces.sql'), 'w') as f:
    f.write("-- Combined CA+IL chronic absenteeism with NCES school/district IDs\n\n")
    f.write(combined_sql.strip() + ";\n")

# ============================================================================
# 10. Sample of the enriched data
# ============================================================================
print("\n=== Sample: Combined data with NCES IDs ===")
sample = con.execute("""
    SELECT state, school, district, reporting_category,
           chronic_absent_rate, nces_school_id, nces_district_id,
           nces_level, nces_charter
    FROM combined_with_nces
    WHERE nces_school_id IS NOT NULL
      AND reporting_category = 'TA'
      AND chronic_absent_rate IS NOT NULL
    ORDER BY chronic_absent_rate DESC
    LIMIT 10
""").fetchdf()
print(sample.to_string())

con.close()
print("\nDone!")

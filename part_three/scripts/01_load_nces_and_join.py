"""
01_load_nces_and_join.py

Load the NCES CCD SEA-level enrollment data and join it to the CA/IL
chronic absenteeism datasets from part_two.

The NCES file (ccd_sea_052_2122_l_1a_071722.csv) is:
  - Common Core of Data (CCD)
  - State Education Agency (SEA) level — NOT school/district level
  - Membership/enrollment counts (file type 052)
  - School year 2021-22
  - Contains enrollment by state × grade × race/ethnicity × sex

Join strategy:
  We map NCES demographic categories to the reporting category codes used
  in our CA/IL chronic absenteeism data, then join at the STATE level to
  enrich absenteeism rates with federal enrollment counts.

Key challenge:
  - NCES data is 2021-22; our absenteeism data is 2023-24 (2-year gap)
  - NCES has no school/district IDs in this file (SEA-level only)
  - Category granularity differs (NCES has race×sex×grade; our data has
    race OR sex OR grade separately)
"""

import duckdb
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PART_TWO_DB = os.path.join(os.path.dirname(__file__), '..', '..', 'part_two', 'data', 'education.duckdb')
DB_PATH = os.path.join(DATA_DIR, 'part_three.duckdb')
SQL_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')
os.makedirs(SQL_DIR, exist_ok=True)

# ============================================================================
# 1. Load NCES data
# ============================================================================
print("Loading NCES CCD SEA enrollment data...")
nces = pd.read_csv(os.path.join(DATA_DIR, 'nces_ccd_crosswalk.csv'), dtype=str)
print(f"  Total rows: {len(nces):,}")
print(f"  States/territories: {nces['ST'].nunique()}")

# Clean STUDENT_COUNT
nces['STUDENT_COUNT'] = pd.to_numeric(nces['STUDENT_COUNT'], errors='coerce')

# ============================================================================
# 2. Build aggregate views from the NCES granular data
# ============================================================================

# Filter to CA and IL only
nces_ca_il = nces[nces['ST'].isin(['CA', 'IL'])].copy()
print(f"  CA+IL rows: {len(nces_ca_il):,}")

# The granular data has race × sex × grade crossed.
# We need to aggregate to match our reporting categories:
#   TA = total all students
#   GM/GF = by sex only (sum across race and grade)
#   RA/RB/RH/etc = by race only (sum across sex and grade)
#   SD = students with disabilities (NOT available in NCES SEA file)

# --- STRATEGY ---
# Use the pre-computed subtotals in the file:
#   "Derived - Subtotal by Race/Ethnicity and Sex minus Adult Education Count"
#     → gives race × sex totals (summed across grades)
#   "Subtotal 4 - By Grade"
#     → gives grade totals (summed across race and sex)
#   "Derived - Education Unit Total minus Adult Education Count"
#     → gives grand total

# ============================================================================
# 3. Create mapping tables
# ============================================================================

# NCES Race → our reporting category codes
RACE_MAP = {
    'American Indian or Alaska Native': 'RI',
    'Asian': 'RA',
    'Black or African American': 'RB',
    'Hispanic/Latino': 'RH',
    'Native Hawaiian or Other Pacific Islander': 'RP',
    'Two or more races': 'RT',
    'White': 'RW',
}

SEX_MAP = {
    'Female': 'GF',
    'Male': 'GM',
}

GRADE_MAP = {
    'Kindergarten': 'GRK',
    'Grade 1': 'GR1',
    'Grade 2': 'GR2',
    'Grade 3': 'GR3',
    'Grade 4': 'GR4',
    'Grade 5': 'GR5',
    'Grade 6': 'GR6',
    'Grade 7': 'GR7',
    'Grade 8': 'GR8',
    'Grade 9': 'GR9',
    'Grade 10': 'GR10',
    'Grade 11': 'GR11',
    'Grade 12': 'GR12',
    'Pre-Kindergarten': 'GRPK',
}

# ============================================================================
# 4. Build aggregated NCES enrollment by reporting category
# ============================================================================
print("\nAggregating NCES enrollment by reporting category...")

records = []

for state in ['CA', 'IL']:
    st_data = nces_ca_il[nces_ca_il['ST'] == state]
    fipst = st_data['FIPST'].iloc[0]
    state_name = st_data['STATENAME'].iloc[0]

    # --- Grand total (TA) ---
    total_rows = st_data[st_data['TOTAL_INDICATOR'].str.contains('Derived - Education Unit Total')]
    if len(total_rows) > 0:
        total_enroll = total_rows['STUDENT_COUNT'].sum()
        records.append({
            'state': state,
            'fipst': fipst,
            'state_name': state_name,
            'reporting_category': 'TA',
            'category_description': 'Total (All Students)',
            'nces_enrollment_2122': total_enroll,
            'nces_join_method': 'Education Unit Total minus Adult Ed',
        })

    # --- By sex (GF, GM) ---
    # Sum the race/sex subtotals across races for each sex
    race_sex_rows = st_data[st_data['TOTAL_INDICATOR'].str.contains('Derived - Subtotal by Race')]
    for sex_label, sex_code in SEX_MAP.items():
        sex_rows = race_sex_rows[race_sex_rows['SEX'] == sex_label]
        if len(sex_rows) > 0:
            enrollment = sex_rows['STUDENT_COUNT'].sum()
            records.append({
                'state': state,
                'fipst': fipst,
                'state_name': state_name,
                'reporting_category': sex_code,
                'category_description': f'Gender: {sex_label}',
                'nces_enrollment_2122': enrollment,
                'nces_join_method': f'Sum of race/sex subtotals where SEX={sex_label}',
            })

    # --- By race (RA, RB, RH, etc.) ---
    # Sum the race/sex subtotals across sexes for each race
    for race_label, race_code in RACE_MAP.items():
        race_rows = race_sex_rows[race_sex_rows['RACE_ETHNICITY'] == race_label]
        if len(race_rows) > 0:
            enrollment = race_rows['STUDENT_COUNT'].sum()
            records.append({
                'state': state,
                'fipst': fipst,
                'state_name': state_name,
                'reporting_category': race_code,
                'category_description': f'Race: {race_label}',
                'nces_enrollment_2122': enrollment,
                'nces_join_method': f'Sum of race/sex subtotals where RACE={race_label}',
            })

    # --- By grade (GRK, GR1, GR2, etc.) ---
    grade_rows = st_data[st_data['TOTAL_INDICATOR'].str.contains('Subtotal 4 - By Grade')]
    for grade_label, grade_code in GRADE_MAP.items():
        gr = grade_rows[grade_rows['GRADE'] == grade_label]
        if len(gr) > 0:
            enrollment = gr['STUDENT_COUNT'].sum()
            records.append({
                'state': state,
                'fipst': fipst,
                'state_name': state_name,
                'reporting_category': grade_code,
                'category_description': f'Grade: {grade_label}',
                'nces_enrollment_2122': enrollment,
                'nces_join_method': f'Grade subtotal where GRADE={grade_label}',
            })

nces_agg = pd.DataFrame(records)
print(f"  Aggregated NCES records: {len(nces_agg)}")
print(nces_agg.to_string())

# ============================================================================
# 5. Load into DuckDB alongside part_two data
# ============================================================================
print(f"\nLoading into DuckDB at {DB_PATH}...")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

con = duckdb.connect(DB_PATH)

# Load the NCES aggregated data
con.execute("CREATE TABLE nces_sea_enrollment AS SELECT * FROM nces_agg")

# Load the full NCES raw data
con.execute("CREATE TABLE nces_raw AS SELECT * FROM nces")

# Attach part_two database to pull in existing tables
con.execute(f"ATTACH '{PART_TWO_DB}' AS part_two (READ_ONLY)")
con.execute("CREATE TABLE ca_chronic_absenteeism AS SELECT * FROM part_two.ca_chronic_absenteeism")
con.execute("CREATE TABLE il_chronic_absenteeism_long AS SELECT * FROM part_two.il_chronic_absenteeism_long")
con.execute("CREATE TABLE combined_chronic_absenteeism AS SELECT * FROM part_two.combined_chronic_absenteeism")
con.execute("DETACH part_two")

print("  Tables loaded.")

# ============================================================================
# 6. Join: Enrich state-level absenteeism with NCES enrollment
# ============================================================================
print("\n=== Joining NCES enrollment to state-level absenteeism ===")

join_sql = """
CREATE TABLE state_absenteeism_with_nces AS
SELECT
    c.state,
    c.academic_year as absenteeism_year,
    n.state_name as nces_state_name,
    n.fipst as nces_fips_code,
    '2021-22' as nces_enrollment_year,
    c.reporting_category,
    c.category_description,
    c.chronic_absent_rate,
    c.eligible_enrollment as state_eligible_enrollment_2324,
    n.nces_enrollment_2122,
    n.nces_join_method,
    CASE
        WHEN c.eligible_enrollment IS NOT NULL AND n.nces_enrollment_2122 IS NOT NULL
        THEN ROUND((c.eligible_enrollment - n.nces_enrollment_2122) * 100.0
                    / n.nces_enrollment_2122, 2)
        ELSE NULL
    END as enrollment_change_pct
FROM combined_chronic_absenteeism c
LEFT JOIN nces_sea_enrollment n
    ON c.state = n.state
    AND c.reporting_category = n.reporting_category
WHERE c.entity_level = 'State'
ORDER BY c.state, c.reporting_category
"""

con.execute(join_sql)

result = con.execute("SELECT * FROM state_absenteeism_with_nces").fetchdf()
print(result.to_string())

# Save the join SQL
with open(os.path.join(SQL_DIR, 'join_nces_to_absenteeism.sql'), 'w') as f:
    f.write("-- Join NCES SEA enrollment to state-level chronic absenteeism\n")
    f.write("-- NCES data: 2021-22 | Absenteeism data: 2023-24\n\n")
    f.write(join_sql + "\n")

# ============================================================================
# 7. Analyze join quality
# ============================================================================
print("\n=== Join Quality Analysis ===")

quality_sql = """
SELECT
    c.state,
    COUNT(*) as total_state_rows,
    COUNT(n.nces_enrollment_2122) as nces_matched,
    COUNT(*) - COUNT(n.nces_enrollment_2122) as nces_unmatched,
    ROUND(COUNT(n.nces_enrollment_2122) * 100.0 / COUNT(*), 1) as match_pct,
    STRING_AGG(
        CASE WHEN n.nces_enrollment_2122 IS NULL THEN c.reporting_category END,
        ', '
    ) as unmatched_categories
FROM combined_chronic_absenteeism c
LEFT JOIN nces_sea_enrollment n
    ON c.state = n.state
    AND c.reporting_category = n.reporting_category
WHERE c.entity_level = 'State'
GROUP BY c.state
"""

quality = con.execute(quality_sql).fetchdf()
print(quality.to_string())

with open(os.path.join(SQL_DIR, 'join_quality_analysis.sql'), 'w') as f:
    f.write("-- Analyze join match quality between NCES and absenteeism data\n\n")
    f.write(quality_sql + "\n")

# ============================================================================
# 8. Full enriched combined dataset (all levels, not just state)
# ============================================================================
print("\n=== Creating full enriched dataset ===")

enriched_sql = """
CREATE TABLE enriched_combined AS
SELECT
    c.*,
    n.fipst as nces_fips_code,
    n.state_name as nces_state_name,
    n.nces_enrollment_2122 as nces_state_enrollment_2122,
    n.nces_join_method
FROM combined_chronic_absenteeism c
LEFT JOIN nces_sea_enrollment n
    ON c.state = n.state
    AND c.reporting_category = n.reporting_category
"""

con.execute(enriched_sql)

enriched_count = con.execute("SELECT COUNT(*) FROM enriched_combined").fetchone()[0]
matched = con.execute("SELECT COUNT(*) FROM enriched_combined WHERE nces_fips_code IS NOT NULL").fetchone()[0]
print(f"  Total rows: {enriched_count:,}")
print(f"  With NCES match: {matched:,} ({matched*100/enriched_count:.1f}%)")

# Export
export_path = os.path.join(DATA_DIR, 'enriched_combined.csv')
con.execute(f"COPY enriched_combined TO '{export_path}' (HEADER, DELIMITER ',')")
print(f"  Exported to {export_path}")

with open(os.path.join(SQL_DIR, 'create_enriched_combined.sql'), 'w') as f:
    f.write("-- Create enriched combined table with NCES enrollment data\n\n")
    f.write(enriched_sql + "\n")

# ============================================================================
# 9. Cross-dataset category coverage matrix
# ============================================================================
print("\n=== Category Coverage Matrix ===")

coverage_sql = """
WITH categories AS (
    SELECT DISTINCT reporting_category, category_description
    FROM combined_chronic_absenteeism
),
ca_cats AS (
    SELECT DISTINCT reporting_category FROM combined_chronic_absenteeism WHERE state = 'CA'
),
il_cats AS (
    SELECT DISTINCT reporting_category FROM combined_chronic_absenteeism WHERE state = 'IL'
),
nces_cats AS (
    SELECT DISTINCT reporting_category FROM nces_sea_enrollment
)
SELECT
    c.reporting_category,
    c.category_description,
    CASE WHEN ca.reporting_category IS NOT NULL THEN 'Y' ELSE '' END as in_ca_absenteeism,
    CASE WHEN il.reporting_category IS NOT NULL THEN 'Y' ELSE '' END as in_il_absenteeism,
    CASE WHEN n.reporting_category IS NOT NULL THEN 'Y' ELSE '' END as in_nces_enrollment,
    CASE
        WHEN ca.reporting_category IS NOT NULL
         AND il.reporting_category IS NOT NULL
         AND n.reporting_category IS NOT NULL
        THEN 'FULL 3-WAY'
        WHEN ca.reporting_category IS NOT NULL AND il.reporting_category IS NOT NULL
        THEN 'CA+IL only'
        WHEN n.reporting_category IS NOT NULL
        THEN 'NCES only'
        ELSE 'PARTIAL'
    END as join_status
FROM categories c
LEFT JOIN ca_cats ca ON c.reporting_category = ca.reporting_category
LEFT JOIN il_cats il ON c.reporting_category = il.reporting_category
LEFT JOIN nces_cats n ON c.reporting_category = n.reporting_category
ORDER BY c.reporting_category
"""

coverage = con.execute(coverage_sql).fetchdf()
print(coverage.to_string())

with open(os.path.join(SQL_DIR, 'category_coverage_matrix.sql'), 'w') as f:
    f.write("-- Category coverage across all three data sources\n\n")
    f.write(coverage_sql + "\n")

# Also include NCES categories NOT in combined
print("\n=== NCES categories NOT in combined absenteeism ===")
nces_only = con.execute("""
    SELECT DISTINCT n.reporting_category, n.category_description
    FROM nces_sea_enrollment n
    LEFT JOIN combined_chronic_absenteeism c
        ON n.reporting_category = c.reporting_category
    WHERE c.reporting_category IS NULL
    ORDER BY n.reporting_category
""").fetchdf()
print(nces_only.to_string())

con.close()
print("\nDone! Database at:", DB_PATH)

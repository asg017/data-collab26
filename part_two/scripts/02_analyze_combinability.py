"""
02_analyze_combinability.py
Use DuckDB to deeply analyze both datasets and determine if/how they can be combined.

Outputs analysis results to stdout and saves SQL queries to ../sql/
"""

import duckdb
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SQL_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')
DB_PATH = os.path.join(DATA_DIR, 'education.duckdb')

os.makedirs(SQL_DIR, exist_ok=True)

con = duckdb.connect(DB_PATH, read_only=True)

def run_query(name, sql, description=""):
    """Run a query, print results, and save the SQL."""
    print(f"\n{'='*80}")
    print(f"QUERY: {name}")
    if description:
        print(f"  {description}")
    print(f"{'='*80}")
    print(f"SQL:\n{sql}\n")

    result = con.execute(sql).fetchdf()
    print(result.to_string(max_rows=60, max_cols=20))
    print(f"\n({len(result)} rows)")

    # Save SQL
    sql_file = os.path.join(SQL_DIR, f"{name}.sql")
    with open(sql_file, 'w') as f:
        f.write(f"-- {name}\n-- {description}\n\n{sql}\n")

    return result


# ============================================================================
# SECTION 1: Schema comparison
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 1: SCHEMA COMPARISON")
print("#"*80)

run_query("ca_schema", """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'ca_chronic_absenteeism'
    ORDER BY ordinal_position
""", "California table schema")

run_query("il_long_schema", """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'il_chronic_absenteeism_long'
    ORDER BY ordinal_position
""", "Illinois long-format table schema")


# ============================================================================
# SECTION 2: What does each row represent?
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 2: ROW SEMANTICS - What does each row represent?")
print("#"*80)

run_query("ca_aggregate_levels", """
    SELECT
        "Aggregate Level",
        CASE "Aggregate Level"
            WHEN 'T' THEN 'State Total'
            WHEN 'C' THEN 'County'
            WHEN 'D' THEN 'District'
            WHEN 'S' THEN 'School'
        END as level_meaning,
        COUNT(*) as row_count,
        COUNT(DISTINCT "Reporting Category") as distinct_categories
    FROM ca_chronic_absenteeism
    GROUP BY "Aggregate Level"
    ORDER BY row_count DESC
""", "California: rows by aggregate level")

run_query("il_entity_types", """
    SELECT
        "Type",
        COUNT(*) as row_count,
        COUNT(DISTINCT "Reporting Category") as distinct_categories
    FROM il_chronic_absenteeism_long
    GROUP BY "Type"
    ORDER BY row_count DESC
""", "Illinois: rows by entity type")


# ============================================================================
# SECTION 3: Reporting categories comparison
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 3: REPORTING CATEGORY COMPARISON")
print("#"*80)

run_query("ca_reporting_categories", """
    SELECT
        "Reporting Category",
        COUNT(*) as row_count,
        ROUND(AVG("ChronicAbsenteeismRate"), 2) as avg_rate
    FROM ca_chronic_absenteeism
    GROUP BY "Reporting Category"
    ORDER BY "Reporting Category"
""", "California distinct reporting categories")

run_query("il_reporting_categories", """
    SELECT
        "Reporting Category",
        COUNT(*) as row_count,
        ROUND(AVG("ChronicAbsenteeismRate"), 2) as avg_rate
    FROM il_chronic_absenteeism_long
    GROUP BY "Reporting Category"
    ORDER BY "Reporting Category"
""", "Illinois distinct reporting categories")


# ============================================================================
# SECTION 4: Semantic mapping of reporting categories
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 4: CATEGORY MAPPING - Which categories align?")
print("#"*80)

run_query("category_mapping", """
    WITH ca_cats AS (
        SELECT DISTINCT "Reporting Category" as cat FROM ca_chronic_absenteeism
    ),
    il_cats AS (
        SELECT DISTINCT "Reporting Category" as cat FROM il_chronic_absenteeism_long
    )
    SELECT
        COALESCE(c.cat, '') as ca_category,
        COALESCE(i.cat, '') as il_category,
        CASE
            WHEN c.cat IS NOT NULL AND i.cat IS NOT NULL THEN 'BOTH'
            WHEN c.cat IS NOT NULL THEN 'CA only'
            ELSE 'IL only'
        END as presence
    FROM ca_cats c
    FULL OUTER JOIN il_cats i ON c.cat = i.cat
    ORDER BY COALESCE(c.cat, i.cat)
""", "Full outer join of reporting categories")


# ============================================================================
# SECTION 5: State-level comparison (most comparable)
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 5: STATE-LEVEL RATE COMPARISON")
print("#"*80)

run_query("state_level_comparison", """
    WITH ca_state AS (
        SELECT
            'CA' as state,
            "Reporting Category",
            SUM("ChronicAbsenteeismEligibleCumulativeEnrollment") as total_enrollment,
            SUM("ChronicAbsenteeismCount") as total_absent,
            ROUND(SUM("ChronicAbsenteeismCount") * 100.0 /
                  NULLIF(SUM("ChronicAbsenteeismEligibleCumulativeEnrollment"), 0), 2) as computed_rate
        FROM ca_chronic_absenteeism
        WHERE "Aggregate Level" = 'T'
          AND "Charter School" = 'All'
          AND "DASS" = 'All'
        GROUP BY "Reporting Category"
    ),
    il_state AS (
        SELECT
            'IL' as state,
            "Reporting Category",
            NULL::BIGINT as total_enrollment,
            NULL::BIGINT as total_absent,
            ROUND(AVG("ChronicAbsenteeismRate"), 2) as computed_rate
        FROM il_chronic_absenteeism_long
        WHERE "Type" = 'State'
        GROUP BY "Reporting Category"
    )
    SELECT
        COALESCE(c."Reporting Category", i."Reporting Category") as category,
        c.computed_rate as ca_rate,
        i.computed_rate as il_rate,
        ROUND(c.computed_rate - i.computed_rate, 2) as rate_difference
    FROM ca_state c
    FULL OUTER JOIN il_state i ON c."Reporting Category" = i."Reporting Category"
    WHERE COALESCE(c."Reporting Category", i."Reporting Category") IN
          ('TA', 'GM', 'GF', 'RW', 'RB', 'RH', 'RA', 'RI', 'RT', 'RP')
    ORDER BY category
""", "Compare state-level chronic absenteeism rates where categories match")


# ============================================================================
# SECTION 6: Data quality comparison
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 6: DATA QUALITY")
print("#"*80)

run_query("ca_data_quality", """
    SELECT
        COUNT(*) as total_rows,
        COUNT("ChronicAbsenteeismRate") as non_null_rate,
        ROUND(COUNT("ChronicAbsenteeismRate") * 100.0 / COUNT(*), 1) as pct_non_null,
        ROUND(MIN("ChronicAbsenteeismRate"), 2) as min_rate,
        ROUND(MAX("ChronicAbsenteeismRate"), 2) as max_rate,
        ROUND(AVG("ChronicAbsenteeismRate"), 2) as avg_rate,
        ROUND(MEDIAN("ChronicAbsenteeismRate"), 2) as median_rate
    FROM ca_chronic_absenteeism
""", "California data quality summary")

run_query("il_data_quality", """
    SELECT
        COUNT(*) as total_rows,
        COUNT("ChronicAbsenteeismRate") as non_null_rate,
        ROUND(COUNT("ChronicAbsenteeismRate") * 100.0 / COUNT(*), 1) as pct_non_null,
        ROUND(MIN("ChronicAbsenteeismRate"), 2) as min_rate,
        ROUND(MAX("ChronicAbsenteeismRate"), 2) as max_rate,
        ROUND(AVG("ChronicAbsenteeismRate"), 2) as avg_rate,
        ROUND(MEDIAN("ChronicAbsenteeismRate"), 2) as median_rate
    FROM il_chronic_absenteeism_long
""", "Illinois data quality summary")


# ============================================================================
# SECTION 7: Geographic hierarchy comparison
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 7: GEOGRAPHIC HIERARCHY")
print("#"*80)

run_query("ca_geo_counts", """
    SELECT
        COUNT(DISTINCT "County Name") as counties,
        COUNT(DISTINCT "District Name") as districts,
        COUNT(DISTINCT "School Name") as schools
    FROM ca_chronic_absenteeism
    WHERE "Aggregate Level" = 'S'
""", "California geographic entity counts")

run_query("il_geo_counts", """
    SELECT
        COUNT(DISTINCT "County") as counties,
        COUNT(DISTINCT "District") as districts,
        COUNT(DISTINCT "School Name") as schools
    FROM il_chronic_absenteeism_long
    WHERE "Type" = 'School'
""", "Illinois geographic entity counts")


# ============================================================================
# SECTION 8: Combined dataset feasibility - build a prototype
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 8: PROTOTYPE COMBINED DATASET")
print("#"*80)

combined_sql = """
    -- Prototype combined chronic absenteeism dataset
    WITH ca_normalized AS (
        SELECT
            'CA' as state,
            '2023-24' as academic_year,
            "Aggregate Level" as entity_level,
            "County Name" as county,
            "District Name" as district,
            "School Name" as school,
            "Charter School" as charter_school,
            "Reporting Category" as reporting_category,
            "ChronicAbsenteeismEligibleCumulativeEnrollment" as enrollment,
            "ChronicAbsenteeismCount" as chronic_absent_count,
            "ChronicAbsenteeismRate" as chronic_absent_rate
        FROM ca_chronic_absenteeism
        WHERE "Charter School" = 'All' AND "DASS" = 'All'
    ),
    il_normalized AS (
        SELECT
            'IL' as state,
            '2023-24' as academic_year,
            CASE "Type"
                WHEN 'State' THEN 'T'
                WHEN 'District' THEN 'D'
                WHEN 'School' THEN 'S'
                ELSE "Type"
            END as entity_level,
            "County" as county,
            "District" as district,
            "School Name" as school,
            NULL as charter_school,
            "Reporting Category" as reporting_category,
            NULL::DOUBLE as enrollment,
            NULL::DOUBLE as chronic_absent_count,
            "ChronicAbsenteeismRate" as chronic_absent_rate
        FROM il_chronic_absenteeism_long
    )
    SELECT * FROM ca_normalized
    UNION ALL
    SELECT * FROM il_normalized
"""

result = run_query("prototype_combined", f"""
    WITH combined AS ({combined_sql})
    SELECT
        state,
        entity_level,
        COUNT(*) as rows,
        COUNT(chronic_absent_rate) as non_null_rates,
        ROUND(AVG(chronic_absent_rate), 2) as avg_rate
    FROM combined
    GROUP BY state, entity_level
    ORDER BY state, entity_level
""", "Prototype combined dataset summary")


# ============================================================================
# SECTION 9: Overlapping categories analysis
# ============================================================================
print("\n" + "#"*80)
print("# SECTION 9: OVERLAPPING CATEGORY DEEP DIVE")
print("#"*80)

run_query("shared_categories_detail", """
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
""", "Categories that exist in BOTH datasets")


# ============================================================================
# Save the combined creation SQL for reuse
# ============================================================================
combined_create_sql = f"""
-- Create a combined chronic absenteeism table from both states
CREATE TABLE combined_chronic_absenteeism AS
{combined_sql};
"""
with open(os.path.join(SQL_DIR, 'create_combined_table.sql'), 'w') as f:
    f.write(combined_create_sql)

print(f"\n\nAll SQL queries saved to {SQL_DIR}/")
con.close()

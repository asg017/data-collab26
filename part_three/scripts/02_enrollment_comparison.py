"""
02_enrollment_comparison.py
Deep analysis comparing NCES enrollment figures to state-reported data.
Uses NCES 2021-22 enrollment vs CA 2023-24 absenteeism-eligible enrollment.
"""

import duckdb
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SQL_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')
DB_PATH = os.path.join(DATA_DIR, 'part_three.duckdb')

con = duckdb.connect(DB_PATH, read_only=True)

def run(title, sql):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")
    result = con.execute(sql).fetchdf()
    print(result.to_string())
    return result

# 1. CA enrollment comparison: NCES vs state-reported
run("CA: NCES 2021-22 enrollment vs CA absenteeism-eligible enrollment 2023-24", """
    SELECT
        reporting_category,
        category_description,
        nces_state_enrollment_2122 as nces_2122,
        eligible_enrollment as ca_eligible_2324,
        CASE WHEN nces_state_enrollment_2122 > 0
            THEN ROUND((eligible_enrollment - nces_state_enrollment_2122) * 100.0
                        / nces_state_enrollment_2122, 2)
            ELSE NULL
        END as pct_change,
        chronic_absent_rate
    FROM enriched_combined
    WHERE state = 'CA'
      AND entity_level = 'State'
    ORDER BY reporting_category
""")

# 2. NCES enrollment share by race - both states
run("Racial composition comparison (NCES 2021-22)", """
    WITH totals AS (
        SELECT state, nces_enrollment_2122 as total
        FROM nces_sea_enrollment
        WHERE reporting_category = 'TA'
    ),
    by_race AS (
        SELECT n.state, n.reporting_category, n.category_description,
               n.nces_enrollment_2122,
               ROUND(n.nces_enrollment_2122 * 100.0 / t.total, 2) as pct_of_total
        FROM nces_sea_enrollment n
        JOIN totals t ON n.state = t.state
        WHERE n.reporting_category LIKE 'R%'
    )
    SELECT
        reporting_category,
        category_description,
        MAX(CASE WHEN state='CA' THEN pct_of_total END) as ca_pct,
        MAX(CASE WHEN state='IL' THEN pct_of_total END) as il_pct,
        MAX(CASE WHEN state='CA' THEN nces_enrollment_2122 END) as ca_count,
        MAX(CASE WHEN state='IL' THEN nces_enrollment_2122 END) as il_count
    FROM by_race
    GROUP BY reporting_category, category_description
    ORDER BY reporting_category
""")

# 3. Estimated chronic absent COUNTS for IL using NCES enrollment
run("IL: Estimated chronic absent counts using NCES enrollment as proxy", """
    SELECT
        n.reporting_category,
        n.category_description,
        c.chronic_absent_rate as il_rate_2324,
        n.nces_enrollment_2122 as nces_enrollment,
        ROUND(n.nces_enrollment_2122 * c.chronic_absent_rate / 100.0) as estimated_absent_count,
        '2021-22 enrollment x 2023-24 rate (approximate)' as methodology
    FROM enriched_combined c
    JOIN nces_sea_enrollment n
        ON c.state = n.state AND c.reporting_category = n.reporting_category
    WHERE c.state = 'IL'
      AND c.entity_level = 'State'
      AND c.chronic_absent_rate IS NOT NULL
    ORDER BY n.reporting_category
""")

# 4. All 57 states from NCES for context
run("All states total enrollment (NCES 2021-22) - top 15", """
    SELECT
        state,
        state_name,
        fipst,
        nces_enrollment_2122 as total_enrollment
    FROM nces_sea_enrollment
    WHERE reporting_category = 'TA'
    ORDER BY nces_enrollment_2122 DESC
    LIMIT 15
""")

# 5. How many NCES grade-level categories could match IL but not the combined set?
run("NCES grade categories vs IL absenteeism grade categories", """
    WITH nces_grades AS (
        SELECT reporting_category, category_description, state,
               nces_enrollment_2122
        FROM nces_sea_enrollment
        WHERE reporting_category LIKE 'GR%'
          AND state = 'IL'
    ),
    il_grades AS (
        SELECT DISTINCT "Reporting Category" as reporting_category
        FROM il_chronic_absenteeism_long
        WHERE "Reporting Category" LIKE 'GR%'
    )
    SELECT
        n.reporting_category,
        n.category_description,
        n.nces_enrollment_2122 as nces_enrollment,
        CASE WHEN i.reporting_category IS NOT NULL THEN 'YES' ELSE 'NO' END as in_il_absenteeism
    FROM nces_grades n
    LEFT JOIN il_grades i ON n.reporting_category = i.reporting_category
    ORDER BY n.reporting_category
""")

con.close()
print("\nDone!")

"""
04_run_queries.py
Run all SQL queries against the DuckDB database and display results.
Demonstrates the combined dataset in action.
"""

import duckdb
import os
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SQL_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')
DB_PATH = os.path.join(DATA_DIR, 'education.duckdb')

con = duckdb.connect(DB_PATH, read_only=True)

# Run each SQL file
for sql_file in sorted(glob.glob(os.path.join(SQL_DIR, '*.sql'))):
    name = os.path.basename(sql_file)
    print(f"\n{'='*80}")
    print(f"  {name}")
    print(f"{'='*80}")

    with open(sql_file) as f:
        sql = f.read()

    # Strip comments for display
    lines = [l for l in sql.strip().split('\n') if not l.strip().startswith('--')]
    clean_sql = '\n'.join(lines).strip()

    if not clean_sql:
        print("  (empty query, skipping)")
        continue

    try:
        result = con.execute(clean_sql).fetchdf()
        print(result.to_string(max_rows=30))
        print(f"\n({len(result)} rows)")
    except Exception as e:
        print(f"  ERROR: {e}")

con.close()

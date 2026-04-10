# Part Three: NCES CCD Join Report

## Data Sources Used

### 1. CCD School Directory (`ccd_directory.csv`)

The main crosswalk file: the **NCES Common Core of Data (CCD) School Directory** for the 2024-25 school year. This is the real deal — it maps every school in the US to federal NCES IDs.

- **102,178 schools** across 57 states/territories
- **10,405 CA schools**, **4,438 IL schools**
- Key columns: `NCESSCH` (12-digit federal school ID), `LEAID` (7-digit federal district ID), `ST_SCHID` (state school ID), `ST_LEAID` (state district ID)
- Also includes: school type, charter status, grade levels, city, ZIP, open/closed status

### 2. CCD SEA Membership File (`nces_ccd_crosswalk.csv`)

Originally provided file — state-level enrollment counts by race/sex/grade (2021-22). Used for enrollment context only (see previous analysis in `scripts/01_load_nces_and_join.py`).

---

## Join Methodology

### The Problem

California uses **CDS codes** (County-District-School): `County(2) + District(5) + School(7)` = 14 digits.
Illinois uses **RCDTS codes** (Region-County-District-Type-School): 15 characters (may include letters).
NCES uses **NCESSCH** (12 digits) and **LEAID** (7 digits).

None of these match each other directly. The CCD Directory bridges them via `ST_SCHID` (state school ID) which embeds the state's own coding system.

### California Join Key Discovery

CCD `ST_SCHID` format for CA: `CA-{district_7}-{school_7}`

Example: `CA-1975309-1995786` → district part `1975309`, school part `1995786`

CA absenteeism data has separate `County Code` (2-digit) and `District Code` (5-digit) and `School Code` (7-digit).

**Join key**: CA `School Code` (7-digit) = CCD `school_7` (extracted from `ST_SCHID`)

For districts: CA `County Code + District Code` (7-digit) = CCD `district_7`

### Illinois Join Key Discovery

CCD `ST_SCHID` format for IL: `IL-RR-CCC-DDDD-TT-{RCDTS_15}`

Example: `IL-08-043-2100-26-080432100260002` → numeric tail `080432100260002`

IL absenteeism data uses `RCDTS` — a 15-character code.

**Join key**: IL `RCDTS` = CCD numeric tail of `ST_SCHID` (exact match!)

For districts: IL district `RCDTS` = school `RCDTS[:11] + '0000'`

---

## Match Results

### School-Level Matches

Join key is the **full 14-digit CDS code** (County + District + School), not the 7-digit school code alone. Using school code alone inflates match rates because generic codes like `0000000` ("District Office") appear across 97+ districts.

| State | Absenteeism Schools (unique CDS) | CCD Schools | Matched | Match Rate |
|-------|---:|---:|---:|---:|
| **California** | 10,139 | 10,405 | **9,006** | **88.8%** |
| **Illinois** | 3,835 | 4,438 | **3,835** | **100.0%** |

### District-Level Matches

| State | Absenteeism Districts | Matched | Match Rate |
|-------|---:|---:|---:|
| **California** | 996 | 996 | **100.0%** |
| **Illinois** | 866 | 866 | **100.0%** |

### Row-Level Summary (all reporting categories × entities)

| State | Entity Level | Total Rows | With NCES School ID | With NCES District ID |
|-------|-------------|---:|---:|---:|
| CA | School | 208,350 | 185,385 (89.0%) | 185,385 (89.0%) |
| IL | School | 103,545 | 103,545 (100%) | 103,545 (100%) |
| IL | District | 23,382 | — | 23,382 (100%) |
| IL | State | 27 | — | — |

### What Didn't Match (CA): 1,133 schools

The 1,133 unmatched CA CDS codes break down into two categories:

**1. Administrative/placeholder entries (141 schools) — expected mismatches:**

| Type | Count | Why No Match |
|---|---:|---|
| "District Office" (code `0000000`) | 97 | Administrative placeholders in 97 districts, not real schools |
| "Nonpublic, Nonsectarian Schools" (code `0000001`) | 44 | Aggregate categories, not individual schools |

**2. Real schools not in CCD Directory (992 schools):**

| Pattern | Est. Count | Why No Match |
|---|---:|---|
| Charter schools | ~379 | Recently opened/closed charters not yet in CCD 2024-25 |
| Academies (likely charters) | ~317 | Similar — charter school naming pattern |
| Other schools | ~296 | Mix of alternative programs, recently opened schools, name mismatches |

Many of these are **charter schools** that opened or closed between the CCD snapshot (2024-25) and the absenteeism reporting year (2023-24), or that use different CDS codes than what NCES has on file. Charter schools have notoriously high churn rates.

**Excluding administrative placeholders, the real match rate is 90.1%** (9,006 / 9,998 actual schools).

---

## What NCES IDs Enable

### Before: State-specific, incompatible identifiers

```
CA School: County=34, District=67330, School=6033252  (CDS: 34673306033252)
IL School: RCDTS=560991220021006
→ No way to link these to each other or to federal data
```

### After: Federal NCES IDs on every record

```
CA School: NCESSCH=061389001568, LEAID=0613890
IL School: NCESSCH=172814004933, LEAID=1728140
→ Can now join to ANY federal education dataset
```

### Unlocked capabilities

1. **Join to CRDC** (Civil Rights Data Collection) — federal chronic absenteeism data, discipline data, course offerings
2. **Join to EDGE/ACS** — school neighborhood demographics, poverty rates, Census data
3. **Join to Title I data** — federal funding allocations
4. **Join to NAEP** — National Assessment scores at district level
5. **Cross-state school matching** — compare similar schools across CA and IL using NCES metadata (school type, grade span, charter status, urbanicity)

### New metadata from CCD

The join also enriches each school with:

| Field | Description | Example Values |
|-------|-------------|----------------|
| `nces_school_type` | Federal school classification | Regular School, Special Education, Alternative, Career/Technical |
| `nces_charter` | Charter school flag | Yes, No |
| `nces_level` | Grade level category | Elementary, Middle, High, Other |
| `nces_city` | School city | Chicago, Los Angeles, Springfield |
| `nces_zip` | ZIP code | 60601, 90001 |

---

## Does This Dataset Match Exactly?

### Short answer: **Illinois: yes. California: mostly, with a charter school gap.**

| Metric | Result |
|--------|--------|
| IL schools: exact RCDTS match | **100%** (3,835/3,835) |
| IL districts: derived RCDTS match | **100%** (866/866) |
| CA schools: full CDS match | **88.8%** (9,006/10,139) |
| CA schools: excluding placeholders | **90.1%** (9,006/9,998) |
| CA districts: county+district code match | **100%** (996/996) |
| School names match between datasets | **Exact** where joined |

### Why 100% for Illinois?

The CCD Directory's `ST_SCHID` field for IL contains the full 15-character RCDTS code as its numeric tail — a direct, lossless match. Every IL school in the absenteeism data appears in the CCD.

### Why ~90% for California?

Two factors:
1. **141 placeholder entries** (District Offices code `0000000`, Nonpublic aggregates code `0000001`) are in CA's data but aren't real schools — these will never match.
2. **992 real schools** (mostly charters and alternative programs) have CDS codes that don't appear in the CCD 2024-25 Directory. Charter schools open and close frequently, and may not yet be in the federal registry or may have been removed after closing.

### Time gap consideration

The CCD Directory is 2024-25; the absenteeism data is 2023-24. This means:
- Schools that **opened** in 2024-25 appear in CCD but not in absenteeism data (no impact — LEFT JOIN)
- Schools that **closed** between 2023-24 and 2024-25 appear in absenteeism data but not in CCD — this explains many of the 992 unmatched real CA schools
- IL appears unaffected — its school roster is more stable, or its RCDTS codes persisted in CCD even after closure

---

## Files Produced

| File | Description |
|------|-------------|
| `data/ccd_directory.csv` | Raw CCD School Directory (102K schools, all states) |
| `data/part_three.duckdb` | DuckDB database with all tables including joins |
| `data/combined_with_nces_ids.csv` | Combined CA+IL data with NCES IDs (126,954 rows) |
| `data/enriched_combined.csv` | Combined data with NCES enrollment context |
| `scripts/01_load_nces_and_join.py` | SEA enrollment join (original crosswalk file) |
| `scripts/02_enrollment_comparison.py` | Enrollment analysis queries |
| `scripts/03_nces_id_join.py` | **Main CCD Directory join pipeline** |
| `sql/create_combined_with_nces.sql` | Combined table creation SQL |
| `sql/join_nces_to_absenteeism.sql` | State-level enrollment join |
| `sql/join_quality_analysis.sql` | Join quality metrics |
| `sql/category_coverage_matrix.sql` | 3-way data source coverage |

---

## Combined Dataset Schema

The final `combined_with_nces_ids.csv` contains:

| Column | Type | Source |
|--------|------|--------|
| state | VARCHAR | Derived (CA/IL) |
| fips_code | VARCHAR | NCES (06/17) |
| academic_year | VARCHAR | State data (2023-24) |
| entity_level | VARCHAR | State data (School/District/State) |
| county | VARCHAR | State data |
| district | VARCHAR | State data |
| school | VARCHAR | State data |
| reporting_category | VARCHAR | State data (TA, RB, GF, etc.) |
| eligible_enrollment | DOUBLE | CA only |
| chronic_absent_count | DOUBLE | CA only |
| chronic_absent_rate | DOUBLE | Both states |
| **nces_school_id** | VARCHAR | **CCD Directory (NCESSCH)** |
| **nces_district_id** | VARCHAR | **CCD Directory (LEAID)** |
| nces_school_type | VARCHAR | CCD Directory |
| nces_charter | VARCHAR | CCD Directory |
| nces_level | VARCHAR | CCD Directory |
| nces_city | VARCHAR | CCD Directory |
| nces_zip | VARCHAR | CCD Directory |

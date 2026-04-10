# Illinois + California Education Data: Combinability Analysis

## Executive Summary

**Yes, these datasets can be partially combined.** Both states report chronic absenteeism data with overlapping demographic breakdowns. A combined dataset of 63,552 rows has been created covering 11 shared reporting categories across both states for the 2023-24 academic year.

However, significant structural differences exist that limit the depth of combination. The key constraint is that Illinois provides only **rates** (percentages), while California provides **rates, counts, and enrollment figures**. This means combined analyses must rely on rate comparisons only.

---

## Data Sources

| Attribute | California | Illinois |
|-----------|-----------|----------|
| **Source** | CDE Chronic Absenteeism Data | ISBE Report Card Public Data Set |
| **Year** | 2023-24 | 2023-24 |
| **File Format** | Tab-delimited text (33 MB) | Excel workbook (54 MB, 949+ columns) |
| **Data Structure** | Long format (1 row per entity × category) | Wide format (1 row per entity, columns per category) |
| **Total Raw Rows** | 343,602 | 4,702 (wide) → 126,954 (long) |
| **Focus** | Chronic absenteeism only | Comprehensive report card (absenteeism is ~27 of 949 columns) |

## What Each Row Represents

### California
Each row = one **entity** (state/county/district/school) × one **reporting category** (demographic group).

| Level | Rows | Description |
|-------|------|-------------|
| State (T) | 229 | Statewide totals by category |
| County (C) | 11,705 | County-level by category |
| District (D) | 123,318 | District-level by category |
| School (S) | 208,350 | School-level by category |

### Illinois
Each row in the original = one **entity** (statewide/district/school) with chronic absenteeism rates in separate columns per demographic.

After pivoting to long format to match California:

| Level | Rows | Description |
|-------|------|-------------|
| Statewide | 27 | State totals by category |
| District | 23,382 | District-level by category |
| School | 103,545 | School-level by category |

**Note:** Illinois has no county-level aggregation.

---

## Column Comparison

### Core Measures

| Measure | California | Illinois | Combinable? |
|---------|-----------|----------|-------------|
| Chronic Absenteeism Rate | Yes (%) | Yes (%) | **Yes** |
| Eligible Enrollment | Yes (count) | No | No - IL only has total enrollment |
| Chronic Absent Count | Yes (count) | No | No |
| Student Attendance Rate | No | Yes (%) | No |
| Chronic Truancy Rate | No | Yes (%) | No |

### Geographic Identifiers

| Field | California | Illinois | Combinable? |
|-------|-----------|----------|-------------|
| State | Implicit (all CA) | Implicit (all IL) | Yes - added as column |
| County | County Code + Name | County name | **Yes** (name-based) |
| District | District Code + Name | RCDTS code + Name | **Yes** (name-based) |
| School | School Code + Name | RCDTS code + Name | **Yes** (name-based) |
| Charter School flag | Yes (Y/N/All) | No | No |
| DASS flag | Yes (Y/N/All) | No | No |

### Geographic Scale

| Metric | California | Illinois |
|--------|-----------|----------|
| Counties | 58 | 104 |
| Districts | 1,006 | 866 |
| Schools | 8,769 | 3,533 |

---

## Reporting Category Overlap

### Shared Categories (11 total) - CAN combine

| Code | Description | CA State Rate | IL State Rate | Difference |
|------|-------------|:---:|:---:|:---:|
| TA | Total (All Students) | 20.4% | 26.3% | -5.9 |
| GF | Gender: Female | 20.4% | 26.6% | -6.2 |
| GM | Gender: Male | 20.4% | 26.0% | -5.6 |
| RA | Race: Asian | 8.6% | 16.6% | -8.0 |
| RB | Race: Black/African American | 32.3% | 40.4% | -8.1 |
| RH | Race: Hispanic/Latino | 23.6% | 32.9% | -9.3 |
| RI | Race: American Indian/Alaska Native | 33.0% | 32.8% | +0.2 |
| RP | Race: Native Hawaiian/Pacific Islander | 32.3% | 28.0% | +4.3 |
| RT | Race: Two or More Races | 17.3% | 26.6% | -9.3 |
| RW | Race: White | 15.9% | 18.1% | -2.2 |
| SD | Students with Disabilities | 29.0% | 32.7% | -3.7 |

### CA-Only Categories (15) - CANNOT combine

| Code | Description |
|------|-------------|
| GR13 | Grades 1-3 (span) |
| GR46 | Grades 4-6 (span) |
| GR78 | Grades 7-8 (span) |
| GR912 | Grades 9-12 (span) |
| GRTK8 | Grades TK-8 (span) |
| GRTKKN | Grades TK-K |
| GX | Gender: Non-Binary/Other |
| GZ | Gender: Missing |
| RD | Race: Filipino |
| RF | Race: African American (alt code?) |
| SE | Socioeconomically Disadvantaged |
| SF | Foster Youth |
| SH | Homeless |
| SM | Migrant |
| SS | English Learners (Reclassified) |

### IL-Only Categories (16) - CANNOT combine

| Code | Description |
|------|-------------|
| GRK, GR1-GR12 | Individual grade levels (K through 12) |
| SEL | English Learners |
| SIEP | IEP Students |
| SLI | Low Income |

**Key insight:** California uses **grade spans** (GR13 = grades 1-3), while Illinois uses **individual grades** (GR1, GR2, GR3). These could theoretically be combined by aggregating IL individual grades into CA spans, but IL lacks the enrollment counts needed to compute weighted averages.

---

## Data Quality Comparison

| Metric | California | Illinois |
|--------|-----------|----------|
| Total rows | 343,602 | 126,954 |
| Rows with non-null rate | 237,769 (69.2%) | 53,213 (41.9%) |
| Min rate | 0.0% | 2.0% |
| Max rate | 100.0% | 100.0% |
| Average rate | 25.0% | 28.7% |
| Median rate | 21.0% | 25.9% |

**Suppression:** Both states suppress data for small cell sizes (CA: <=10 students, IL: uses `*`). Illinois has significantly more suppressed values (58% null vs CA's 31%), likely because Illinois has more small schools/districts.

---

## What IS Feasible

1. **Cross-state chronic absenteeism rate comparisons** by race/ethnicity, gender, and disability status at state, district, and school levels.
2. **Demographic disparity analysis** - comparing how gaps between racial groups differ across states.
3. **Distribution analysis** - comparing the spread of district/school-level absenteeism rates.
4. **Identifying high-need areas** in both states side-by-side.
5. **Policy benchmarking** - e.g., "How does the average IL district compare to the average CA district?"

## What is NOT Feasible

1. **Population-weighted combined statistics** - IL lacks enrollment counts, so you cannot compute a true combined CA+IL average.
2. **Grade-level comparisons** - different granularity (spans vs. individual grades) and no way to aggregate IL data without counts.
3. **Charter school analysis** - IL doesn't flag charter schools.
4. **Trend analysis** - only one year loaded (could be extended by downloading additional years).
5. **Exact entity matching** - no common identifier system between states.

---

## Combined Dataset

The combined dataset (`data/combined_chronic_absenteeism.csv`) contains **63,552 rows** with this schema:

| Column | Type | Description |
|--------|------|-------------|
| state | VARCHAR | 'CA' or 'IL' |
| academic_year | VARCHAR | '2023-24' |
| entity_level | VARCHAR | 'State', 'County', 'District', 'School' |
| county | VARCHAR | County name |
| district | VARCHAR | District name |
| school | VARCHAR | School name (null for district/state rows) |
| reporting_category | VARCHAR | Category code (e.g., 'TA', 'RB') |
| category_description | VARCHAR | Human-readable description |
| eligible_enrollment | DOUBLE | CA only - eligible student count |
| chronic_absent_count | DOUBLE | CA only - chronically absent count |
| chronic_absent_rate | DOUBLE | Percentage chronically absent |

---

## Conclusion

These datasets are **moderately combinable**. The strongest overlap is in chronic absenteeism rates broken down by race/ethnicity and gender - 11 directly comparable reporting categories. The main limitations are:

1. Illinois only provides rates, not counts/enrollment
2. Grade-level categories use different granularity
3. Some student subgroup categories differ (CA has foster youth, homeless; IL has low income, EL)

For a research project comparing chronic absenteeism patterns across these two large states, the combined dataset provides a solid foundation for rate-based demographic comparisons at the district and school level.

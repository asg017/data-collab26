# Crosswalk Results: Revised Harmonized Comparison

Generated from `03_crosswalk_queries.sql` using the CA data dictionary and Oregon website documentation. All results filtered to the overlapping period (2010-01-01 to 2024-06-30).

---

## What Was Corrected from the Initial Analysis

1. **CA's `LTC` field** is now used to filter long-term care facilities (instead of guessing from facility type codes)
2. **CA's "Abuse/Facility Not Self Reported"** is correctly identified as a *failure to report* category, not an abuse finding -- excluded from cross-state comparison
3. **OR's `Allegation` field** is mapped using the exact dropdown values from the Oregon website (~90 options), not keyword guessing
4. **Abuse findings** (42% of OR data) are excluded from cross-state comparison since CA has no equivalent
5. **CA categories with no OR equivalent** (Privacy Breach, Adverse Events, Failure to Self-Report) are excluded
6. **OR categories with no CA equivalent** ("Abuse Protection" allegations like "Failed to protect resident from physical abuse") are excluded

---

## Records Excluded from Cross-State Comparison

| State | Category | Excluded Records | Why |
|---|---|---|---|
| CA | Failure to Self-Report (CA only) | 2,572 | OR has no equivalent mandatory self-reporting framework |
| CA | Privacy Breach (CA only) | 84 | OR does not track data breaches in this dataset |
| CA | Other (unmapped) | 892 | Categories that don't map to OR |
| OR | Abuse Protection (OR only) | 3,018 | CA has no abuse finding equivalent |
| OR | Abuse findings (all `Type` LIKE 'Abuse:%') | ~18,500 | CA dataset does not contain abuse substantiation data |

After exclusions, the comparable subsets are: **~14,400 CA records** and **~22,100 OR licensing violation records**.

---

## Nursing Facility Comparison (Cleanest Analysis)

Filtering to SNF (CA) and NF (OR), comparable categories only, OR licensing violations only (no abuse findings):

| Category | CA Count | CA % | OR Count | OR % |
|---|---|---|---|---|
| Care Quality | 7,024 | 55.9% | 1,993 | 35.6% |
| Staffing (Hours/NHPPD) | 2,086 | 16.6% | -- | -- |
| Resident Rights | 1,582 | 12.6% | 645 | 11.5% |
| Transfer/Discharge | 588 | 4.7% | 72 | 1.3% |
| Medication | 404 | 3.2% | 655 | 11.7% |
| Environment/Safety | 378 | 3.0% | 445 | 7.9% |
| Administration/Records | 308 | 2.4% | 92 | 1.6% |
| Staffing (General) | 32 | 0.3% | 1,277 | 22.8% |
| Falsification/Records | 106 | 0.8% | -- | -- |
| Dietary | 64 | 0.5% | 121 | 2.2% |
| Falls | -- | -- | 120 | 2.1% |
| Reporting/Notification | -- | -- | 178 | 3.2% |

### Key Observations

1. **"Care Quality" is the largest category in both states** but much larger in CA (56% vs 36%). CA's broad "Patient Care" penalty category likely bundles issues that OR breaks into specific allegations (medication, environment, falls, etc.).

2. **Staffing is categorized very differently.** CA has a specific administrative penalty for nursing-hours-per-patient-day (NHPPD) violations under HSC 1276.5 (16.6% of CA NF records). OR tracks staffing through general licensing violations (22.8% of OR NF records) including ABST (Acuity-Based Staffing Tool) compliance. These measure staffing differently and should be compared cautiously.

3. **Medication is proportionally much larger in OR (11.7%) vs CA (3.2%).** This may reflect OR's more granular allegation taxonomy -- OR has 8 distinct medication-related allegations vs CA's single "Medication" category. OR may also be catching violations that CA classifies under "Patient Care."

4. **Environment/Safety is larger in OR (7.9%) vs CA (3.0%).** Similar explanation -- OR's specific "Failed to provide safe environment" is the single most common allegation.

---

## Facility Type Distribution (All LTC)

| Facility Type | CA Count | CA % | OR Count | OR % |
|---|---|---|---|---|
| Nursing Facility | 15,636 | 87.3% | 7,645 | 18.7% |
| Intermediate Care (CA) / Residential Care (OR) | 1,754 (9.8%) | -- | 26,372 (64.4%) | -- |
| Congregate Living (CA) / Adult Foster Home (OR) | 520 (2.9%) | -- | 6,963 (17.0%) | -- |

The datasets have **completely different facility type mixes**. CA is 87% nursing facilities; OR is 64% residential care. This is a fundamental structural difference -- OR regulates a much broader spectrum of community-based care settings.

---

## Annual Volume: Nursing Facilities Only

Comparing only NF/SNF records, with OR filtered to licensing violations only (no abuse):

| Year | CA (SNF) | OR (NF, licensing only) |
|---|---|---|
| 2010 | 1,112 | 358 |
| 2011 | 958 | 218 |
| 2012 | 600 | 216 |
| 2013 | 532 | 224 |
| 2014 | 750 | 312 |
| 2015 | 888 | 341 |
| 2016 | 930 | 429 |
| 2017 | 1,146 | 455 |
| 2018 | 1,316 | 563 |
| 2019 | 1,870 | 544 |
| 2020 | 1,408 | 379 |
| 2021 | 970 | 465 |
| 2022 | 1,148 | 410 |
| 2023 | 1,444 | 541 |
| 2024 | 564 | 273 |

Both states show a COVID dip in 2020, a deeper trough in 2021, and recovery in 2022-2023. CA volumes are roughly 2-3x OR volumes for nursing facilities, which is more proportional to the relative number of facilities (CA has ~1,200 SNFs; OR has ~130 NFs).

---

## Oregon: Abuse vs. Licensing Violation Trends

This data is unique to Oregon and has no CA equivalent:

| Year | Abuse Findings | Licensing Violations | Abuse % |
|---|---|---|---|
| 2010 | 529 | 855 | 38.2% |
| 2011 | 673 | 616 | 52.2% |
| 2012 | 696 | 619 | 52.9% |
| 2013 | 839 | 704 | 54.4% |
| 2014 | 1,028 | 882 | 53.8% |
| 2015 | 1,127 | 1,099 | 50.6% |
| 2016 | 1,259 | 1,665 | 43.1% |
| 2017 | 1,321 | 2,662 | 33.2% |
| 2018 | 1,522 | 2,280 | 40.0% |
| 2019 | 1,779 | 1,866 | 48.8% |
| 2020 | 1,430 | 1,730 | 45.3% |
| 2021 | 1,743 | 1,897 | 47.9% |
| 2022 | 1,777 | 2,511 | 41.4% |
| 2023 | 1,434 | 2,459 | 36.8% |

The proportion of abuse findings vs licensing violations fluctuates between 33-54%. The shift toward more licensing violations in 2016-2017 and 2022-2023 may reflect regulatory focus changes.

---

## California: Enforcement Severity and Penalties

This data is unique to California and has no OR equivalent:

| Category | Class | Count | Avg Penalty | Total Penalties |
|---|---|---|---|---|
| Care Quality | AA (most serious) | 330 | $72,982 | $24.1M |
| Care Quality | A (serious) | 3,180 | $19,527 | $62.1M |
| Care Quality | B (moderate) | 4,450 | $2,079 | $9.3M |
| Staffing (Hours) | AP NHPPD | 2,086 | $18,292 | $38.2M |
| Resident Rights | A | 226 | $14,623 | $3.3M |
| Resident Rights | B | 1,876 | $1,731 | $3.2M |
| Medication | AA | 18 | $71,156 | $1.3M |
| Medication | A | 90 | $15,722 | $1.4M |

Total penalties in the comparable period: **~$147M** across all LTC categories.

---

## Top Repeat Offenders

The top 25 facilities by violation count are dominated by **Oregon Residential Care (memory care) facilities**. The top CA facility (#22 overall) is Kingston Healthcare Center with 164 records. This pattern reflects OR's granular allegation system -- a single investigation can generate many substantiated findings across multiple specific allegations, whereas CA might issue a single citation covering the same scope.

---

## Final Assessment

### What this analysis supports:
- **Trend comparison** (year-over-year patterns, COVID impact) for nursing facilities
- **Proportional analysis** of violation categories within each state
- **Within-state analysis** of each dataset independently (CA severity/penalties, OR abuse subtypes)

### What this analysis does NOT support:
- Direct "violation rate" comparison between states (different units of measurement)
- Abuse rate comparison (CA dataset doesn't track abuse findings)
- Financial penalty comparison (OR dataset doesn't include penalties)
- Facility-level comparison across states (no shared facilities)
- Combining into a single unified dataset without extensive caveats

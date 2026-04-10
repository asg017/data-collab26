# CRITICAL ANALYSIS: False Equivalence in Facility Type Crosswalk

## Severity: HIGH -- Apples-to-Oranges Comparison

The facility type crosswalk in `01_matching_analysis.md` and `03_crosswalk_queries.sql` maps California and Oregon facility types into "harmonized" categories that obscure fundamental differences in the populations served, facility sizes, and regulatory contexts.

---

## Flaw 1: CA ICF/DD != OR ALF/RCF

The crosswalk maps both into **"Intermediate Care / Residential"**:

| Harmonized Category | CA Types | OR Types |
|---|---|---|
| Intermediate Care / Residential | ICF, ICFDDH, ICFDDN, ICFDD | ALF, RCF |

But these serve **entirely different populations**:

- **CA ICF/DD**: Intermediate Care Facilities for the **Developmentally Disabled** (DD/H/N/CN/IID). These are licensed facilities providing 24-hour care to individuals with intellectual and developmental disabilities. The CA data confirms the description: `"Intermediate Care Facility-DD/H/N/CN/IID"`.
- **OR ALF/RCF**: Assisted Living Facilities and Residential Care Facilities primarily serving **elderly adults** who need help with activities of daily living but not necessarily skilled medical care.

Lumping developmentally disabled care with elderly assisted living creates a category that has no real-world meaning. The regulatory requirements, staffing models, patient acuity, and types of violations differ drastically between these populations.

### Impact on Results

The `04_crosswalk_results.md` facility type table shows:
- CA: 17.5% "Intermediate Care / Residential" (3,200 violations)
- OR: 71.3% "Intermediate Care / Residential" (29,199 violations)

This comparison is meaningless. California's 3,200 violations are from DD care facilities. Oregon's 29,199 are from elderly assisted living. Comparing these numbers teaches you nothing about either state's regulatory performance.

---

## Flaw 2: Oregon Adult Foster Homes Have No CA Equivalent

Oregon's dataset includes **Adult Foster Homes (AFH)** -- small, individually-operated residences (typically 1-5 residents) run out of a person's home. There are **1,732 distinct AFH providers** in Oregon's data.

California does not regulate an equivalent facility type in this dataset. The crosswalk acknowledges this by mapping AFH to its own category ("Adult Foster Home"), but then proceeds to include AFH violations in aggregate state-level comparisons without adjusting for this.

Oregon has 1,732 AFH facilities contributing 6,657 violations. These are micro-scale operations where a single missed medication or a single documentation lapse generates a violation. Including them in per-state totals inflates Oregon's numbers against California, which has no comparable micro-facility category.

---

## Flaw 3: CA SNF != OR NF (Subtler but Real)

The report treats California's **Skilled Nursing Facility (SNF)** as equivalent to Oregon's **Nursing Facility (NF)**, mapping both to "Nursing Facility." While these are the closest match in the data, they are not identical:

- **SNF** (federal Medicare definition): Provides skilled nursing care and rehabilitation services. Requires daily skilled care from licensed nurses or therapists. Medicare-certified.
- **NF** (federal Medicaid definition): Provides custodial/nursing care to Medicaid-eligible individuals. May not require daily skilled care.
- **SNF/NF (dual-certified)**: Many facilities hold both designations.

The distinction matters because SNFs tend to have higher-acuity patients, stricter staffing requirements, and more clinical violations. NFs may have more custodial-care violations. Comparing violation rates between SNFs and NFs without acknowledging this conflates two different tiers of care.

---

## Flaw 4: The LTC Filter Ignores California's Own LTC Column

California's data includes an explicit `LTC` column with values `"LTC"` and `"Non-LTC"`. The crosswalk queries ignore this column entirely, instead manually filtering by `FAC_TYPE_CODE IN ('SNF', 'ICF', 'ICFDDH', 'ICFDDN', 'ICFDD', 'CLHF')`.

This ad-hoc filter:
- **Misses `PDHRCF`** (Pediatric Day Health & Respite Care Facility), which is flagged `LTC` in the data (8 rows -- minor but sloppy).
- **Relies on the analyst's judgment** about which codes are "long-term care" rather than using the authoritative flag the data provider included for exactly this purpose.

The correct approach is `WHERE LTC = 'LTC'`, which is both simpler and authoritative.

---

## Bottom Line

The "harmonized" facility type categories create an illusion of comparability where none exists. The only genuinely comparable pair is CA SNF vs. OR NF, and even that has caveats. Any analysis using the broader "Intermediate Care / Residential" category is comparing developmentally disabled care to elderly assisted living -- a comparison that would not survive peer review.

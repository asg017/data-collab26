# CRITICAL ANALYSIS: Flawed Per-Capita Reasoning and Missing Normalization

## Severity: MEDIUM-HIGH -- Conclusions Are Unsupported

The reports repeatedly gesture at population-based normalization but never actually perform it correctly, and when they do reference population, they use the wrong denominator entirely.

---

## Flaw 1: Per-Capita Is the Wrong Metric

The `01_matching_analysis.md` report states:

> "Oregon records significantly more violations per year despite being a much smaller state (4.2M vs 39M population). This likely reflects differences in reporting scope and regulatory thresholds, not actual violation rates."

And later recommends:

> "Normalize by state population or facility count."

**Per-capita normalization is misleading here.** Violations don't happen to the general population -- they happen at facilities. A state's violation count is driven by:

1. **Number of facilities** (more facilities = more opportunities for violations)
2. **Number of beds/residents** (larger facilities = more potential violations per facility)
3. **Inspection frequency** (more inspections = more violations found)
4. **Regulatory scope** (what counts as a violation varies by state)
5. **Reporting practices** (substantiated vs. all complaints)

The correct denominators are **per-facility** or **per-licensed-bed**, neither of which is available in these datasets. Using state population creates an illusion of Oregon being a wildly more dangerous place to receive care, when the actual driver is likely Oregon's much broader regulatory scope (covering AFHs, ALFs, and RCFs that California doesn't track in this dataset).

### Actual Numbers (2010-2023)

| Metric | California (LTC) | Oregon (All) |
|---|---|---|
| Total violations | 17,252 | 39,002 |
| Distinct facilities | 1,651 | 2,345 |
| Violations per facility | 10.4 | 16.6 |
| Per 100K population | 44.2 | 928.6 |

The per-capita figure (928.6 vs. 44.2 -- a **21x difference**) is shocking but meaningless. Oregon has more facilities per capita (especially thousands of tiny AFHs), each generating violations. The per-facility rate is only 1.6x, and even that is inflated by Oregon's inclusion of AFHs (4.2 violations/facility) alongside larger operations.

When you look at just nursing facilities -- the only truly comparable type:

| State | NF Violations | NF Facilities | Violations/Facility |
|---|---|---|---|
| OR NF | 7,332 | 143 | 51.3 |

California SNF data would need similar computation, but the point stands: per-capita is a distortion.

---

## Flaw 2: Population Numbers Are Static, But the Data Spans 14 Years

The report uses **a single population figure** for each state (CA: 39M, OR: 4.2M) for a dataset spanning 2010-2024. But:

- CA population: 37.3M (2010 census) -> 39.5M (2020 census) -> ~38.9M (2024 estimate, post-pandemic decline)
- OR population: 3.8M (2010) -> 4.2M (2020) -> ~4.3M (2024)

Using a single number for a 14-year span introduces up to a ~5% error for CA and ~10% for OR. If you're going to do per-capita (which you shouldn't -- see above), at minimum use year-matched population estimates.

---

## Flaw 3: The 2024 Year-Over-Year Table Is Misleading

The table in `01_matching_analysis.md` includes 2024 data showing:
- CA: 670 violations
- OR: 4,008 violations

But California's data **ends at June 17, 2024** while Oregon's data **extends to February 2026**. The 2024 row is comparing ~5.5 months of CA data to **12 full months** of OR data. Oregon's 2024 breaks down as:

| Period | OR Violations |
|---|---|
| 2024 H1 (Jan-Jun) | 1,978 |
| 2024 H2 (Jul-Dec) | 2,030 |

A fair H1-only comparison would be CA: 670 vs OR: 1,978 -- still a large gap, but less than half the reported disparity.

The report acknowledges the need to filter to the overlapping period but then **includes the unfiltered 2024 data in its year-by-year table** without any caveat on that specific row. A reader scanning the table would take the 670 vs. 4,008 comparison at face value.

---

## Flaw 4: No Facility Count Normalization Is Attempted Anywhere

Despite recommending per-facility normalization, the report never:

- Counts facilities per state per year
- Computes violations-per-facility trends
- Accounts for facilities opening/closing over the 14-year span
- Considers that Oregon's facility count may have grown (explaining the 3x volume increase 2010-2023)

The year-over-year trend (Oregon nearly tripling from 1,384 to 3,893) is presented without asking: did Oregon get 3x more dangerous, or did Oregon add facilities to its regulatory scope, increase inspection frequency, or change its reporting threshold? Without facility-count denominators, this question cannot be answered from the data.

---

## Bottom Line

The report's population-based framing leads readers toward a conclusion ("Oregon is worse") that the data cannot support. The 21x per-capita disparity is an artifact of comparing different facility universes with a denominator (state population) that has no causal relationship to violation counts. Any published version of this analysis needs to either use per-facility rates or explicitly state that raw counts cannot be compared between states.

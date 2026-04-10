# Matching Analysis: Can These Datasets Be Combined?

## Summary

These two datasets track **health facility regulatory outcomes** but represent fundamentally different things: California records **enforcement actions** (penalties/citations issued), while Oregon records **substantiated findings** (violations and abuse confirmed through investigation). They cannot be joined row-to-row, and even aggregate comparison requires careful attention to what each dataset actually measures.

---

## 1. No Record-Level Matching Is Possible

**No shared identifiers exist:**

- **Facility IDs**: CA uses 9-digit `FACID` from ELMS. OR uses mixed-format `Provider ID` from CALMS. No overlap.
- **Facility names**: Zero exact matches. Different states, different facilities. (Oregon AFH names are often *personal names* of individual providers, not facility names.)
- **Case/report numbers**: CA uses `PENALTY_NUMBER` / `EVENTID`. OR uses `CALMS` report numbers. No overlap.

**Conclusion**: Row-level joins are impossible and meaningless -- these are entirely different facilities.

---

## 2. The Core Comparability Problem: Different Units of Measurement

This is the most important finding, and it was **not apparent before reviewing the data dictionaries**.

### California: Enforcement Actions

Each CA row is a **penalty or citation issued by CDPH**. The path is:

```
Complaint/Survey → Investigation → Violation Found → Enforcement Action Issued → (Appeal) → Closed
```

- A single investigation (`EVENTID`) can produce multiple enforcement actions
- Records include both open (appealable) and closed (final) actions
- The dataset captures the *regulatory response*, not the underlying finding
- There is **no direct abuse substantiation** -- CA's "Abuse/Facility Not Self Reported" category is about the *facility's failure to report* adverse events, not about abuse findings themselves

### Oregon: Substantiated Findings

Each OR row is a **substantiated violation or abuse finding**. The path is:

```
Complaint → Investigation → Finding: Substantiated/Unsubstantiated/Inconclusive → (If substantiated) → Published
```

- Only substantiated findings appear; open investigations and appeals are excluded
- The dataset captures the *investigation outcome*, not the regulatory response
- Financial penalties exist in a separate Regulatory Actions dataset (only 1,289 records, acknowledged as incomplete)
- Abuse is a distinct legal finding under OAR 411-020-0002, not just a violation category

### Why This Matters

| Scenario | CA records it as... | OR records it as... |
|---|---|---|
| Facility fails to give medication | Citation B for "Medication" (if cited) | "Licensing Violation" + "Failed to administer medication as ordered" |
| Neglect causes patient harm | Citation A or AA for "Patient Care" | "Abuse: Neglect" + specific allegation |
| Facility fails to report a death | "Failure to Report Penalty" (FTR AE) | May not appear at all (different reporting framework) |
| Staffing below required hours | Admin Penalty for NHPPD (HSC 1276.5) | "Licensing Violation" + "Failed to provide appropriate staffing" |
| Abuse allegation investigated, substantiated | May or may not result in a citation | "Abuse: [subtype]" record published |
| Abuse allegation investigated, NOT substantiated | No record | No record |
| Citation issued but appealed and overturned | Record exists (DISPOSITION = Closed, modified amounts) | No record (excluded during appeal) |

**A 1:1 mapping between "one CA enforcement action" and "one OR substantiated finding" does not exist.** The datasets measure different stages of the regulatory pipeline.

---

## 3. What CAN Be Compared (With Caveats)

Despite the structural differences, **aggregate trend and proportional analysis** is possible if you clearly define what you're measuring.

### 3a. Facility Type Crosswalk

| Comparison Category | California (filter: `LTC = 'LTC'`) | Oregon |
|---|---|---|
| Nursing Facility | SNF (Skilled Nursing Facility) -- 29,072 records | NF (Nursing Facility) -- 8,257 records |
| Residential/Intermediate Care | ICF, ICFDDH, ICFDDN, ICFDD -- 5,364 records | ALF + RCF -- 29,199 records |
| Congregate/Group Living | CLHF -- 552 records | AFH (Adult Foster Home) -- 8,115 records |

**Best match**: SNF ↔ NF. Both are nursing facilities subject to federal recertification requirements. This is the cleanest comparison.

**Poor match**: CA's ICF types vs OR's ALF/RCF/AFH. These serve overlapping but different populations under different regulatory frameworks. OR's AFH (individual providers caring for 1-5 residents) has no CA equivalent in this dataset.

**Recommendation**: Compare only **SNF (CA) vs NF (OR)** for the most defensible analysis. Use the explicit `LTC = 'LTC'` filter rather than guessing from facility type codes.

### 3b. Violation Category Crosswalk

Oregon's allegation field is a **fixed dropdown of ~90 options**, not free text. This makes keyword-based mapping more reliable than initially assumed. However, the same allegation can appear under either "Licensing Violation" or an abuse type, so the mapping must account for both the `Type` and `Allegation` fields.

| Harmonized Category | CA (`PENALTY_CATEGORY`) | OR (`Allegation` keywords) | Quality of Match |
|---|---|---|---|
| Care Quality | Patient Care (16,590) | care plan, plan care, provide service, condition changed | Moderate -- CA's category is very broad |
| Medication | Medication (948) | medication, ordered medication | Good |
| Resident Rights | Patient Rights (6,192) | resident rights | Good |
| Staffing | Staffing (432) + DHPPD categories (2,086) | staffing, ABST | Moderate -- CA splits regulatory (DHPPD) from general staffing |
| Environment/Safety | Physical Environment (794) | safe environment, physical environment, door alarm, fire | Good |
| Dietary | Dietary (162) | diet, nutrition, food, hydration | Good |
| Records/Admin | Administration (1,134) + Patient Record (198) | record, falsified, documentation | Good |
| Falls | AE22 (74) | falls | Good but small volume in CA |
| Abuse/Neglect | **No direct equivalent** (see below) | `Type` LIKE 'Abuse:%' (19,297) | **Poor** |
| Failure to Report | Failure to Report Penalty (3,910) | report potential or suspected abuse (775) | Poor -- different reporting obligations |
| Privacy/Data Breach | Breach categories (2,118) | No equivalent | **No match** |
| Adverse Events | AE categories (3,596) | No equivalent | **No match** |

### 3c. The Abuse Problem (Critical)

**CA's dataset does not directly track abuse findings.** The `PENALTY_CATEGORY` value "Abuse/Facility Not Self Reported" (3,120 records) means the facility **failed to self-report** an adverse event -- it is NOT a finding that abuse occurred. CA tracks abuse investigations through a different system (the complaint intake process), not through enforcement actions.

**OR's dataset explicitly tracks abuse findings.** 19,297 records (42% of the dataset) are substantiated abuse under OAR 411-020, with legal definitions for each subtype (Neglect, Physical, Sexual, Financial, etc.).

**This means**: Any analysis comparing "abuse rates" between the two states would be comparing fundamentally different things. CA's number would represent *facilities penalized for not reporting*, while OR's number would represent *substantiated abuse findings*. These are not equivalent and should NOT be compared directly.

### 3d. Overlapping Time Period

- **California**: 1994 -- 2024 (violation dates)
- **Oregon**: 2010 -- 2026 (substantiated finding dates)
- **Overlap**: **2010-01-01 through 2024-06-30**

| Year | CA (LTC only) | OR (all) | Notes |
|---|---|---|---|
| 2010 | 2,050 | 1,384 | |
| 2011 | 1,694 | 1,289 | |
| 2012 | 1,164 | 1,315 | |
| 2013 | 1,126 | 1,543 | |
| 2014 | 1,260 | 1,910 | |
| 2015 | 1,384 | 2,226 | |
| 2016 | 1,430 | 2,924 | |
| 2017 | 1,596 | 3,983 | |
| 2018 | 1,688 | 3,802 | |
| 2019 | 2,180 | 3,645 | |
| 2020 | 1,742 | 3,160 | COVID impact in both states |
| 2021 | 1,240 | 3,640 | |
| 2022 | 1,464 | 4,288 | |
| 2023 | 1,840 | 3,893 | |
| 2024 | 670 | 4,008 | CA data ends mid-year |

Oregon records 2-3x more findings despite having ~1/9th of CA's population. This does NOT indicate worse care in Oregon -- it reflects:
- Different regulatory thresholds and enforcement philosophies
- OR includes all substantiated findings; CA only includes findings that result in formal enforcement actions
- OR's dataset includes abuse findings; CA's does not
- OR's scope includes AFH (small individual providers) which generate many findings

---

## 4. Recommended Comparison Approaches

### Approach A: Nursing Facility Only, Trend Comparison (Best)

Filter CA to `LTC = 'LTC' AND FAC_TYPE_CODE = 'SNF'` and OR to `Provider type = 'NF'`. Compare year-over-year trends in volume (not absolute numbers). Both facility types are subject to federal requirements, making this the most apples-to-apples comparison.

### Approach B: Violation Category Proportions (Good with Caveats)

Compare *what proportion* of each state's findings fall into each harmonized category. This controls for volume differences and reveals whether the states have similar violation profiles. Exclude abuse categories from the comparison (see Section 3c).

### Approach C: Repeat Offender Analysis (Good, Within-State Only)

Identify high-violation facilities within each state and compare the *distribution shape* (e.g., what % of facilities account for what % of violations). Do not compare specific facilities across states.

### Approach D: COVID Impact Analysis (Interesting)

Both datasets show 2020-2021 disruption. Compare the magnitude and timing of the COVID dip/recovery between states as a natural experiment.

---

## 5. What Should NOT Be Compared

| Comparison | Why Not |
|---|---|
| Absolute violation counts between states | Different units of measurement (enforcement actions vs. findings) |
| "Abuse rates" between states | CA doesn't track abuse findings in this dataset |
| Financial penalties | OR's violation data has no penalty amounts (separate incomplete dataset) |
| Severity levels | OR has no severity classification |
| Per-facility violation rates across states | Different facility type mixes and regulatory scopes |

---

## 6. Verdict

| Question | Answer |
|---|---|
| Can these be joined row-to-row? | **No** -- different states, no shared keys |
| Do they measure the same thing? | **No** -- CA measures enforcement actions, OR measures substantiated findings |
| Can they be stacked into a common schema? | **Partially** -- facility type and some violation categories can be harmonized, but abuse data cannot |
| Is the comparison fair out-of-the-box? | **No** -- requires filtering to SNF/NF, excluding abuse categories, and comparing proportions/trends rather than absolutes |
| Is this worth pursuing? | **Yes, if** (1) you limit to nursing facilities, (2) you compare trends and proportions rather than absolute numbers, (3) you clearly document that the datasets measure different regulatory stages, and (4) you exclude abuse-related categories from cross-state comparison |

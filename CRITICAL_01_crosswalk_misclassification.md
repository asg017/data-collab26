# CRITICAL ANALYSIS: Crosswalk Misclassification Bug

## Severity: HIGH -- Invalidates Core Findings

The harmonized violation category crosswalk in `03_crosswalk_queries.sql` contains a **SQL CASE statement ordering bug** that silently misclassifies **76.7% of Oregon abuse records** into non-abuse categories. This fundamentally corrupts the cross-state comparison that the entire analysis is built around.

---

## The Bug

In the Oregon harmonized view (lines 100-125 of `03_crosswalk_queries.sql`), the `CASE` statement for `violation_category_harmonized` checks keyword matches on the `Allegation` field **before** checking the `Type` field for `'Abuse:*'`. Because SQL `CASE` evaluates top-to-bottom and returns the **first** match, any abuse record whose allegation text contains keywords like "medication", "safe environment", "care plan", etc. gets classified by those keywords rather than by its abuse designation.

### Example

A row with:
- `Type` = `"Abuse: Physical Abuse"`
- `Allegation` = `"Failed to provide safe environment"`

Gets classified as **"Environment/Safety"** rather than **"Abuse/Neglect"** because the `'safe environment'` keyword check (line 111) fires before the `Type LIKE 'Abuse:%'` check (line 123).

### Scale of the Problem

| Metric | Value |
|---|---|
| Total Oregon `Type = 'Abuse:*'` rows | 19,297 |
| Correctly classified as Abuse/Neglect | 4,495 |
| **Misclassified into other categories** | **14,802 (76.7%)** |

### Where the Misclassified Abuse Records Went

| Received Category | Abuse Records Absorbed |
|---|---|
| Care Quality | 6,260 |
| Environment/Safety | 5,295 |
| Medication | 2,825 |
| Resident Rights | 320 |
| Staffing | 63 |
| Dietary | 37 |
| Administration/Records | 2 |

### Impact on Reported Results

The `04_crosswalk_results.md` report states:

> "Abuse/Neglect is comparable (~13% CA, ~12% OR) -- this is the most structurally similar category since both states track it as a distinct concept."

This finding is **wrong**. Oregon's true abuse rate is far higher than reported. With correct classification:

- **Reported OR Abuse/Neglect**: ~4,797 (11.7%)
- **Actual OR Abuse/Neglect** (if `Type` checked first): ~19,297 (47.1% of all OR records)

The claim that abuse rates are "comparable" between states collapses entirely.

### Fix

The `Type LIKE 'Abuse:%'` check must be moved to the **top** of the `CASE` statement, or the logic must use a two-pass approach: first classify by `Type`, then fall through to keyword matching only for `Licensing Violation` rows.

```sql
-- Fixed: check Type FIRST
CASE
    WHEN "Type" LIKE 'Abuse:%' THEN 'Abuse/Neglect'
    WHEN lower("Allegation") LIKE '%medication%' THEN 'Medication'
    -- ... remaining keyword checks ...
END AS violation_category_harmonized
```

---

## Broader Implication

Every downstream number in the category distribution table (`04_crosswalk_results.md`) is corrupted by this bug. The Environment/Safety, Care Quality, and Medication categories for Oregon are all inflated by thousands of misrouted abuse records. No cross-state category comparison from this analysis should be cited without first fixing the CASE ordering.

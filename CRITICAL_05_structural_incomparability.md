# CRITICAL ANALYSIS: Fundamental Structural Incomparability

## Severity: HIGH -- The Comparison Framework Itself Is Flawed

Beyond the specific bugs in the crosswalk SQL, there are deeper structural problems with comparing these two datasets that the report acknowledges in passing but then proceeds to ignore in its analysis and recommendations.

---

## Flaw 1: The Datasets Measure Different Things

**California**: "Health Facilities State Enforcement Actions" -- these are **enforcement actions** (citations, administrative penalties, failure-to-report penalties). Each row represents a formal enforcement outcome with a penalty type, severity class, and dollar amount. This is the **end of a regulatory process**: inspection -> finding -> enforcement.

**Oregon**: "Licensing violations and substantiated abuse" -- these are **findings** (licensing violations and substantiated abuse allegations). Each row represents a determination that a violation occurred or that abuse was substantiated. This may or may not lead to enforcement.

The distinction matters enormously:
- California: One inspection might find 5 problems but result in only 1 enforcement action (the most serious). The other 4 problems might generate warnings, corrective action plans, or no formal action.
- Oregon: The same inspection might generate 5 separate violation records.

Comparing row counts between these datasets is comparing **enforcement actions** to **findings** -- fundamentally different units of measurement. The report never addresses this distinction.

---

## Flaw 2: Different Regulatory Scopes Are Not Just a Filter Problem

The report's solution to Oregon including ALFs/RCFs/AFHs (which CA doesn't cover) is to filter California to "long-term care only." But:

1. **CA's filtered LTC set is still broader than OR's**: CA includes ICFDDH/ICFDDN/ICFDD (developmentally disabled facilities) which have no Oregon equivalent. Oregon's RCFs/ALFs serve elderly populations.

2. **OR's data excludes categories CA includes**: California tracks hospitals (GACH), home health agencies (HHA), hospices, and clinics. Oregon's dataset is limited to NF, ALF, RCF, and AFH. There is no way to create a symmetric comparison -- each state covers facility types the other doesn't.

3. **The "fair comparison" filter doesn't make it fair**: Even after filtering CA to LTC, you're comparing:
   - CA: 1,651 facilities (almost all institutional, 50+ beds)
   - OR: 2,345 facilities (including 1,732 tiny Adult Foster Homes with 1-5 residents)

The comparison should be restricted to CA SNF vs. OR NF **only** -- the single facility type pair with genuine equivalence. This would reduce the usable dataset dramatically but produce honest results.

---

## Flaw 3: Oregon's Abuse Data Is Structurally Different

Oregon explicitly tracks **abuse subtypes** as a first-class concept in the `Type` field:
- Abuse: Physical Abuse
- Abuse: Sexual Abuse / Sexual abuse
- Abuse: Verbal Abuse / Verbal/Mental abuse
- Abuse: Financial Exploitation / Financial abuse
- Abuse: Neglect
- Abuse: Involuntary Seclusion
- Abuse: Restraints / Wrongful Restraint
- Abuse: Abandonment

California tracks abuse as a **penalty category** (`"Abuse/Facility Not Self Reported"`) without subtypes. CA also has adverse event codes (AE26 = sexual assault, AE27 = physical assault) that represent abuse but are classified separately.

This means:
- Oregon may record the **same incident** as both a Licensing Violation and an Abuse finding (two rows)
- California records a single enforcement action with one penalty category

The report does not investigate whether Oregon's data contains such duplicates. If it does, Oregon's abuse counts are inflated by double-counting.

---

## Flaw 4: California Has Severity Data That Is Completely Ignored in Comparison

California provides:
- Severity class (A = serious, AA = most serious, B = moderate)
- Dollar penalty amounts
- Death-related flag
- Appeal outcomes

Oregon provides none of these. The report's recommended "Approach A: Side-by-Side Aggregate Comparison" treats all violations as equal. But a CA Class AA citation with a $100,000 penalty and a death flag is categorically different from an OR licensing violation for "Failed to provide a homelike environment."

Any meaningful comparison should either:
- Weight CA violations by severity, or
- Restrict CA to Class A/AA violations only (serious/most serious) to approximate Oregon's threshold for recording violations

---

## Flaw 5: Inconsistent Case Sensitivity in OR Abuse Type Values

Oregon's `Type` field contains inconsistent values that the crosswalk doesn't account for:
- `"Abuse: Sexual Abuse"` vs. `"Abuse: Sexual abuse"`
- `"Abuse: Verbal Abuse"` vs. `"Abuse: Verbal/Mental abuse"`
- `"Abuse: Financial Exploitation"` vs. `"Abuse: Financial abuse"`

The `LIKE 'Abuse:%'` pattern catches all of these (it's case-sensitive and they all start with capital "Abuse:"), but any downstream analysis that groups by exact `Type` value will split what should be single categories into duplicates. The report mentions none of this.

---

## Flaw 6: No Discussion of Inspection Frequency or Methodology

The single largest driver of violation counts is **how often and how thoroughly facilities are inspected**. A state that inspects every facility annually will find more violations than a state that inspects every 2-3 years. A state that does complaint-driven inspections will have a different violation profile than one doing routine surveys.

The report never asks:
- How often does each state inspect facilities?
- Are these datasets populated from routine inspections, complaint investigations, or both?
- Did inspection frequency change over time (e.g., during COVID)?
- Does Oregon's 3x increase in violations (2010-2023) reflect an increase in inspections or an increase in actual problems?

Without this context, year-over-year trends are uninterpretable.

---

## Bottom Line

These datasets were collected by different agencies, under different state laws, using different definitions, different reporting thresholds, and different units of measurement. The report's framework of "harmonize and compare" understates how fundamentally non-comparable these datasets are. The only defensible cross-state analysis would be narrowly scoped to CA SNF vs. OR NF, restricted to a specific violation category (e.g., abuse), with explicit caveats about every assumption. The broad-spectrum comparison the report proposes would not withstand scrutiny.

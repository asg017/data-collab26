# CRITICAL ANALYSIS: Oregon Keyword-Based Classification Is Unreliable

## Severity: MEDIUM -- Produces Systematically Biased Categories

The Oregon violation category crosswalk relies on substring keyword matching against free-text `Allegation` fields. This approach has multiple failure modes that produce biased, inaccurate category distributions.

---

## Flaw 1: "Food Safety" Classified as Environment/Safety Instead of Dietary

The `CASE` statement checks for `'safety'` in the Environment/Safety branch (line 112):

```sql
WHEN lower("Allegation") LIKE '%safe environment%'
  OR lower("Allegation") LIKE '%fire%'
  OR lower("Allegation") LIKE '%safety%' THEN 'Environment/Safety'
```

This catches `"Failed to assure food safety"` (61 rows) and routes it to Environment/Safety instead of Dietary, where it belongs. The Dietary check (`'%diet%' OR '%nutrition%' OR '%food%'`) appears later and never gets a chance to match these rows.

---

## Flaw 2: "Safe Physical Environment" Misses the Environment/Safety Category

The keyword `'safe environment'` does not match the allegation `"Failed to maintain a safe physical environment"` (312 rows) because the word `"physical"` sits between `"safe"` and `"environment"`. These 312 rows fall through to **Other**.

However, they ARE caught by the broader `'%safety%'` pattern. So the logic works by accident via a different keyword than intended, masking the gap. If `'%safety%'` were ever removed or reordered, these 312 rows would silently disappear from Environment/Safety.

---

## Flaw 3: Massive "Other" Bucket Contains Clearly Classifiable Violations

6,198 Oregon records (13.6%) land in "Other." Inspection of the top allegations in this bucket reveals that many are easily classifiable:

| Allegation | Count | Should Be |
|---|---|---|
| Failed to use an ABST | 526 | Staffing/Training or Administration |
| Failed to assure a qualified caregiver was present | 419 | Staffing |
| Failed to assure that a qualified caregiver was present | 342 | Staffing |
| Failed to answer call light in a timely manner | 339 | Care Quality |
| Failed to provide medical treatment as ordered | 287 | Care Quality |
| Failed to maintain a safe physical environment | 283 | Environment/Safety (caught by 'safety' keyword but only by coincidence) |
| Failed to assure resident was safe | 278 | Environment/Safety or Care Quality |
| Failed to hire according to administrative rules | 273 | Staffing/Administration |
| Failed to address resident's behavior | 220 | Care Quality |
| Failed to provide appropriate housekeeping services | 200 | Environment/Safety |
| Failed to assist with toileting | 192 | Care Quality |
| Failed to perform adequate screening or assessment | 171 | Care Quality |
| Failed to provide or assist with hygiene | 169 | Care Quality |
| Failed to provide appropriate skin care | 153 | Care Quality |
| Failed to provide infection control | 138 | Environment/Safety |

Just the top 15 "Other" allegations account for **3,990 rows** that could be classified with better keyword patterns. The report acknowledges the 17-21% "Other" rate but dismisses it as "imperfect" rather than recognizing that it systematically undercounts Care Quality and Staffing.

---

## Flaw 4: "Staffing" Keyword Is Too Narrow

The keyword `'staffing'` (line 109) only matches allegations that literally contain the word "staffing." But common staffing-related violations use different language:

- `"Failed to assure a qualified caregiver was present"` (419 + 342 = 761 rows)
- `"Failed to hire according to administrative rules"` (273 rows)

These 1,034 rows represent nearly as many violations as the 2,814 that do match `'staffing'`, meaning the Staffing category is undercounted by roughly 37%.

---

## Flaw 5: No Validation Against Known Distributions

The report presents the keyword-classified distribution as findings without any validation step. Standard practice would be to:

1. Manually classify a random sample of 100-200 Oregon allegations
2. Compare manual classifications to the keyword-based classifications
3. Report a precision/recall score for each category
4. Identify systematic misclassification patterns

None of this was done. The crosswalk was built by inspection and deployed without testing.

---

## Flaw 6: Oregon Has Only 98 Unique Allegations

Oregon's `Allegation` field contains only **98 distinct values** across 45,571 rows. This is a controlled vocabulary, not truly free text. The report describes it as "free-text allegations" (line 78 of `00_data_overview.md`), which implies unstructured data requiring NLP.

In reality, 98 distinct values is small enough to map **exhaustively** with a lookup table rather than relying on brittle keyword matching. A complete lookup table would eliminate the "Other" bucket entirely and produce exact category mappings. The keyword approach was an unnecessarily lossy solution to a tractable problem.

---

## Bottom Line

The keyword-based classification introduces systematic bias: it undercounts Staffing and Care Quality, misroutes food safety to Environment/Safety, and leaves 13.6% of records uncategorized despite having a closed vocabulary of only 98 distinct allegations. The entire Oregon category distribution in `04_crosswalk_results.md` should be treated as approximate at best.

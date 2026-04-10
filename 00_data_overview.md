# Data Overview: California & Oregon Health Facility Enforcement Data

## California (`california.csv`)

- **Source**: Health Facilities State Enforcement Actions (CA Dept. of Public Health, Center for Health Care Quality, Licensing & Certification Program)
- **System of record**: Electronic Licensing Management System (ELMS)
- **Rows**: 41,098 enforcement actions
- **Distinct Facilities**: 2,709 (identified by `FACID`)
- **Date Range**: 1994-01-12 to 2024-06-17 (violation dates)
- **Columns**: 32

### What This Dataset Represents

Each row is a **state enforcement action** -- a citation or penalty issued to a California healthcare facility. This is the *regulatory response* to a violation, not the violation investigation itself. A single survey/investigation (`EVENTID`) can produce multiple enforcement actions. Enforcement actions may be open (still appealable) or closed (final).

### Key Fields (per data dictionary)

| Field | Description |
|---|---|
| `FACID` | 9-digit facility identifier; primary key from ELMS FACILITY table. Links to other CDPH open data files (Healthcare Facility Services, Bed Types and Counts) |
| `FACILITY_NAME` | From facility's license application |
| `LTC` | **"LTC"** = long-term care, **"Non-LTC"** = non-long-term care. Explicit flag -- no need to infer from facility type |
| `FAC_TYPE_CODE` | Facility type acronym (see lookup table) |
| `FAC_FDR` | Facility type roll-up used in L&C Fee Development Report |
| `PENALTY_TYPE` | **Citation** (HSC 1424), **Administrative Penalty** (HSC 1276.5/1280.3/1280.15), or **Failure to Report Penalty** (HSC 1280.4/1280.15) |
| `PENALTY_DETAIL` | Specific HSC code reference and enforcement type (e.g., "Citation B (HSC 1424)") |
| `CLASS_ASSESSED_INITIAL` | Severity class at issuance: **AA** (most serious), **A** (serious), **B** (moderate), **AP IJ** (admin penalty - immediate jeopardy), **AP NON-IJ**, **AP NHPPD** (staffing hours), **FTR AE/BR/RES** (failure to report subtypes) |
| `PENALTY_CATEGORY` | Violation category (Patient Care, Patient Rights, Medication, etc.) |
| `DISPOSITION` | **Open** (appealable) or **Closed** (final/paid). 38,594 closed, 2,504 open |
| `APPEALED` | Whether the facility appealed the enforcement action |
| `TOTAL_AMOUNT_INITIAL` | Original penalty amount |
| `TOTAL_AMOUNT_DUE_FINAL` | Final penalty after appeals, offsets, or trebling |
| `TOTAL_PENALTY_OFFSET_AMOUNT` | Reductions: 35% early-pay discount (HSC 1428.1), appeal settlements, bankruptcy, closures |
| `DEATH_RELATED` | Whether the *investigation* (not just the violation) is related to a patient death |
| `EVENTID` | Survey/investigation ID. Multiple complaints can be investigated in one survey |
| `INTAKEID_ALL` | Complaint intake IDs. Blank = relicensure/recertification visit (not complaint-driven) |
| `PRIORITY_ALL` | Complaint intake priority |
| `SFY` | State Fiscal Year based on penalty issue date |

### Enforcement Action Types (from PENALTY_DETAIL)

| Type | HSC Reference | Count | Description |
|---|---|---|---|
| Citation B | HSC 1424 | 25,108 | Moderate violation |
| Citation A | HSC 1424 | 6,648 | Serious violation |
| Citation AA | HSC 1424 | 828 | Most serious violation |
| Citation WF | HSC 1424(f)(1) | 208 | Willful Material Falsification |
| Citation WO | HSC 1424(f)(1) | 16 | Willful Material Omission |
| Citation RD | HSC 1432 | 12 | Retaliation/Discrimination |
| AP - NHPPD | HSC 1276.5 | 2,086 | Staffing hours (3.2 nursing-hours-per-patient-day) |
| AP - IJ | HSC 1280.3 | 1,128 | Immediate Jeopardy |
| AP - Non-IJ | HSC 1280.3 | 510 | Non-Immediate Jeopardy |
| AP - Breach | HSC 1280.15 | 610 | Patient data breach |
| FTR - AE | HSC 1280.4 | 2,370 | Failure to report adverse event to CDPH |
| FTR - Breach CDPH | HSC 1280.15(b)(1) | 1,086 | Failure to report breach to CDPH |
| FTR - Breach Resident | HSC 1280.15(b)(2) | 454 | Failure to report breach to affected resident |

### Facility Types

| LTC | Code | Description | Count |
|---|---|---|---|
| LTC | SNF | Skilled Nursing Facility | 29,072 |
| LTC | ICFDDH | Intermediate Care Facility - DD/H | 2,810 |
| LTC | ICFDDN | Intermediate Care Facility - DD/N | 1,386 |
| LTC | ICFDD | Intermediate Care Facility - DD | 834 |
| LTC | CLHF | Congregate Living Health Facility | 552 |
| LTC | ICF | Intermediate Care Facility | 334 |
| LTC | PDHRCF | Pediatric Day Health & Respite Care | 8 |
| Non-LTC | GACH | General Acute Care Hospital | 5,810 |
| Non-LTC | APH | Acute Psychiatric Hospital | 80 |
| Non-LTC | COMTYC | Primary Care Clinic | 86 |
| Non-LTC | HHA | Home Health Agency | 66 |
| Non-LTC | HOSPICE | Hospice | 32 |
| Non-LTC | Others | CTC, ESRD/CDC, SPHOSP, ASC | 26 |

---

## Oregon (`oregon.csv`)

- **Source**: Oregon Department of Human Services (ODHS), Long-Term Care Licensing website (ltclicensing.oregon.gov)
- **System of record**: CALMS (report numbers prefixed "CALMS -")
- **Rows**: 45,571 substantiated violations
- **Distinct Providers**: 2,483
- **Date Range**: 2010-01-01 to 2026-02-26
- **Columns**: 7

### What This Dataset Represents

Each row is a **substantiated finding** -- either a substantiated licensing violation or a substantiated instance of abuse. Only final findings appear; open investigations and appealed findings are excluded. This is fundamentally different from CA's dataset, which tracks *enforcement actions* (penalties/citations) rather than *investigation findings*.

### Key Fields (per Oregon website)

| Field | Description |
|---|---|
| `Date` | Date of the substantiated finding |
| `Provider ID` | Provider identifier (mixed formats: numeric, alphanumeric) |
| `Name` | Provider or individual name (AFH names are often personal names, not facility names) |
| `Provider type` | NF, ALF, RCF, or AFH |
| `Report number` | CALMS investigation report ID |
| `Allegation` | Specific allegation from a fixed dropdown of ~90 options (NOT free text) |
| `Type` | "Licensing Violation" or one of 11 abuse subtypes |

### Violation Types (from Oregon website and OAR 411-020-0002)

**Licensing Violation** (26,274 records): A substantiated finding that the provider failed to comply with licensing rules/laws.

**Abuse subtypes** (19,297 records total), legally defined under OAR 411-020-0002:

| Type | Count | Legal Definition |
|---|---|---|
| Abuse: Neglect | 16,473 | Active or passive failure to provide basic care/services necessary for health and safety |
| Abuse: Financial abuse | 1,730 | Wrongfully taking money, property, assets, or medications |
| Abuse: Verbal/Mental abuse | 437 | Threats, intimidation, humiliation, harassment causing emotional harm |
| Abuse: Physical Abuse | 349 | Non-accidental injury resulting in pain, impairment, or bodily injury |
| Abuse: Sexual abuse | 115 | Sexual contact with non-consenting adult, harassment, exploitation |
| Abuse: Involuntary Seclusion | 55 | Confining/isolating or restricting communication for convenience or discipline |
| Abuse: Restraints | 52 | Wrongful use of physical or chemical restraint |
| Abuse: Verbal Abuse | 27 | *(appears to be legacy label, overlaps with Verbal/Mental abuse)* |
| Abuse: Financial Exploitation | 23 | *(appears to be legacy label, overlaps with Financial abuse)* |
| Abuse: Sexual Abuse | 19 | *(capitalization variant of Sexual abuse)* |
| Abuse: Wrongful Restraint | 11 | *(variant of Restraints)* |
| Abuse: Abandonment | 6 | Willfully leaving an adult without care, creating serious risk of harm |

### Provider Types (from Oregon website)

| Code | Description | Count | Notes |
|---|---|---|---|
| RCF | Residential Care Facility | 18,327 | Community-based care, licensed by APD |
| ALF | Assisted Living Facility | 10,872 | Community-based care, licensed by APD |
| NF | Nursing Facility | 8,257 | Federally regulated, recertification inspections required |
| AFH | Adult Foster Home | 8,115 | Individual providers, 1-5 residents, classified as Class 1/2/3 by provider qualifications |

### Important: Allegation Field Is a Fixed Taxonomy

The `Allegation` field is **not free text** -- it is drawn from a dropdown of ~90 standardized options (e.g., "Failed to provide safe environment", "Failed to administer medication as ordered"). The same allegation can appear under either a "Licensing Violation" or an "Abuse" type, depending on the investigation pathway and findings.

---

## Fundamental Structural Differences

| Dimension | California | Oregon |
|---|---|---|
| **Unit of record** | Enforcement action (penalty/citation issued) | Substantiated finding (violation/abuse confirmed) |
| **What triggers a record** | CDPH issues a citation or penalty | Investigation substantiates an allegation |
| **Includes open/pending** | Yes (2,504 open records) | No (only final/substantiated) |
| **Financial data** | Yes (amounts, offsets, collections, balances) | No (penalties are in separate Regulatory Actions dataset with only 1,289 records) |
| **Severity classification** | Yes (AA/A/B classes, IJ/Non-IJ) | No |
| **Death flag** | Yes (investigation-level) | No |
| **Appeal tracking** | Yes | No (appealed findings are excluded entirely) |
| **Abuse categorization** | Not directly -- "Abuse/Facility Not Self Reported" is about *failure to report*, not abuse findings | Yes -- 11 abuse subtypes with legal definitions under OAR |
| **Violation taxonomy** | 52 structured PENALTY_CATEGORY values | ~90 standardized allegations (dropdown) + 12 Type values |
| **Facility scope** | All licensed healthcare facilities (hospitals, SNFs, ICFs, clinics, HHA, hospice) | Long-term care only (NF, ALF, RCF, AFH) |
| **LTC identification** | Explicit `LTC` field | All records are LTC by definition |

-- Racial disparity analysis: compare chronic absenteeism gaps across states
-- Uses state-level data to compare the gap between each racial group and the overall rate

WITH state_totals AS (
    SELECT
        state,
        chronic_absent_rate as overall_rate
    FROM combined_chronic_absenteeism
    WHERE entity_level = 'State'
      AND reporting_category = 'TA'
),
racial_rates AS (
    SELECT
        c.state,
        c.category_description,
        c.chronic_absent_rate as group_rate,
        t.overall_rate,
        ROUND(c.chronic_absent_rate - t.overall_rate, 2) as gap_vs_overall
    FROM combined_chronic_absenteeism c
    JOIN state_totals t ON c.state = t.state
    WHERE c.entity_level = 'State'
      AND c.reporting_category LIKE 'R%'
)
SELECT * FROM racial_rates
ORDER BY state, gap_vs_overall DESC;

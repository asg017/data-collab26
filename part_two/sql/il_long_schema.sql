-- il_long_schema
-- Illinois long-format table schema


    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'il_chronic_absenteeism_long'
    ORDER BY ordinal_position


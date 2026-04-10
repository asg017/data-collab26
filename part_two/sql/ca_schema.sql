-- ca_schema
-- California table schema


    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'ca_chronic_absenteeism'
    ORDER BY ordinal_position


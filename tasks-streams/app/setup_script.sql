-- This is the setup script that runs while installing a Snowflake Native App in a consumer account.
-- For more information on how to create setup file, visit https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script

-- A general guideline to building this script looks like:
-- 1. Create application roles
CREATE APPLICATION ROLE IF NOT EXISTS app_public;

-- 2. Create a versioned schema to hold those UDFs/Stored Procedures
CREATE OR ALTER VERSIONED SCHEMA core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_public;

-- 3. Creates a procedure to be executed as a callback defined in the manifest.yml
create or replace procedure core.register_single_callback(ref_name string, operation string, ref_or_alias string)
returns string
language sql
as $$
    begin
        case (operation)
            when 'ADD' then
                select system$set_reference(:ref_name, :ref_or_alias);
            when 'REMOVE' then
                select system$remove_reference(:ref_name);
            when 'CLEAR' then
                select system$remove_reference(:ref_name);
            else
                return 'Unknown operation: ' || operation;
        end case;
        system$log('debug', 'register_single_callback: ' || operation || ' succeeded');
        return 'Operation ' || operation || ' succeeded';
    end;
$$;

grant usage on procedure core.register_single_callback(string, string, string)
    to application role app_public;

-- 4. Creates a table that will have the value incremented by the task.
CREATE SCHEMA IF NOT EXISTS internal;
GRANT USAGE ON SCHEMA internal TO APPLICATION ROLE app_public;

CREATE OR REPLACE TABLE internal.incremented_values
(
    value number
);

CREATE OR REPLACE STREAM internal.incremented_values_stream
ON TABLE internal.incremented_values;

INSERT INTO internal.incremented_values values (0);

-- 5. Defines a procedure that updates the table value.
CREATE OR REPLACE PROCEDURE core.increment_by_one(x NUMBER)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
  UPDATE internal.incremented_values SET value = value + :x;
  RETURN 'Success';
END;
$$;

-- 6. Procedure that creates an internal task after giving the proper rights.
CREATE OR REPLACE PROCEDURE core.create_task()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
  CREATE OR REPLACE TASK internal.increment_by_one_every_minute
   warehouse= reference('warehouse_reference')
   schedule = '1 minute'  
  AS
  CALL core.increment_by_one(1);
  ALTER TASK internal.increment_by_one_every_minute RESUME;
END;
$$;

CREATE OR REPLACE PROCEDURE core.stop_task()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
  ALTER TASK IF EXISTS internal.increment_by_one_every_minute SUSPEND;
END;
$$;

-- 7. Grant appropriate privileges over these objects to your application roles. 
GRANT USAGE ON PROCEDURE core.create_task() TO APPLICATION ROLE app_public;
GRANT USAGE ON PROCEDURE core.stop_task() TO APPLICATION ROLE app_public;

-- 8. Create a streamlit object using the code you wrote in src/module-ui, as shown below. 
-- The `from` value is derived from the stage path described in snowflake.yml
CREATE STREAMLIT core.ui
     FROM '/streamlit/'
     MAIN_FILE = 'ui.py';

-- 9. Grant appropriate privileges over these objects to your application roles. 
GRANT USAGE ON STREAMLIT core.ui TO APPLICATION ROLE app_public;

-- A detailed explanation can be found at https://docs.snowflake.com/en/developer-guide/native-apps/adding-streamlit 
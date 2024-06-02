-- This is the setup script that runs while installing a Snowflake Native App in a consumer account.
-- For more information on how to create setup file, visit https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script

-- A general guideline to building this script looks like:
-- 1. Create application roles
CREATE APPLICATION ROLE IF NOT EXISTS app_public;

-- 2. Create versioned schemas to hold UDFs/Stored Procedures
CREATE OR ALTER VERSIONED SCHEMA core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_public;
CREATE OR ALTER VERSIONED SCHEMA config;
GRANT USAGE ON SCHEMA config TO APPLICATION ROLE app_public;

-- 3. Create UDFs and Stored Procedures using the python code you wrote in src/module-add, as shown below.
CREATE OR REPLACE PROCEDURE config.register_single_reference(ref_name STRING, operation STRING, ref_or_alias STRING)
  RETURNS STRING
  LANGUAGE SQL
  AS $$
    BEGIN
      CASE (operation)
        WHEN 'ADD' THEN
          SELECT SYSTEM$SET_REFERENCE(:ref_name, :ref_or_alias);
        WHEN 'REMOVE' THEN
          SELECT SYSTEM$REMOVE_REFERENCE(:ref_name);
        WHEN 'CLEAR' THEN
          SELECT SYSTEM$REMOVE_REFERENCE(:ref_name);
      ELSE
        RETURN 'unknown operation: ' || operation;
      END CASE;
      system$log('debug', 'register_single_callback: ' || operation || ' succeeded');
      return 'Operation ' || operation || ' succeeded';
    END;
  $$;

GRANT USAGE ON PROCEDURE config.register_single_reference(STRING, STRING, STRING)
  TO APPLICATION ROLE app_public;


CREATE PROCEDURE IF NOT EXISTS core.app_procedure(x NUMBER, y NUMBER)
RETURNS NUMBER
LANGUAGE SQL
AS
$$
  DECLARE
    RESULT NUMBER;
  BEGIN
    CALL reference('procedure_reference')(:x, :y) INTO RESULT;
    RETURN RESULT;
  END;
$$;


CREATE OR REPLACE PROCEDURE core.app_update_table(x NUMBER)
RETURNS BOOLEAN
LANGUAGE SQL
AS
$$
    BEGIN
        INSERT INTO reference('table_reference') VALUES (:x);
        RETURN TRUE;
    END;
$$;

-- 4. Grant appropriate privileges over these objects to your application roles. 
GRANT USAGE ON PROCEDURE core.app_procedure(NUMBER, NUMBER) TO APPLICATION ROLE app_public;
GRANT USAGE ON PROCEDURE core.app_update_table(NUMBER) TO APPLICATION ROLE app_public;

-- 5. Create a streamlit object using the code you wrote in you wrote in src/module-ui, as shown below. 
-- The `from` value is derived from the stage path described in snowflake.yml
CREATE STREAMLIT core.ui
     FROM '/streamlit/'
     MAIN_FILE = 'ui.py';

-- 6. Grant appropriate privileges over these objects to your application roles. 
GRANT USAGE ON STREAMLIT core.ui TO APPLICATION ROLE app_public;

-- A detailed explanation can be found at https://docs.snowflake.com/en/developer-guide/native-apps/adding-streamlit 
-- This is the setup script that runs while installing a Snowflake Native App in a consumer account.
-- For more information on how to create setup file, visit https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script

-- A general guideline to building this script looks like:
-- 1. Create application roles
CREATE APPLICATION ROLE IF NOT EXISTS APP_PUBLIC;

-- 2. Create a versioned schema to hold those UDFs/Stored Procedures
CREATE OR ALTER VERSIONED SCHEMA CORE;
GRANT USAGE ON SCHEMA CORE TO APPLICATION ROLE APP_PUBLIC;

-- This procedure allows a select statement on a table, view or external table.
CREATE OR REPLACE PROCEDURE CORE.SELECT_OBJECT(ref_name VARCHAR)
RETURNS TABLE()
LANGUAGE SQL
AS $$
    BEGIN
    let res RESULTSET := (SELECT * FROM REFERENCE(:ref_name));
        RETURN TABLE(res);
    END;
$$;

-- This procedure allows you to obtain a table, external table or view description.
CREATE OR REPLACE PROCEDURE CORE.DESCRIBE_OBJECT(ref_name VARCHAR, type VARCHAR)
RETURNS TABLE()
LANGUAGE SQL
AS $$
  DECLARE
    rs RESULTSET;
  BEGIN
  CASE(type)
    WHEN 'TABLE' THEN
      rs := (DESCRIBE TABLE REFERENCE(:ref_name));
    WHEN 'VIEW' THEN
      rs := (DESCRIBE VIEW REFERENCE(:ref_name));
    WHEN 'EXTERNAL TABLE' THEN
      rs := (DESCRIBE EXTERNAL TABLE REFERENCE(:ref_name));
  END CASE;
  RETURN TABLE(rs);
  END;
$$;

-- This is a miscellaneous procedure to obtain a table column name.
CREATE OR REPLACE PROCEDURE CORE.TABLE_COL_NAME(ref_name VARCHAR)
RETURNS STRING
LANGUAGE SQL
AS $$
  BEGIN
    DESCRIBE TABLE REFERENCE(:ref_name);
    let variable VARCHAR := (SELECT TOP 1 t.$1 FROM TABLE (RESULT_SCAN ( LAST_QUERY_ID())) AS t);
    return variable;
END;
$$;

-- this procedure is used every time the user wants to either update, insert, delete or truncate a table.
CREATE OR REPLACE PROCEDURE CORE.MODIFY_TABLE(operation VARCHAR, table_name VARCHAR)
RETURNS STRING
LANGUAGE SQL
AS $$
    DECLARE
      table_col VARCHAR;
      query VARCHAR;
      response VARCHAR DEFAULT 'ERROR';
    BEGIN
        CASE (operation)
            WHEN 'INSERT' THEN
                INSERT INTO REFERENCE(:table_name) VALUES (12345);
                response := 'SUCCESS';
            WHEN 'UPDATE' THEN
                CALL CORE.TABLE_COL_NAME(:table_name) into :table_col;
                UPDATE REFERENCE(:table_name) SET val = 99999;
                response := 'SUCCESS';
            WHEN 'DELETE' THEN
                DELETE FROM REFERENCE(:table_name);
                response := 'SUCCESS';
        END CASE;
        RETURN response;
    END;
$$;

-- this procedure calls to the consumer referenced procedure inside its body and returns its result.
CREATE OR REPLACE PROCEDURE CORE.USE_PROC(ref_name VARCHAR, num1 NUMBER, num2 NUMBER)
RETURNS NUMBER
LANGUAGE SQL
AS $$
DECLARE
result INTEGER;
BEGIN
    CALL REFERENCE(:ref_name)(:num1,:num2) into :result;
    RETURN result;
END
$$;

CREATE OR REPLACE PROCEDURE CORE.DESCRIBE_WH(consumer_wh varchar)
RETURNS TABLE()
LANGUAGE SQL
AS $$
    DECLARE
        rs RESULTSET;
    BEGIN
        rs := (DESCRIBE WAREHOUSE REFERENCE(:consumer_wh));
        return TABLE(rs);
    END;
$$;

-- The following external function and procedure are commented so you can use the app without the api integration feature,
-- if you want to enable it, please follow the directions given in the readme. 

-- CREATE OR REPLACE EXTERNAL FUNCTION CORE.TRANSLATE_ENG_ITALIAN(message STRING)
--     returns variant
--     api_integration = REFERENCE('consumer_api')
--     as '***************** REPLACE EXTERNAL FUNCTION PLACEHOLDER *****************'
--     ;

-- CREATE OR REPLACE PROCEDURE CORE.CALL_API(word VARCHAR)
-- RETURNS TABLE()
-- LANGUAGE SQL
-- AS $$
-- DECLARE
--     rs RESULTSET;
-- BEGIN
--     rs := (select :word as original_word, translate_eng_italian(:word) as italian_word);
--     return table(rs);
-- END;
-- $$;

GRANT USAGE ON PROCEDURE CORE.SELECT_OBJECT(VARCHAR)
  TO APPLICATION ROLE app_public;

GRANT USAGE ON PROCEDURE CORE.DESCRIBE_OBJECT(VARCHAR, VARCHAR)
  TO APPLICATION ROLE app_public;

GRANT USAGE ON PROCEDURE CORE.TABLE_COL_NAME(VARCHAR)
  TO APPLICATION ROLE app_public;

GRANT USAGE ON PROCEDURE CORE.MODIFY_TABLE(VARCHAR, VARCHAR)
  TO APPLICATION ROLE app_public;

GRANT USAGE ON PROCEDURE CORE.USE_PROC(VARCHAR, NUMBER, NUMBER)
  TO APPLICATION ROLE app_public;

GRANT USAGE ON PROCEDURE CORE.DESCRIBE_WH(VARCHAR)
  TO APPLICATION ROLE app_public;

-- Enable this lines to grant usage to the API integration procedure and function.
-- GRANT USAGE ON PROCEDURE CORE.CALL_API(VARCHAR)
--   TO APPLICATION ROLE APP_PUBLIC;

-- GRANT USAGE ON FUNCTION CORE.TRANSLATE_ENG_ITALIAN(STRING)
--   TO APPLICATION ROLE APP_PUBLIC;

-- 5. Create a streamlit object using the code you wrote in you wrote in src/module-ui, as shown below. 
-- The `from` value is derived from the stage path described in snowflake.yml
CREATE OR REPLACE STREAMLIT CORE.DASHBOARD
     FROM '/streamlit/'
     MAIN_FILE = 'ui.py';

-- 6. Grant appropriate privileges over these objects to your application roles. 
GRANT USAGE ON STREAMLIT CORE.DASHBOARD TO APPLICATION ROLE APP_PUBLIC;

CREATE OR REPLACE APPLICATION ROLE APP_ADMIN;

CREATE OR ALTER VERSIONED SCHEMA CONFIG;
GRANT USAGE ON SCHEMA CONFIG TO APPLICATION ROLE APP_ADMIN;

CREATE PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(ref_name STRING, operation STRING, ref_or_alias STRING)
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
      RETURN NULL;
    END;
  $$;

GRANT USAGE ON PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(STRING, STRING, STRING)
  TO APPLICATION ROLE app_admin;
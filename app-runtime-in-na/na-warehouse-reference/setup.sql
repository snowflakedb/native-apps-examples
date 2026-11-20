CREATE APPLICATION ROLE IF NOT EXISTS app_user;

CREATE SCHEMA IF NOT EXISTS app_public;
GRANT USAGE ON SCHEMA app_public TO APPLICATION ROLE app_user;

CREATE OR ALTER VERSIONED SCHEMA app_callbacks;
GRANT USAGE ON SCHEMA app_callbacks TO APPLICATION ROLE app_user;

CREATE OR REPLACE PROCEDURE app_callbacks.configure_query_warehouse()
  RETURNS STRING
  LANGUAGE SQL
  EXECUTE AS OWNER
AS
$$
BEGIN
  ALTER APPLICATION SERVICE app_public.warehouse_whisperer
    SET QUERY_WAREHOUSE = REFERENCE('QUERY_WAREHOUSE');
  RETURN 'query warehouse configured';
END;
$$;

CREATE OR REPLACE PROCEDURE app_callbacks.register_single_reference(
  ref_name STRING, operation STRING, ref_or_alias STRING
)
  RETURNS STRING
  LANGUAGE SQL
  EXECUTE AS OWNER
AS
$$
BEGIN
  CASE (operation)
    WHEN 'ADD' THEN
      SELECT SYSTEM$SET_REFERENCE(:ref_name, :ref_or_alias);
      IF (UPPER(ref_name) = 'QUERY_WAREHOUSE') THEN
        CALL app_callbacks.configure_query_warehouse();
      END IF;
    WHEN 'REMOVE' THEN
      SELECT SYSTEM$REMOVE_REFERENCE(:ref_name, :ref_or_alias);
    WHEN 'CLEAR' THEN
      SELECT SYSTEM$REMOVE_ALL_REFERENCES(:ref_name);
    ELSE
      RETURN 'unknown operation: ' || operation;
  END CASE;
  RETURN NULL;
END;
$$;

CREATE APPLICATION SERVICE IF NOT EXISTS app_public.warehouse_whisperer
  FROM PACKAGE warehouse_whisperer
  COMPUTE_RESOURCE = SERVERLESS;

CREATE OR REPLACE PROCEDURE app_callbacks.version_init()
  RETURNS STRING
  LANGUAGE SQL
  EXECUTE AS OWNER
AS
$$
BEGIN
  ALTER APPLICATION SERVICE IF EXISTS app_public.warehouse_whisperer UPGRADE;
  BEGIN
    CALL app_callbacks.configure_query_warehouse();
  EXCEPTION
    WHEN OTHER THEN NULL;
  END;
  RETURN 'Warehouse Whisperer application service upgraded';
END;
$$;

GRANT USAGE ON APPLICATION SERVICE app_public.warehouse_whisperer
  TO APPLICATION ROLE app_user;
GRANT USAGE ON PROCEDURE app_callbacks.register_single_reference(STRING, STRING, STRING)
  TO APPLICATION ROLE app_user;

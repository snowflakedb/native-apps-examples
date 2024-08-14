CREATE APPLICATION ROLE IF NOT EXISTS app_admin;
CREATE APPLICATION ROLE IF NOT EXISTS app_user;
CREATE SCHEMA IF NOT EXISTS app_public;
GRANT USAGE ON SCHEMA app_public TO APPLICATION ROLE app_admin;
GRANT USAGE ON SCHEMA app_public TO APPLICATION ROLE app_user;
CREATE OR ALTER VERSIONED SCHEMA versioned_schema;
GRANT USAGE ON SCHEMA versioned_schema TO APPLICATION ROLE app_admin;


CREATE OR REPLACE PROCEDURE versioned_schema.register_single_callback(ref_name STRING, operation STRING, ref_or_alias STRING)
 RETURNS STRING
 LANGUAGE SQL
 AS $$
      BEGIN
      CASE (operation)
         WHEN 'ADD' THEN
            SELECT system$set_reference(:ref_name, :ref_or_alias);
         WHEN 'REMOVE' THEN
            SELECT system$remove_reference(:ref_name);
         WHEN 'CLEAR' THEN
            SELECT system$remove_reference(:ref_name);
         ELSE
            RETURN 'Unknown operation: ' || operation;
      END CASE;
      RETURN 'Operation ' || operation || ' succeeds.';
      END;
   $$;
GRANT USAGE ON PROCEDURE versioned_schema.register_single_callback(STRING, STRING, STRING) TO APPLICATION ROLE app_admin;

CREATE OR REPLACE PROCEDURE versioned_schema.get_configuration(ref_name STRING)
RETURNS STRING
LANGUAGE SQL
AS 
$$
BEGIN
  CASE (UPPER(ref_name))
      WHEN 'WIKIPEDIA_EAI' THEN
          RETURN OBJECT_CONSTRUCT(
              'type', 'CONFIGURATION',
              'payload', OBJECT_CONSTRUCT(
                  'host_ports', ARRAY_CONSTRUCT('upload.wikimedia.org'),
                  'allowed_secrets', 'NONE')
          )::STRING;
      ELSE
          RETURN '';
  END CASE;
END;	
$$;

GRANT USAGE ON PROCEDURE versioned_schema.get_configuration(STRING) TO APPLICATION ROLE app_admin;

-- The version initializer callback is executed after a successful run of the setup script.
-- In case the versioned_schema.init() failed, the version initializer of the previous version will be executed
CREATE OR REPLACE PROCEDURE versioned_schema.init()
RETURNS STRING 
LANGUAGE SQL
EXECUTE AS OWNER 
AS
$$
BEGIN    
    ALTER SERVICE IF EXISTS app_public.frontend FROM SPECIFICATION_FILE='frontend.yaml';
    ALTER SERVICE IF EXISTS app_public.backend FROM SPECIFICATION_FILE='backend.yaml';
    select system$wait_for_services(300, 'app_public.backend', 'app_public.frontend');
    RETURN 'init complete';
END $$;

CREATE OR REPLACE PROCEDURE versioned_schema.start_backend(pool_name VARCHAR)
    RETURNS string
    LANGUAGE sql
    AS $$
BEGIN
    CREATE SERVICE IF NOT EXISTS app_public.backend
        IN COMPUTE POOL Identifier(:pool_name)
        FROM SPECIFICATION_FILE='backend.yaml'
        QUERY_WAREHOUSE = 'WH_NAC';
    GRANT USAGE ON SERVICE app_public.backend TO APPLICATION ROLE app_user;
END
$$;
GRANT USAGE ON PROCEDURE versioned_schema.start_backend(VARCHAR) TO APPLICATION ROLE app_admin;

CREATE OR REPLACE PROCEDURE versioned_schema.start_frontend(pool_name VARCHAR)
    RETURNS string
    LANGUAGE sql
    AS $$
BEGIN
    CREATE SERVICE IF NOT EXISTS app_public.frontend
        IN COMPUTE POOL Identifier(:pool_name)
        FROM SPECIFICATION_FILE='frontend.yaml'
        EXTERNAL_ACCESS_INTEGRATIONS=( reference('WIKIPEDIA_EAI') );
    
    GRANT USAGE ON SERVICE app_public.frontend TO APPLICATION ROLE app_user;

    RETURN 'Service started. Check status, and when ready, get URL';
END
$$;
GRANT USAGE ON PROCEDURE versioned_schema.start_frontend(VARCHAR) TO APPLICATION ROLE app_admin;


CREATE OR REPLACE PROCEDURE versioned_schema.create_services(privileges array)
 RETURNS STRING
 LANGUAGE SQL
 AS 
 $$
    BEGIN
        CREATE COMPUTE POOL IF NOT EXISTS frontend_compute_pool
        MIN_NODES = 1
        MAX_NODES = 1
        INSTANCE_FAMILY = CPU_X64_XS;

        CREATE COMPUTE POOL IF NOT EXISTS backend_compute_pool
        MIN_NODES = 1
        MAX_NODES = 1
        INSTANCE_FAMILY = CPU_X64_XS;

        CALL versioned_schema.start_backend('backend_compute_pool');
        CALL versioned_schema.start_frontend('frontend_compute_pool');
    END;
$$;
GRANT USAGE ON PROCEDURE versioned_schema.create_services(array) TO APPLICATION ROLE app_admin;


CREATE OR REPLACE PROCEDURE app_public.stop_app()
    RETURNS string
    LANGUAGE sql
    AS
$$
BEGIN
    DROP SERVICE IF EXISTS app_public.backend;
    DROP SERVICE IF EXISTS app_public.frontend;
END
$$;
GRANT USAGE ON PROCEDURE app_public.stop_app() TO APPLICATION ROLE app_admin;

CREATE OR REPLACE PROCEDURE versioned_schema.app_url()
    RETURNS string
    LANGUAGE sql
    AS
$$
DECLARE
    ingress_url VARCHAR;
BEGIN
    SHOW ENDPOINTS IN SERVICE app_public.frontend;
    SELECT "ingress_url" INTO :ingress_url FROM TABLE (RESULT_SCAN (LAST_QUERY_ID())) LIMIT 1;
    RETURN ingress_url;
END
$$;
GRANT USAGE ON PROCEDURE versioned_schema.app_url() TO APPLICATION ROLE app_admin;
GRANT USAGE ON PROCEDURE versioned_schema.app_url() TO APPLICATION ROLE app_user;

-- Support functions
EXECUTE IMMEDIATE FROM 'support.sql';
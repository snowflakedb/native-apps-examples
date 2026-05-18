-- Application Roles and Schemas
CREATE APPLICATION ROLE IF NOT EXISTS app_admin;
CREATE APPLICATION ROLE IF NOT EXISTS app_user;
CREATE SCHEMA IF NOT EXISTS app_public;
GRANT USAGE ON SCHEMA app_public TO APPLICATION ROLE app_admin;
GRANT USAGE ON SCHEMA app_public TO APPLICATION ROLE app_user;
CREATE OR ALTER VERSIONED SCHEMA v1;
GRANT USAGE ON SCHEMA v1 TO APPLICATION ROLE app_admin;

-- Version initializer callback - executed after installation, upgrade, or downgrade
CREATE OR REPLACE PROCEDURE v1.init()
RETURNS STRING 
LANGUAGE SQL
EXECUTE AS OWNER 
AS
$$
BEGIN    
    ALTER SERVICE IF EXISTS app_public.backend FROM SPECIFICATION_FILE='backend.yaml';
    RETURN 'init complete';
END $$;
GRANT USAGE ON PROCEDURE v1.init() TO APPLICATION ROLE app_admin;

-- Create compute pool (privileges auto-granted with manifest v2)
CREATE COMPUTE POOL IF NOT EXISTS mcp_compute_pool
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS;

-- Start the backend service
CREATE SERVICE IF NOT EXISTS app_public.backend
    IN COMPUTE POOL mcp_compute_pool
    FROM SPECIFICATION_FILE='backend.yaml';
GRANT USAGE ON SERVICE app_public.backend TO APPLICATION ROLE app_user;

-- Stop the app
CREATE OR REPLACE PROCEDURE app_public.stop_app()
    RETURNS string
    LANGUAGE sql
    AS
$$
BEGIN
    DROP SERVICE IF EXISTS app_public.backend;
END
$$;
GRANT USAGE ON PROCEDURE app_public.stop_app() TO APPLICATION ROLE app_admin;

-- Get the app URL
CREATE OR REPLACE PROCEDURE v1.app_url()
    RETURNS string
    LANGUAGE sql
    AS
$$
DECLARE
    ingress_url VARCHAR;
BEGIN
    SHOW ENDPOINTS IN SERVICE app_public.backend;
    SELECT "ingress_url" INTO :ingress_url FROM TABLE (RESULT_SCAN (LAST_QUERY_ID())) LIMIT 1;
    RETURN ingress_url;
END
$$;
GRANT USAGE ON PROCEDURE v1.app_url() TO APPLICATION ROLE app_admin;
GRANT USAGE ON PROCEDURE v1.app_url() TO APPLICATION ROLE app_user;

-- Service function that calls the echo endpoint
CREATE OR REPLACE FUNCTION v1.echo(input VARCHAR)
RETURNS VARCHAR
SERVICE = app_public.backend
ENDPOINT = api
AS '/echo';
GRANT USAGE ON FUNCTION v1.echo(VARCHAR) TO APPLICATION ROLE app_user;
GRANT USAGE ON FUNCTION v1.echo(VARCHAR) TO APPLICATION ROLE app_admin;

-- MCP SERVER with custom tool pointing to the service function
CREATE MCP SERVER IF NOT EXISTS v1.echo_mcp_server
FROM SPECIFICATION $$
tools:
- title: "Echo Tool"
  identifier: "mcp_server_app_v1_instance.v1.echo"
  name: "echo"
  type: "GENERIC"
  description: "Echoes back the input text"
  config:
    type: "function"
    warehouse: "WH_NAC"
    input_schema:
      type: "object"
      properties:
        input:
          description: "The text to echo back"
          type: "string"
$$;
GRANT USAGE ON MCP SERVER v1.echo_mcp_server TO APPLICATION ROLE app_user;
GRANT USAGE ON MCP SERVER v1.echo_mcp_server TO APPLICATION ROLE app_admin;

-- Support functions
EXECUTE IMMEDIATE FROM 'support.sql';

-- This is the setup script that runs while installing a Snowflake Native App in a consumer account.
-- To write this script, you can familiarize yourself with some of the following concepts:
-- Application Roles
-- Versioned Schemas
-- UDFs/Procs
-- Extension Code
-- Refer to https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script for a detailed understanding of this file.

CREATE APPLICATION ROLE IF NOT EXISTS app_public;
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS service_schema;
CREATE SCHEMA IF NOT EXISTS udf_schema;
CREATE OR ALTER VERSIONED SCHEMA core;
CREATE image repository IF NOT EXISTS public.tutorial_repo;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_public;
GRANT USAGE ON SCHEMA public TO APPLICATION ROLE app_public;

GRANT USAGE ON SCHEMA service_schema TO APPLICATION ROLE app_public;
GRANT USAGE ON SCHEMA udf_schema TO APPLICATION ROLE app_public;
GRANT READ ON image repository public.tutorial_repo TO APPLICATION ROLE app_public;
GRANT WRITE ON image repository public.tutorial_repo TO APPLICATION ROLE app_public;

CREATE OR REPLACE TABLE core.debug_logs (
    log_type STRING,
    log_message STRING,
    log_timestamp TIMESTAMP_NTZ
);


-- GRANT USAGE ON TABLE core.debug_logs TO APPLICATION ROLE app_public;
-- The rest of this script is left blank for purposes of your learning and exploration.

create or replace stage public.kaniko_stage;
grant read on stage public.kaniko_stage to application role app_public;
grant write on stage public.kaniko_stage to application role app_public;

-- 3. Create callbacks called in the manifest.yml
CREATE OR REPLACE PROCEDURE core.register_single_callback(ref_name STRING, operation STRING, ref_or_alias STRING)
RETURNS STRING
LANGUAGE SQL
AS 
$$
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
  END;
$$;

GRANT USAGE ON PROCEDURE core.register_single_callback(STRING, STRING, STRING)
  TO APPLICATION ROLE app_public;
-- GRANT USAGE ON EXTERNAL ACCESS INTEGRATION pypi_access_integration TO APPLICATION ROLE app_public;

CREATE OR REPLACE PROCEDURE core.get_configuration(ref_name STRING)
RETURNS STRING
LANGUAGE SQL
AS 
$$
BEGIN
  CASE (UPPER(ref_name))
      WHEN 'EXTERNAL_ACCESS_REFERENCE' THEN
          -- RETURN '{
          -- "type": "CONFIGURATION",
          -- "payload": {
          -- "host_ports": ["pypi.org", "pypi.python.org", "pythonhosted.org", "files.pythonhosted.org", "docker.io", "index.docker.io", "gcr.io", "auth.docker.io", "production.cloudflare.docker.com"],
          -- "allowed_secrets": "NONE"
          -- }
          -- }';
          RETURN '{
          "type": "CONFIGURATION",
          "payload": {
          "host_ports": ["0.0.0.0"],
          "allowed_secrets": "NONE"
          }
          }';
      ELSE
          RETURN '';
  END CASE;
END;	
$$;

create or replace procedure public.create_kaniko_job(compute_pool_name STRING, kaniko_job_name STRING, regestry_local_url STRING, base_image STRING, service_image_name STRING, stage STRING)
returns STRING
language sql
as
begin
    execute job service
      in compute pool Identifier(:compute_pool_name)
      name=Identifier(:kaniko_job_name)
      EXTERNAL_ACCESS_INTEGRATIONS=(reference('external_access_reference'))
      from specification_template $$
      spec:
        containers:
        - name: main
          image: "/spcs_easyrun_db/spcs_easyrun_schema/spcs_easyrun_repo/easy-run-mode:latest"
          env:
            IMAGE_REGISTRY_URL: {{regestry_local_url}}
            BASE_IMG: {{base_image}}
            FINAL_IMAGE: {{service_image_name}}
          volumeMounts:
            - name: test-volume
              mountPath: /app/src
        volumes:
          - name: test-volume
            source: {{stage}}
      $$
      -- using (specification_template1 => '114', specification_template2 => '114');
      using (regestry_local_url => :regestry_local_url, base_image => :base_image, service_image_name => :service_image_name, stage => :stage);
    system$log('info', 'Job ' || :kaniko_job_name || ' created successfully');
    grant usage on service Identifier(:kaniko_job_name) to application role app_public;
    return 'Job created successfully';
end;

create or replace procedure public.list_images(path STRING)
returns STRING
language sql
as
begin
  return (select system$registry_list_images(:path));
end;

create or replace procedure public.start_frontend(privileges array)
returns STRING
AS
$$
BEGIN
  create warehouse if not exists easy_run_wh with WAREHOUSE_SIZE='XSMALL';
  grant usage on warehouse easy_run_wh to application role app_public;

  create compute pool if not exists frontend_pool with
    min_nodes = 1
    max_nodes = 1
    INSTANCE_FAMILY = CPU_X64_XS;

    create service if not exists public.frontend_service
    IN COMPUTE POOL frontend_pool
    FROM SPECIFICATION_FILE = 'frontend.yaml'
    external_access_integrations = (reference('external_access_reference'))
    query_warehouse = 'easy_run_wh';
  GRANT USAGE ON SERVICE public.frontend_service TO APPLICATION ROLE app_public;
  GRANT SERVICE ROLE public.frontend_service!all_endpoints_usage TO APPLICATION ROLE app_public;
  return 'Frontend service started successfully';
END
$$;

create or replace procedure public.stop_frontend()
returns STRING
language sql
AS
$$
BEGIN
  DROP SERVICE IF EXISTS public.frontend_service;
  return 'Frontend service stopped successfully';
END
$$;

CREATE OR REPLACE PROCEDURE public.init()
RETURNS STRING 
LANGUAGE SQL
EXECUTE AS OWNER 
AS
$$
BEGIN    
    ALTER SERVICE IF EXISTS public.frontend FROM SPECIFICATION_FILE='frontend.yaml';
    RETURN 'init complete';
END $$;

GRANT USAGE ON PROCEDURE public.start_frontend(array) TO APPLICATION ROLE app_public;

GRANT USAGE ON PROCEDURE core.get_configuration(STRING) TO APPLICATION ROLE app_public;
GRANT USAGE ON PROCEDURE public.list_images(STRING) TO APPLICATION ROLE app_public;
GRANT USAGE ON PROCEDURE public.create_kaniko_job(STRING, STRING, STRING, STRING, STRING, STRING) TO APPLICATION ROLE app_public;

GRANT USAGE ON PROCEDURE public.init() TO APPLICATION ROLE app_public;

-- call create_my_kaniko_job2('test_compute_2', 'kaniko_job_name', 'kaniko_image_path', 'regestry_local_url', 'base_image', 'service_image_name', 'stage');
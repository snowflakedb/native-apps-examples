USE ROLE ACCOUNTADMIN;
-- Abort the whole bootstrap before any privilege grant if a role is untrusted.
EXECUTE IMMEDIATE $$
DECLARE
    trusted_roles INTEGER;
    unexpected_grants INTEGER;
    untrusted_role EXCEPTION (-20001, 'Demo roles must be owned by ACCOUNTADMIN and granted only to ACCOUNTADMIN. Review existing roles before setup.');
BEGIN
    CREATE ROLE IF NOT EXISTS naspcs_role;
    CREATE ROLE IF NOT EXISTS nac;
    SHOW ROLES;
    SELECT COUNT(*) INTO :trusted_roles
        FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
        WHERE "name" IN ('NASPCS_ROLE', 'NAC') AND "owner" = 'ACCOUNTADMIN';
    IF (trusted_roles != 2) THEN
        RAISE untrusted_role;
    END IF;
    SHOW GRANTS OF ROLE naspcs_role;
    SELECT COUNT(*) INTO :unexpected_grants
        FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
        WHERE "granted_to" != 'ROLE' OR "grantee_name" != 'ACCOUNTADMIN';
    IF (unexpected_grants != 0) THEN
        RAISE untrusted_role;
    END IF;
    SHOW GRANTS OF ROLE nac;
    SELECT COUNT(*) INTO :unexpected_grants
        FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
        WHERE "granted_to" != 'ROLE' OR "grantee_name" != 'ACCOUNTADMIN';
    IF (unexpected_grants != 0) THEN
        RAISE untrusted_role;
    END IF;

    GRANT ROLE naspcs_role TO ROLE accountadmin;
    GRANT CREATE DATABASE ON ACCOUNT TO ROLE naspcs_role;
    GRANT CREATE APPLICATION PACKAGE ON ACCOUNT TO ROLE naspcs_role;
    CREATE WAREHOUSE IF NOT EXISTS wh_nap WITH WAREHOUSE_SIZE='XSMALL';
    GRANT USAGE ON WAREHOUSE wh_nap TO ROLE naspcs_role;

    USE ROLE naspcs_role;
    CREATE DATABASE IF NOT EXISTS spcs_app;
    CREATE SCHEMA IF NOT EXISTS spcs_app.napp;

    -- For Provider-side Testing
    USE ROLE ACCOUNTADMIN;
    GRANT CREATE APPLICATION ON ACCOUNT TO ROLE nac;
    GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE nac;

    -- Create the Image Repository
    USE ROLE naspcs_role;
    CREATE IMAGE REPOSITORY IF NOT EXISTS spcs_app.napp.img_repo;
    GRANT USAGE ON DATABASE spcs_app TO ROLE nac;
    GRANT USAGE ON SCHEMA spcs_app.napp TO ROLE nac;
    GRANT READ ON IMAGE REPOSITORY spcs_app.napp.img_repo TO ROLE nac;
END;
$$;

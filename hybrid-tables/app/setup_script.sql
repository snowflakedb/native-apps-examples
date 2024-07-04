-- This is the setup script that runs while installing a Snowflake Native App in a consumer account.
-- To write this script, you can familiarize yourself with some of the following concepts:
-- Application Roles
-- Versioned Schemas
-- UDFs/Procs
-- Extension Code
-- Refer to https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script for a detailed understanding of this file. 

CREATE APPLICATION ROLE IF NOT EXISTS app_public;
CREATE OR ALTER VERSIONED SCHEMA core;
CREATE SCHEMA IF NOT EXISTS internal;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_public;
GRANT USAGE ON SCHEMA internal TO APPLICATION ROLE app_public;

CREATE HYBRID TABLE IF NOT EXISTS internal.dictionary
(
    key VARCHAR,
    value VARCHAR,
    CONSTRAINT pkey PRIMARY KEY (key)
);

CREATE OR REPLACE PROCEDURE core.add_key_value(KEY VARCHAR, VALUE VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO internal.dictionary VALUES (:KEY, :VALUE);
    RETURN OBJECT_CONSTRUCT('STATUS', 'OK');
    EXCEPTION
        WHEN STATEMENT_ERROR THEN
            RETURN OBJECT_CONSTRUCT('STATUS', 'FAILED',
                                    'SQLCODE', SQLCODE,
                                    'SQLERRM', SQLERRM,
                                    'SQLSTATE', SQLSTATE);
END;
$$;

CREATE OR REPLACE STREAMLIT core.ui
     FROM '/streamlit/'
     MAIN_FILE = 'ui.py';

GRANT USAGE ON STREAMLIT core.ui TO APPLICATION ROLE app_public;
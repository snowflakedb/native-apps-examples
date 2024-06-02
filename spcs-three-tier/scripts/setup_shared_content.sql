-- For Support functions
CREATE SCHEMA IF NOT EXISTS {{ package_name }}.shared_data;
CREATE TABLE IF NOT EXISTS {{ package_name }}.shared_data.feature_flags(flags VARIANT, acct VARCHAR);
CREATE SECURE VIEW IF NOT EXISTS {{ package_name }}.shared_data.feature_flags_vw AS SELECT * FROM {{ package_name }}.shared_data.feature_flags WHERE acct = current_account();
GRANT USAGE ON SCHEMA {{ package_name }}.shared_data TO SHARE IN APPLICATION PACKAGE {{ package_name }};
GRANT SELECT ON VIEW {{ package_name }}.shared_data.feature_flags_vw TO SHARE IN APPLICATION PACKAGE {{ package_name }};
GRANT INSTALL, DEVELOP ON APPLICATION PACKAGE {{ package_name }} TO ROLE nac;
INSERT INTO {{ package_name }}.shared_data.feature_flags SELECT parse_json('{"debug": ["GET_SERVICE_STATUS", "GET_SERVICE_LOGS", "LIST_LOGS", "TAIL_LOG"]}') AS flags, current_account() AS acct;
GRANT USAGE ON SCHEMA {{ package_name }}.shared_data TO SHARE IN APPLICATION PACKAGE {{ package_name }};

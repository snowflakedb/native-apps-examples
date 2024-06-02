-- Break Glass Support Functions
CREATE SCHEMA IF NOT EXISTS app_internal;

CREATE OR REPLACE SECURE VIEW app_internal.feature_flags AS
    SELECT * FROM shared_data.feature_flags_vw;
CREATE OR REPLACE FUNCTION app_internal.debug_flag(flag VARCHAR)
    RETURNS BOOLEAN
AS $$
    SELECT array_contains(flag::VARIANT, flags:debug::ARRAY) FROM app_internal.feature_flags
$$;

CREATE OR REPLACE PROCEDURE app_public.get_service_status(service VARCHAR)
    RETURNS VARCHAR
    LANGUAGE SQL
AS $$
DECLARE
    res VARCHAR;
    okay BOOLEAN;
BEGIN
    SELECT app_internal.debug_flag('GET_SERVICE_STATUS') INTO :okay;
    IF (:okay) THEN
        SELECT SYSTEM$GET_SERVICE_status(:service) INTO res;
        RETURN res;
    ELSE
        RETURN 'Not authorized.';
    END IF;
END;
$$;
GRANT USAGE ON PROCEDURE app_public.get_service_status(VARCHAR) TO APPLICATION ROLE app_admin;

CREATE OR REPLACE PROCEDURE app_public.get_service_logs(service VARCHAR, instance INT, container VARCHAR, num_lines INT)
    RETURNS VARCHAR
    LANGUAGE SQL
AS $$
DECLARE
    res VARCHAR;
    okay BOOLEAN;
BEGIN
    SELECT app_internal.debug_flag('GET_SERVICE_LOGS') INTO :okay;
    IF (:okay) THEN
        SELECT SYSTEM$GET_SERVICE_LOGS(:service, :instance, :container, :num_lines) INTO res;
        RETURN res;
    ELSE
        RETURN 'Not authorized.';
    END IF;
END;
$$;
GRANT USAGE ON PROCEDURE app_public.get_service_logs(VARCHAR, INT, VARCHAR, INT) TO APPLICATION ROLE app_admin;

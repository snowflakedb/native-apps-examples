--Create a schema in the applcation package
CREATE SCHEMA IF NOT EXISTS {{ package_name }}.IP2LOCATION;

--Grant the application permissions on the schema we just created
GRANT USAGE ON SCHEMA {{ package_name }}.IP2LOCATION TO SHARE IN APPLICATION PACKAGE {{ package_name }};

GRANT REFERENCE_USAGE ON DATABASE IP2LOCATION TO SHARE IN APPLICATION PACKAGE {{ package_name }};
--We need to create a proxy artefact here referencing the data we want to use
CREATE VIEW IF NOT EXISTS {{ package_name }}.IP2LOCATION.LITEDB11
AS
SELECT * FROM IP2LOCATION.IP2LOCATION.LITEDB11;
--Grant permissions to the application
GRANT SELECT ON VIEW {{ package_name }}.IP2LOCATION.LITEDB11 TO SHARE IN APPLICATION PACKAGE {{ package_name }};
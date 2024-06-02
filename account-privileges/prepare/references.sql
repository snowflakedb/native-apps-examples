USE ROLE accountadmin;
CREATE DATABASE IF NOT EXISTS consumer_database;
CREATE SCHEMA IF NOT EXISTS consumer_database.consumer_schema;

CREATE OR REPLACE TABLE consumer_database.consumer_schema.table_reference
(
    value NUMBER
);

CREATE OR REPLACE VIEW consumer_database.consumer_schema.view_reference
AS
SELECT * FROM consumer_database.consumer_schema.table_reference;

CREATE OR REPLACE FUNCTION consumer_database.consumer_schema.function_reference(x NUMBER, y NUMBER)
  RETURNS NUMBER
  LANGUAGE SQL
  AS 'x + y';

CREATE OR REPLACE PROCEDURE consumer_database.consumer_schema.procedure_reference(x NUMBER, y NUMBER)
RETURNS NUMBER
LANGUAGE SQL
AS
$$
    BEGIN
        RETURN :x + :y;
    END;
$$;


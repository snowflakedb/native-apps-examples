USE ROLE accountadmin;
CREATE DATABASE IF NOT EXISTS reference_usage_app_sample;
CREATE SCHEMA IF NOT EXISTS reference_usage_app_sample.provider_schema;

CREATE OR REPLACE TABLE reference_usage_app_sample.provider_schema.provider_table
(
    value NUMBER
);

insert into reference_usage_app_sample.provider_schema.provider_table values
    (1),(2),(3),(4),(5),(6),(7),(8),(9);
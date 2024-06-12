
# create database, schema and table for consumer's example data
snow sql -q"

CREATE OR REPLACE DATABASE SPOTIFY_RATINGS_DB;
CREATE OR REPLACE SCHEMA SPOTIFY_RATINGS_SCHEMA;

CREATE OR REPLACE TABLE SPOTIFY_RATINGS_DB.SPOTIFY_RATINGS_SCHEMA.SPOTIFY_CONSUMER_DATA(
    name VARCHAR;
    artists VARCHAR;
    danceabilty FLOAT
);"

# loading sportify dataset into table stage
snow object stage copy ./data/spotify_consumer.csv @%SPOTIFY_CONSUMER_DATA --database SPOTIFY_RATINGS_DB --schema SPOTIFY_RATINGS_SCHEMA

# loading sportify dataset from table stage into consumer table
snow sql -q "
-- this database is used to store our data
USE DATABASE SPOTIFY_RATINGS_DB;

USE SCHEMA SPOTIFY_RATINGS_SCHEMA;

COPY INTO SPOTIFY_CONSUMER_DATA
FILE_FORMAT = (TYPE = CSV
FIELD_OPTIONALLY_ENCLOSED_BY = '\"');"
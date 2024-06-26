# Create a database and a schema to hold the data to lookup.
snow sql -q "
CREATE DATABASE IF NOT EXISTS IP2LOCATION;
CREATE SCHEMA IF NOT EXISTS IP2LOCATION;
"
# Create the table to host the data.
# Create a file format for the file
# Create a stage so we can upload the file

snow sql -q "
CREATE TABLE IF NOT EXISTS LITEDB11 (
ip_from INT,
ip_to INT,
country_code char(2),
country_name varchar(64),
region_name varchar(128),
city_name varchar(128),
latitude DOUBLE,
longitude DOUBLE,
zip_code varchar(30),
time_zone varchar(8)
);

--Create a file format for the file
CREATE OR REPLACE FILE FORMAT LOCATION_CSV
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '\"'
COMPRESSION = AUTO;

--create a stage so we can upload the file
CREATE STAGE IF NOT EXISTS IP2LOCATION.IP2LOCATION.LOCATION_DATA_STAGE
file_format = LOCATION_CSV;" --database ip2location --schema ip2location 

# Copy the csv files from your local machine to the stage we created previously
snow stage copy /USER_PATH_HERE/IP2LOCATION-LITE-DB11.CSV @location_data_stage --database ip2location --schema ip2location 

# Copy the csv file from the stage to load the table
snow sql -q "
copy into litedb11 from @location_data_stage
files = ('IP2LOCATION-LITE-DB11.CSV')
;" --database ip2location --schema ip2location

# Simple query test to ensure the table is correctly filled.
snow sql -q "SELECT COUNT(*) FROM LITEDB11;
SELECT * FROM LITEDB11 LIMIT 10;" --database ip2location --schema ip2location

# Create test database and schema.
snow sql -q "CREATE DATABASE IF NOT EXISTS TEST_IPLOCATION;
CREATE SCHEMA IF NOT EXISTS TEST_IPLOCATION;"

# Create test table to insert some values
snow sql -q "
CREATE OR REPLACE TABLE TEST_IPLOCATION.TEST_IPLOCATION.TEST_DATA (
	IP VARCHAR(16),
	IP_DATA VARIANT
);"

# Insert testing values to use later on
snow sql -q "
INSERT INTO TEST_IPLOCATION.TEST_IPLOCATION.TEST_DATA(IP) VALUES('73.153.199.206'),('8.8.8.8');"
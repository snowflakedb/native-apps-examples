USE ROLE ACCOUNTADMIN;
-- (Mock) Consumer role
GRANT ROLE nac TO ROLE ACCOUNTADMIN;
CREATE WAREHOUSE IF NOT EXISTS wh_nac WITH WAREHOUSE_SIZE='XSMALL';

CREATE DATABASE IF NOT EXISTS snowflake_sample_data;
CREATE SCHEMA IF NOT EXISTS snowflake_sample_data.tpch_sf10;
GRANT USAGE ON WAREHOUSE wh_nac TO ROLE nac WITH GRANT OPTION;
GRANT USAGE ON DATABASE snowflake_sample_data TO ROLE nac;
GRANT USAGE ON SCHEMA snowflake_sample_data.tpch_sf10 TO ROLE nac;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE nac;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE nac WITH GRANT OPTION;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE nac WITH GRANT OPTION;

USE SCHEMA snowflake_sample_data.tpch_sf10;

CREATE OR REPLACE TABLE ORDERS (
	O_ORDERKEY		NUMBER PRIMARY KEY,
	O_CUSTKEY		BIGINT NOT NULL,
	O_ORDERSTATUS	CHAR(1),
	O_TOTALPRICE	DECIMAL,
	O_ORDERDATE		DATE,
	O_ORDERPRIORITY	VARCHAR,
	O_CLERK			VARCHAR,
	O_SHIPPRIORITY	INTEGER,
	O_COMMENT		VARCHAR(79)
);

INSERT INTO ORDERS VALUES
(33338469,9145955,'F',103134.13,'1992-01-01','4-NOT SPECIFIED','Clerk#000017453',0,'y express theodolites cajole above the '),
(32147872,8994326,'F',12923.92,'1992-01-02','5-LOW','Clerk#000043949',0,'ly pending asymptotes sleep quic'),
(33960166,6710056,'F',218290.93,'1992-01-03','2-HIGH','Clerk#000028165',0,'nal excuses cajole blithely along the pending theodolites'),
(33837314,617875,'F',207334.00,'1992-01-04','2-HIGH','Clerk#000065474',0,'dependencies above the slyly express dependencies wake after the doggedly ev'),
(32982371,6532817,'F',326510.81,'1992-01-05','3-MEDIUM','Clerk#000041209',0,' final deposits. furiously bold deposits unwind along the'),
(33327456,2392715,'F',293445.83,'1992-01-06','1-URGENT','Clerk#000022357',0,'iously even excuses use across the regula'),
(33891493,6257296,'F',221969.98,'1992-01-07','3-MEDIUM','Clerk#000069192',0,'y special accounts doubt. ironic, final deposits x-ray furiou'),
(33982369,12169382,'F',16492.82,'1992-01-08','4-NOT SPECIFIED','Clerk#000012422',0,'ays are slyly after the slyly regular platelets. expres'),
(32225184,2546588,'F',299433.02,'1992-01-09','1-URGENT','Clerk#000004466',0,'l packages wake slyly: fluffily regular packages boost along the ironic foxes.'),
(32988261,11935817,'F',388914.37,'1992-01-10','4-NOT SPECIFIED','Clerk#000043048',0,'sits according to the quickly final deposits ');

GRANT ALL PRIVILEGES ON TABLE snowflake_sample_data.tpch_sf10.orders TO ROLE nac;

USE ROLE nac;
CREATE DATABASE IF NOT EXISTS nac_test;
CREATE SCHEMA IF NOT EXISTS nac_test.data;

USE SCHEMA nac_test.data;

CREATE VIEW IF NOT EXISTS orders AS SELECT * FROM snowflake_sample_data.tpch_sf10.orders;

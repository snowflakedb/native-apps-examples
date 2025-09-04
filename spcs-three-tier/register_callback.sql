USE ROLE nac;
USE WAREHOUSE wh_nac;
GRANT USAGE ON WAREHOUSE wh_nac TO APPLICATION spcs_app_instance;

CALL spcs_app_instance.versioned_schema.register_single_callback('ORDERS_TABLE' , 'ADD', SYSTEM$REFERENCE('VIEW', 'NAC_TEST.DATA.ORDERS', 'PERSISTENT', 'SELECT'));
grant create compute pool on account to application spcs_app_instance;
grant bind service endpoint on account to application spcs_app_instance;
USE ROLE nac;
USE WAREHOUSE wh_nac;
GRANT USAGE ON WAREHOUSE wh_nac TO APPLICATION spcs_app_instance;
CALL spcs_app_instance.v1.register_single_callback('ORDERS_TABLE' , 'ADD', SYSTEM$REFERENCE('VIEW', 'NAC_TEST.DATA.ORDERS', 'PERSISTENT', 'SELECT'));

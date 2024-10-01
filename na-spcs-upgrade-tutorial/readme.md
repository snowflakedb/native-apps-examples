### Summary:
This guide walks through managing versions of a Snowflake Native App using Snowpark Container Services:

1. **Setup Version `v1.0`:** An application package is created, along with schemas, roles, and procedures. A Docker-based echo service and UDF are deployed.
   
2. **Upgrade to Version `v1.1` (Hotfix):** A hotfix changes the service endpoint from public to private. The service's YAML file is updated, and a version upgrade applies the fix.

3. **Simulate Upgrade Failure (Version `v2.0`):** The guide simulates an upgrade failure by introducing an error in the setup script. The system automatically reverts to version `v1.1`, keeping the service operational.

4. **Fix the Error (Version `v2.1`):** After fixing the error, the app is successfully upgraded to version `v2.1`.

5. **Upgrade to Version `v3.0`:** To create version `v3.0`, version `v1` is dropped (since only two active versions are allowed), and the upgrade is completed.

This tutorial demonstrates managing lifecycle upgrades, dealing with failures, and ensuring service continuity.







This tutorial is built upon the tutorial `Create a Snowflake Native App with Snowpark Container Services`(https://docs.snowflake.com/en/developer-guide/native-apps/tutorials/na-spcs-tutorial).
Please skip the last step `Teardown the app and objects`


So now we should have application package `NA_SPCS_TUTORIAL_PKG` and the files in the stage:
```sql
list @na_spcs_tutorial_pkg.app_src.stage;
```
Output:
stage/README.md
stage/manifest.yml
stage/service/echo_spec.yaml
stage/setup_script.sql


We also should have the docker image `my_echo_service_image` in the image repository, and it can be revealed by
```sql
SHOW IMAGES IN IMAGE REPOSITORY tutorial_image_database.tutorial_image_schema.tutorial_image_repo;
```


### Step 1: Set Up Version `v1.0`


Firstly we need to drop the app as the app is installed from stage, and it is not suitable for upgrade demo(we will get error `Operation 'UPGRADE' is not supported on applications created from versions or stages.`).


```sql
use role tutorial_role
DROP APPLICATION na_spcs_tutorial_app CASCADE;
```


Change the setup_script.sql into
```sql
CREATE APPLICATION ROLE IF NOT EXISTS app_user;


CREATE SCHEMA IF NOT EXISTS core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_user;


CREATE OR ALTER VERSIONED SCHEMA app_public;
GRANT USAGE ON SCHEMA app_public TO APPLICATION ROLE app_user;
CREATE OR REPLACE PROCEDURE app_public.service_status()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
AS $$
  DECLARE
        service_status VARCHAR;
  BEGIN
        CALL SYSTEM$GET_SERVICE_STATUS('core.echo_service') INTO :service_status;
        RETURN PARSE_JSON(:service_status)[0]['status']::VARCHAR;
  END;
$$;
GRANT USAGE ON PROCEDURE app_public.service_status() TO APPLICATION ROLE app_user;


--check if a service exists
CREATE OR REPLACE PROCEDURE app_public.service_exists(name STRING)
   RETURNS boolean
   LANGUAGE sql
   AS $$
   DECLARE
       ct INTEGER;
   BEGIN
       SELECT ARRAY_SIZE(PARSE_JSON(SYSTEM$GET_SERVICE_STATUS(:name))) INTO ct;
       IF (ct > 0) THEN
           RETURN true;
       END IF;
       RETURN false;
   EXCEPTION WHEN OTHER THEN
       RETURN false;
   END;
   $$;


CREATE OR REPLACE PROCEDURE app_public.create_service_and_function()
  RETURNS string
  LANGUAGE sql
  AS
$$
BEGIN
  -- account-level compute pool object prefixed with app name to prevent clashes
  LET pool_name := (SELECT CURRENT_DATABASE()) || '_compute_pool';


  CREATE COMPUTE POOL IF NOT EXISTS IDENTIFIER(:pool_name)
     MIN_NODES = 1
     MAX_NODES = 1
     INSTANCE_FAMILY = CPU_X64_XS
     AUTO_RESUME = true;


  CREATE SERVICE IF NOT EXISTS core.echo_service
     IN COMPUTE POOL identifier(:pool_name)
     FROM spec='echo_spec.yaml';
      -- Since the ALTER SERVICE is an async process, wait for the service to be ready
     SELECT SYSTEM$WAIT_FOR_SERVICES(100, 'core.echo_service');


    GRANT USAGE ON SERVICE core.echo_service TO APPLICATION ROLE app_user;
    CREATE OR REPLACE FUNCTION core.my_echo_udf (TEXT VARCHAR)
     RETURNS varchar
     SERVICE=core.echo_service
     ENDPOINT=echoendpoint
     AS '/echo';
     GRANT USAGE ON FUNCTION core.my_echo_udf (varchar) TO APPLICATION ROLE app_user;
  RETURN 'Created successfully';
END;
$$;


grant usage on procedure app_public.create_service_and_function() to APPLICATION ROLE app_user;


CREATE OR REPLACE PROCEDURE app_public.start_app()
  RETURNS string
  LANGUAGE sql
  AS
$$
BEGIN
  call app_public.create_service_and_function();
  return 'DONE';
END;
$$;
GRANT USAGE ON PROCEDURE app_public.start_app() TO APPLICATION ROLE app_user;


-- This procedure is a version_initializer callback. It is called in two cases:
-- i) After all other setup queries have finished.
-- ii) When an upgrade to the next version/patch fails, and the system falls back to the current version.


CREATE OR REPLACE PROCEDURE app_public.version_init()
  RETURNS STRING
  LANGUAGE SQL
AS
$$
DECLARE
   can_create_compute_pool BOOLEAN;  -- Flag to check if 'CREATE COMPUTE POOL' privilege is held
   service_existed BOOLEAN;          -- Flag to check if the 'core.echo_service' exists
BEGIN
   -- Check if the account holds the 'CREATE COMPUTE POOL' privilege
   SELECT SYSTEM$HOLD_PRIVILEGE_ON_ACCOUNT('CREATE COMPUTE POOL')
   INTO can_create_compute_pool;

   -- Check if the service 'core.echo_service' exists
   CALL app_public.service_exists('core.echo_service')
   INTO service_existed;

   IF (can_create_compute_pool) THEN
       -- This block should not run during the app installation, as the app consumer
       -- does not grant the 'CREATE COMPUTE POOL' privilege at installation time.
       IF (NOT service_existed) THEN
           -- If service does not exist, create the service and its associated function
           CALL app_public.create_service_and_function();
       ELSE
           -- If the service exists, update it using the specification file
           ALTER SERVICE IF EXISTS core.echo_service
           FROM SPECIFICATION_FILE = 'echo_spec.yaml';

           -- Since the ALTER SERVICE is an async process, wait for the service to be ready
           SELECT SYSTEM$WAIT_FOR_SERVICES(100, 'core.echo_service');
       END IF;
   END IF;

   -- Default return value if none of the conditions are met
   RETURN 'DONE';
END;
$$;
```


change the manfifest.yml to
```yaml
manifest_version: 1


artifacts:
 setup_script: setup_script.sql
 readme: README.md
 container_services:
   images:
     - /tutorial_image_database/tutorial_image_schema/tutorial_image_repo/my_echo_service_image:latest


lifecycle_callbacks:
 version_initializer: app_public.version_init


privileges:
 - BIND SERVICE ENDPOINT:
     description: "A service that can respond to requests from public endpoints."
 - CREATE COMPUTE POOL:
     description: "Permission to create compute pools for running services"


```


Upload the updated files to the stage by running:


```bash
snow sql -q 'PUT FILE://<PATH_TO_FOLDER_CONTAIN_SETUP_SCRIPT>/* @na_spcs_tutorial_pkg.app_src.stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE';
```


Next, create version `v1.0` and set the release directive:


```sql
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG ADD VERSION v1 USING @na_spcs_tutorial_pkg.app_src.stage;
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG SET DEFAULT RELEASE DIRECTIVE VERSION=v1 PATCH=0;
```


Finally, install the app for the upgrade demo:


```sql
CREATE APPLICATION app_up FROM APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG;
```


Before using the app, we need to grant the CREATE COMPUTE POOL privilege to the app by running the following:
```sql
grant create compute pool on account to application app_up;
grant bind service endpoint on account to application app_up;
```


Then we can start app
```sql
CALL app_up.app_public.start_app();
```


Verify that the app is installed at version `v1.0`:


```sql
DESC APPLICATION app_up;
```

We can call the function
```sql
SELECT app_up.core.my_echo_udf('hello!');
```
It should return `Bob said hello!`.

We also can visit the service from UI.
First we get the service's ingress_url by 

```sql
SHOW ENDPOINTS IN SERVICE app_up.core.echo_service;
```

Then we can visit the it from UI by the follow url
https://<ingress_url>/ui

### Step 2: Upgrade to Version `v1.1` for a hotfix

Soon we realize that we should not expose the service's to the public.
We need to fix it by setting the endpint from `public` to `false` in the file `echo_spec.yaml`.
```yml
  endpoint:
  - name: echoendpoint
    port: 8000
    public: true
``` 

Firstly we update the file into the stage by

```bash
snow sql -q 'PUT FILE://<PATH_TO_FOLDER_CONTAIN_SETUP_SCRIPT>/* @na_spcs_tutorial_pkg.app_src.stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE';
```
To upgrade the app, add a patch for version `v1.1`:


```sql
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG ADD PATCH FOR VERSION v1 USING @na_spcs_tutorial_pkg.app_src.stage;
```


Set version `v1.1` as the default release directive:


```sql
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG SET DEFAULT RELEASE DIRECTIVE VERSION=v1 PATCH=1;
```


Perform the manual upgrade:


```sql
ALTER APPLICATION app_up UPGRADE;
```


Confirm that the upgrade is successful by running the following:


```sql
DESC APPLICATION app_up;
```

The service should not be accessed from the consumer directly:
The `ingress_url` is `null` by the sql

```sql
SHOW ENDPOINTS IN SERVICE app_up.core.echo_service;
```

But we still can access the service through the function `core.my_echo_udf (TEXT VARCHAR)`



---


### Step 3: Upgrade to Version `v2.0` and Simulate an Error


Next, we will simulate a failed upgrade to version `v2.0`. Update the `setup_script.sql` to include an intentional error:


```sql
SELECT * FROM non_exist_table;
```


change the setup_script.sql into:
```sql
CREATE APPLICATION ROLE IF NOT EXISTS app_user;


CREATE SCHEMA IF NOT EXISTS core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_user;


CREATE OR ALTER VERSIONED SCHEMA app_public;
GRANT USAGE ON SCHEMA app_public TO APPLICATION ROLE app_user;
GRANT USAGE ON PROCEDURE app_public.service_status() TO APPLICATION ROLE app_user;


CREATE OR REPLACE PROCEDURE app_public.service_exists(name STRING)
   RETURNS boolean
   LANGUAGE sql
   AS $$
   DECLARE
       ct INTEGER;
   BEGIN
       SELECT ARRAY_SIZE(PARSE_JSON(SYSTEM$GET_SERVICE_STATUS(:name))) INTO ct;
       IF (ct > 0) THEN
           RETURN true;
       END IF;
       RETURN false;
   EXCEPTION WHEN OTHER THEN
       RETURN false;
   END;
   $$;


CREATE OR REPLACE PROCEDURE app_public.version_init()
  RETURNS string
  LANGUAGE sql
  AS
$$
BEGIN
   DROP SERVICE IF EXISTS core.echo_service;
   CREATE OR REPLACE FUNCTION core.my_echo_udf (say VARCHAR)
     RETURNS varchar
     as
      $$
        'Bob said ' || say || '!'
     $$;
  GRANT USAGE ON FUNCTION core.my_echo_udf (varchar) TO APPLICATION ROLE app_user;
  -- trigger an error
  select * from non_exist_table;
END;
$$;
```


Upload the modified files to the stage, then add version `v2.0` and set it as the default:


```sql
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG ADD VERSION v2 USING @NA_SPCS_TUTORIAL_PKG2.test.st;
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG SET DEFAULT RELEASE DIRECTIVE VERSION=v2 PATCH=0;
```


Try to upgrade the app manually:


```sql
ALTER APPLICATION app_up UPGRADE;
```


You'll see an error message due to the failed setup script. To inspect the app's status:


```sql
DESC APPLICATION app_up;
```


Additionally, verify that the service was not dropped despite the failed upgrade:


```sql
DESC SERVICE app_up.core.echo_service;
```


The system automatically invokes the `version_initializer` for version `v1.1`, which ensures the service remains operational after the failure.


---


### Step 4: Fix the Error in Version `v2.1`


To resolve the issue, remove the faulty query (`SELECT * FROM non_exist_table;`) from `setup_script.sql`. Upload the corrected files to the stage, then create a patch for version `v2.1`:


```sql
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG ADD PATCH TO VERSION v2 USING @NA_SPCS_TUTORIAL_PKG2.test.st;
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG SET DEFAULT RELEASE DIRECTIVE VERSION=v2 PATCH=1;
```


Perform the upgrade again:


```sql
ALTER APPLICATION app_up UPGRADE;
```


Check that the upgrade to version `v2.1` is now successful:


```sql
DESC APPLICATION app_up;
```


---


### Step 5: Upgrade to Version `v3.0`


Now, we'll create version `v3.0`. Before doing so, note that Native App Framework allows only two active versions of an application package at a time. Therefore, you must drop version `v1` to proceed.


Attempting to create version `v3.0` without dropping an existing version will result in this error:


```sql
There are 2 active versions, the maximum allowed. An existing version must be dropped before adding an additional version.
```


Drop version `v1`:


```sql
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG DROP VERSION v1;
```


Now create and set version `v3.0`:


```sql
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG ADD VERSION v3 USING @NA_SPCS_TUTORIAL_PKG2.test.st;
ALTER APPLICATION PACKAGE NA_SPCS_TUTORIAL_PKG SET DEFAULT RELEASE DIRECTIVE VERSION=v3 PATCH=0;
```


Finally, perform the upgrade to `v3.0`:


```sql
ALTER APPLICATION app_up UPGRADE;
```

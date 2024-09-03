# Example Native App with Snowpark Container Services

This is a simple three-tiered web app that can be deployed
in Snowpark Container Services. It queries the TPC-H 100 
data set and returns the top sales clerks. The web app
provides date pickers to restrict the range of the sales
data and a slider to determine how many top clerks to display.
The data is presented in a table sorted by highest seller
to lowest.

This app was built with 3 containers:
* Frontend written in JavaScript using the Vue framework
* Backend written in Python using the Flask framework
* Router using nginx to allow the Frontend and Backend to 
  be on the same URL and avoid CORS issues.

This app is deployed as 2 separate `SERVICE`s:
* The Frontend and Router containers are deployed in one service.
* The Backend container is deployed in its own service.

The reason to split them this way is so that the Frontend and 
Backend can autoscale differently. Moreover, you could deploy
the Frontend and Backend to different `COMPUTE POOL`s, which would
support the case where the Backend needs more compute power than 
the Frontend, which is typically pretty light.

## Getting Started

### Prerequisites

1. Install Docker
    - [Windows](https://docs.docker.com/desktop/install/windows-install/)
    - [Mac](https://docs.docker.com/desktop/install/mac-install/)
    - [Linux](https://docs.docker.com/desktop/install/linux-install/)

2. Setup connection

    Before running the **setup.sh** file you should run the following command to set a snowflake default connection by choosing it from your config.toml file.

    ```bash
    export SNOWFLAKE_DEFAULT_CONNECTION_NAME=<your_connection>
    ```

    Replacing `<your_connection>` with you actual connection name, without the `<>`.

### Setup

Execute the shell script named `setup.sh` in the root folder:

```bash
./setup.sh
```

The setup script runs the following scripts:

- Provider side setup (`provider_setup.sql`)
- Consumer side setup (`consumer_setup.sql`)
- Image repository setup by executing `make all` command

### Deploy application package

Run the following command in your opened terminal:

```bash
./deploy.sh
```
This bash file performs two operations:

- `snow app run`
- Creates a reference to the `orders` view.

For this command to function, your shell must be in the same directory as `snowflake.yml` (the project root).

### Run application

When you enter the application UI for the first time, an initial setup screen will appear:

#### Step 1: Grant Account Privileges

This step allows the application to bind `SERVICE ENDPOINT`s and create `COMPUTE POOL`s. Click the `Grant` button to grant these privileges on the account to the application object.

#### Step 2: Allow Connections

The second step creates a new `EXTERNAL ACCESS INTEGRATION` targeting the `upload.wikimedia.org` website. Click on `Review`, then on `Connect`.

#### Activate the application

Once all the steps are completed, you can activate the application by clicking the `Activate` button. When the button is clicked, the `grant_callback` defined in the [manifest.yml](app/manifest.yml) is executed.
In this example, our callback creates two `COMPUTE POOL`s in the account and two `SERVICE`s inside of the application object.

#### Launch Application

Once all these dependencies have been met, you can launch the app by clicking on the `Launch App` button. A new window will be displayed with the URL provided by the service and endpoint defined by `default_web_endpoint` in the [manifest.yml](app/manifest.yml).

#### Cleanup
To clean up the Native App test install, you can execute `cleanup.sh`, which will stop the services and run `snow app teardown`:

```bash
./cleanup.sh
```

### Publishing / Sharing your Native App
Your Native App is now ready on the Provider Side. You can make the Native App available
for installation in other Snowflake Accounts by creating a version and release directive, then setting
the default patch and Sharing the App in the Snowsight UI.

See the [documentation](https://other-docs.snowflake.com/en/native-apps/provider-publishing-app-package) for more information.

1. Navigate to the "Apps" tab and select "Packages" at the top.

2. Now click on your App Package (`NA_SPCS_PYTHON_PKG`).

3. From here you can click on "Set release default" and choose the latest patch (the largest number) for version `v1`. 

4. Next, click "Share app package". This will take you to the Provider Studio.

5. Give the listing a title, choose "Only Specified Consumers", and click "Next".

6. For "What's in the listing?", select the App Package (`NA_SPCS_PYTHON_PKG`). Add a brief description.

7. Lastly, add the Consumer account identifier to the "Add consumer accounts".

8. Click "Publish".


### Upgrade
Upgrades can be performed in two ways:

* Automated Upgrades: These occur when the provider updates the release directive on the application package, 
triggering an automatic upgrade for all installed instances specified by the directive.

* Manual Upgrades: These are initiated by the consumer, who manually runs the ALTER APPLICATION command to perform 
the upgrade.

In this tutorial, we will focus on manual upgrades to demonstrate how the upgrade process works within the Native App Framework. The application is installed in the provider's account, so all commands will be executed within the provider's environment.

#### Add version
```sql
    alter application package spcs_app_pkg add version v1 using @spcs_app_pkg.napp.app_stage;
```
#### Set release directive
```sql
     alter application package spcs_app_pkg set default release directive version=v1 patch=0;
```
#### manual upgrade
```sql
    alter application app upgrade
```
#### check application status
```sql
    desc application app
```
it will show the application's current version, patch, update_state and more.

#### add version v2 and upgrade

##### change endpoints
in frontend.yaml
change the endpoints from
```yaml
endpoints:
  - name: app
    port: 8000
    public: true
```
to
```yaml
endpoints:
  - name: app1
    port: 8003
    public: true
  - name: app2
    port: 8004
    public: true
```

To upload the file into the stage @spcs_app_pkg.napp.app_stage, we can use snowsql such as

```bash
  snow sql -q 'put file:///DIRECTOR_TO_EXAMPLE/native-apps-examples/spcs-three-tier/app/* @spcs_app_pkg.napp.app_stage auto_compress=false overwrite=true'
```
```sql
    alter application package spcs_app_pkg add patch for version v1 using @spcs_app_pkg.napp.app_stage;
    alter application package spcs_app_pkg set default release directive version=v1 patch=0;
    alter application app upgrade;
```
After that, you can show the service endpoints by 
```sql
    SHOW ENDPOINTS IN SERVICE spcs_app_instance.app_public.frontend;
```
it will show as

| Name | Port | Port Range | Protocol | Is_Public | Ingress_URL                                                                    |
|------|------|------------|----------|-----------|--------------------------------------------------------------------------------|
| app1 | 8003 |            | HTTP     | true      | c3xsbsr-sfengineering-na-spcs-p1-qa6.awsuswest2qa6.test-snowflakecomputing.app |
| app2 | 8004 |            | HTTP     | true      | c3xsbsn-sfengineering-na-spcs-p1-qa6.awsuswest2qa6.test-snowflakecomputing.app |


##### add version v2
```sql
    alter application package spcs_app_pkg add version v2 using @spcs_app_pkg.napp.app_stage;
    alter application package spcs_app_pkg set default release directive version=v2 patch=0;
```
##### upgrade fails
change endpoints in the spec file `frontend.yaml`
  ```yaml
endpoints:
  - name: app1
    port: 8003
    public: true
  - name: app2
    port: 8004
    public: true
  - name: app3
    port: 8005
    public: true
```
replace the PROCEDURE `CREATE OR REPLACE PROCEDURE versioned_schema.init()` into
```sql
CREATE OR REPLACE PROCEDURE versioned_schema.init()
RETURNS STRING
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    can_create_compute_pool BOOLEAN;
BEGIN
    SELECT SYSTEM$HOLD_PRIVILEGE_ON_ACCOUNT('create compute pool') INTO :can_create_compute_pool;
    IF (:can_create_compute_pool) THEN
        ALTER SERVICE IF EXISTS app_public.frontend FROM SPECIFICATION_FILE='frontend.yaml';
        ALTER SERVICE IF EXISTS app_public.backend FROM SPECIFICATION_FILE='backend.yaml';
        -- ALTER SERVICE is async. To minimize the downtime we need to wait until the services are ready.
        SELECT system$wait_for_services(180, 'app_public.backend', 'app_public.frontend');
        
        -- This SQL will trigger an error and the upgrade will fail
        SELECT * FROM non_exists_table;
        
    END IF;
    RETURN 'init complete';
END $$;

```

Then upgrade the app
```sql
    alter application package spcs_app_pkg add version v2 using @spcs_app_pkg.napp.app_stage;
    alter application package spcs_app_pkg set default release directive version=v2 patch=0;
```
When querying 
```sql
    desc application app   
```
The table below shows part of the output. Please note that the upgrade_target_version is 2 and upgrade target patch 
is 0. The update_state is failed, and it also gives the 
upgrade_failure_reason. In this case, the app is running v1.1 version.

| Property                          | Value                                                                                                                                                                                                                                                  |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| name                              | SPCS_APP_INSTANCE                                                                                                                                                                                                                                      |
| version                           | V1                                                                                                                                                                                                                                                     |
| patch                             | 1                                                                                                                                                                                                                                                      |
| created_on                        | 2024-08-30 13:42:58.250 -0700                                                                                                                                                                                                                          |
| upgrade_state                     | FAILED                                                                                                                                                                                                                                                 |
| upgrade_target_version            | 2                                                                                                                                                                                                                                                      |
| upgrade_target_patch              | 0                                                                                                                                                                                                                                                      |
| upgrade_attempt                   | 3                                                                                                                                                                                                                                                      |
| upgrade_started_on                | 2024-09-02 06:23:37.210 -0700                                                                                                                                                                                                                          |
| upgrade_attempted_on              | 2024-09-02 06:25:17.247 -0700                                                                                                                                                                                                                          |
| upgrade_failure_type              | VERSION_SETUP                                                                                                                                                                                                                                          |
| upgrade_failure_reason            | "[ErrorCode 2003] Uncaught exception of type 'STATEMENT_ERROR' on line 171 at position 0 : Uncaught exception of type 'STATEMENT_ERROR' on line 12 at position 8 : SQL compilation error: Object 'NON_EXISTS_TABLE' does not exist or not authorized." |

The failed SQL query `SELECT * FROM non_exists_table` occurs after the  `ALTER SERVICE` statement. This raises concerns 
about the service version, as it might suggest the services are running the version defined in v2.0. However, the 
services are actually running version v1.1, which can be confirmed by executing the query `SHOW ENDPOINTS IN SERVICE 
spcs_app_instance.app_public.frontend`. The secret is we put `ALTER SERVICE` command within the `version_initializer` 
of the `lifecycle_callbacks`. This ensures that if the upgrade to the target version (v2.0) fails, the system will 
invoke the `version_initializer` for the current version (v1.1), thereby reverting the services to the correct version.

#### Handling Upgrade Failures

Upgrade failures can occur for various reasons, often due to issues on the provider's side, such as errors in the setup script. When this happens, all upgrades may fail. To address this, you have a couple of options:

* Rollback to a previous version: For example, in the scenario mentioned above, you can revert the release directive 
to version v1.1 by running the following command:

```sql
    ALTER APPLICATION PACKAGE spcs_app_pkg SET DEFAULT RELEASE DIRECTIVE VERSION=v1.1 PATCH=0;
```

* Create a new version: Correct the errors and release a new version. After passing the necessary security review, 
you can set this new version as the default release directive. However, be aware that the security review process can take some time.


### Debugging
There are some Stored Procedures to allow the Consumer to see the status
and logs for the containers and services. These procedures are granted to the `app_admin`
role and are in the `app_public` schema:
* `GET_SERVICE_STATUS()` which takes the same arguments and returns the same information as `SYSTEM$GET_SERVICE_STATUS()`
* `GET_SERVICE_LOGS()` which takes the same arguments and returns the same information as `SYSTEM$GET_SERVICE_LOGS()`

The permissions to debug are managed on the Provider in the 
`NA_SPCS_PYTHON_PKG.SHARED_DATA.FEATURE_FLAGS` table. 
It has a very simple schema:
* `acct` - the Snowflake account to enable. This should be set to the value of `SELECT current_account()` in that account.
* `flags` - a VARIANT object. For debugging, the object should have a field named `debug` which is an 
  array of strings. These strings enable the corresponding stored procedure:
  * `GET_SERVICE_STATUS`
  * `GET_SERVICE_LOGS`

An example of how to enable logging for a particular account (for example, account 
`ABC12345`) to give them all the debugging permissions would be

```sql
INSERT INTO llama2_pkg.shared_data.feature_flags 
  SELECT parse_json('{"debug": ["GET_SERVICE_STATUS", "GET_SERVICE_LOGS"]}') AS flags, 
         'ABC12345' AS acct;
```

To enable on the Provider account for use while developing on the Provider side, you could run

```sql
INSERT INTO llama2_pkg.shared_data.feature_flags 
  SELECT parse_json('{"debug": ["GET_SERVICE_STATUS", "GET_SERVICE_LOGS"]}') AS flags,
         current_account() AS acct;
```

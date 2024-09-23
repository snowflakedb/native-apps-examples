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

Add the version and set the release directive in the provider account
```sql
    ALTER APPLICATION PACKAGE spcs_app_pkg ADD VERSION v1 using @spcs_app_pkg.napp.app_stage;
    ALTER APPLICATION PACKAGE spcs_app_pkg SET DEFAULT RELEASE DIRECTIVE VERSION=v1 PATCH=0;
```

Publish the app:

1. Navigate to the "Apps" tab and select "Packages" at the top.
   spcs_app_pkg
2. Now click on your App Package (`spcs_app_pkg`).

3. From here you can click on "Set release default" and choose the latest patch (the largest number) for version `v1`. 

4. Next, click "Share app package". This will take you to the Provider Studio.

5. Give the listing a title, choose "Only Specified Consumers", and click "Next".

6. For "What's in the listing?", select the App Package (`spcs_app_pkg`). Add a brief description.

7. Lastly, add the Consumer account identifier to the "Add consumer accounts".

8. Click "Publish".

### Install Native App in Consumer Account


### Upgrade a Native App
Upgrades can be performed in two ways:

* Automated Upgrades: Triggered automatically  when the provider updates the release directive on the application 
  package. All installed instances specified by the directive are upgraded automatically.

* Manual Upgrades:  Initiated by the consumer, who manually executes the ALTER APPLICATION command to perform the upgrade.

From the last step, we had an app called `spcs_app_instance` in the consumer account.

In this tutorial, we'll demonstrate the upgrade process within the Native App Framework.

#### Add a Patch to Version v1 and Upgrade

##### change endpoints
Update the endpoints in the frontend.yaml file.
Before:
```yaml
endpoints:
  - name: app
    port: 8000
    public: true
```
After
```yaml
endpoints:
  - name: app1
    port: 8003
    public: true
  - name: app2
    port: 8004
    public: true
```

To upload the file into the stage @spcs_app_pkg.napp.app_stage, we can use snowsql:

```bash
  snow sql -q 'put file:///DIRECTOR_TO_EXAMPLE/native-apps-examples/spcs-three-tier/app/* @spcs_app_pkg.napp.app_stage auto_compress=false overwrite=true'
```

add a patch and set default release directive in the provider account
```sql
    alter application package spcs_app_pkg add patch for version v1 using @spcs_app_pkg.napp.app_stage;
    alter application package spcs_app_pkg set default release directive version=v1 patch=1;
```

#### Upgrade process
The app should automatically update to version v1.1 after several minutes or hours once the default release directive is set.

For manual upgrades (immediate and synchronous), run the following in the consumer account:

```sql
    alter application spcs_app_instance upgrade
```

#### Check Application Status
To check the status of the application, including the current version and patch:
```sql
    desc application app
```
This will display the application's current version, patch, upgrade state, and more.

To verify that the updated services are deployed:
```sql
    SHOW ENDPOINTS IN SERVICE spcs_app_instance.app_public.frontend;
```
**Expected output:**

| Name | Port | Port Range | Protocol | Is_Public | Ingress_URL  |
|------|------|------------|----------|-----------|--------------|
| app1 | 8003 |            | HTTP     | true      | [app1-url]   |
| app2 | 8004 |            | HTTP     | true      | [app1-url]   |


##### upgrades to version v2 and fails

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
        
        -- ALTER SERVICE is async process. To minimize the downtime we need to wait until the services are ready.
        SELECT system$wait_for_services(180, 'app_public.backend', 'app_public.frontend');
        
        -- Trigger an error
        SELECT * FROM non_exists_table;
                
    END IF;
    RETURN 'init complete';
END $$;

```

###### Add Version v2 and Attempt the Upgrade

In the provider account
```sql
    alter application package spcs_app_pkg add version v2 using @spcs_app_pkg.napp.app_stage;
    alter application package spcs_app_pkg set default release directive version=v2 patch=0;
```
In the consumer account
```sql
    alter application spcs_app_instance upgrade;
```
Check the application’s upgrade status in the consumer account:
```sql
    desc application app   
```
The table below shows part of the output. Please note that the `upgrade_target_version` is `v2` and 
`upgrade_target_patch` is `0`. The `update_state` is `FAILED`, and it also gives the 
`upgrade_failure_reason`. In this case, the app remains on the previous version (v1.1).

| Property                          | Value                                                                                                                                                                                                                                                  |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| name                              | SPCS_APP_INSTANCE                                                                                                                                                                                                                                      |
| version                           | V1                                                                                                                                                                                                                                                     |
| patch                             | 1                                                                                                                                                                                                                                                      |
| upgrade_state                     | FAILED                                                                                                                                                                                                                                                 |
| upgrade_target_version            | 2                                                                                                                                                                                                                                                      |
| upgrade_target_patch              | 0                                                                                                                                                                                                                                                      |
| upgrade_attempt                   | 3                                                                                                                                                                                                                                                      |
| upgrade_failure_type              | VERSION_SETUP                                                                                                                                                                                                                                          |
| upgrade_failure_reason            | "[ErrorCode 2003] Uncaught exception of type 'STATEMENT_ERROR' on line 171 at position 0 : Uncaught exception of type 'STATEMENT_ERROR' on line 12 at position 8 : SQL compilation error: Object 'NON_EXISTS_TABLE' does not exist or not authorized." |

##### Version Initializer for SPCS Service Upgrade

The failed SQL query `SELECT * FROM non_exists_table` occurs **after** the `ALTER SERVICE` statement in v2.0, but the 
`ALTER SERVICE` command still runs successfully. This raises concerns about the service version: although the services might appear to be running version `v2.0`, they are actually running version `v1.1`.

The key is the `ALTER SERVICE` command is inside the `version_initializer` of the `lifecycle_callbacks`. If the upgrade to version `v2.0` fails, the system will invoke the `version_initializer` for the current version (`v1.1`), effectively reverting the services to the correct version.

**Important Tips for the `version_initializer` Callback Procedure**:
- The callback procedure should reside in a **versioned schema**.
- Code/SQL responsible for creating and altering SPCS services must be included **within the callback procedure** to ensure proper rollback in the event of upgrade failure.
- If the `ALTER SERVICE` command is not placed inside `version_initializer`, the services might remain in version `v2.0`, even after an upgrade failure.

---

##### Handling Upgrade Failures

Upgrade failures can happen due to issues on the provider's side, such as errors in the setup script. In such cases, upgrades might fail for all consumers. To handle this, you have a few options:

* Rollback to a previous version: In the scenario described above, you can revert the release directive to version `v1.1` by running the following command:

```sql
    ALTER APPLICATION PACKAGE spcs_app_pkg SET DEFAULT RELEASE DIRECTIVE VERSION=v1 PATCH=1;
```

* Create a new version: Correct the errors and release a new version. After passing the necessary security review, you can set this new version as the default release directive. However, be aware that the security review process can take some time.


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

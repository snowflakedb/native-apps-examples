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

- Snowpark Container Services setup (`spcs_setup.sql`)
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

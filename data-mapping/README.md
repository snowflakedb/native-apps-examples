# Data Mapping

This code accompanies the "**Data Mapping in Snowflake Native Apps using Streamlit**" quickstart. Please refer to [this page](https://quickstarts.snowflake.com/guide/data_mapping_in_native_apps/index.html?index=..%2F..index#0) for a more detailed explanation of this application and its components.

## Prerequisites

1. Download the CSV file from [here](https://lite.ip2location.com/database/db11-ip-country-region-city-latitude-longitude-zipcode-timezone?_fsi=cmNyOoGm&_fsi=cmNyOoGm) and unzip it in your local machine, the **IPV4** file is the one we are using in this quickstart. **Note:** An account is needed to download the file, refer to the **step 2** of the quickstart page.
2. Replace the CSV filepath inside the [prepare_data.sh](./prepare_data.sh) file, like this:  
    ```sh
    snow object stage copy /USER_PATH_HERE/IP2LOCATION-LITE-DB11.CSV @location_data_stage --database ip2location --schema ip2location
    ```
3. Setup your preferred connection using the latest Snowflake CLI version available, which can be downloaded **[here](https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/installation/installation)**.

## Run instructions 


1. After cloning the repo and replacing the CSV path, run this in your terminal (inside the native app root folder) to create and prepare the necessary data:

    `
    SNOWFLAKE_DEFAULT_CONNECTION_NAME=<your_connection> ./prepare_data.sh
    `

    replacing <your_connection> with you actual connection name, without the <>.
Note that the CSV file might take a while to upload to the stage, depending on your internet connection's upload speed.

2. To create the application, type:
    ```sh
    snow app run
    ```
3. Open the link to your app that appeared in the terminal output.
4. Give the needed permissions to the TEST_IPLOCATION.TEST_IPLOCATION.TEST_DATA table using the **Manage Access** option at the top right corner of your app page, then go to the App **Dashboard** tab located a little to the left.
5. Change the **RESULT COLUMN** option to: IP_DATA and then press **UPDATE MAPPINGS** and **UPDATE** buttons, in that order.
6. Run 
    ```sh
    snow sql -q "
    USE DATABASE TEST_IPLOCATION;
    USE SCHEMA TEST_IPLOCATION;
    SELECT * FROM TEST_DATA;"
    ```
    to verify that the **UPDATE** button actually added some ip info inside your table.
7. To delete the app, run: 
    ```sh
    snow app teardown
    snow sql -q "
    DROP DATABASE IP2LOCATION;
    DROP DATABASE TEST_IPLOCATION;"
    ```

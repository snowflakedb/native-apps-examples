# Object-level References

The goal of this simple native app is to showcase the capabilities of object-level references. These references allow a native app to access specific objects outside the application and selected by the consumer after the application has been installed. These references grant the application permission to interact with user data and functions.

## Data Preparation

The first step is to execute [prepare_data.sh](./prepare_data.sh), so the necessary sample objects exist in your account. A few considerations before executing it:
- You must have setup your preferred connection using the latest Snowflake CLI version available, which can be downloaded [here](https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/installation/installation).
- Because the external table and the API integration examples require you to use an external service such as Azure Blobs or Amazon Lambda Functions, the UI implementation of these capabilities are disabled by default. Take the next step into consideration if you want to enable them.
- You must execute the prepare_data.sh and choose **y** when the option for external table or api integration is prompted, then add the necessary credentials when the console asks for them.
- When adding the stage path in the external table creation, remember to point it to the containing folder instead of the file itself. And take into consideration that Snowflake will include all the files inside that folder.
- To use the **API integration example**, you can follow this tutorial on [Getting Started With External Functions on AWS](https://quickstarts.snowflake.com/guide/getting_started_external_functions_aws/index.html?index=..%2F..index#0). Follow it until the **Creating an API Integration in Snowflake** step when it creates an api integration, at that point, it indicates you to replace the placeholders for the api integration, those are the ones you should add AT THE PROMPTED INPUT of the **prepare_data.sh** file and CONTINUE with the tutorial, later on at **Calling the external function** step replace the placeholders AT THE EXTERNAL FUNCTION asterkisks mark in the **setup_script.sql** file . Remember to enable the GRANT USAGE permissions AT THE END of the **setup_script.sql** file.

Before running the **prepare_data.sh** you should run the following command to set a snowflake default connection by choosing it from your config.toml file.

   `
   export SNOWFLAKE_DEFAULT_CONNECTION_NAME=<your_connection>
   `

replacing <your_connection> with you actual connection name, without the <>.

To execute the file run this in your terminal (inside the native app root folder) to create and prepare the necessary data:

   `
   ./prepare_data.sh
   `


## App Execution

1. To create the application, type:
    ```sh
    snow app run
    ```
2. Open the link to your app that appears in the terminal output.

3. Bind references to the previously created TABLE, VIEW, FUNCTION, and PROCEDURE that were created by `prepare_data.sh`. If you chose to include them, you should also bind the EXTERNAL TABLE, WAREHOUSE and API INTEGRATION. Do this by using the **Shield icon** option at the top right corner of your app page, then going to the App **Dashboard** tab in the popup. For the warehouse to work properly, ACCOUNTADMIN must have owner permissions on the warehouse, or the monitor privilege has to be granted explicitly.


## App and Data Deletion
 To delete the app and the previously created objects, run in your terminal:

   ```sh
   snow app teardown
   snow sql -q "DROP DATABASE obj_reference_db;"
   # Optionally execute this line if you created the warehouse
   # snow sql -q "DROP WAREHOUSE obj_reference_wh;"
   ```
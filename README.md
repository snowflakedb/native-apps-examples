# Snowflake Native App Examples

**Note**: Snowflake CLI is in Public Preview (PuPr). You can find the official documentation and download links [here](https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/index).

This repository contains example applications built using the [Snowflake Native App](https://docs.snowflake.com/en/developer-guide/native-apps/native-apps-about) Framework. These examples have been built and are supported by Snowflake Inc., are self-contained, and can be deployed directly to your account using Snowflake CLI. 

## Deploying example applications

Deploying and exploring any of the example applications available in this repository is simple. Generally speaking, the process is:

1. Ensure Snowflake CLI is installed and up-to-date
2. Clone this repository
3. Change to the example application directory of your choosing
4. Execute `snow app run` from your command line to deploy the app using your default connection

Some applications require other account-level setup before they can be properly deployed; see the individual application directories for more detailed instructions. To manage your Snowflake CLI connections, see the [Snowflake CLI documentation](https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/connecting/connect).

## Available examples

| Application | Description |
| --- | --- |
| [Account Privileges](./account-privileges/) | How to add account privileges to an object reference within a native application. |
| [Custom Billing Events](./custom-billing-events/) | How to bill costs from the provider side by adding a billing event to a procedure call. |
| [Data Mapping](./data-mapping/) | Accompaniment to the [Data Mapping in Snowflake Native Apps using Streamlit](https://quickstarts.snowflake.com/guide/data_mapping_in_native_apps/index.html?index=..%2F..index#0) quickstart. |
| [External Access Integration](./external-access-integration/) | How to create an external access integration and connect to an API within a native application. |
| [Mailorder](./mailorder/) | How to implement the business operations of an imaginary mail-order business within a native application using Snowpark. |
| [Object-level References](./object-level-references/) | A simple dashboard to show how to interact with the object-level references and bindings. |
| [Reference Usage](./reference-usage/) | How to share a provider table with a native application whose data is replicated to any consumer in the data cloud. |
| [SPCS Three-tier](./spcs-three-tier/) | A simple three-tiered web app that can be deployed in Snowpark Container Services. It queries the TPC-H 100 data set and returns the top sales clerks. |
| [Snowflake Cortex](./snowflake-cortex/) | A simple example on how to implement the Cortex Complete and to make it interact with user data. |
| [Tasks and Streams](./tasks-streams/) | How to execute a task and visualize changes using streams within a native application. |

## Contributing

Contributions are welcome and encouraged under the [Apache 2.0 License](./LICENSE.txt). Please feel free to open issues or pull requests.

# External Access Integration

This Snowflake Native Application sample demonstrates how to add external access integrations as references within a native application.

## Getting Started

This application shows a line chart based on the price timeline of each crypto coin by accessing the [Coincap API](https://docs.coincap.io/) that provides the price timeline in real time of each coin in the market.

To connect to the API, the native application creates a secure connection by creating an [External Access Integration](https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration) from the application to the external API.

The setup script contains some key steps to pay attention to:

- Define an EAI reference in the [manifest.yml](app/manifest.yml).
- Define a `configuration_callback` and `register_callback` in the [setup](app/setup_script.sql) script file.
- Define a stored procedure that creates `function` or `stored procedure` objects binding the EAI reference after it is set.

### Installation

Execute the following command:

```bash
snow app run
```

### First-time setup

You must bind a reference before using the app:

   - *external_access_reference:* The EAI reference will create a [NETWORK RULE](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule) and an External Access Integration with the `json` defined in the `configuration_callback`.

> These references and permissions are defined in [manifest.yml](app/manifest.yml).

Once the EAI reference is created, you can continue to the app by clicking the button. Before the app is loaded, the `create_eai_objects` is called, and creates two new procedures that uses the EAI created to get data from the API.

### Test the app

When you continue to the app, you must see two different controls:

- A date picker that select a date range.
- A select box that contains all the crypto coin names.

The date picker selects the range on where you want to get the price timeline of the choosen coin in the select box and the select box choose the coin which you want to see the price timeline.

When you change the values from both controls, the line chart below will be refreshed with the new information.

### Additional Resources

- [Grant access to a Snowflake Native App](https://other-docs.snowflake.com/en/native-apps/consumer-granting-privs)
- [Create a user interface to request privileges and references](https://docs.snowflake.com/en/developer-guide/native-apps/requesting-ui)
- [CREATE EXTERNAL ACCESS INTEGRATION](https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration)
- [CREATE NETWORK RULE](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule)

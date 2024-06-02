# Tasks and Streams

This Snowflake Native Application sample demonstrates how to execute a task and visualize changes using streams within a native application.

## Getting Started

### Installation

Execute the following command:

```bash
snow app run
```

### First-time setup

You should grant some permissions and bind some references before start with the app.

   - *warehouse_reference:* You must choose the warehouse that your tasks will execute on periodically. This reference grants usage on the selected warehouse to the application. (See `setup_script.sql` on line 70)

   - *EXECUTE TASK* permission: You must grant your application the permission to execute a task.

> These references and permissions are defined in [manifest.yml](app/manifest.yml).

Once permissions and bindings are set, execute the `create_task` procedure to create and start a task that runs every minute. The application cannot create the task directly in the setup script, since it does not have  the `EXECUTE TASK` permission by default.

The created `task` updates the `internal.incremented_values` table by incrementing its only value by one calling the `increment_by_one` procedure.

### Test the app

In the main page of the app, you will see a `dataframe` with the values from the `internal.incremented_values_stream`, a `stream` based on the `internal.incremented_values` table.

The dataframe has two columns:
   - *VALUE*: The incremented number by the task every minute.
   - *ACTION*: The last action applied to the table in each row at a specific time. The action should always be insert. 

At the end of the page, there are three buttons:

- *Start task*: Executes the `create_task` procedure and creates a new task if not exists.
- *Stop Task*: Executes the `stop_task` procedure and stops the already created task if it exists.
- *Refresh*: Reloads the page to see the updated value by the task.

### Additional Resources

- [Grant access to a Snowflake Native App](https://other-docs.snowflake.com/en/native-apps/consumer-granting-privs)
- [Create a user interface to request privileges and references](https://docs.snowflake.com/en/developer-guide/native-apps/requesting-ui)
- [CREATE TASK](https://docs.snowflake.com/en/sql-reference/sql/create-task)
- [CREATE STREAM](https://docs.snowflake.com/en/sql-reference/sql/create-stream)

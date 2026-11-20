# Warehouse Whisperer: Snowflake App Runtime in Native Apps

Warehouse Whisperer is a Next.js chat application that uses Cortex AI to answer questions about `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`. This example demonstrates how to build the application once with Snowflake App Runtime (SAR), publish its artifact, and package that same artifact in two Snowflake Native App architectures.

## Projects

| Project | Purpose | Query warehouse |
| --- | --- | --- |
| [`SAR-standalone`](./SAR-standalone/) | Builds and publishes the shared SAR application artifact. | Provider warehouse `WAREHOUSE_WHISPERER_BUILD_WH` |
| [`na-warehouse-in-app`](./na-warehouse-in-app/) | **Recommended Native App variant.** The app creates and owns dedicated compute. | `WAREHOUSE_WHISPERER_APP_WH` |
| [`na-warehouse-reference`](./na-warehouse-reference/) | Alternative for consumers who must supply and control an existing warehouse. | Bound through `QUERY_WAREHOUSE` |

Both Native App projects package the same SAR artifact. The only intentional difference is how each installed application obtains query compute.

## Application Behavior

For each question, the application:

1. asks Cortex AI to generate Snowflake SQL;
2. validates that the SQL is a single read-only statement;
3. permits only `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` and derived CTEs;
4. enforces a 90-day lookback and a 200-row maximum;
5. executes the query and asks Cortex AI to summarize its evidence;
6. shows the answer, SQL, and result rows.

`ACCOUNT_USAGE` timestamps are UTC, and query history can lag by up to 45 minutes.

## Prerequisites

- Snowflake CLI 3.26.0 or later.
- A provider account with SAR and SAR-in-Native-App support.
- A role that can create roles, databases, warehouses, application packages, and applications.
- Node.js and npm for local tests.

## Deployment Order

### 1. Prepare provider resources

Run [`SAR-standalone/prepare.sql`](./SAR-standalone/prepare.sql) as `ACCOUNTADMIN`. It creates a dedicated execution role, provider database, and X-Small build/query warehouse.

### 2. Build the SAR artifact

```bash
cd SAR-standalone
npm ci
npm test
npm run build
snow app deploy --connection <connection> --role WAREHOUSE_WHISPERER_EXECUTOR
```

Inspect the published version:

```sql
SHOW VERSIONS IN ARTIFACT REPOSITORY
  WAREHOUSE_WHISPERER_PROVIDER.PUBLIC.WAREHOUSE_WHISPERER_REPO
  FOR PACKAGE WAREHOUSE_WHISPERER;
```

Fresh deployments normally produce `VERSION$1`. If your repository already contains versions, update the `version` field in both Native App manifests to the newly published version before continuing.

### 3. Install the recommended app-managed variant

```bash
snow app run --connection <connection> --role ACCOUNTADMIN \
  --project ./na-warehouse-in-app
```

Grant the two manual data/AI permissions after installation:

```sql
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE
  TO APPLICATION WAREHOUSE_WHISPERER_NA_MANAGED;

GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER
  TO APPLICATION WAREHOUSE_WHISPERER_NA_MANAGED;
```

The app creates `WAREHOUSE_WHISPERER_APP_WH` as an X-Small warehouse with 60-second auto-suspend and configures its serverless Application Service automatically.

### 4. Optionally install the reference variant

```bash
snow app run --connection <connection> --role ACCOUNTADMIN \
  --project ./na-warehouse-reference
```

Grant shared-database and Cortex access, then bind an existing warehouse:

```sql
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE
  TO APPLICATION WAREHOUSE_WHISPERER_NA_REFERENCE;

GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER
  TO APPLICATION WAREHOUSE_WHISPERER_NA_REFERENCE;

GRANT USAGE ON WAREHOUSE <consumer_warehouse>
  TO APPLICATION WAREHOUSE_WHISPERER_NA_REFERENCE;

CALL WAREHOUSE_WHISPERER_NA_REFERENCE.APP_CALLBACKS.REGISTER_SINGLE_REFERENCE(
  'QUERY_WAREHOUSE',
  'ADD',
  SYSTEM$REFERENCE('WAREHOUSE', '<consumer_warehouse>', 'PERSISTENT', 'USAGE')
);
```

## Verify

```sql
SHOW APPLICATION SERVICES IN APPLICATION WAREHOUSE_WHISPERER_NA_MANAGED;
SHOW APPLICATION SERVICES IN APPLICATION WAREHOUSE_WHISPERER_NA_REFERENCE;
```

For each installed variant, verify:

- `status` is `RUNNING`;
- `compute_resource` is `SERVERLESS`;
- `source` names the expected SAR version;
- `query_warehouse` is populated;
- a representative chat request succeeds.

Service status alone is not a functional test. If a request fails, inspect live Application Service logs after reproducing it.

## Architecture Notes

The analysis endpoint uses owner rights because `SNOWFLAKE` is a shared database and caller grants cannot be assigned directly to `SNOWFLAKE.ACCOUNT_USAGE` views. Native App consumers explicitly grant imported privileges and the `SNOWFLAKE.CORTEX_USER` database role to each installed application.

The managed variant is recommended because it is self-contained. Use the reference variant only when the consumer must reuse an existing warehouse or directly control warehouse-level governance.

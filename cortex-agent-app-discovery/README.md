# Cortex Agent: App Discovery

A [Cortex Agent](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agent) that helps consumers discover Native Apps available in the Snowflake Marketplace or already installed in their account. Users describe what they need in natural language, and the agent searches, ranks, and recommends matching apps.

## How It Works

The sample consists of two components:

1. **`SEARCH_NATIVE_APPS` stored procedure** -- Enumerates all available marketplace listings (`SHOW AVAILABLE LISTINGS`), enriches each with detailed metadata (`DESC AVAILABLE LISTING`), cross-references installed apps (`SHOW APPLICATIONS`), and returns a filtered JSON array with install status.

2. **`APP_DISCOVERY_AGENT` Cortex Agent** -- Wraps the stored procedure as a tool. The agent accepts natural-language queries, calls the procedure, and returns ranked recommendations with install status for each app.

## Prerequisites

- A Snowflake account with access to [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agent)
- Access to the Snowflake Marketplace (to list available apps)
- `ACCOUNTADMIN` role or sufficient privileges to create databases, warehouses, procedures, and agents
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/index) installed (optional, for running SQL files)

## Setup

Run the setup script to create all required objects:

```bash
snow sql -f setup.sql
```

This creates:
- Database `SAMPLE_AGENT_DB` with schema `SAMPLE_AGENT_SCH`
- Warehouse `SAMPLE_AGENT_WH` (X-Small, auto-suspend 60s)
- Stored procedure `SEARCH_NATIVE_APPS`
- Cortex Agent `APP_DISCOVERY_AGENT`

## Usage

### Test the stored procedure directly

```sql
-- Search for apps matching a keyword
CALL SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS('data enrichment');

-- Return all available apps
CALL SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS('');

-- Debug mode: inspect listing counts and enrichment details
CALL SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS('data enrichment', TRUE);
```

### Query the agent

```sql
SELECT TRY_PARSE_JSON(
  SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
    'SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.APP_DISCOVERY_AGENT',
    $$
    {
      "messages": [
        {
          "role": "user",
          "content": [{ "type": "text", "text": "Are there any apps for data enrichment or identity resolution?" }]
        }
      ]
    }
    $$
  )
) AS resp;
```

You can also run all test queries at once:

```bash
snow sql -f test.sql
```

## Cleanup

To remove all objects created by this sample:

```bash
snow sql -f cleanup.sql
```

## Notes

- The stored procedure runs as `EXECUTE AS CALLER`, so it inherits the caller's privileges for marketplace access and listing visibility.
- The enrichment loop iterates over all available listings to fetch detailed metadata. In accounts with many listings, this may take some time on the first call.
- The procedure performs case-insensitive keyword matching (`ILIKE`) across title, description, business needs, categories, and subtitle fields.
- Unlike other samples in this repository, this is not a Native App Framework package -- it is a standalone Cortex Agent deployed directly to your account.

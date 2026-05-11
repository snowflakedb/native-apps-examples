-- ============================================================
-- Test queries for the App Discovery Agent
--
-- Run after setup.sql to verify everything works.
-- ============================================================

USE DATABASE SAMPLE_AGENT_DB;
USE SCHEMA SAMPLE_AGENT_SCH;
USE WAREHOUSE SAMPLE_AGENT_WH;

-- ============================================================
-- 1. Verify the agent was created
-- ============================================================

DESCRIBE AGENT SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.APP_DISCOVERY_AGENT;

-- ============================================================
-- 2. Test the stored procedure directly
-- ============================================================

-- Search for a specific keyword
CALL SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS('data enrichment');

-- Return all available apps (empty query)
CALL SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS('');

-- Run in debug mode to inspect internals
CALL SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS('data enrichment', TRUE);

-- ============================================================
-- 3. Test the Cortex Agent end-to-end
-- ============================================================

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

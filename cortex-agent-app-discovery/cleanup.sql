-- ============================================================
-- Cleanup: Remove all objects created by setup.sql
--
-- Run with: snow sql -f cleanup.sql
-- ============================================================

DROP AGENT IF EXISTS SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.APP_DISCOVERY_AGENT;
DROP PROCEDURE IF EXISTS SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS(VARCHAR, BOOLEAN);
DROP DATABASE IF EXISTS SAMPLE_AGENT_DB;
DROP WAREHOUSE IF EXISTS SAMPLE_AGENT_WH;

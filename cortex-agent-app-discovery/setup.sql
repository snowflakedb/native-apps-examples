-- ============================================================
-- Cortex Agent: App Discovery
--
-- This script creates a Cortex Agent that helps consumers
-- discover Native Apps available in the Snowflake Marketplace
-- or already installed in their account.
--
-- Run with: snow sql -f setup.sql
-- ============================================================

-- ============================================================
-- 1. Setup: Create database, schema, and warehouse
-- ============================================================

CREATE DATABASE IF NOT EXISTS SAMPLE_AGENT_DB;
CREATE SCHEMA IF NOT EXISTS SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH;
CREATE WAREHOUSE IF NOT EXISTS SAMPLE_AGENT_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

USE DATABASE SAMPLE_AGENT_DB;
USE SCHEMA SAMPLE_AGENT_SCH;
USE WAREHOUSE SAMPLE_AGENT_WH;

-- ============================================================
-- 2. Create the stored procedure: SEARCH_NATIVE_APPS
--
-- This procedure:
--   a) Runs SHOW AVAILABLE LISTINGS, filters to app listings
--   b) For each app listing, calls DESC AVAILABLE LISTING
--      to get title, description, business_needs, categories
--   c) Runs SHOW APPLICATIONS to find installed apps
--   d) Returns a JSON array of matching apps with install status
-- ============================================================

CREATE OR REPLACE PROCEDURE SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS(
  USER_QUERY VARCHAR,
  DEBUG_MODE BOOLEAN DEFAULT FALSE
)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
  result_json VARCHAR DEFAULT '[]';
  available_app_count INTEGER DEFAULT 0;
  installed_app_count INTEGER DEFAULT 0;
  detail_row_count INTEGER DEFAULT 0;
  current_gn VARCHAR;
  rows_inserted INTEGER DEFAULT 0;
  debug_log ARRAY DEFAULT ARRAY_CONSTRUCT();
BEGIN

  -- Step 1: Get all available app listings
  SHOW AVAILABLE LISTINGS;

  CREATE OR REPLACE TEMPORARY TABLE SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_available_apps AS
  SELECT "global_name" AS global_name, "title" AS title
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
  WHERE "is_application" = 'true';

  SELECT COUNT(*) INTO :available_app_count
  FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_available_apps;

  -- Step 2: Get installed apps
  SHOW APPLICATIONS;

  CREATE OR REPLACE TEMPORARY TABLE SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_installed_apps AS
  SELECT "name" AS app_name, "source_type" AS source_type,
         "source" AS source, "comment" AS comment,
         "version" AS version, "label" AS version_label
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

  SELECT COUNT(*) INTO :installed_app_count
  FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_installed_apps;

  -- Step 3: Detail enrichment loop
  CREATE OR REPLACE TEMPORARY TABLE SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details (
    global_name VARCHAR, title VARCHAR, subtitle VARCHAR,
    description VARCHAR, business_needs VARCHAR,
    usage_examples VARCHAR, categories VARCHAR, is_imported VARCHAR
  );

  LET listing_cursor CURSOR FOR
    SELECT global_name FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_available_apps;

  FOR rec IN listing_cursor DO
    LET gn VARCHAR := rec.global_name;
    LET rows_before INTEGER DEFAULT 0;
    LET rows_after INTEGER DEFAULT 0;

    SELECT COUNT(*) INTO :rows_before
    FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details;

    EXECUTE IMMEDIATE 'DESC AVAILABLE LISTING ' || :gn;

    INSERT INTO SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details
    SELECT "global_name", "title", "subtitle", "description",
           "business_needs", "usage_examples", "categories", "is_imported"
    FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

    SELECT COUNT(*) INTO :rows_after
    FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details;

    LET rows_inserted INTEGER := :rows_after - :rows_before;

    -- Append per-listing debug entry
    debug_log := ARRAY_APPEND(:debug_log,
      OBJECT_CONSTRUCT('global_name', :gn, 'rows_inserted', :rows_inserted)
    );

  END FOR;

  SELECT COUNT(*) INTO :detail_row_count
  FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details;

  -- Return debug info early if debug mode
  IF (DEBUG_MODE) THEN
    RETURN OBJECT_CONSTRUCT(
      'available_app_count', :available_app_count,
      'installed_app_count', :installed_app_count,
      'detail_row_count', :detail_row_count,
      'per_listing', :debug_log,
      'sample_details', (
        SELECT ARRAY_AGG(OBJECT_CONSTRUCT('global_name', global_name, 'title', title))
        FROM (SELECT global_name, title FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details LIMIT 5)
      )
    );
  END IF;

  -- Step 4: Final result (filtered by USER_QUERY)
  SELECT ARRAY_AGG(
    OBJECT_CONSTRUCT(
      'global_name', d.global_name, 'title', d.title, 'subtitle', d.subtitle,
      'description', d.description, 'business_needs', d.business_needs,
      'usage_examples', d.usage_examples, 'categories', d.categories,
      'install_status', CASE WHEN d.is_imported = 'true' THEN 'installed' ELSE 'available_to_install' END,
      'installed_app_name', i.app_name, 'installed_version', i.version_label
    )
  )::VARCHAR INTO :result_json
  FROM SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details d
  LEFT JOIN SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_installed_apps i
    ON i.source_type = 'LISTING' AND i.source = d.global_name
  WHERE :USER_QUERY IS NULL
     OR :USER_QUERY = ''
     OR d.title ILIKE '%' || :USER_QUERY || '%'
     OR d.description ILIKE '%' || :USER_QUERY || '%'
     OR d.business_needs ILIKE '%' || :USER_QUERY || '%'
     OR d.categories ILIKE '%' || :USER_QUERY || '%'
     OR d.subtitle ILIKE '%' || :USER_QUERY || '%';

  DROP TABLE IF EXISTS SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_available_apps;
  DROP TABLE IF EXISTS SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_installed_apps;
  DROP TABLE IF EXISTS SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH._tmp_app_details;

  RETURN :result_json::VARIANT;
END;
$$;

-- ============================================================
-- 3. Create the Cortex Agent
-- ============================================================

CREATE OR REPLACE AGENT SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.APP_DISCOVERY_AGENT
  COMMENT = 'Helps consumers discover Native Apps installed in their account or available on the marketplace'
  FROM SPECIFICATION
  $$
  models:
    orchestration: auto

  instructions:
    system: |
      You are a Native App Discovery Assistant for Snowflake.
      Your job is to help users find Native Apps that match their needs.
      You can search both apps already installed in the user's account
      and apps available to install from the Snowflake Marketplace.

      When the user describes what they are looking for, use the
      search_native_apps tool to retrieve all available app listings.
      Then analyze the results and recommend the most relevant apps
      based on the user's description.

      For each recommended app, tell the user:
      - The app title and a summary of what it does
      - Whether it is already installed or available to install
      - If installed, the app name and version
      - Why it matches their requirements

      If no apps match, say so clearly and suggest the user refine
      their search or check the Snowflake Marketplace directly.

    response: |
      Be concise and helpful. Present results in a clear list format.
      Highlight the install status prominently for each app.
      If there are many results, rank them by relevance to the user's
      query and show the top matches first.

    orchestration: |
      Always call the search_native_apps tool first to get the full
      catalog of available app listings. Then use the returned metadata
      (title, description, business_needs, categories) to rank and
      filter results based on the user's query. Do not make up app
      names or descriptions.

    sample_questions:
      - question: "Are there any apps for data enrichment?"
        answer: "Let me search for apps related to data enrichment in your account and the marketplace."
      - question: "I need an app that provides weather data APIs"
        answer: "I'll look for weather data apps available to you."
      - question: "What apps do I already have installed?"
        answer: "Let me check all the apps currently installed in your account."

  tools:
    - tool_spec:
        type: "generic"
        name: "search_native_apps"
        description: >
          Searches all Native App listings available to the user's account,
          including both installed apps and apps available to install from
          the Snowflake Marketplace. Returns app metadata including title,
          description, business needs, categories, and install status.
          Always call this tool to answer user questions about app discovery.
        input_schema:
          type: "object"
          properties:
            user_query:
              type: "string"
              description: >
                The user's description of what kind of app or API they
                are looking for. Pass the user's query as-is.
          required:
            - user_query

  tool_resources:
    search_native_apps:
      type: "procedure"
      identifier: "SAMPLE_AGENT_DB.SAMPLE_AGENT_SCH.SEARCH_NATIVE_APPS"
      execution_environment:
        type: "warehouse"
        warehouse: "SAMPLE_AGENT_WH"
  $$;

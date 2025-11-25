# MCP Server Native App

A Snowflake SPCS Native App that exposes an echo service via MCP SERVER REST API.

## Features

- **SPCS Backend Service** - Flask-based container running in Snowflake
- **Service Function** - SQL function `v1.echo(VARCHAR)` that calls the backend
- **MCP SERVER** - Exposes the echo tool via standard MCP REST API

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/health` | GET | Health check |
| `/echo` | GET/POST | Echo endpoint (supports service function format) |

## Usage

### SQL - Service Function

```sql
-- Direct function call
SELECT mcp_server_app_v1_instance.v1.echo('Hello World');
-- Returns: "Echo: Hello World"
```

### MCP REST API

#### List Tools
```bash
curl -X POST "https://<account>.snowflakecomputing.com/api/v2/databases/mcp_server_app_v1_instance/schemas/v1/mcp-servers/echo_mcp_server" \
  -H "Authorization: Bearer <PAT_TOKEN>" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

#### Call Tool
```bash
curl -X POST "https://<account>.snowflakecomputing.com/api/v2/databases/mcp_server_app_v1_instance/schemas/v1/mcp-servers/echo_mcp_server" \
  -H "Authorization: Bearer <PAT_TOKEN>" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"echo","arguments":{"input":"Hello!"}}}'
```

### HTTP - Direct Access

```bash
# After authentication via Snowflake
curl "https://<app-url>/echo?message=hello"

curl -X POST "https://<app-url>/echo" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello world"}'
```

## Debug Procedures

```sql
-- Get service status
SELECT SYSTEM$GET_SERVICE_STATUS('mcp_server_app_v1_instance.app_public.backend');

-- Get service logs
CALL mcp_server_app_v1_instance.app_public.get_service_logs('app_public.backend', 0, 'echo-backend', 100);

-- Get app URL
CALL mcp_server_app_v1_instance.v1.app_url();

-- Describe MCP SERVER
DESC MCP SERVER mcp_server_app_v1_instance.v1.echo_mcp_server;

-- Stop the app
CALL mcp_server_app_v1_instance.app_public.stop_app();
```

## MCP Server Details

- **Server Name**: `v1.echo_mcp_server`
- **Tool Name**: `echo`
- **Tool Input**: `{"input": "string"}`

## Granting Access for MCP REST API

If using PAT tokens to access the MCP REST API:

```sql
USE ROLE nac;
GRANT APPLICATION ROLE mcp_server_app_v1_instance.app_admin TO ROLE PUBLIC;
GRANT USAGE ON WAREHOUSE wh_nac TO ROLE PUBLIC;
```

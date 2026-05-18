# MCP Server Native App

A Snowflake SPCS Native App that exposes an echo service via SQL function and MCP REST API.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/health` | GET | Health check |
| `/echo` | GET/POST | Echo back input |

## Usage

### SQL Function

```sql
SELECT mcp_server_app_v1_instance.v1.echo('Hello World');
-- Returns: "Echo: Hello World"
```

### MCP REST API

```bash
curl -X POST "https://<account>.snowflakecomputing.com/api/v2/databases/mcp_server_app_v1_instance/schemas/v1/mcp-servers/echo_mcp_server" \
  -H "Authorization: Bearer <PAT_TOKEN>" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"echo","arguments":{"input":"Hello!"}}}'
```

## Debug Commands

```sql
-- Service status
SELECT SYSTEM$GET_SERVICE_STATUS('mcp_server_app_v1_instance.app_public.backend');

-- Service logs
CALL mcp_server_app_v1_instance.app_public.get_service_logs('app_public.backend', 0, 'mcp-backend', 100);

-- Get app URL
CALL mcp_server_app_v1_instance.v1.app_url();

-- Stop app
CALL mcp_server_app_v1_instance.app_public.stop_app();
```

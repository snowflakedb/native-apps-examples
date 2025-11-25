#!/bin/bash
set -e

echo "=== Deploying application ==="
snow app run

echo ""
echo "=== Deployment complete! ==="
echo ""
echo "Next steps:"
echo "1. Open the app in Snowsight (URL printed above)"
echo "2. Click 'Grant' to grant account privileges"
echo "3. Click 'Activate' to create compute pools and start services"
echo "4. Click 'Launch App' to access the MCP server endpoint"
echo ""
echo "To get the app URL programmatically after activation:"
echo "  snow sql -q \"CALL mcp_server_app_v1_instance.v1.app_url()\""
echo ""
echo "To test the MCP REST API, grant access first:"
echo "  snow sql -q \"GRANT APPLICATION ROLE mcp_server_app_v1_instance.app_admin TO ROLE PUBLIC\""
echo "  snow sql -q \"GRANT USAGE ON WAREHOUSE wh_nac TO ROLE PUBLIC\""

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
echo "4. Click 'Launch App' to access the Cortex API endpoint"
echo ""
echo "To get the app URL programmatically after activation:"
echo "  snow sql -q \"CALL cortex_api_rest_call_app_instance.v1.app_url()\""
echo ""
echo "To test the Cortex API:"
echo "  snow sql -q \"SELECT cortex_api_rest_call_app_instance.v1.cortex_complete('What is Snowflake?')\""


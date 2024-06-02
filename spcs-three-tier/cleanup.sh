set -e
snow sql -q "CALL spcs_app_instance.app_public.stop_app();"
snow sql -q "DROP COMPUTE POOL IF EXISTS frontend_compute_pool;"
snow sql -q "DROP COMPUTE POOL IF EXISTS backend_compute_pool;"
snow app teardown

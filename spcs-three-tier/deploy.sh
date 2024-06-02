set -e
snow app run
snow sql -f "register_callback.sql"

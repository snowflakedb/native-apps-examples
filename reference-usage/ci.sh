set -e
snow sql -f 'prepare/provider.sql'
snow app run
snow app teardown
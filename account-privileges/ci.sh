set -e
snow sql -f 'prepare/references.sql'
snow app run
snow app teardown
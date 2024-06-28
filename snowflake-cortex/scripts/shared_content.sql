-- Grant usage to a external database from the application.
create schema if not exists {{ package_name }}.PACKAGE_SHARED;
use schema {{ package_name }}.PACKAGE_SHARED;

grant reference_usage on database SONGS_CORTEX_DB
    to share in application package {{ package_name }};

-- Create a view that references the provider table.
-- The view is going to be shared by the package to the application.
create view if not exists PACKAGE_SHARED.PROVIDER_SONGS_VIEW
  as select * from SONGS_CORTEX_DB.SONGS_CORTEX_SCHEMA.SONGS_PROVIDER_DATA;

grant usage on schema PACKAGE_SHARED
  to share in application package {{ package_name }};
grant select on view PACKAGE_SHARED.PROVIDER_SONGS_VIEW
  to share in application package {{ package_name }};
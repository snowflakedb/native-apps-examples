-- Grant usage to a external database from the application.
grant reference_usage on database SPOTIFY_CORTEX_DB
    to share in application package {{ package_name }};

create schema if not exists {{ package_name }}.PACKAGE_SHARED;
use schema {{ package_name }}.PACKAGE_SHARED;

-- Create a view that references the provider table.
-- The view is going to be shared by the package to the application.
create view if not exists PACKAGE_SHARED.PROVIDER_SPOTIFY_VIEW
  as select * from SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA.SPOTIFY_PROVIDER_DATA;

grant usage on schema PACKAGE_SHARED
  to share in application package {{ package_name }};
grant select on view PACKAGE_SHARED.PROVIDER_SPOTIFY_VIEW
  to share in application package {{ package_name }};
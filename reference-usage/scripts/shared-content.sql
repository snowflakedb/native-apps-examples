-- Grant usage to a external database from the application.
grant reference_usage on database reference_usage_app_sample
    to share in application package {{ package_name }};

create schema if not exists {{ package_name }}.package_shared;
use schema {{ package_name }}.package_shared;

-- Create a view that references the provider table.
-- The view is going to be shared by the package to the application.
create view if not exists package_shared.view_shared
  as select * from reference_usage_app_sample.provider_schema.provider_table;

grant usage on schema package_shared
  to share in application package {{ package_name }};
grant select on view package_shared.view_shared
  to share in application package {{ package_name }};
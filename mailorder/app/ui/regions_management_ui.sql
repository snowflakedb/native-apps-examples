create or replace streamlit ui.manage_regions
  from 'python/ui' main_file='regions_management_ui.py';

grant usage on streamlit ui.manage_regions to application role app_admin;

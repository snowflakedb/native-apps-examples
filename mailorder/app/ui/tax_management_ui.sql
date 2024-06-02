create or replace streamlit ui.manage_taxes
  from 'python/ui' main_file='tax_management_ui.py';

grant usage on streamlit ui.manage_taxes to application role app_admin;

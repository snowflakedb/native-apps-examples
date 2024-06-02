create or replace streamlit ui.manage_customers
  from 'python/ui' main_file='customers_management_ui.py';

grant usage on streamlit ui.manage_customers to application role app_admin;

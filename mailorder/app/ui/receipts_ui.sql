create or replace streamlit ui.receipts_ui
  from 'python/ui' main_file='receipts_ui.py';

grant usage on streamlit ui.receipts_ui to application role app_csr;
grant usage on streamlit ui.receipts_ui to application role app_admin;

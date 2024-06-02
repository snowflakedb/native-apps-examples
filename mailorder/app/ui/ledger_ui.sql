create or replace streamlit ui.ledger_ui
  from 'python/ui' main_file='ledger_ui.py';

grant usage on streamlit ui.ledger_ui to application role app_admin;

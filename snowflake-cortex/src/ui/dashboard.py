import streamlit as st
from snowflake.snowpark import Session
from cortexCaller import CortexCaller
import snowflake.permissions as permission

class Dashboard:
   
   def __init__(self, session: Session, cortex_caller: CortexCaller = CortexCaller()) -> None:
      self.session = session
      self.cortex_caller = cortex_caller

   def setup(self):
      st.header("Privileges setup")
      st.caption("""
         Follow the instructions below to set up your application.
         Once you have completed the steps, you will be able to continue to the main example.
      """)
      privilege = 'IMPORTED PRIVILEGES ON SNOWFLAKE DB'
      if not permission.get_held_account_privileges([privilege]):
         st.button(f"Grant import privileges on snowflake DB ↗", on_click=permission.request_account_privileges, args=[[privilege]], key='IMPORTED PRIVILEGES ON SNOWFLAKE DB')
      else:
         st.session_state.privileges_granted = True
         st.rerun()

   def run_streamlit(self):
      if not permission.get_held_account_privileges(['IMPORTED PRIVILEGES ON SNOWFLAKE DB']):
         del st.session_state.privileges_granted
         st.rerun()
      
      st.header('Snowflake Cortex Example')
      st.subheader("Simple app showing how cortex can answer questions using the following song's ranking table")
      table_df = self.session.table("PACKAGE_SHARED.PROVIDER_SONGS_VIEW").to_pandas()
      st.write(table_df)

      cortex_chat = st.container(height=200)
      cortex_input = st.chat_input("What do you want to ask to cortex about the table from above?", key="cortex_input")
      if cortex_input and not cortex_input.isspace():
         cortex_chat.chat_message("user").write(cortex_input)
         cortex_fn = self.cortex_caller.call_cortex(table_df, cortex_input)
         cortex_chat.chat_message("assistant").write(cortex_fn)


if __name__ == '__main__':
   if 'privileges_granted' not in st.session_state:
      Dashboard(Session.builder.getOrCreate()).setup()
   else:
      Dashboard(Session.builder.getOrCreate()).run_streamlit()

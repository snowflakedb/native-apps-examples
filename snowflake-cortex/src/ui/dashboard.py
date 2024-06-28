import streamlit as st
from snowflake.snowpark import Session
from cortexCaller import CortexCaller

class Dashboard:
   
   def __init__(self, session: Session, cortex_caller: CortexCaller = CortexCaller()) -> None:
      self.session = session
      self.cortex_caller = cortex_caller
      
   def run_streamlit(self):
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
   Dashboard(Session.builder.getOrCreate()).run_streamlit()

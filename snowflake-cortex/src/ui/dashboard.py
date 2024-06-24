import streamlit as st
from snowflake.snowpark import Session
from cortexCaller import CortexCaller

class Dashboard:
   
   def __init__(self, session: Session = None) -> None:
      self.session = session if session else Session.builder.getOrCreate()
      
   def run_streamlit(self):
      import streamlit as st

      st.header('Snowflake Cortex Example')
      st.subheader("Simple app showing how cortex can answer questions using the following spotify's ranking table")

      table_df = self.session.table("PACKAGE_SHARED.PROVIDER_SPOTIFY_VIEW")
      st.write(table_df)

      cortex_chat = st.container(height=200)
      cortex_input = st.chat_input("What do you want to ask to cortex about the table from above?", key="cortex_input")
      if cortex_input and not cortex_input.isspace():
         cortex_chat.chat_message("user").write(cortex_input)
         cortex_fn = CortexCaller.call_cortex(self.session, table_df, cortex_input)
         cortex_chat.chat_message("assistant").write(cortex_fn)

if __name__ == '__main__':
   Dashboard().run_streamlit()

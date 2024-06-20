import snowflake.snowpark.functions as F
import pandas as pd
from snowflake.cortex import Complete

def run_streamlit():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   import streamlit as st
   from snowflake.snowpark import Session

   def call_cortex(session, df, input: str):
      sample_df = df.to_pandas().to_string()
      input_with_table = f"""The following data is a table that contains songs information it is wrapped in this tags <dataset>{sample_df}</dataset> {input}"""
      response = Complete('llama2-70b-chat', input_with_table)
      return response

   st.header('Snowflake Cortex Example')

   # Get the current credentials
   session = Session.builder.getOrCreate()

   table_df = session.table("PACKAGE_SHARED.PROVIDER_SPOTIFY_VIEW")
   st.subheader("Simple app showing how cortex can answer questions using the following spotify's ranking table")
   st.write(table_df)
   cortex_chat = st.container(height=300)
   cortex_input = st.chat_input("What do you want to ask to cortex about the table from above?")
   if cortex_input and not cortex_input.isspace():
      cortex_chat.chat_message("user").write(cortex_input)
      cortex_fn = call_cortex(session, table_df, cortex_input)
      cortex_chat.chat_message("assistant").write(cortex_fn)

if __name__ == '__main__':
   run_streamlit()

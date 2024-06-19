import snowflake.snowpark.functions as F
import pandas as pd

def call_cortex(session, df, input: str):
   sample_df = df.to_pandas().to_string()
   input_with_table = f"""The following data is a table that contains songs information it is wrapped in this tags <dataset>{sample_df}</dataset> {input}"""
   new_df = session.create_dataframe([[1]],schema=["A"])
   new_df = new_df.with_column("CORTEX", F.call_builtin("SNOWFLAKE.CORTEX.COMPLETE", F.lit('llama2-70b-chat'), F.lit(input_with_table)))
   return new_df.select(F.col("CORTEX"))

def run_streamlit():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   import streamlit as st
   from snowflake.snowpark import Session

   st.header('Snowflake Cortex Example')

   # Get the current credentials
   session = Session.builder.getOrCreate()

   table_df = session.table("core.shared_view")
   st.write(table_df)
   cortex_input = st.text_input("What do you want to ask to cortex about the table from above?")
   if cortex_input is not "":
      cortex_fn = call_cortex(session, table_df, cortex_input)
      st.write(cortex_fn)

if __name__ == '__main__':
   run_streamlit()

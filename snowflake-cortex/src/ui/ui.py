import snowflake.snowpark.functions as F

def call_cortex(df, input: str):
   sample_df = df.to_pandas().to_string()
   input_with_table = f"""The following data is a table that contains songs information it is wrapped in this tags <dataset>{sample_df}</dataset> {input}"""
   new_df = df.with_column("CORTEX", F.call_builtin("SNOWFLAKE.CORTEX.COMPLETE", F.lit('llama2-70b-chat'), F.lit(input_with_table))).collect()
   return new_df

def run_streamlit():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   import pandas as pd
   import streamlit as st
   from snowflake.snowpark import Session

   st.header('Snowflake Cortex Example')

   # Get the current credentials
   session = Session.builder.getOrCreate()

   df1 = session.create_dataframe([[1, 2, 3, 4, 5]], schema=["number1","number2","number3","number4","number5"])
   df1.write.save_as_table("my_table", mode="overwrite")
   table_df = session.table("my_table")
   st.write(table_df)
   cortex_input = st.text_input("What do you want to ask to cortex about the table from above?")
   if cortex_input is not "":
      cortex_fn = call_cortex(table_df, cortex_input)
      st.write(cortex_fn)

if __name__ == '__main__':
   run_streamlit()

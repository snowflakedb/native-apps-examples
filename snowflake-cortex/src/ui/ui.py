def run_streamlit():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   import pandas as pd
   import streamlit as st
   from snowflake.snowpark.functions import call_udf, col, call_builtin, lit
   from snowflake.snowpark import Session
   from snowflake.cortex import Complete, Summarize

   st.title('Hello Snowflake!')


   st.header('Snowflake Cortex Example')

   # Get the current credentials
   session = Session.builder.getOrCreate()

   spotify_df = session.table('core.shared_view')
   st.write("intento")
   st.dataframe(spotify_df)

   cortex_fn = spotify_df.with_column("CORTEX",call_builtin("SNOWFLAKE.CORTEX.COMPLETE", lit('llama2-70b-chat'), lit("What are large language models?")))
   st.write(cortex_fn)


if __name__ == '__main__':
   run_streamlit()

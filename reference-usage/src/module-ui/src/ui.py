def run_streamlit():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   # Streamlit app testing documentation: https://docs.streamlit.io/library/api-reference/app-testing
   import pandas as pd
   import streamlit as st
   from snowflake.snowpark import Session

   st.title('Hello Snowflake!')

   st.header('Shared Data Example')

   st.write(
      """The following data frame shows all the values from a table shared by the provider.
      """)

   # Get the current credentials
   session = Session.builder.getOrCreate()

   #  Create an example data frame
   data_frame = session.table('core.shared_view').to_pandas()

   # Display the Pandas data frame as a Streamlit data frame.
   st.dataframe(data_frame, use_container_width=True)

if __name__ == '__main__':
   run_streamlit()

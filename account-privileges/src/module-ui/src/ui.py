import json
import random
import pandas as pd
import streamlit as st
import snowflake.permissions as permission
from snowflake.snowpark.functions import call_udf, col, lit
from snowflake.snowpark import Session

session = Session.builder.getOrCreate()

def setup():
   st.header("First-time setup")
   st.caption("""
        Follow the instructions below to set up your application.
        Once you have completed the steps, you will be able to continue to the main example.
    """)

   refs = get_references()
   for row in refs:
      name = row['name']
      binding = row["bindings"][0]["alias"] if row["bindings"] else None
      label = row["label"]
      
      if not binding:
         st.button(f"Select {label} ↗", on_click=permission.request_reference, args=[name], key=name)
      else:
          st.caption(f"*{label}* binding exists ✅")     

      if not binding: return

   st.session_state.privileges_granted = True
   st.experimental_rerun()

def get_references():
   app_name = session.get_current_database()
   data_frame = session.create_dataframe([''])
   refs = data_frame.select(call_udf('system$get_reference_definitions', lit(app_name))).collect()[0][0]
   return json.loads(refs)


def run_streamlit():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   # Streamlit app testing documentation: https://docs.streamlit.io/library/api-reference/app-testing

   st.title('Hello Snowflake!')


   st.header('UDF Example')

   st.write(
      """
      Calls the core.app_function created by the core.create_function_binding procedure, that performs the sum of two random numbers.
      The udf binds the function granted with privileges in the setup.
      """)

   # Get the current credentials
   if st.button("Call Udf reference", type="primary"):
      num1 = random.randint(1, 9)
      num2 = random.randint(1, 9)
      data_frame = session.sql(f"select reference('function_reference')({num1}, {num2})")
      
      # Execute the query and convert it into a Pandas data frame
      queried_data = data_frame.to_pandas()

      # Display the Pandas data frame as a Streamlit data frame.
      st.dataframe(queried_data, use_container_width=True)


   st.header('Stored Procedure Example')

   st.write(
      """
      Calls the core.app_procedure stored procedure, that performs the sum of two random numbers.
      The procedure binds the stored procedure granted with privileges in the setup.
      """)

   if st.button("Call Procedure reference", type="primary"):
      num1 = random.randint(1, 9)
      num2 = random.randint(1, 9)
   
      result = session.call('core.app_procedure', num1, num2)
      st.dataframe(pd.DataFrame([[result]], columns=['RESULT']), use_container_width=True)

   
   st.header('Table and View Example')
   st.write(
      """
      Shows the binded view values and updates table referenced by the view by adding new rows to the binded table with insert privileges.
      """)
   
   result = session.sql("select * from reference('view_reference')")
   st.dataframe(result.to_pandas(), use_container_width=True)

   if st.button("Insert rows", type="primary"):
      session.call('core.app_update_table', random.randint(1, 9))
      st.experimental_rerun()

if __name__ == '__main__':
   if 'privileges_granted' not in st.session_state:
      setup()
   else:
      run_streamlit()

# Import python packages
# Streamlit app testing framework requires imports to reside here
# Streamlit app testing documentation: https://docs.streamlit.io/library/api-reference/app-testing
import json
import time
import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session
import snowflake.permissions as permission
from snowflake.snowpark.functions import lit, call_udf, col

PRIVILEGES = ["EXECUTE TASK"]

# Get the current credentials
session = get_active_session()

def run_streamlit():
   st.title('Hello Snowflake!')

   st.header('Task Example')

   st.write(
      """Increments a number by one by executing the task increment_by_one_every_minute
         which calls the increment_by_one() Stored Procedure, both defined in your setup_script.sql script.
      """)

   result = session.table('internal.incremented_values_stream').select(col('value'), col('metadata$action').alias('action')).to_pandas()

   st.dataframe(result, use_container_width=True)

   col1, col2, col3 = st.columns(3)

   if col1.button(f"Start task", type="primary"):
      session.call('core.create_task')
      st.toast('Task started!')
   if col2.button(f"Stop task", type="primary"):
      session.call('core.stop_task')
      st.toast('Task stopped!')
   if col3.button(f"Refresh"):
      st.experimental_rerun()


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

      if not binding:
         st.button(f"Select a warehouse ↗", on_click=permission.request_reference, args=[name], key=name)
      else:
          label = row["label"]
          st.caption(f"*{label}* binding exists ✅")     
      
      if not binding: return

   st.divider()
   res = permission.get_missing_account_privileges(PRIVILEGES)

   if res and len(res) > 0:
      st.caption(f"The following privileges are needed")
      privileges = st.code(','.join(PRIVILEGES), language="markdown")
      st.button("Request Privileges", on_click=permission.request_account_privileges, args=[PRIVILEGES])
      return
   else:
      st.session_state.privileges_granted = True
      st.experimental_rerun()

def get_references():
   app_name = session.get_current_database()
   data_frame = session.create_dataframe([''])
   refs = data_frame.select(call_udf('system$get_reference_definitions', lit(app_name))).collect()[0][0]
   return json.loads(refs)

if __name__ == '__main__':
   try:
      if 'privileges_granted' not in st.session_state:
         setup()
      else:
         run_streamlit()
         
   except Exception as e:
        st.write(e)
      
   

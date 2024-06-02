def run_streamlit():
   # Import python packages
   import pandas as pd
   import streamlit as st
   from snowflake.snowpark import Session
   import json

   st.title('Object Level References Example')

   # Get the current credentials
   session = Session.builder.getOrCreate()

   #Table permissions example
   st.subheader('Table Example')
   st.write('This is an example of the execution of SELECT SQL command in a consumer table.')
   table_select = session.call('core.select_object','consumer_table').to_pandas()
   st.write(table_select)

   def call_modify_procedure_insert():
      response = session.call('core.modify_table', 'INSERT', 'consumer_table')

   def call_modify_procedure_update():
      response = session.call('core.modify_table', 'UPDATE', 'consumer_table')

   def call_modify_procedure_delete():
      response = session.call('core.modify_table', 'DELETE', 'consumer_table')

   st.write('Insert a row with the value 12345 in the table')
   st.button('INSERT', key='InsertTableButton',on_click=call_modify_procedure_insert)

   st.write('Update all the values in the table to 9999')
   st.button('UPDATE', key='UpdateTableButton',on_click=call_modify_procedure_update)

   st.write('Truncate all the values in the table')
   st.button('DELETE', key='DeleteTableButton',on_click=call_modify_procedure_delete)

   #View permissions example
   st.subheader('View example')
   st.write('This is an example of a SELECT SQL command that references a consumer view.')
   view_select = session.call('core.select_object','consumer_view').to_pandas()
   st.write(view_select)

   # External table permissions example

   ref_ext_table_response = session.sql(f"SELECT(SYSTEM$GET_ALL_REFERENCES('consumer_external_table')) as REFERENCES").collect()[0]['REFERENCES']
   response_ext_array = json.loads(ref_ext_table_response)
   if (len(response_ext_array)) > 0:
      st.subheader('External table Example')
      st.write('This is an example of executing a DESCRIBE SQL command on a consumer external table.')
      table_desc = session.call('core.describe_object', 'consumer_external_table', 'EXTERNAL TABLE').to_pandas()
      st.write(table_desc)

   def call_function(num1, num2):
      response = session.sql(f"SELECT REFERENCE('consumer_function')({num1},{num2})").to_pandas().to_numpy()
      st.write(int(response[0]))

   #Procedure permissions example
   st.subheader('Procedure Example')
   st.write('Input the number you want to add in the procedure')
   numProc1 = st.number_input(label='First number', key='numToAddProc1', step=1, format='%i')
   numProc2 = st.number_input(label='Second number', key='numToAddProc2', step=1, format='%i')
   st.write(session.call('core.use_proc','consumer_procedure',numProc1,numProc2))
   
   #Function permissions example
   st.subheader('Function Example')
   st.write('Input the number you want to add in the function')
   numFunc1 = st.number_input(label='First number', key='numToAddFunc1', step=1, format='%i')
   numFunc2 = st.number_input(label='Second number', key='numToAddFunc2', step=1, format='%i')
   func_result = call_function(numFunc1,numFunc2)

   #Warehouse permissiones example
   st.subheader('Warehouse Example')

   st.info('For the warehouse to work properly, ACCOUNTADMIN must be the owner of the warehouse, or the monitor privilege has to be granted explicitly.')
   warehouse_response = st.session_state['warehouse_response'] if 'warehouse_response' in st.session_state else pd.DataFrame()

   def call_describe_wh():
      st.session_state['warehouse_response'] = session.call('core.describe_wh', 'consumer_warehouse')

   st.button('DESCRIBE WAREHOUSE', key='DescribeWarehouseButton',on_click=call_describe_wh)
   st.dataframe(warehouse_response)

   # API integration permissions example

   ref_api_response = session.sql(f"SELECT SYSTEM$GET_ALL_REFERENCES('consumer_api') as REFERENCES").collect()[0]['REFERENCES']
   response_api_array = json.loads(ref_api_response)
   
   if(len(response_api_array))>0:
      st.subheader('API Integration Example')
      
      translate_word = st.text_input(label='Type a word to translate', key='translateWord')
      if translate_word and not translate_word.isspace():
         st.session_state['api_response'] =  session.call('core.call_api',translate_word) 
      else:
         if 'api_response' in st.session_state:
            del st.session_state['api_response']

      if 'api_response' in st.session_state:
         st.write(st.session_state['api_response'])

   

if __name__ == '__main__':
   run_streamlit()

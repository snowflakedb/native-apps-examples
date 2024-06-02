def run_streamlit():
   # Import python packages
   # Streamlit app testing framework requires imports to reside here
   # Streamlit app testing documentation: https://docs.streamlit.io/library/api-reference/app-testing
   import pandas as pd
   import streamlit as st
   from snowflake.snowpark.context import get_active_session
   from snowflake.snowpark.functions import call_udf, col

   st.title('Hello Snowflake!')


   st.header('UDF Example')

   st.write(
      """The sum of the two numbers is calculated by the Python add_fn() function
         which is called from core.add() UDF defined in your setup_script.sql.
      """)

   # Get the current credentials
   session = get_active_session()

   num1 = st.number_input('First number', key='numToAdd1', value=1)
   num2 = st.number_input('Second number', key='numToAdd2', value=1)

   #  Create an example data frame
   data_frame = session.create_dataframe([[num1, num2]], schema=['num1', 'num2'])
   data_frame = data_frame.select(call_udf('core.add', col('num1'), col('num2')))

   # Execute the query and convert it into a Pandas data frame
   queried_data = data_frame.to_pandas()

   # Display the Pandas data frame as a Streamlit data frame.
   st.dataframe(queried_data, use_container_width=True)


   st.header('Stored Procedure Example')

   st.write(
      """Incrementing a number by one is calculated by the Python increment_by_one_fn() function
         which implements the core.increment_by_one() Stored Procedure defined in your setup_script.sql.
         If the billing event was set up properly, this procedure will execute a new charge based on
         the cost specified in the billing event.
      """)

   num_to_increment = st.number_input('Number to increment', key='numToIncrement', value=1)
   result = session.call('core.increment_by_one', num_to_increment)

   st.dataframe(pd.DataFrame([[result]]), use_container_width=True)

   if st.button('Test Billing Event'):
      event = session.call('core.billing_event')
      if event == 'Success':
         st.success('Billing Event was setup successfully!', icon="✅")
      else:
         st.error('An error ocurred trying to setup the billing event', icon="🚨")

if __name__ == '__main__':
   run_streamlit()

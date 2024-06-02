from dataclasses import dataclass
from dateutil import parser
from datetime import date, datetime
import pandas as pd
import streamlit as st
import snowflake.permissions as permission
from snowflake.snowpark.functions import call_udf, lit
from snowflake.snowpark import Session
import json

# Get the current credentials
session = Session.builder.getOrCreate()

@dataclass
class Reference:
    name: str
    label: str
    type: str
    description: str
    bound_alias: str

def setup():
   st.header("First-time setup")
   st.caption("""
        Follow the instructions below to set up your application.
        Once you have completed the steps, you will be able to continue to the main example.
    """)

   refs = get_references()
   
   for ref in refs:
      name = ref.name
      label = ref.label

      if not ref.bound_alias:
         st.button(f"{label} ↗", on_click=permission.request_reference, args=[name], key=name)
      else:
          st.caption(f"*{label}* binding exists ✅")     

      if not ref.bound_alias: return
   
   if st.button("Continue to app", type="primary"):
      result = session.call('create_eai_objects')
      if result == 'SUCCESS':
         st.session_state.privileges_granted = True
         st.experimental_rerun()
      else:
         st.error('Connection to `api.coincap.io` failed. Try again later', icon="🚨")

def get_references():
   app_name = session.get_current_database()
   data_frame = session.create_dataframe([''])
   refs = data_frame.select(call_udf('system$get_reference_definitions', lit(app_name))).collect()[0][0]
   references = []
   for row in json.loads(refs):
      bound_alias = row["bindings"][0]["alias"] if row["bindings"] else None
      references.append(Reference(row["name"], row["label"], row["object_type"], row["description"], bound_alias))
   return references

def run_streamlit():
   st.title('Hello Snowflake!')

   st.header('External Access Integration Example')
   st.write(
      """
      Shows the price timeline of the selected currency in a specified date range
      using the `api.coincap.io` API to get real-time prices.
      Coin names and prices are retrieved from the `core.get_coin_story` and `core.get_crypto_coins`
      stored procedures who use an External Access Integration.
      """)

   today = datetime.now()
   jan_1 = date(today.year, 1, 1)

   col1, col2 = st.columns(2)

   range = col1.date_input(
    "Select a date range",
    (jan_1, today),
    format="MM/DD/YYYY")
   
   if 'coins' not in st.session_state:
      st.session_state.coins = json.loads(session.call('core.get_crypto_coins'))

   coin = col2.selectbox(
   "Choose a coin",
   [coin["id"].upper() for coin in st.session_state.coins],
   placeholder="Select coin type...")
   
   start = datetime.timestamp(datetime.combine(range[0], datetime.min.time())) * 1000

   if len(range) == 1:
      return

   end = datetime.timestamp(datetime.combine(range[1], datetime.min.time())) * 1000

   coin_history = session.call('core.get_coin_story', coin.lower(), start, end)
   prices = []
   dates = []

   for history in json.loads(coin_history):
      date_time = parser.parse(history["date"])
      prices.append(float(history["priceUsd"]))
      dates.append(date_time.strftime("%m/%d/%Y"))


   data_frame = pd.DataFrame(data = {'USD Price': prices, 'Date': dates })
   data_frame = data_frame.set_index('Date')
   st.line_chart(data_frame)
   

if __name__ == '__main__':
   if 'privileges_granted' not in st.session_state:
      setup()
   else:
      run_streamlit()

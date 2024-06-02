import time

# Helper method that calls the system function for billing
def create_billing_event(session, class_name, subclass_name, start_timestamp, timestamp, base_charge, objects, additional_info):
   session.sql(f"SELECT SYSTEM$CREATE_BILLING_EVENT('{class_name}', '{subclass_name}', {start_timestamp}, {timestamp}, {base_charge}, '{objects}', '{additional_info}')").collect()
   return "Success"

# Handler function for the stored procedure
def bill(session):
   # insert code to identify monthly active rows and calculate a charge
   try:
      # Define the price to charge per call
      billing_quantity = 1.0

      # Current time in Unix timestamp (epoch) time in milliseconds
      current_time_epoch = int(time.time() * 1000)

      return create_billing_event(session, 'PROCEDURE_CALL', '', current_time_epoch, current_time_epoch, billing_quantity, '["core.increment_by_one"]', '')
   except Exception as ex:
      return "Error " + ex
from snowflake.cortex import Complete

class CortexCaller:

   def call_complete(_self,input_with_table):
      response = Complete('llama2-70b-chat', input_with_table)
      return response

   def call_cortex(_self, df, input: str):
      sample_df = df.to_string()
      input_with_table = f"""The following data is a table that contains songs information it is wrapped in this tags <dataset>{sample_df}</dataset> {input}"""
      response = _self.call_complete(input_with_table)
      return response
   
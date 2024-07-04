from snowflake.snowpark import Session
import json
import streamlit as st

class UI:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self):
        with st.form('key_value_form', clear_on_submit=True):
            col1, col2 = st.columns(2)
            key = col1.text_input('Add a key', key='Key')
            value = col2.text_input('Add a value for the key', key='Value')
            if st.form_submit_button('Add'):
                if key == '' or value == '':
                    st.error("Key-value pairs should not be empty")           
                else: 
                    self.add(key, value)

        st.dataframe(self.session.table('internal.dictionary').to_pandas(), use_container_width=True)

    def add(self, key: str, value: str):
        result = json.loads(self.session.call('core.add_key_value', key, value))
        if "SQLCODE" in result:
            error = f"Primary key violation on Hybrid Table. **{key}** already exists." if result["SQLCODE"] == 200001 else result["SQLERRM"]
            st.error(error, icon="🚨")

if __name__ == '__main__':
    ui = UI(Session.builder.getOrCreate())
    ui.run()
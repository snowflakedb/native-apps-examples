import customers_management_ui
from streamlit.testing.v1 import AppTest
from common_test_fixtures import session, session_sql, data
from snowflake.snowpark import Session
import pytest as pytest

@pytest.fixture(autouse=True)
def set_up_tables(session: Session):
    session.create_dataframe(data=[data.customer_1], schema=data.customers_schema).write.save_as_table('data.customers')

def test_customers_management_ui_streamlit(session_sql):
    at = AppTest.from_function(customers_management_ui.run_streamlit)
    at.run()
    assert not at.exception

    # check current customers dataframe
    assert (at.dataframe[0].value[:].values == [data.customer_1]).all()

    # test adding new customer
    at.text_input('customerId').set_value('id123').run()
    at.text_input('customerName').set_value('Customer Name').run()

    at.button[0].click().run()
    session_sql.assert_called_once_with('insert into data.customers(id, name, created_at) values (?, ?, current_timestamp())', params=['id123', 'Customer Name'])
    session_sql.reset_mock()

    # ensure still no exception
    assert not at.exception
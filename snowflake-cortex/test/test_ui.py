from dashboard import Dashboard
from cortexCaller import CortexCaller
from streamlit.testing.v1 import AppTest
from snowflake.snowpark import Session
from unittest.mock import patch, MagicMock
import pytest as pytest

@pytest.fixture(autouse=True)
def session():
    session = Session.builder.config('local_testing', True).create()
    yield session
    session.close()

@pytest.fixture(autouse=True)
def cortex_caller():
    cortex_caller = CortexCaller()
    yield cortex_caller

@patch('cortexCaller.CortexCaller.call_cortex')
@patch('snowflake.snowpark.session.Session.table')
def test_cortex_call_mock(table: MagicMock, call_cortex: MagicMock, session, cortex_caller):
    
    def script(session, cortex_caller):
        from dashboard import Dashboard
        dashboard = Dashboard(session, cortex_caller)
        return dashboard.run_streamlit()
    
    table.return_value=session.create_dataframe([{"TestColumn": "TestValue"}])
    call_cortex.return_value='Mocked response from cortex'
    at = AppTest.from_function(script, kwargs={ "session": session, "cortex_caller": cortex_caller }).run()
    
    at.chat_input(key='cortex_input').set_value('text for testing purposes').run()
    assert at.chat_message[0].name == 'user'
    assert at.chat_message[1].name == 'assistant'

def test_input_showed_in_chat():
    dashboard = Dashboard(session)
    at = AppTest.from_function(dashboard.run_streamlit).run()
    at.chat_input(key='cortex_input').set_value('text for testing purposes').run()
    assert at.chat_message[0].name == 'user'

def test_input_empty():
    dashboard = Dashboard(session)
    at = AppTest.from_function(dashboard.run_streamlit).run()
    at.chat_input(key='cortex_input').set_value(' ').run()
    assert not at.chat_message

    at.chat_input(key='cortex_input').set_value('').run()
    assert not at.chat_message
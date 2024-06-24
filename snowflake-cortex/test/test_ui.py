from dashboard import Dashboard
from streamlit.testing.v1 import AppTest
from snowflake.snowpark import Session
from unittest.mock import patch, MagicMock
import pytest as pytest

@pytest.fixture(autouse=True)
def session():
    session = Session.builder.config('local_testing', True).create()
    yield session
    session.close()

# @patch('cortexCaller.CortexCaller.call_cortex', autospec=True)
def test_cortex_call_mock(call_cortex: MagicMock, session):
    dashboard = Dashboard(session)
    at = AppTest.from_function(dashboard.run_streamlit).run()
    call_cortex.return_value='Mocked response from cortex'
    at.chat_input(key='cortex_input').set_value('text for testing purposes').run()
    assert at.chat_message[0].name == 'user'
    assert at.chat_message[1].name == 'assistant'
    assert call_cortex.assert_called_once()

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
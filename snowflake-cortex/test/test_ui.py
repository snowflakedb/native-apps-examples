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


@patch('snowflake.permissions.request_account_privileges')
def test_setup(request_account_privileges: MagicMock, session, cortex_caller):

    def script(session, cortex_caller):
        from dashboard import Dashboard
        dashboard = Dashboard(session, cortex_caller)
        return dashboard.setup()
        
    with patch('snowflake.permissions.request_account_privileges', return_value=True) as request_account_privileges:
        at = AppTest.from_function(script, kwargs={ "session": session, "cortex_caller": cortex_caller }).run()
        assert at.header[0].value == 'Privileges setup'
        assert at.caption[0].value == 'Follow the instructions below to set up your application.\nOnce you have completed the steps, you will be able to continue to the main example.'
        assert at.button[0].label == 'Grant import privileges on snowflake DB ↗'  
        assert 'privileges_granted' not in at.session_state
        at.button(key='IMPORTED PRIVILEGES ON SNOWFLAKE DB').click().run()
        request_account_privileges.assert_called_once_with(['IMPORTED PRIVILEGES ON SNOWFLAKE DB'])


@patch('snowflake.permissions.get_held_account_privileges')
def test_not_granted_privileges(get_held_account_privileges: MagicMock, session, cortex_caller):

    get_held_account_privileges.return_value = False

    at = AppTest.from_file("./src/ui/dashboard.py").run()
    assert at.header[0].value == 'Privileges setup'
    assert at.caption[0].value == 'Follow the instructions below to set up your application.\nOnce you have completed the steps, you will be able to continue to the main example.'
    assert at.button[0].label == 'Grant import privileges on snowflake DB ↗'

@patch('cortexCaller.CortexCaller.call_cortex')
@patch('snowflake.snowpark.session.Session.table')
@patch('snowflake.permissions.get_held_account_privileges')
def test_cortex_call_mock(get_held_account_privileges: MagicMock, table: MagicMock, call_cortex: MagicMock, session, cortex_caller):
    
    get_held_account_privileges.return_value = True

    def script(session, cortex_caller):
        from dashboard import Dashboard
        dashboard = Dashboard(session, cortex_caller)
        return dashboard.run_streamlit()
    
    table.return_value=session.create_dataframe([{"TestColumn": "TestValue"}])
    call_cortex.return_value='Mocked response from cortex'
    at = AppTest.from_function(script, kwargs={ "session": session, "cortex_caller": cortex_caller }).run()
    
    at.chat_input(key='cortex_input').set_value('text for testing purposes').run()
    call_cortex.assert_called_once()
    assert at.chat_message[1].name == 'assistant'

@patch('cortexCaller.CortexCaller.call_cortex')
@patch('snowflake.snowpark.session.Session.table')
@patch('snowflake.permissions.get_held_account_privileges')
def test_input_showed_in_chat(get_held_account_privileges: MagicMock, table: MagicMock, call_cortex: MagicMock, session, cortex_caller):

    get_held_account_privileges.return_value = True

    def script(session, cortex_caller):
        from dashboard import Dashboard
        dashboard = Dashboard(session, cortex_caller)
        return dashboard.run_streamlit()
    
    table.return_value=session.create_dataframe([{"TestColumn": "TestValue"}])
    at = AppTest.from_function(script, kwargs={ "session": session, "cortex_caller": cortex_caller }).run()
    at.chat_input(key='cortex_input').set_value('text for testing purposes').run()
    assert at.chat_message[0].name == 'user'

@patch('cortexCaller.CortexCaller.call_cortex')
@patch('snowflake.snowpark.session.Session.table')
@patch('snowflake.permissions.get_held_account_privileges')
def test_input_empty(get_held_account_privileges: MagicMock, table: MagicMock, call_cortex: MagicMock, session, cortex_caller):
    
    get_held_account_privileges.return_value = True

    def script(session, cortex_caller):
        from dashboard import Dashboard
        dashboard = Dashboard(session, cortex_caller)
        return dashboard.run_streamlit()

    table.return_value=session.create_dataframe([{"TestColumn": "TestValue"}])
    at = AppTest.from_function(script, kwargs={ "session": session, "cortex_caller": cortex_caller }).run()
    at.chat_input(key='cortex_input').set_value(' ').run()
    assert not at.chat_message

    at.chat_input(key='cortex_input').set_value('').run()
    assert not at.chat_message
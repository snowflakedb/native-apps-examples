import pytest
from unittest.mock import patch, MagicMock
from snowflake.snowpark import Session
from streamlit.testing.v1 import AppTest
from ui import UI

@pytest.fixture()
def session():
    session = Session.builder.config('local_testing', True).create()
    yield session
    session.close()

@patch('snowflake.snowpark.session.Session.table')
def test_run(table: MagicMock, session):
    # arrange
    def script(session):
        from ui import UI
        sut = UI(session)
        return sut.run()
    
    table.return_value = session.create_dataframe([{"key": "mykey", "value": "myvalue"}])
    
    # act
    at = AppTest.from_function(script, kwargs={ "session": session }).run()

    # assert
    assert len(at.dataframe[0].value.index) == 1

@patch('snowflake.snowpark.session.Session.call')
def test_add(call: MagicMock, session):
    # arrange    
    call.return_value = '{ "STATUS": "OK" }'
    sut = UI(session)

    # act
    sut.add('', '')

    # assert
    call.assert_called_once()
    
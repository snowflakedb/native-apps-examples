import regions_management_ui
from streamlit.testing.v1 import AppTest
import pytest as pytest
from common_test_fixtures import session, session_sql, data
from snowflake.snowpark import Session

@pytest.fixture(autouse=True)
def set_up_tables(session: Session):
    session.create_dataframe(data=[data.region_1], schema=data.regions_schema).write.save_as_table('data.regions')

def test_regions_management_ui_streamlit(session_sql):
    at = AppTest.from_function(regions_management_ui.run_streamlit)
    at.run()
    assert not at.exception

    # check current regions dataframe
    expected_region = data.region_1.copy()
    expected_region[2] = expected_region[2] * 100 # displaying percentages to users
    assert (at.dataframe[0].value[:].values == [expected_region]).all()

    # test adding new region
    tax_percent = 15
    at.text_input('regionId').set_value('qc').run()
    at.text_input('regionName').set_value('Quebec').run()
    at.number_input('taxPercent').set_value(tax_percent).run()

    at.button('addRegion').click().run()
    session_sql.assert_called_once_with('insert into data.regions(id, name, tax_amount_pct, created_at) values (?, ?, ?, current_timestamp())', params=['qc', 'Quebec', tax_percent/100])
    session_sql.reset_mock()

    # ensure still no exception
    assert not at.exception
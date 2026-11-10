"""Exercise both SQL boundaries with consumer-controlled column names."""

import importlib.util
from pathlib import Path
import re
import sqlite3
from unittest.mock import Mock

import pytest


APP = Path(__file__).resolve().parents[1] / "app"
spec = importlib.util.spec_from_file_location("enricher_dash", APP / "ui/enricher_dash.py")
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)

NAMES = [
    "IP_ADDRESS",
    "Mixed Case",
    "column.with.dots",
    "quote'and\"double",
    'IP\") -- harmless comment',
    'RESULT\" = NULL --',
]


@pytest.mark.parametrize("input_column", NAMES)
@pytest.mark.parametrize("result_column", NAMES)
def test_dashboard_binds_names(input_column, result_column):
    session = Mock()
    dashboard.update_table(session, input_column, result_column)
    session.sql.assert_called_once_with(
        "CALL ENRICHIP.enrich_ip_data(?, ?)",
        params=[input_column, result_column],
    )
    session.sql.return_value.collect.assert_called_once_with()


def render_update(connection, input_column, result_column):
    """Evaluate the actual SQL DEFAULT expressions using SQLite's SQL functions."""
    source = (APP / "setup_script.sql").read_text()
    procedure = source.split("CREATE OR REPLACE PROCEDURE ENRICHIP.enrich_ip_data", 1)[1]
    values = {"inp_field": input_column, "out_field": result_column}
    for name, expression in re.findall(r"(\w+) VARCHAR DEFAULT (.*);", procedure):
        for variable in values:
            expression = re.sub(r"\b" + variable + r"\b", ":" + variable, expression)
        values[name] = connection.execute("SELECT " + expression, values).fetchone()[0]
    return values["q"]


@pytest.mark.parametrize("input_column", NAMES)
@pytest.mark.parametrize("result_column", ["ENRICHED", 'result\" --', "result.with.dots"])
def test_procedure_updates_only_the_named_column(input_column, result_column):
    connection = sqlite3.connect(":memory:")
    connection.create_function("ip2data", 1, lambda value: "enriched:" + value)
    quote = lambda name: '"' + name.replace('"', '""') + '"'
    connection.execute(
        f"CREATE TABLE bound_table ({quote(input_column)} TEXT, "
        f"{quote(result_column)} TEXT, untouched TEXT)"
    )
    connection.execute("INSERT INTO bound_table VALUES ('1.2.3.4', NULL, 'keep')")
    statement = render_update(connection, input_column, result_column)
    # Only replace the Snowflake-specific target and function name for this engine.
    statement = statement.replace("REFERENCE('tabletouse')", "bound_table")
    statement = statement.replace("ENRICHIP.ip2data", "ip2data")
    connection.execute(statement)
    assert connection.execute("SELECT * FROM bound_table").fetchall() == [
        ("1.2.3.4", "enriched:1.2.3.4", "keep")
    ]
    connection.close()

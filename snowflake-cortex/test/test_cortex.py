import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest as pytest
from snowflake import cortex
from snowflake.cortex import Complete

class TestDataExporter(unittest.TestCase):

    def test_cortex_response(self):
        from cortexCaller import CortexCaller

        mock_df = pd.DataFrame([{"TestColumn": "TestValue"}])
        mock_input = 'Test input from user'
        cortexCaller = CortexCaller()
        cortexCaller.call_complete = MagicMock(name='call_complete')
        cortexCaller.call_complete.return_value = 'test answer from cortex'
        response = cortexCaller.call_cortex(mock_df, mock_input)
        cortexCaller.call_complete.assert_called_once()
        assert response == cortexCaller.call_complete.return_value
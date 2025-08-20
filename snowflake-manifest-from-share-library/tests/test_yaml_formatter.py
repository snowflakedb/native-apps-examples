"""Tests for YAMLFormatter class."""

import pytest
import yaml
import tempfile
import os
from unittest.mock import patch
from snowflake_manifest_from_share.yaml_formatter import YAMLFormatter, EmptyValue, FlowStyleList


class TestYAMLFormatter:
    """Test cases for YAMLFormatter."""

    def test_init_default_values(self):
        """Test YAMLFormatter initialization with default values."""
        formatter = YAMLFormatter()
        assert formatter.indent == 2
        assert formatter.sort_keys == True

    def test_init_custom_values(self):
        """Test YAMLFormatter initialization with custom values."""
        formatter = YAMLFormatter(indent=4, sort_keys=False)
        assert formatter.indent == 4
        assert formatter.sort_keys == False

    def test_format_analysis_basic(self):
        """Test basic YAML formatting."""
        formatter = YAMLFormatter()
        data = {
            'manifest_version': 2,
            'roles': [],
            'shared_content': {
                'databases': []
            }
        }

        result = formatter.format_analysis(data)

        # Verify it's valid YAML
        parsed = yaml.safe_load(result)
        assert parsed == data

    def test_format_analysis_with_roles(self):
        """Test YAML formatting with roles."""
        formatter = YAMLFormatter()
        data = {
            'manifest_version': 2,
            'roles': [
                {'DR1': {'comment': 'Test role'}},
                {'DR2': EmptyValue()}
            ],
            'shared_content': {
                'databases': []
            }
        }

        result = formatter.format_analysis(data)

        # Verify the YAML contains the expected structure
        assert 'DR1:' in result
        assert 'comment: Test role' in result
        assert 'DR2:' in result

    def test_format_analysis_with_flow_style_lists(self):
        """Test YAML formatting with flow style lists."""
        formatter = YAMLFormatter()
        data = {
            'manifest_version': 2,
            'roles': [],
            'shared_content': {
                'databases': [
                    {
                        'TEST_DB': {
                            'roles': FlowStyleList(['ROLE1', 'ROLE2']),
                            'schemas': [
                                {
                                    'PUBLIC': {
                                        'roles': FlowStyleList(['ROLE1']),
                                        'tables': [
                                            {
                                                'TABLE1': {
                                                    'roles': FlowStyleList(['ROLE1'])
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        result = formatter.format_analysis(data)

        # Verify flow style is used for roles
        assert 'roles: [ROLE1, ROLE2]' in result
        assert 'roles: [ROLE1]' in result

    def test_format_analysis_with_empty_values(self):
        """Test YAML formatting with empty values."""
        formatter = YAMLFormatter()
        data = {
            'manifest_version': 2,
            'roles': [{'EMPTY_ROLE': EmptyValue()}],
            'shared_content': {
                'databases': [
                    {
                        'TEST_DB': {
                            'schemas': [
                                {
                                    'PUBLIC': {
                                        'views': [
                                            {'EMPTY_VIEW': EmptyValue()}
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        result = formatter.format_analysis(data)

        # Verify empty values render correctly (just key with colon)
        assert 'EMPTY_ROLE:' in result
        assert 'EMPTY_VIEW:' in result
        # Should not have 'null' or '{}' after the colon
        assert 'EMPTY_ROLE: null' not in result
        assert 'EMPTY_VIEW: null' not in result

    def test_format_analysis_indentation(self):
        """Test YAML formatting with custom indentation."""
        formatter = YAMLFormatter(indent=4)
        data = {
            'manifest_version': 2,
            'shared_content': {
                'databases': [
                    {
                        'TEST_DB': {
                            'schemas': []
                        }
                    }
                ]
            }
        }

        result = formatter.format_analysis(data)

        # Verify 4-space indentation is used
        lines = result.split('\n')
        for line in lines:
            if line.startswith('    '):  # 4 spaces
                assert not line.startswith('  ') or line.startswith('    ')

    def test_format_analysis_no_sort_keys(self):
        """Test YAML formatting without sorting keys."""
        formatter = YAMLFormatter(sort_keys=False)
        data = {
            'z_key': 'value',
            'a_key': 'value',
            'manifest_version': 2
        }

        result = formatter.format_analysis(data)

        # The order should be preserved (not alphabetical)
        lines = [line.strip() for line in result.split('\n') if line.strip()]
        assert lines[0].startswith('z_key:')
        assert lines[1].startswith('a_key:')
        assert lines[2].startswith('manifest_version:')

    def test_save_to_file(self):
        """Test saving YAML to file."""
        formatter = YAMLFormatter()
        data = {
            'manifest_version': 2,
            'test': 'data'
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as f:
            filename = f.name

        try:
            formatter.save_to_file(data, filename)

            # Verify file was created and contains correct data
            assert os.path.exists(filename)
            
            with open(filename, 'r') as f:
                content = f.read()
            
            parsed = yaml.safe_load(content)
            assert parsed == data

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_save_to_file_error(self):
        """Test save to file with invalid path."""
        formatter = YAMLFormatter()
        data = {'test': 'data'}

        # Try to save to an invalid path
        with pytest.raises(Exception):
            formatter.save_to_file(data, '/invalid/path/file.yml')

    def test_format_analysis_error_handling(self):
        """Test error handling in format_analysis."""
        # Test with a mock that raises an exception
        with patch('snowflake_manifest_from_share.yaml_formatter.yaml.dump', side_effect=Exception("YAML error")):
            formatter = YAMLFormatter()
            data = {'test': 'data'}

            with pytest.raises(Exception, match="YAML error"):
                formatter.format_analysis(data)

    def test_real_world_manifest_structure(self):
        """Test formatting a realistic manifest structure."""
        formatter = YAMLFormatter()
        data = {
            'manifest_version': 2,
            'roles': [
                {'VIEWER': {'comment': 'Read-only access'}},
                {'ANALYST': EmptyValue()}
            ],
            'shared_content': {
                'databases': [
                    {
                        'DEMO_DB': {
                            'roles': FlowStyleList(['ANALYST']),
                            'schemas': [
                                {
                                    'ANALYTICS': {
                                        'roles': FlowStyleList(['VIEWER', 'ANALYST']),
                                        'tables': [
                                            {
                                                'EMPLOYEES': {
                                                    'roles': FlowStyleList(['ANALYST'])
                                                }
                                            }
                                        ],
                                        'views': [
                                            {
                                                'SUMMARY_VIEW': {
                                                    'roles': FlowStyleList(['VIEWER', 'ANALYST'])
                                                }
                                            },
                                            {
                                                'PUBLIC_VIEW': EmptyValue()
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        result = formatter.format_analysis(data)

        # Verify the structure is correct
        parsed = yaml.safe_load(result)
        assert parsed['manifest_version'] == 2
        assert 'roles' in parsed
        assert 'shared_content' in parsed

        # Verify flow style was applied to roles lists
        assert 'roles: [ANALYST]' in result
        assert 'roles: [VIEWER, ANALYST]' in result

        # Verify empty values are handled correctly
        assert 'ANALYST:' in result
        assert 'PUBLIC_VIEW:' in result


class TestEmptyValue:
    """Test the EmptyValue class."""

    def test_empty_value_creation(self):
        """Test EmptyValue can be created."""
        empty = EmptyValue()
        assert isinstance(empty, EmptyValue)


class TestFlowStyleList:
    """Test the FlowStyleList class."""

    def test_flow_style_list_creation(self):
        """Test FlowStyleList creation."""
        items = ['item1', 'item2', 'item3']
        flow_list = FlowStyleList(items)
        assert flow_list.items == items

    def test_flow_style_list_empty(self):
        """Test FlowStyleList with empty list."""
        flow_list = FlowStyleList([])
        assert flow_list.items == []
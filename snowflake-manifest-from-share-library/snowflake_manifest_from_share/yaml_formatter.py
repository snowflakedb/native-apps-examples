"""
YAML formatter for Snowflake share analysis results.
"""

import yaml
from typing import Dict, Any, Optional
import logging

class EmptyValue:
    """Represents an empty value that should render as just a key with colon in YAML."""
    pass

class FlowStyleList:
    """Represents a list that should be rendered in flow style [item1, item2]."""
    def __init__(self, items):
        self.items = items

class CustomYAMLDumper(yaml.SafeDumper):
    """Custom YAML dumper with thread-safe representers."""
    pass

def represent_empty_value(dumper, data):
    """Custom YAML representer for empty values."""
    return dumper.represent_scalar('tag:yaml.org,2002:null', '')

def represent_flow_style_list(dumper, data):
    """Custom YAML representer for flow style lists."""
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data.items, flow_style=True)

# Register representers on custom dumper class (thread-safe)
CustomYAMLDumper.add_representer(EmptyValue, represent_empty_value)
CustomYAMLDumper.add_representer(FlowStyleList, represent_flow_style_list)

logger = logging.getLogger(__name__)


class YAMLFormatter:
    """Formats share analysis results into YAML output."""
    
    def __init__(self, indent: int = 2, sort_keys: bool = True):
        """
        Initialize YAML formatter.
        
        Args:
            indent: Number of spaces for indentation
            sort_keys: Whether to sort dictionary keys
        """
        self.indent = indent
        self.sort_keys = sort_keys
    
    def format_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """
        Format the share analysis into YAML.
        
        Args:
            analysis_result: Dictionary containing share analysis results
            
        Returns:
            YAML formatted string
        """
        try:
            # Use custom dumper with thread-safe representers
            yaml_output = yaml.dump(
                analysis_result,
                Dumper=CustomYAMLDumper,
                default_flow_style=False,
                indent=self.indent,
                sort_keys=self.sort_keys,
                allow_unicode=True,
                default_style=None,
                width=1000  # Prevent line wrapping
            )
            return yaml_output
        except Exception as e:
            logger.error(f"Error formatting to YAML: {e}")
            raise
    
    def save_to_file(self, analysis_result: Dict[str, Any], filename: str) -> None:
        """
        Save analysis results to a YAML file.
        
        Args:
            analysis_result: Dictionary containing share analysis results
            filename: Output filename
        """
        yaml_content = self.format_analysis(analysis_result)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            logger.info(f"Analysis results saved to: {filename}")
        except Exception as e:
            logger.error(f"Error saving to file {filename}: {e}")
            raise
    

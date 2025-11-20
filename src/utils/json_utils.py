"""
JSON utilities for Guard AI Security System
"""
import json
from typing import Any, Dict, Union
from exceptions import LoggingError


class JsonUtils:
    """Utility class for common JSON operations"""
    
    @staticmethod
    def safe_dump(data: Any, file_path: str, ensure_ascii: bool = False, 
                  indent: int = 2, default: Any = str) -> None:
        """Safely dump data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent, default=default)
        except Exception as e:
            raise LoggingError(f"Failed to save JSON to {file_path}: {str(e)}", file_path)
    
    @staticmethod
    def safe_load(file_path: str) -> Dict[str, Any]:
        """Safely load data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise LoggingError(f"JSON file not found: {file_path}", file_path)
        except json.JSONDecodeError as e:
            raise LoggingError(f"Invalid JSON in {file_path}: {str(e)}", file_path)
        except Exception as e:
            raise LoggingError(f"Failed to load JSON from {file_path}: {str(e)}", file_path)
    
    @staticmethod
    def format_for_display(data: Any, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Format data as pretty JSON string for display"""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        except Exception:
            return str(data)
    
    @staticmethod
    def extract_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        """Extract nested value from dictionary using dot notation (e.g., 'log.colang_history')"""
        keys = key_path.split('.')
        current = data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
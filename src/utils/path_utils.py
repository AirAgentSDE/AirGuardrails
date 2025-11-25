"""
Path utilities for Guard AI Security System
"""
import os
from typing import Union


class PathUtils:
    """Utility class for common path operations"""
    
    @staticmethod
    def get_project_root() -> str:
        """Get the project root directory"""
        return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    @staticmethod
    def get_config_dir() -> str:
        """Get the configuration directory"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
    
    @staticmethod
    def get_log_dir() -> str:
        """Get the log directory"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
    
    @staticmethod
    def ensure_dir_exists(path: Union[str, os.PathLike]) -> None:
        """Ensure directory exists, create if it doesn't"""
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def join_paths(*paths) -> str:
        """Join multiple path components safely"""
        return os.path.join(*paths)
    
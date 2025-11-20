"""
Log Manager for Guard AI Security System
"""
import os
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils import PathUtils, JsonUtils
from exceptions import LoggingError


class LogManager:
    """Manages interaction logging with rotation and cleanup"""
    
    def __init__(self, log_dir: str = None, max_logs: int = 100):
        """Initialize log manager
        
        Args:
            log_dir: Directory to store logs. If None, uses default.
            max_logs: Maximum number of log files to keep
        """
        self.log_dir = log_dir or PathUtils.get_log_dir()
        self.max_logs = max_logs
        self._ensure_log_directory()
    
    def _ensure_log_directory(self) -> None:
        """Ensure log directory exists"""
        try:
            PathUtils.ensure_dir_exists(self.log_dir)
        except Exception as e:
            raise LoggingError(f"Failed to create log directory: {str(e)}", self.log_dir)
    
    def save_interaction_log(self, user_input: str, response_data: Dict[str, Any], 
                           use_nemoguardrails: bool) -> str:
        """Save interaction log to file
        
        Args:
            user_input: User input message
            response_data: Response data from API
            use_nemoguardrails: Whether NeMo Guardrails was used
            
        Returns:
            Path to saved log file
            
        Raises:
            LoggingError: If saving fails
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"log_{timestamp}.json"
            log_file_path = PathUtils.join_paths(self.log_dir, log_filename)
            
            # Build log data structure
            log_data = self._build_log_data(user_input, response_data, use_nemoguardrails, timestamp)
            
            # Save to file
            JsonUtils.safe_dump(log_data, log_file_path)
            
            # Cleanup old logs if needed
            self._cleanup_old_logs()
            
            return log_file_path
            
        except Exception as e:
            raise LoggingError(f"Failed to save interaction log: {str(e)}", log_file_path)
    
    def _build_log_data(self, user_input: str, response_data: Dict[str, Any], 
                       use_nemoguardrails: bool, timestamp: str) -> Dict[str, Any]:
        """Build log data structure
        
        Args:
            user_input: User input message
            response_data: Response data from API
            use_nemoguardrails: Whether NeMo Guardrails was used
            timestamp: Timestamp for the log entry
            
        Returns:
            Structured log data
        """
        log_data = {
            "timestamp": timestamp,
            "user_input": user_input,
            "use_nemoguardrails": use_nemoguardrails
        }
        
        # Extract response content based on the source
        if use_nemoguardrails and "messages" in response_data:
            if response_data["messages"] and len(response_data["messages"]) > 0:
                log_data["response"] = response_data["messages"][0].get("content", "")
            
            # Extract detailed logging information when using nemoguardrails
            if "llm_output" in response_data:
                log_data["llm_output"] = response_data["llm_output"]
            
            if "log" in response_data:
                log_info = response_data["log"]
                log_data["colang_history"] = log_info.get("colang_history", "")
                log_data["activated_guardrails"] = log_info.get("activated_rails", [])
                log_data["llm_calls"] = log_info.get("llm_calls", [])
                
        elif not use_nemoguardrails and "response" in response_data:
            log_data["response"] = response_data["response"]
        else:
            # Fallback for unexpected response format
            log_data["response"] = str(response_data)
            log_data["raw_response"] = response_data
        
        return log_data
    
    def get_available_logs(self) -> List[str]:
        """Get list of available log files
        
        Returns:
            List of log filenames, sorted by newest first
        """
        try:
            log_pattern = PathUtils.join_paths(self.log_dir, "log_*.json")
            log_files = glob.glob(log_pattern)
            
            # Sort by modification time (newest first)
            log_files.sort(key=os.path.getmtime, reverse=True)
            
            # Return just the filenames
            return [os.path.basename(f) for f in log_files]
            
        except Exception as e:
            raise LoggingError(f"Failed to get available logs: {str(e)}", self.log_dir)
    
    def load_log_content(self, log_filename: str) -> str:
        """Load and format log content for display
        
        Args:
            log_filename: Name of the log file to load
            
        Returns:
            Formatted log content as string
            
        Raises:
            LoggingError: If loading fails
        """
        try:
            log_path = PathUtils.join_paths(self.log_dir, log_filename)
            log_data = JsonUtils.safe_load(log_path)
            
            return self._format_log_for_display(log_data)
            
        except Exception as e:
            raise LoggingError(f"Failed to load log content: {str(e)}", log_path)
    
    def _format_log_for_display(self, log_data: Dict[str, Any]) -> str:
        """Format log data for display
        
        Args:
            log_data: Log data dictionary
            
        Returns:
            Formatted log content
        """
        formatted = f"时间戳: {log_data.get('timestamp', 'N/A')}\n"
        formatted += f"安全防护模式: {'启用' if log_data.get('use_nemoguardrails', False) else '未启用'}\n\n"
        
        formatted += f"用户输入:\n{log_data.get('user_input', 'N/A')}\n\n"
        
        if log_data.get('response'):
            formatted += f"响应内容:\n{log_data['response']}\n\n"
        
        # Display detailed logging information when nemoguardrails is used
        if log_data.get('use_nemoguardrails', False):
            if log_data.get('activated_guardrails'):
                formatted += f"激活的防护规则:\n{JsonUtils.format_for_display(log_data['activated_guardrails'])}\n\n"
            
            if log_data.get('colang_history'):
                formatted += f"Colang History:\n{JsonUtils.format_for_display(log_data['colang_history'])}\n\n"
            
            if log_data.get('llm_calls'):
                formatted += f"LLM Calls:\n{JsonUtils.format_for_display(log_data['llm_calls'])}\n\n"
            
            if log_data.get('llm_output'):
                formatted += f"LLM输出:\n{JsonUtils.format_for_display(log_data['llm_output'])}\n\n"
        
        return formatted
    
    def _cleanup_old_logs(self) -> None:
        """Remove old log files if exceeding max_logs limit"""
        try:
            log_files = self.get_available_logs()
            
            if len(log_files) > self.max_logs:
                # Remove oldest logs
                files_to_remove = log_files[self.max_logs:]
                for filename in files_to_remove:
                    file_path = PathUtils.join_paths(self.log_dir, filename)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        # Log but don't fail if cleanup fails
                        print(f"Warning: Failed to remove old log file {filename}: {str(e)}")
                        
        except Exception as e:
            # Log but don't fail if cleanup fails
            print(f"Warning: Failed to cleanup old logs: {str(e)}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about logs
        
        Returns:
            Dictionary with log statistics
        """
        try:
            log_files = self.get_available_logs()
            
            total_size = 0
            log_count = len(log_files)
            
            for filename in log_files:
                file_path = PathUtils.join_paths(self.log_dir, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except:
                    pass
            
            return {
                "log_count": log_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "log_directory": self.log_dir,
                "max_logs": self.max_logs
            }
            
        except Exception as e:
            raise LoggingError(f"Failed to get log stats: {str(e)}", self.log_dir)
    
    def clear_all_logs(self) -> int:
        """Clear all log files
        
        Returns:
            Number of files removed
            
        Raises:
            LoggingError: If clearing fails
        """
        try:
            log_files = self.get_available_logs()
            removed_count = 0
            
            for filename in log_files:
                file_path = PathUtils.join_paths(self.log_dir, filename)
                try:
                    os.remove(file_path)
                    removed_count += 1
                except Exception as e:
                    print(f"Warning: Failed to remove log file {filename}: {str(e)}")
            
            return removed_count
            
        except Exception as e:
            raise LoggingError(f"Failed to clear logs: {str(e)}", self.log_dir)

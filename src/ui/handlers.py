"""
UI Event Handlers for Guard AI Security System
"""
from typing import List, Callable, Any
import gradio as gr
from services import ChatService, LogManager


class UIHandlers:
    """Handles UI event logic"""
    
    def __init__(self, chat_service: ChatService, log_manager: LogManager):
        """Initialize UI handlers
        
        Args:
            chat_service: Chat service instance
            log_manager: Log manager instance
        """
        self.chat_service = chat_service
        self.log_manager = log_manager
    
    def create_respond_handler(self) -> Callable:
        """Create chat response handler
        
        Returns:
            Handler function for chat responses
        """
        def respond(message: str, chat_history: List[List[str]], use_guardrails: bool) -> tuple:
            """Handle chat response
            
            Args:
                message: User message
                chat_history: Chat history
                use_guardrails: Whether to use guardrails
                
            Returns:
                Tuple of (empty_message, updated_history)
            """
            if not message or not message.strip():
                return "", chat_history
            
            try:
                response = self.chat_service.chat(
                    user_input=message,
                    use_nemoguardrails=use_guardrails
                )
                chat_history.append([message, response])
            except Exception as e:
                error_response = f"聊天发生错误: {str(e)}"
                chat_history.append([message, error_response])
            
            return "", chat_history
        
        return respond
    
    def create_load_log_handler(self) -> Callable:
        """Create log loading handler
        
        Returns:
            Handler function for loading log content
        """
        def load_selected_log(log_filename: str) -> str:
            """Load selected log content
            
            Args:
                log_filename: Name of log file to load
                
            Returns:
                Formatted log content
            """
            if not log_filename:
                return "未选择日志文件。"
            
            try:
                return self.log_manager.load_log_content(log_filename)
            except Exception as e:
                return f"加载日志失败: {str(e)}"
        
        return load_selected_log
    
    def create_refresh_logs_handler(self) -> Callable:
        """Create log refresh handler
        
        Returns:
            Handler function for refreshing log list
        """
        def refresh_logs() -> gr.Dropdown:
            """Refresh available logs
            
            Returns:
                Updated dropdown component
            """
            try:
                log_files = self.log_manager.get_available_logs()
                return gr.Dropdown(
                    choices=log_files, 
                    value=log_files[0] if log_files else None
                )
            except Exception as e:
                print(f"Failed to refresh logs: {str(e)}")
                return gr.Dropdown(choices=[], value=None)
        
        return refresh_logs
    
    def create_clear_chat_handler(self) -> Callable:
        """Create clear chat handler
        
        Returns:
            Handler function for clearing chat
        """
        def clear_chat() -> List:
            """Clear chat history
            
            Returns:
                Empty chat history
            """
            return []
        
        return clear_chat
    
    def wire_events(self, components: dict) -> None:
        """Wire up all UI events
        
        Args:
            components: Dictionary of UI components
        """
        # Get handlers
        respond_handler = self.create_respond_handler()
        load_log_handler = self.create_load_log_handler()
        refresh_logs_handler = self.create_refresh_logs_handler()
        clear_chat_handler = self.create_clear_chat_handler()
        
        # Wire up chat events
        components['msg'].submit(
            respond_handler,
            [components['msg'], components['chatbot'], components['use_nemoguardrails']],
            [components['msg'], components['chatbot']]
        )
        
        components['submit_btn'].click(
            respond_handler,
            [components['msg'], components['chatbot'], components['use_nemoguardrails']],
            [components['msg'], components['chatbot']]
        )
        
        components['clear_btn'].click(
            clear_chat_handler,
            outputs=[components['chatbot']]
        )
        
        # Wire up log events
        components['refresh_btn'].click(
            refresh_logs_handler,
            outputs=[components['log_dropdown']]
        )
        
        components['log_dropdown'].change(
            load_log_handler,
            [components['log_dropdown']],
            [components['log_display']]
        )
        
        # Auto-refresh logs on interface load
        # This will be handled in the main interface creation
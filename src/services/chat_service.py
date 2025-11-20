"""
Chat Service for Guard AI Security System
"""
from typing import Dict, Any, Optional
from .api_client import ApiClient
from .log_manager import LogManager
from exceptions import GuardApiError


class ChatService:
    """Core chat business logic service"""
    
    def __init__(self,
                 api_client: ApiClient = None, 
                 log_manager: LogManager = None):
        """Initialize chat service
        
        Args:
            config_manager: Configuration manager instance
            api_client: API client instance
            log_manager: Log manager instance
        """
        self.api_client = api_client or ApiClient()
        self.log_manager = log_manager or LogManager()
        
    
    def chat_with_nemoguardrails(self, user_input: str, config_id: str = "config") -> Dict[str, Any]:
        """Chat using NeMo Guardrails with safety checks
        
        Args:
            user_input: User input message
            config_id: Configuration ID to use
            
        Returns:
            Response data from NeMo Guardrails
            
        Raises:
            GuardApiError: If chat request fails
            ConfigurationError: If configuration is invalid
        """
        if not user_input:
            raise GuardApiError("User input cannot be empty")
        
        try:            
            # Make request to NeMo Guardrails
            response_data = self.api_client.request_nemoguardrails_single_config(
                user_input=user_input,
                config_id=config_id
            )
            
            # Log the interaction
            self.log_manager.save_interaction_log(
                user_input=user_input,
                response_data=response_data,
                use_nemoguardrails=True
            )
            
            return response_data
            
        except Exception as e:
            # Log failed attempt
            self.log_manager.save_interaction_log(
                user_input=user_input,
                response_data={"error": str(e)},
                use_nemoguardrails=True
            )
            raise
    
    def chat_directly(self, user_input: str, model: str = "qwen3:30b-instruct") -> Dict[str, Any]:
        """Chat directly with Ollama without safety checks
        
        Args:
            user_input: User input message
            model: Model name to use. If None, uses configured main model
            
        Returns:
            Response data from Ollama
            
        Raises:
            GuardApiError: If chat request fails
            ConfigurationError: If configuration is invalid
        """
        if not user_input:
            raise GuardApiError("User input cannot be empty")
        
        try:
            
            # Make request to Ollama
            response_data = self.api_client.request_ollama(
                user_input=user_input,
                model=model
            )
            
            # Log the interaction
            self.log_manager.save_interaction_log(
                user_input=user_input,
                response_data=response_data,
                use_nemoguardrails=False
            )
            
            return response_data
            
        except Exception as e:
            # Log failed attempt
            self.log_manager.save_interaction_log(
                user_input=user_input,
                response_data={"error": str(e)},
                use_nemoguardrails=False
            )
            raise
    
    def get_response_text(self, response_data: Dict[str, Any], use_nemoguardrails: bool) -> str:
        """Extract response text from API response data
        
        Args:
            response_data: Response data from API
            use_nemoguardrails: Whether NeMo Guardrails was used
            
        Returns:
            Response text string
        """
        try:
            if use_nemoguardrails:
                if "messages" in response_data and response_data["messages"]:
                    return response_data["messages"][0].get("content", "")
                else:
                    return "蓝擎安全防护服务返回了意外的响应格式"
            else:
                if "response" in response_data:
                    return response_data["response"]
                else:
                    return "直接对话服务返回了意外的响应格式"
        except Exception:
            return "响应解析失败"
    
    def chat(self, user_input: str, use_nemoguardrails: bool = True, 
             config_id: str = "config", model: str = None) -> str:
        """Main chat method that handles both modes
        
        Args:
            user_input: User input message
            use_nemoguardrails: Whether to use NeMo Guardrails
            config_id: Configuration ID for NeMo Guardrails
            model: Model name for direct chat
            
        Returns:
            Response text string
            
        Raises:
            GuardApiError: If chat request fails
        """
        if not user_input or not user_input.strip():
            return "请输入您的消息。"
        
        try:
            if use_nemoguardrails:
                response_data = self.chat_with_nemoguardrails(user_input, config_id)
            else:
                response_data = self.chat_directly(user_input, model)
            
            return self.get_response_text(response_data, use_nemoguardrails)
            
        except GuardApiError:
            # Re-raise API errors
            raise
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"聊天服务发生错误: {str(e)}"
            
            # Log the error
            self.log_manager.save_interaction_log(
                user_input=user_input,
                response_data={"error": error_msg},
                use_nemoguardrails=use_nemoguardrails
            )
            
            return error_msg
        
    def cleanup(self):
        """Cleanup API client resources"""
        if hasattr(self, 'api_client') and self.api_client is not None:
            try:
                self.api_client.close()
            except Exception as e:
                print(f"Warning: Failed to cleanup API client: {str(e)}")
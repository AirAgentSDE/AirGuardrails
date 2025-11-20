import gradio as gr
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services import ChatService, LogManager
from ui.components import UIComponents
from ui.handlers import UIHandlers
from exceptions import GuardApiError


class ChatbotInterface:
    def __init__(self):
        """Initialize the chatbot interface with services"""
        # Initialize services
        self.chat_service = ChatService()
        self.log_manager = LogManager()
        self.ui_handlers = UIHandlers(self.chat_service, self.log_manager)
        
    def get_available_logs(self) -> list[str]:
        """Get list of available log files"""
        try:
            return self.log_manager.get_available_logs()
        except Exception as e:
            print(f"Failed to get available logs: {str(e)}")
            return []
    
    def load_log_content(self, log_filename: str) -> str:
        """Load and format log content for display"""
        try:
            return self.log_manager.load_log_content(log_filename)
        except Exception as e:
            return f"加载日志时出错: {str(e)}"
    
    def chat_response(self, message: str, history: list[list[str]], use_nemoguardrails: bool) -> str:
        """Generate chat response using services"""
        try:
            return self.chat_service.chat(
                user_input=message,
                use_nemoguardrails=use_nemoguardrails
            )
        except (GuardApiError) as e:
            return f"服务错误: {str(e)}"
        except Exception as e:
            return f"聊天发生未知错误: {str(e)}"
    
    def refresh_logs(self) -> gr.Dropdown:
        """Refresh the log file dropdown"""
        log_files = self.get_available_logs()
        return gr.Dropdown(choices=log_files, value=log_files[0] if log_files else None)
    
    def create_interface(self):
        """Create the Gradio interface using components and handlers"""
        with gr.Blocks(title="蓝擎安全助手", theme=gr.themes.Soft()) as interface:
            # Create UI components
            components = UIComponents.create_layout()
            
            # Update log dropdown with initial data
            log_files = self.get_available_logs()
            components['log_dropdown'].choices = log_files
            components['log_dropdown'].value = log_files[0] if log_files else None
            
            # Wire up events using handlers
            self.ui_handlers.wire_events(components)
            
            # Auto-refresh logs on load
            interface.load(self.refresh_logs, outputs=[components['log_dropdown']])
        
        return interface
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'chat_service'):
            self.chat_service.cleanup()

def main():
    """Main function to launch the Gradio app"""
    chatbot = ChatbotInterface()
    
    try:
        interface = chatbot.create_interface()
        
        # Launch on port 5071
        interface.launch(
            server_name="127.0.0.1",
            server_port=5071,
            share=False,
            debug=True,
            show_error=True
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Application error: {str(e)}")
    finally:
        # Cleanup resources
        chatbot.cleanup()

if __name__ == "__main__":
    main()
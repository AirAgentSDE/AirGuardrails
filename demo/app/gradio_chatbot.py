import gradio as gr
import requests
import json
import os
import glob
from datetime import datetime
from typing import Dict, Any

class ChatbotInterface:
    def __init__(self):
        self.nemoguardrails_url = "http://127.0.0.1:5070"
        self.ollama_url = "http://127.0.0.1:11434"
        self.log_dir = os.path.join(os.path.dirname(__file__), "..", "log")
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "config")
        
    def get_available_logs(self) -> list[str]:
        """Get list of available log files"""
        try:
            log_files = glob.glob(os.path.join(self.log_dir, "log_*.json"))
            log_files.sort(reverse=True)  # Most recent first
            return [os.path.basename(f) for f in log_files]
        except Exception as e:
            return []
    
    def load_log_content(self, log_filename: str) -> str:
        """Load and format log content for display"""
        try:
            log_path = os.path.join(self.log_dir, log_filename)
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # Format log data for display
            formatted = f"时间戳: {log_data.get('timestamp', 'N/A')}\n"
            formatted += f"安全防护模式: {'启用' if log_data.get('use_nemoguardrails', False) else '未启用'}\n\n"
            
            formatted += f"用户输入:\n{log_data.get('user_input', 'N/A')}\n\n"
            
            if log_data.get('response'):
                formatted += f"响应内容:\n{log_data['response']}\n\n"
            
            # Display detailed logging information when nemoguardrails is used
            if log_data.get('use_nemoguardrails', False):
                
                if log_data.get('colang_history'):
                    formatted += f"Colang History:\n{json.dumps(log_data['colang_history'], indent=2, ensure_ascii=False)}\n\n"
                
            return formatted
        except Exception as e:
            return f"加载日志时出错: {str(e)}"
    
    def request_nemoguardrails(self, user_input: str) -> Dict[str, Any]:
        """Make request to nemoguardrails server"""
        try:
            response = requests.post(
                f"{self.nemoguardrails_url}/v1/chat/completions",
                json={
                    "config_id": "config",
                    "messages": [{
                        "role": "user",
                        "content": user_input
                    }],
                    "options": {
                        "log": {
                            "colang_history": True
                        }
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"蓝擎安全防护服务请求失败: {str(e)}"}
    
    def request_ollama(self, user_input: str) -> Dict[str, Any]:
        """Make direct request to Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "qwen3:30b-instruct",
                    "prompt": user_input,
                    "stream": False
                },
                timeout=90
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Ollama直接对话服务请求失败: {str(e)}"}
    
    def save_log(self, user_input: str, response_data: Dict[str, Any], use_nemoguardrails: bool):
        """Save interaction log"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file_path = os.path.join(self.log_dir, f"log_{timestamp}.json")
            
            log_data = {
                "timestamp": timestamp,
                "user_input": user_input,
                "use_nemoguardrails": use_nemoguardrails
            }
            
            # Extract response content based on the source
            if use_nemoguardrails and "messages" in response_data:
                log_data["response"] = response_data["messages"][0]["content"]

                # Extract detailed logging information when using nemoguardrails
                if "log" in response_data:
                    log_info = response_data["log"]
                    log_data["colang_history"] = log_info.get("colang_history", "")
                    
            elif not use_nemoguardrails and "response" in response_data:
                log_data["response"] = response_data["response"]
            else:
                log_data["response"] = str(response_data)
            
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving log: {str(e)}")
    
    def chat_response(self, message: str, history: list[list[str]], use_nemoguardrails: bool) -> str:
        """Generate chat response"""
        if not message.strip():
            return "请输入您的消息。"
        
        # Make request based on toggle
        if use_nemoguardrails:
            response_data = self.request_nemoguardrails(message)
            if response_data:
                response = response_data["messages"][0]["content"]
            else:
                response = "蓝擎安全防护服务返回了意外的响应格式"
        else:
            response_data = self.request_ollama(message)
            if response_data:
                response = response_data["response"]
            else:
                response = "Ollama直接对话服务返回了意外的响应格式"
        
        # Save log
        self.save_log(message, response_data, use_nemoguardrails)
        
        return response
    
    def refresh_logs(self) -> gr.Dropdown:
        """Refresh the log file dropdown"""
        log_files = self.get_available_logs()
        return gr.Dropdown(choices=log_files, value=log_files[0] if log_files else None)
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="蓝擎安全助手", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🤖 蓝擎安全助手")
            gr.Markdown("与蓝擎安全助手对话，支持安全防护模式和直接对话模式，可查看调试日志。")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Chat interface
                    use_nemoguardrails = gr.Checkbox(
                        label="使用安全防护模式", 
                        value=True,
                        info="在安全防护模式和直接对话模式之间切换"
                    )
                    
                    chatbot = gr.Chatbot(
                        label="对话窗口",
                        height=500,
                        show_copy_button=True
                    )
                    
                    msg = gr.Textbox(
                        label="您的消息",
                        placeholder="请输入您的消息...",
                        lines=2
                    )
                    
                    with gr.Row():
                        submit_btn = gr.Button("发送", variant="primary")
                        clear_btn = gr.Button("清空对话")
                
                with gr.Column(scale=1):
                    # Debug log viewer
                    gr.Markdown("### 📋 调试日志")
                    
                    with gr.Row():
                        log_dropdown = gr.Dropdown(
                            label="选择日志文件",
                            choices=self.get_available_logs(),
                            value=self.get_available_logs()[0] if self.get_available_logs() else None
                        )
                        refresh_btn = gr.Button("🔄 刷新")
                    
                    log_display = gr.Textbox(
                        label="日志内容",
                        lines=25,
                        max_lines=30,
                        show_copy_button=True,
                        interactive=False
                    )
            
            # Event handlers
            def respond(message, chat_history, use_guardrails):
                if not message:
                    return "", chat_history
                
                response = self.chat_response(message, chat_history, use_guardrails)
                chat_history.append([message, response])
                return "", chat_history
            
            def load_selected_log(log_filename):
                if log_filename:
                    return self.load_log_content(log_filename)
                return "未选择日志文件。"
            
            # Wire up the events
            msg.submit(respond, [msg, chatbot, use_nemoguardrails], [msg, chatbot])
            submit_btn.click(respond, [msg, chatbot, use_nemoguardrails], [msg, chatbot])
            clear_btn.click(lambda: [], outputs=[chatbot])
            
            refresh_btn.click(self.refresh_logs, outputs=[log_dropdown])
            log_dropdown.change(load_selected_log, [log_dropdown], [log_display])
            
            # Auto-refresh logs on load
            interface.load(self.refresh_logs, outputs=[log_dropdown])
        
        return interface

def main():
    """Main function to launch the Gradio app"""
    chatbot = ChatbotInterface()
    interface = chatbot.create_interface()
    
    # Launch on port 5071
    interface.launch(
        server_name="127.0.0.1",
        server_port=5071,
        share=False,
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main()
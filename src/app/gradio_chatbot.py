import gradio as gr
import json
import os
import requests
from datetime import datetime
from typing import Dict, Any, List


class ApiClient:
    """API客户端，处理NeMo Guardrails和Ollama请求"""
    
    def __init__(self):
        self.nemoguardrails_url = "http://127.0.0.1:5070"
        self.ollama_url = "http://127.0.0.1:11434"
        self.timeout = 120
    
    def request_nemoguardrails(self, user_input: str) -> Dict[str, Any]:
        """请求NeMo Guardrails API"""
        payload = {
            "config_ids": ["main", "content_safety_local"],
            "messages": [{"role": "user", "content": user_input}],
            "options": {
                "output_vars": ["triggered_input_rail", "triggered_output_rail"],
                "log": {
                    "colang_history": True
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.nemoguardrails_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": f"NeMo Guardrails请求超时({self.timeout}秒)"}
        except requests.exceptions.ConnectionError:
            return {"error": "无法连接到NeMo Guardrails服务"}
        except Exception as e:
            return {"error": f"NeMo Guardrails请求失败: {str(e)}"}
    
    def request_ollama(self, user_input: str) -> Dict[str, Any]:
        """请求Ollama API"""
        payload = {
            "model": "qwen3:30b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": f"Ollama请求超时({self.timeout}秒)"}
        except requests.exceptions.ConnectionError:
            return {"error": "无法连接到Ollama服务"}
        except Exception as e:
            return {"error": f"Ollama请求失败: {str(e)}"}


class LogManager:
    """日志管理器"""

    def __init__(self):
        # 获取日志目录（src/app/log）
        self.log_dir = os.path.join(os.path.dirname(__file__), "log")
        # 确保目录存在
        os.makedirs(self.log_dir, exist_ok=True)

    def save_log(self, user_input: str, response: Dict[str, Any], service_name: str) -> str:
        """保存服务日志到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"log_{timestamp}.json"
        log_file_path = os.path.join(self.log_dir, log_filename)
        
        log_data = {
            "timestamp": timestamp,
            "service": service_name,
            "user_input": user_input
        }
        
        # 根据服务类型提取响应内容
        if service_name == "guardrails":
            if "messages" in response and response["messages"]:
                log_data["response"] = response["messages"][0].get("content", "")
            if "log" in response:
                log_data["colang_history"] = response["log"].get("colang_history", "")
        else:
            if "message" in response and response["message"]:
                log_data["response"] = response["message"].get("content", "")
            if "error" in response:
                log_data["error"] = response["error"]
        
        # 保存到文件
        try:
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存服务日志失败: {str(e)}")
        
        return log_filename
    

class ChatbotInterface:
    """聊天界面"""
    
    def __init__(self):
        self.api_client = ApiClient()
        self.log_manager = LogManager()
    
    def chat_response(self, message: str, enable_guardrails: bool, chat_history: List[List[str]]) -> tuple:
        """根据护栏选项向相应服务发送请求并返回响应"""
        if not message or not message.strip():
            return "", chat_history
        
        try:
            # 根据护栏选项选择服务
            if enable_guardrails:
                response_data = self.api_client.request_nemoguardrails(message)
                response_text = self._extract_response_text(response_data, True)
                service_name = "guardrails"
            else:
                response_data = self.api_client.request_ollama(message)
                response_text = self._extract_response_text(response_data, False)
                service_name = "ollama"
            
            # 保存日志
            self.log_manager.save_log(message, response_data, service_name)
            
            # 更新聊天历史
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response_text})

            return "", chat_history

        except Exception as e:
            error_msg = f"聊天发生错误: {str(e)}"
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": error_msg})
            return "", chat_history
    
    def _extract_response_text(self, response_data: Dict[str, Any], use_nemoguardrails: bool) -> str:
        """从响应数据中提取文本"""
        try:
            if use_nemoguardrails:
                if "messages" in response_data and response_data["messages"]:
                    return response_data["messages"][0].get("content", "蓝擎安全护栏未返回预期内容")
                else:
                    return f"NeMo Guardrails返回了意外的响应格式:{response_data}"
            else:
                if "message" in response_data and response_data["message"]:
                    return response_data["message"].get("content", "ollama未返回预期内容")
                elif "error" in response_data:
                    return f"Ollama错误: {response_data['error']}"
                else:
                    return f"Ollama返回了意外的响应格式:{response_data}"

        except Exception as e:
            return f"响应解析失败: {str(e)}"
    
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="蓝擎大模型安全护栏体验广场") as interface:
            gr.Markdown(
                '<div style="background: #1a73e8; '
                'padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 20px;">'
                '<h1 style="margin: 0; color: white; font-size: 28px; font-weight: 600;">'
                '🛡️ 蓝擎大模型安全护栏体验广场'
                '</h1></div>'
            )
            
            # 控制区域
            with gr.Row():
                enable_guardrails = gr.Checkbox(
                    label="启用安全护栏",
                    value=False,
                    info="勾选后请求将发送到蓝擎安全对话服务，否则发送到Ollama服务"
                )
            
            # 聊天区域
            with gr.Row():
                chatbot = gr.Chatbot(
                    label="对话记录",
                    show_label=True,
                    height=500
                )
            
            # 输入区域
            with gr.Row():
                msg = gr.Textbox(
                    label="用户",
                    placeholder="请输入您的消息...",
                    lines=3,
                    scale=4,
                    container=False
                )
                with gr.Column(scale=1):
                    submit_btn = gr.Button("发送", variant="primary", size="lg", elem_id="submit-btn")
                    clear_btn = gr.Button("清空对话", size="lg", elem_id="clear-btn")
            
            # 状态提示
            status_text = gr.Markdown(
                "💡 **提示**: 当前使用 **Ollama** 服务（无护栏）",
                elem_id="status_text"
            )
            
            # 事件处理
            def respond(message, guardrails_enabled, history):
                return self.chat_response(message, guardrails_enabled, history)
            
            def clear_chat():
                return [], None
            
            def update_status(guardrails_enabled):
                if guardrails_enabled:
                    return "💡 **提示**: 当前使用 **蓝擎安全对话** 服务（已启用护栏）"
                else:
                    return "💡 **提示**: 当前使用 **Ollama** 服务（无护栏）"
            
            # 绑定事件
            msg.submit(
                respond,
                [msg, enable_guardrails, chatbot],
                [msg, chatbot]
            )
            submit_btn.click(
                respond,
                [msg, enable_guardrails, chatbot],
                [msg, chatbot]
            )
            clear_btn.click(clear_chat, outputs=[chatbot, msg])
            enable_guardrails.change(
                update_status,
                [enable_guardrails],
                [status_text]
            )
            
        return interface


def main():
    """主函数：启动Gradio应用"""
    chatbot = ChatbotInterface()
    
    try:
        interface = chatbot.create_interface()
        
        # 启动应用
        interface.launch(
            server_name="127.0.0.1",
            server_port=5071,
            share=False,
            debug=True,
            show_error=True,
            theme=gr.themes.Soft(),
            css="#submit-btn, #clear-btn { background-color: #1a73e8 !important; color: white !important; }"
        )
    except KeyboardInterrupt:
        print("\n应用正在关闭...")
    except Exception as e:
        print(f"应用错误: {str(e)}")
        raise


if __name__ == "__main__":
    main()
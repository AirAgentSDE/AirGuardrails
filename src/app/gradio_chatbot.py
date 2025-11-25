import gradio as gr
import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.path_utils import PathUtils


class ApiClient:
    """API客户端，处理NeMo Guardrails和Ollama请求"""
    
    def __init__(self):
        self.nemoguardrails_url = "http://127.0.0.1:5070"
        self.ollama_url = "http://127.0.0.1:11434"
        self.timeout = 120
    
    def request_nemoguardrails(self, user_input: str) -> Dict[str, Any]:
        """请求NeMo Guardrails API"""
        payload = {
            "config_id": "config",
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
                timeout=self.timeout - 30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": f"Ollama请求超时({self.timeout-30}秒)"}
        except requests.exceptions.ConnectionError:
            return {"error": "无法连接到Ollama服务"}
        except Exception as e:
            return {"error": f"Ollama请求失败: {str(e)}"}


class LogManager:
    """日志管理器"""
    
    def __init__(self):
        self.log_dir = PathUtils.get_log_dir()
        PathUtils.ensure_dir_exists(self.log_dir)
    
    def save_log(self, user_input: str, guardrails_response: Dict[str, Any], ollama_response: Dict[str, Any]) -> str:
        """保存服务日志到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"log_{timestamp}.json"
        log_file_path = PathUtils.join_paths(self.log_dir, log_filename)
        
        log_data = {
            "timestamp": timestamp,
            "user_input": user_input
        }
        
        # 提取NeMo Guardrails响应内容
        if "messages" in guardrails_response and guardrails_response["messages"]:
            log_data["guardrails_response"] = guardrails_response["messages"][0].get("content", "")
        if "log" in guardrails_response:
            log_data["guardrails_colang_history"] = guardrails_response["log"].get("colang_history", "")
                
        # 提取Ollama响应内容
        if "message" in ollama_response and ollama_response["message"]:
            log_data["ollama_response"] = ollama_response["message"].get("content", "")
        if "error" in ollama_response:
            log_data["ollama_error"] = ollama_response["error"]
        
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
    
    def dual_chat_response(self, message: str, guardrails_history: List[List[str]], ollama_history: List[List[str]]) -> tuple:
        """同时向两个服务发送请求并返回响应"""
        if not message or not message.strip():
            return "", guardrails_history, ollama_history
        
        try:
            # 并行请求两个服务
            guardrails_response_data = self.api_client.request_nemoguardrails(message)
            ollama_response_data = self.api_client.request_ollama(message)
            
            # 提取响应文本
            guardrails_response = self._extract_response_text(guardrails_response_data, True)
            ollama_response = self._extract_response_text(ollama_response_data, False)
            
            # 保存日志
            self.log_manager.save_log(message, guardrails_response_data, ollama_response_data)
            
            # 更新聊天历史
            guardrails_history.append([message, guardrails_response])
            ollama_history.append([message, ollama_response])
            
            return "", guardrails_history, ollama_history
            
        except Exception as e:
            error_msg = f"聊天发生错误: {str(e)}"
            guardrails_history.append([message, error_msg])
            ollama_history.append([message, error_msg])
            return "", guardrails_history, ollama_history
    
    def _extract_response_text(self, response_data: Dict[str, Any], use_nemoguardrails: bool) -> str:
        """从响应数据中提取文本"""
        try:
            if use_nemoguardrails:
                if "messages" in response_data and response_data["messages"]:
                    return response_data["messages"][0].get("content", "蓝擎安全防护服务返回了意外的响应格式")
                else:
                    return "蓝擎安全防护服务返回了意外的响应格式"
            else:
                # Ollama API返回格式: {"message": {"role": "assistant", "content": "..."}}
                if "message" in response_data and response_data["message"]:
                    return response_data["message"].get("content", "Ollama返回了意外的响应格式")
                else:
                    return "Ollama返回了意外的响应格式"
                    
        except Exception as e:
            return f"响应解析失败: {str(e)}"
    
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="快速演示", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 蓝擎大模型安全护栏 vs Ollama直接对话 对比演示")
            
            # 共享输入区域
            with gr.Row():
                msg = gr.Textbox(
                    label="用户消息",
                    placeholder="请输入您的消息...",
                    lines=3,
                    scale=4
                )
                with gr.Column(scale=1):
                    submit_btn = gr.Button("发送", variant="primary", size="lg")
                    clear_btn = gr.Button("清空对话", size="lg")
            
            # 并排聊天框
            with gr.Row():
                # 左侧：安全护栏
                with gr.Column(scale=1):
                    gr.Markdown("## 🛡️ 蓝擎大模型安全护栏")
                    guardrails_chatbot = gr.Chatbot(
                        label="安全护栏对话",
                        height=500,
                        show_copy_button=True
                    )
                
                # 右侧：Ollama
                with gr.Column(scale=1):
                    gr.Markdown("## 🐪 Ollama")
                    ollama_chatbot = gr.Chatbot(
                        label="Ollama对话", 
                        height=500,
                        show_copy_button=True
                    )
            
            # 事件处理
            def dual_respond(message, guardrails_history, ollama_history):
                return self.dual_chat_response(message, guardrails_history, ollama_history)
            
            def clear_both_chats():
                return [], []
            
            # 绑定事件
            msg.submit(
                dual_respond, 
                [msg, guardrails_chatbot, ollama_chatbot], 
                [msg, guardrails_chatbot, ollama_chatbot]
            )
            submit_btn.click(
                dual_respond, 
                [msg, guardrails_chatbot, ollama_chatbot], 
                [msg, guardrails_chatbot, ollama_chatbot]
            )
            clear_btn.click(clear_both_chats, outputs=[guardrails_chatbot, ollama_chatbot])
            
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
            show_error=True
        )
    except KeyboardInterrupt:
        print("\n应用正在关闭...")
    except Exception as e:
        print(f"应用错误: {str(e)}")


if __name__ == "__main__":
    main()
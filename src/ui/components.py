"""
UI Components for Guard AI Security System
"""
import gradio as gr
from typing import List, Callable, Optional


class UIComponents:
    """Factory for creating UI components"""
    
    @staticmethod
    def create_chat_interface() -> tuple:
        """Create chat interface components
        
        Returns:
            Tuple of chat components (use_nemoguardrails, chatbot, msg, submit_btn, clear_btn)
        """
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
            label="用户消息",
            placeholder="请输入您的消息...",
            lines=2
        )
        
        with gr.Row():
            submit_btn = gr.Button("发送", variant="primary")
            clear_btn = gr.Button("清空对话")
        
        return use_nemoguardrails, chatbot, msg, submit_btn, clear_btn
    
    @staticmethod
    def create_log_viewer(log_files: List[str], load_log_callback: Callable) -> tuple:
        """Create log viewer components
        
        Args:
            log_files: List of available log files
            load_log_callback: Callback function to load log content
            
        Returns:
            Tuple of log viewer components (log_dropdown, refresh_btn, log_display)
        """
        with gr.Row():
            log_dropdown = gr.Dropdown(
                label="选择日志文件",
                choices=log_files,
                value=log_files[0] if log_files else None
            )
            refresh_btn = gr.Button("🔄 刷新")
        
        log_display = gr.Textbox(
            label="日志内容",
            lines=25,
            max_lines=30,
            show_copy_button=True,
            interactive=False
        )
        
        # Wire up log loading
        if load_log_callback:
            log_dropdown.change(
                load_log_callback,
                [log_dropdown],
                [log_display]
            )
        
        return log_dropdown, refresh_btn, log_display
    
    @staticmethod
    def create_header() -> tuple:
        """Create header components
        
        Returns:
            Tuple of header markdown components
        """
        title = gr.Markdown("# 🤖 蓝擎安全助手")
        subtitle = gr.Markdown("与蓝擎安全助手对话，支持安全防护模式和直接对话模式，可查看调试日志。")
        debug_header = gr.Markdown("### 📋 调试日志")
        
        return title, subtitle, debug_header
    
    @staticmethod
    def create_layout() -> tuple:
        """Create complete layout structure
        
        Returns:
            Tuple of all layout components
        """
        # Create header
        title, subtitle, debug_header = UIComponents.create_header()
        
        # Create main layout
        with gr.Row():
            with gr.Column(scale=2):
                # Chat interface
                use_nemoguardrails, chatbot, msg, submit_btn, clear_btn = UIComponents.create_chat_interface()
                
            with gr.Column(scale=1):
                # Debug log viewer
                debug_header
                log_dropdown, refresh_btn, log_display = UIComponents.create_log_viewer(
                    log_files=[],  # Will be populated dynamically
                    load_log_callback=None  # Will be set later
                )
        
        return {
            'title': title,
            'subtitle': subtitle,
            'debug_header': debug_header,
            'use_nemoguardrails': use_nemoguardrails,
            'chatbot': chatbot,
            'msg': msg,
            'submit_btn': submit_btn,
            'clear_btn': clear_btn,
            'log_dropdown': log_dropdown,
            'refresh_btn': refresh_btn,
            'log_display': log_display
        }
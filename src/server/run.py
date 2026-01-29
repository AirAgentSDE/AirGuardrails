import os
import signal
import sys
from nemoguardrails.server.api import app
import uvicorn


def signal_handler(sig, frame):
    """信号处理器，用于优雅关闭"""
    print("\nReceived interrupt signal. Shutting down server...")
    sys.exit(0)


def main():
    """主函数：启动NeMo Guardrails服务器"""
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    # 配置NeMo Guardrails
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")
    print(f"NeMo Guardrails配置路径: {config_path}")
    
    # 启动服务器
    print("启动NeMo Guardrails服务器...")
    print("服务器地址: http://0.0.0.0:5070")
    print("按 Ctrl+C 停止服务器")
    app.rails_config_path = config_path
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5070,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
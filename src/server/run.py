import os
import signal
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from nemoguardrails.server.api import app
import uvicorn
from utils.path_utils import PathUtils


def signal_handler(sig, frame):
    """信号处理器，用于优雅关闭"""
    print("\nReceived interrupt signal. Shutting down server...")
    sys.exit(0)


def main():
    """主函数：启动NeMo Guardrails服务器"""
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 配置NeMo Guardrails
    config_path = PathUtils.get_config_dir()
    print(f"NeMo Guardrails配置路径: {config_path}")
    
    # 启动服务器
    print("启动NeMo Guardrails服务器...")
    print("服务器地址: http://127.0.0.1:5070")
    print("按 Ctrl+C 停止服务器")
    app.rails_config_path = config_path
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
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
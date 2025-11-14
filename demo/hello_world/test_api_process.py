import os
import sys
import signal
import subprocess
import time
import requests
from pathlib import Path

def create_server_script():
    """创建独立的服务器脚本"""
    script_content = '''
import os
import sys
from nemoguardrails.server.api import app
import uvicorn

if __name__ == "__main__":
    app.rails_config_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "config"))
    uvicorn.run(app, host="127.0.0.1", port=5070, log_level="info")
'''
    
    script_path = Path(__file__).parent / "standalone_server.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return script_path

def test_api_with_process():
    """使用独立进程运行服务器并测试API"""
    # 创建独立服务器脚本
    server_script = create_server_script()
    
    # 配置参数
    base_url = "http://127.0.0.1:5070"
    max_attempts = 10
    
    server_process = None
    
    try:
        # 启动服务器进程
        server_process = subprocess.Popen(
            [sys.executable, str(server_script)]
        )
        
        print("Starting server...")
        
        # 等待服务器启动
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{base_url}/v1/rails/configs", timeout=2)
                if response.status_code == 200:
                    print("Server started successfully!")
                    print("API Response:")
                    print(response.json())
                    break
            except requests.exceptions.RequestException:
                time.sleep(1)
        else:
            print("Failed to start server")
            return
        
        print("\nServer is running. Press Ctrl+C to stop...")
        
        # 保持运行直到用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nReceived interrupt signal. Shutting down server...")
    finally:
        # 终止服务器进程
        if server_process and server_process.poll() is None:  # 进程仍在运行
            server_process.terminate()
            
            # 等待进程优雅退出
            try:
                server_process.wait(timeout=5)
                print("Server stopped gracefully")
            except subprocess.TimeoutExpired:
                # 强制杀死进程
                server_process.kill()
                print("Server force-killed")
        
        # 清理临时脚本
        if server_script.exists():
            server_script.unlink()

if __name__ == "__main__":
    test_api_with_process()
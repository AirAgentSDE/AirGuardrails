from nemoguardrails import LLMRails, RailsConfig


config_path='demo\hello_world\config'
config = RailsConfig.from_path(config_path=config_path)
rails = LLMRails(config=config)

options = {
    "log": {
        "activated_rails": True,
        "colang_history": True
    }
    }

def generate_response(user_input:str, options:dict) -> list:
    messages=[{
        "role": "user",
        "content": user_input
    }]

    output = rails.generate(messages=messages, options=options)
    print(output)
    return output

# 将log输出日志保存到`log`文件夹下
def save_log(user_input, output_log):
    # 需保存output.response, output.llm_output, output.output_data以及output.log.colang_history
    import json
    import os
    from datetime import datetime
    
    # 确保log目录存在
    log_dir = os.path.join(os.path.dirname(__file__), "log")
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"log_{timestamp}.json")
    
    # 提取需要保存的数据
    log_data = {
        "timestamp": timestamp,
        "user_input": user_input,
        "response": getattr(output_log, 'response', None),
        "llm_output": getattr(output_log, 'llm_output', None),
        "colang_history": None
    }
    
    # 提取colang_history
    if hasattr(output_log, 'log') and hasattr(output_log.log, 'colang_history'):
        log_data["colang_history"] = output_log.log.colang_history
    
    # 保存到JSON文件
    try:
        with open(log_file_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"日志已保存到: {log_file_path}")
    except Exception as e:
        print(f"保存日志时出错: {e}")



if __name__=="__main__":
    usr_input = '当前英伟达的股票是否被高估？'
    output = generate_response(usr_input, options)
    # save_log(usr_input, output)
# Guard 项目 - iFlow 上下文文档

## 项目概述

Guard 是一个基于 NeMo Guardrails 的大模型安全护栏系统，用于为 AI 对话提供内容安全防护。该项目提供了"蓝擎大模型安全护栏体验广场"可视化界面，允许用户在启用或关闭安全护栏的情况下与 AI 模型进行交互，以观察和测试安全防护效果。

### 核心功能

- **安全护栏系统**：基于 NeMo Guardrails 框架，提供多层安全防护
- **可视化体验界面**：使用 Gradio 构建的 Web 界面，支持实时对话
- **灵活的配置管理**：支持多种安全策略配置（幻觉检测、注入防护、内容安全等）
- **日志记录**：自动记录所有对话和响应，便于分析和审计
- **实时护栏切换**：用户可在界面中实时切换是否启用安全护栏

### 技术栈

- **后端框架**：Python + NeMo Guardrails + FastAPI
- **前端界面**：Gradio
- **LLM 服务**：Ollama (使用 qwen3:30b-instruct 模型)
- **服务器**：Uvicorn

## 项目结构

```
E:\guard\
├── .gitignore              # Git 忽略配置
├── AGENTS.md              # 本文档
├── .venv\                 # Python 虚拟环境
└── src\
    ├── app\               # 应用层
    │   ├── gradio_chatbot.py   # Gradio 聊天机器人界面
    │   └── log\               # 日志存储目录
    ├── configs\            # NeMo Guardrails 配置
    │   ├── content_safety_local\   # 内容安全配置
    │   │   ├── config.yml
    │   │   └── prompts.yml
    │   ├── hallucination\          # 幻觉检测配置
    │   │   ├── config.yml
    │   │   ├── prompts.yml
    │   │   └── warn.co
    │   ├── injection\              # 注入防护配置
    │   │   └── config.yml
    │   ├── main\                   # 主配置
    │   │   ├── config.yml
    │   │   ├── prompts.yml
    │   │   └── rails.co
    │   └── self_check\             # 自检配置
    │       ├── config.yml
    │       └── prompts.yml
    ├── server\             # NeMo Guardrails 服务器
    │   └── run.py              # 服务器启动脚本
    └── test\               # 测试脚本
        ├── test_ollama.py     # Ollama API 测试
        └── test_request.py    # Guardrails 请求测试
```

## 构建和运行

### 前置要求

- Python 3.12+ (已在 .venv 中配置)
- Ollama 服务运行在 `http://192.168.101.232:11434`
- qwen3:30b-instruct 模型已下载到 Ollama

### 启动服务

#### 1. 启动 NeMo Guardrails 服务器

```powershell
cd E:\guard
python src/server/run.py
```

服务器将在 `http://0.0.0.0:5070` 启动。

#### 2. 启动 Gradio 界面

```powershell
cd E:\guard
python src/app/gradio_chatbot.py
```

界面将在 `http://0.0.0.0:5071` 启动。

### 运行测试

#### 测试 Ollama 服务

```powershell
cd E:\guard
python src/test/test_ollama.py
```

#### 测试 Guardrails 服务

```powershell
cd E:\guard
python src/test/test_request.py
```

## Colang 编写规范

### 版本说明

本项目使用 **Colang 1.0** 语法（基于 NeMo Guardrails 旧版本）。

⚠️ **注意**：NeMo Guardrails 已升级到 Colang 2.0，新版本移除了 `define` 和 `execute` 关键字。本项目继续使用 Colang 1.0 语法以保持兼容性。

### 基本语法结构

Colang 1.0 使用以下核心关键字：

#### 1. 定义用户意图 (define user)

用于定义用户的输入模式和意图。

```colang
define user <intent_name>
  "示例文本 1"
  "示例文本 2"
  "示例文本 3"
```

**规则**：
- 意图名称使用小写字母
- 每行一个示例文本，用双引号包裹
- 示例文本应覆盖该意图的典型表达方式

**命名约定**（遵循官方建议）：
- 第一个词应该是动词：`ask`、`respond`、`inform`、`provide`、`express`、`comment`、`confirm`、`deny`、`request`
- 其余词应该是名词
- 应该读起来自然（例如：`user ask about investment` 比 `user investment problem` 更好）

#### 2. 定义机器人响应 (define bot)

用于定义机器人的标准响应消息。

```colang
define bot <response_name>
  "响应文本"
```

**规则**：
- 响应名称使用小写字母
- 响应文本应清晰、友好

#### 3. 定义对话流 (define flow)

用于定义对话的交互流程。

```colang
define flow <flow_name>
  user <intent_name>
  bot <response_name>
```

**规则**：
- 流名称使用小写字母
- 每行一个步骤，按顺序执行
- 可以包含多个 `user` 和 `bot` 语句

### 项目中的实际示例

#### 问候流程

```colang
define user express greeting
  "Hello"
  "Hi"
  "你好"
  "在吗"

define bot express greeting
  "您好，我是蓝擎智能助手，请问有什么可以帮到您？" 

define flow
  user express greeting
  bot express greeting
```

#### 专业领域警告

```colang
# 定义警告消息
define bot warn unprofessional advice
  "人工智能生成内容可能存在幻觉，建议咨询专业人士"

# 定义投资咨询意图
define user ask about investment
  "我应该买什么股票？"
  "这个理财产品怎么样？"
  "给我一些投资建议"

# 定义投资咨询流程
define flow investment
  user ask about investment
  bot warn unprofessional advice
```

### 最佳实践

1. **意图命名**：
   - 使用 `user <verb> about <topic>` 格式（如：`user ask about healthcare`）
   - 使用清晰、描述性的名称
   - 避免使用歧义或过于宽泛的名称

2. **示例多样性**：
   - 为每个意图提供 3-5 个不同的示例
   - 覆盖常见的表达方式（正式、口语、中英文等）
   - 示例应具有代表性

3. **响应一致性**：
   - 机器人的响应应保持一致的语调和风格
   - 重要响应（如警告）应定义标准模板
   - 避免重复定义相似的响应

4. **流程清晰性**：
   - 每个流程应专注于单一目的
   - 流程名称应描述其功能
   - 避免过于复杂的嵌套流程

5. **注释使用**：
   - 使用 `#` 添加注释说明流程目的
   - 在复杂逻辑前添加注释
   - 注释应简洁明了

### 语法检查清单

添加或修改 Colang 规则时，请确保：

- [ ] 使用双引号包裹所有文本
- [ ] 每个语句占一行
- [ ] 意图和响应名称使用小写字母和下划线
- [ ] 流定义中的 `user` 和 `bot` 语句对齐
- [ ] 意图示例具有多样性
- [ ] 响应文本清晰友好
- [ ] 添加必要的注释

### 配置文件位置

Colang 规则文件位于：
- 主规则：`src/configs/main/rails.co`
- 幻觉检测：`src/configs/hallucination/warn.co`

### 相关资源

- [NeMo Guardrails 官方文档](https://docs.nvidia.com/nemo/guardrails/latest/)
- [Colang 2.0 迁移指南](https://blog.csdn.net/gitblog_00835/article/details/148523483)
- [项目命名约定参考](https://docs.nvidia.com/nemo/guardrails/latest/resources/glossary.html)

## 开发约定

### 配置管理

- NeMo Guardrails 配置文件位于 `src/configs/` 目录
- 主配置文件：`src/configs/main/config.yml`
- 对话规则：`src/configs/main/rails.co`
- 支持的配置类型：
  - `content_safety_local`：本地内容安全
  - `hallucination`：幻觉检测（包含投资建议等场景的幻觉警告）
  - `injection`：提示注入防护（支持模板注入检测）
  - `self_check`：输出自检

### 代码结构

- **ApiClient**：负责与 NeMo Guardrails 和 Ollama API 通信
  - `request_nemoguardrails()`: 请求 NeMo Guardrails API
  - `request_ollama()`: 请求 Ollama API
- **LogManager**：管理对话日志的存储
  - `save_log()`: 保存对话日志到 JSON 文件
- **ChatbotInterface**：封装 Gradio 界面逻辑
  - `chat_response()`: 处理用户输入并返回响应
  - `create_interface()`: 创建 Gradio 界面
- **main()**：应用入口点

### 服务端点

- NeMo Guardrails API：`http://192.168.101.232:5070/v1/chat/completions`
- NeMo Guardrails 配置：`http://192.168.101.232:5070/v1/rails/configs`
- Ollama API：`http://192.168.101.232:11434/api/chat`
- Gradio 界面：`http://0.0.0.0:5071`

### 安全规则示例

项目包含预定义的安全规则（在 `src/configs/main/rails.co` 中）：
- 问候语处理（支持中英文问候）
- 政治话题拒绝（涉及地区争端、民族仇恨等）
- 拒绝响应的默认消息

### 幻觉检测规则

在 `src/configs/hallucination/warn.co` 中定义：
- 投资建议场景的幻觉警告
- 当检测到可能产生幻觉的内容时，提示用户谨慎参考

### 日志格式

日志以 JSON 格式存储在 `src/app/log/` 目录，包含：
- timestamp：时间戳（格式：YYYYMMDD_HHMMSS）
- service：服务名称（guardrails/ollama）
- user_input：用户输入
- response：AI 响应
- colang_history：Colang 对话历史（仅 guardrails）
- error：错误信息（如有）

### 环境变量

项目使用硬编码的服务地址（在 `src/app/gradio_chatbot.py` 的 `ApiClient` 类中）：
- NeMo Guardrails：`http://192.168.101.232:5070`
- Ollama：`http://192.168.101.232:11434`
- 请求超时：120 秒

如需修改，请在 `ApiClient` 类中更新相应配置。

## Git 信息

- 远程仓库：`https://github.com/avicbj/guard.git`
- 当前分支：包含多个配置文件的修改
- 主要修改：
  - 添加幻觉检测配置（hallucination）
  - 添加注入防护配置（injection）
  - 更新主配置和对话规则
  - 优化界面标题和状态提示

## 常见任务

### 添加新的安全规则

1. 编辑 `src/configs/main/rails.co`
2. 定义用户输入模式（`define user ...`）
3. 定义机器人响应（`define bot ...`）
4. 创建对话流（`define flow ...`）
5. 重启 NeMo Guardrails 服务器

### 修改 LLM 模型

1. 编辑 `src/configs/main/config.yml`
2. 修改 `model` 字段
3. 确保 Ollama 中已下载对应模型

### 修改服务地址

1. 编辑 `src/app/gradio_chatbot.py`
2. 在 `ApiClient` 类中修改 `nemoguardrails_url` 和 `ollama_url`
3. 在 `src/test/test_request.py` 中修改 `base_url`（如需要）

### 查看对话日志

日志文件位于 `src/app/log/` 目录，以 `log_YYYYMMDD_HHMMSS.json` 格式命名。

### 添加新的配置模块

1. 在 `src/configs/` 下创建新目录
2. 添加 `config.yml` 配置文件
3. （可选）添加 `prompts.yml` 和 `.co` 规则文件
4. 在 `src/app/gradio_chatbot.py` 的 `config_ids` 中添加新配置名称
5. 重启 NeMo Guardrails 服务器

## 注意事项

- 确保在修改配置后重启 NeMo Guardrails 服务器
- 日志文件会持续增长，建议定期清理
- 当前配置使用网络地址的 Ollama 服务，需要确保服务可用
- Gradio 界面默认在 debug 模式下运行，生产环境应关闭
- NeMo Guardrails 服务器监听在 `0.0.0.0:5070`，可从外部访问
- Gradio 界面监听在 `0.0.0.0:5071`，可从外部访问
- 项目使用 `Guardrails` 目录存储框架源代码（在 .gitignore 中忽略）
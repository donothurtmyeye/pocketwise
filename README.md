# PocketWise - 智能理财助手 🤖💰

一个专为学生群体设计的智能理财助手，帮助你理性消费、管理预算，避免冲动花钱。

## 📋 项目概述

PocketWise 是一个基于 AI 的个人理财智能助手，专注于帮助学生群体合理管理自己的可支配资金。通过智能对话、数据分析和个性化建议，帮助用户养成良好的消费习惯，实现财务目标。

## ✨ 核心功能

### 💬 智能对话助手
- **意图识别**：自动理解用户的消费咨询、计划制定等需求
- **个性化建议**：基于用户财务状况提供针对性建议
- **友好交互**：温暖、耐心、鼓励性的对话体验

### 📊 财务管理
- **用户档案管理**：记录收入、预算、存款等基本信息
- **支出追踪**：记录和分析消费行为
- **预算控制**：帮助设定和管理月度预算
- **消费分析**：识别消费模式和趋势

### 🎯 计划制定
- **储蓄计划**：帮助制定存款目标和执行计划
- **消费节制**：设定消费限制和提醒
- **进度追踪**：监控计划执行情况

### 🚫 冲动消费干预
- **智能检测**：基于消费金额、描述和用户习惯判断是否为冲动消费
- **及时提醒**：在潜在冲动消费时提供理性建议

### 核心组件

#### 1. 对话流程管理 (`graph.py`)
- **ContextManager**: 上下文管理和消息历史控制
- **IntentRecognizer**: 用户意图识别
- **ChatbotService**: 主对话服务
- **PlanExecutor**: 计划生成和执行
- **ToolExecutor**: 工具调用执行

#### 2. 工具系统 (`tools.py`)
- `view_user_profile`: 查看用户财务档案
- `edit_user_profile`: 编辑用户档案
- `log_notable_expense`: 记录消费
- `view_recent_expenses`: 查看最近支出
- `detect_impulse_buying`: 冲动消费检测
- `log_plan`/`view_plan`/`update_plan`/`delete_plan`: 计划管理

#### 3. 数据存储 (`database.py`)
- **用户档案表**: 存储收入、预算、性格标签等
- **支出记录表**: 消费历史和上下文
- **计划表**: 储蓄和消费计划

#### 4. 提示词系统 (`prompts.py`)
- 意图识别提示词
- 聊天机器人系统提示词
- 计划生成提示词
- 意图指导映射

## 🚀 快速开始

### 环境要求
- Python 3.11 - 3.13
- uv 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <https://github.com/donothurtmyeye/pocketwise.git>
cd PocketWise
```

2. **安装依赖**
```bash
uv sync
```

3. **配置环境变量**

创建 `.env` 文件：
```env
DASHSCOPE_API_KEY=your_qwen_api_key
BASE_URL=https://dashscope.aliyuncs.com/api/v1
```

4. **运行应用**
```bash
uv run python -m src.agent.cli
```

## 📁 项目结构

```
PocketWise/
├── main.py                 # 主入口文件
├── pyproject.toml          # 项目配置
├── requirements.txt        # 依赖列表
├── README.md              # 项目文档
└── src/
    └── agent/
        ├── __init__.py
        ├── cli.py         # 命令行界面
        ├── graph.py       # 对话流程图
        ├── state.py       # 状态定义
        ├── tools.py       # 工具函数
        ├── database.py    # 数据存储
        ├── prompts.py     # 提示词管理
        ├── model.py       # AI 模型配置
        └── env_utils.py   # 环境变量管理
```

## 🔧 配置说明

### 环境变量
- `DASHSCOPE_API_KEY`: 通义千问 API 密钥
- `BASE_URL`: API 基础地址 (默认: https://dashscope.aliyuncs.com/api/v1)

## 🎯 设计理念

### 用户中心设计
- **针对学生群体**：理解学生特殊的财务状况和消费心理
- **渐进式引导**：从基础档案建立到复杂计划制定
- **非 judgmental**：温暖鼓励而非指责批评

### AI 驱动
- **意图理解**：准确识别用户需求和上下文
- **个性化推荐**：基于历史数据提供针对性建议


### 开发环境设置
```bash
# 安装开发依赖
uv sync --dev

# 运行代码检查
uv run ruff check .

# 运行类型检查
uv run mypy .
```

**PocketWise** - 让理财变得简单有趣，让消费变得理性自觉 💪

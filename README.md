<<<<<<< HEAD
# 外贸B端全链路AI自动化获客转化Agent系统  
## 技术对接需求文档（完整版）

---

# 一、项目整体概述

## 1.1 项目名称

**TikTok & 社媒AI智能获客 + 自动化触达 + 智能询盘转化 Agent 系统**

## 1.2 项目目标

基于 **AI Agent + 可插拔 Skill 插件 + 可视化工作流引擎**，实现外贸B端（品牌方、达人、MCN、渠道商）从：

社媒获客 → 数据整理 → 自动触达 → 智能询盘回复 → 客户跟进 → 老板监控与接管  

的全流程无人自动化，替代人工 80% 以上重复性工作，支持 7×24 小时自动化执行。

## 1.3 适用场景

- TikTok / Instagram / Facebook / YouTube 等社媒B端客户挖掘  
- WhatsApp / 邮件自动化开发  
- AI智能接待询盘  
- 销售过程监控  

---

# 二、核心技术架构要求

## 1. AI Agent 主框架

- 支持多任务、多步骤自动化执行  
- 支持 Skill 插件化安装 / 卸载 / 更新  
- 支持工作流可视化编排  

## 2. Skill 技能包模块

- 独立功能封装  
- 可拖拽组合成自动化流程  

## 3. 工作流引擎

- 条件判断  
- 循环  
- 定时  
- 异常重试  
- 中断接管  

## 4. 后台管理系统（老板端）

- 实时监控  
- 对话查看  
- 一键接管  
- 数据统计  

## 5. 第三方接口集成

- 社媒平台  
- 邮箱  
- WhatsApp  
- Excel / 在线表格  
- CRM  

---

# 三、Skill 技能包详细需求（技术开发清单）

---

## Skill 1：社媒B端客户智能挖掘与抓取

### 目标
从 TikTok 等平台自动抓取 B 端客户公开信息。

### 支持平台
- TikTok  
- Instagram  
- YouTube  
- Facebook  

### 抓取目标
- 品牌方  
- 达人  
- MCN机构  
- 批发商  
- 独立站卖家  

### 抓取字段

- 用户名  
- 主页链接  
- 类目 / 行业  
- 粉丝数  
- 主页公开邮箱  
- WhatsApp  
- 电话  
- Instagram  
- Website  
- 国家 / 地区  
- 语言  
- 活跃时间  

### 能力要求

- 关键词 / 类目 / 话题定向挖掘  
- 自动去重  
- 过滤无效信息  
- 支持批量任务  
- 定时任务  
- 翻页自动抓取  
- 反爬策略（IP池、请求间隔、账号池）  

---

## Skill 2：客户数据自动清洗与Excel结构化输出

### 目标
将杂乱数据生成标准化客户表。

### 功能要求

- 自动清洗（去重、补全、格式统一、空值处理）  
- 输出格式：
  - 本地 Excel  
  - 在线表格（Google Sheets / 飞书 / 钉钉）  

### 自动打标签

- 客户类型（达人 / MCN / 品牌 / 批发商）  
- 意向等级  
- 国家  
- 类目  
- 是否带联系方式  

### 输出字段固定模板

=======
# Trade AI Agent - 外贸B端全链路AI自动化获客转化Agent系统

一个基于AI Agent + 可插拔Skill插件 + 可视化工作流引擎的外贸B端自动化获客系统，实现从社媒获客→数据整理→自动触达→智能询盘回复→客户跟进→老板监控的全流程无人自动化。

## 功能特性

### 核心功能

- **社媒智能挖掘** - 从TikTok、Instagram等平台获取B端客户信息
- **数据清洗与结构化** - 自动去重、格式统一、智能打标签
- **话术生成** - AI生成个性化邮件和WhatsApp话术
- **自动化触达** - 支持邮件和WhatsApp多渠道自动发送
- **智能询盘回复** - AI自动识别意图并生成回复
- **RAG 知识库增强** - 基于本地知识库回答客户专业问题
- **老板监控与接管** - 实时监控、一键接管对话
- **数据统计与报表** - 全流程数据可视化

### 技术亮点

- **可插拔Skill架构** - 轻松扩展新的处理能力
- **可视化工作流引擎** - 拖拽式编排业务流程
- **多AI模型支持** - 通义千问、文心一言、OpenAI
- **异步任务队列** - Celery + Redis 实现高性能任务处理
- **实时通信** - WebSocket 支持实时数据推送

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- SQLAlchemy - ORM
- PostgreSQL - 数据库
- Redis - 缓存和消息队列
- Celery - 异步任务处理
- LangGraph - 工作流引擎
- 通义千问/文心一言 - AI模型

### 前端
- Vue 3 - 前端框架
- TypeScript - 类型安全
- Vite - 构建工具
- Element Plus - UI组件库
- Pinia - 状态管理
- ECharts - 数据可视化

### 部署
- Docker & Docker Compose
- Nginx - 反向代理

## 项目结构

```
trade-ai-agent/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── api/                      # API路由
│   │   ├── core/                     # 核心模块
│   │   ├── skills/                   # Skill插件目录
│   │   ├── models/                   # 数据模型
│   │   ├── integrations/             # 第三方集成
│   │   ├── services/                 # 业务服务
│   │   ├── tasks/                    # 异步任务
│   │   └── templates/                # 模板
│   ├── tests/                        # 测试
│   └── requirements.txt
├── frontend/                         # 前端管理面板
│   ├── src/
│   │   ├── api/                     # API调用
│   │   ├── components/              # 组件
│   │   ├── views/                   # 页面
│   │   ├── stores/                  # Pinia状态管理
│   │   └── types/                   # TypeScript类型
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.11+ (本地开发)
- Node.js 20+ (本地开发)

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/trade-ai-agent.git
cd trade-ai-agent
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 3. 使用Docker启动

```bash
docker-compose up -d
```

服务启动后：
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Flower (Celery监控): http://localhost:5555

### 4. 创建管理员账号

```bash
docker-compose exec backend python -c "
from app.db import SessionLocal
from app.api.v1.auth import get_password_hash
from app.models.database import User

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@example.com',
    hashed_password=get_password_hash('admin123'),
    is_superuser=True
)
db.add(admin)
db.commit()
print('Admin user created: username=admin, password=admin123')
"
```

## 本地开发

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL=postgresql://admin:password@localhost:5432/trade_ai
export REDIS_URL=redis://localhost:6379/0

# 运行迁移
python -c "from app.db import init_db; init_db()"

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery worker (另一个终端)
celery -A app.tasks.celery_worker worker --loglevel=info

# 启动Celery beat (另一个终端)
celery -A app.tasks.celery_worker beat --loglevel=info
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 使用说明

### 1. 配置AI模型

在设置页面或`.env`文件中配置你的AI API密钥：
- 通义千问: `TONGYI_API_KEY`
- 文心一言: `QWEN_API_KEY`
- OpenAI: `OPENAI_API_KEY`

### 2. 添加发送账号

在设置 > 账号 中添加你的邮件或WhatsApp账号凭证。

### 3. 创建工作流

1. 进入工作流页面
2. 点击"创建工作流"
3. 从左侧Skill库拖拽节点到画布
4. 配置节点参数
5. 保存工作流

### 4. 执行获客流程

(详细流程说明...)

### 5. RAG 知识库管理

系统内置了 RAG (检索增强生成) 功能，允许你上传公司文档、产品手册或销售话术，AI 在回复客户时会自动参考这些内容。

#### 命令行管理工具

可以使用提供的脚本管理知识库：

```bash
# 激活虚拟环境
cd backend
source venv/bin/activate

# 添加文档到知识库
python scripts/manage_knowledge.py add --text "我们的产品价格是根据数量阶梯定价的，100个以上享受9折优惠。" --source "pricing_policy"

# 验证查询
python scripts/manage_knowledge.py query --text "批量购买有优惠吗？"

# 清空知识库
python scripts/manage_knowledge.py clear
```

添加文档后，`AIReplySkill` 在生成回复时会自动检索相关信息。
>>>>>>> 11cd409 (first init repo)

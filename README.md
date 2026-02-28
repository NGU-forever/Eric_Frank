# Trade AI Agent - 外贸B端全链路AI自动化获客转化Agent系统

## 项目概述

Trade AI Agent 是一个基于AI Agent + 可插拔Skill插件 + 可视化工作流引擎的外贸B端自动化获客系统，实现从社媒获客→数据整理→自动触达→智能询盘回复→客户跟进→老板监控的全流程无人自动化。

## 启动说明书

### 前置要求

- Docker & Docker Compose
- Python 3.11+ (本地开发)
- Node.js 20+ (本地开发)

### 1. 克隆项目

```bash
git clone https://github.com/NGU-forever/Eric_Frank.git
cd Eric_Frank
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
- 前端管理面板: http://localhost:80
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

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

### 5. 配置AI模型

在设置页面或`.env`文件中配置你的AI API密钥：
- 通义千问: `TONGYI_API_KEY`
- 文心一言: `QWEN_API_KEY`
- OpenAI: `OPENAI_API_KEY`

### 6. 添加发送账号

在设置 > 账号 中添加你的邮件或WhatsApp账号凭证。

## Agent系统介绍

### Agent 1: 市场侦察员 (Scout Agent)

**作用**: 负责第一阶段"由面到点精准搜索"

**功能**:
- 调用Google Search API进行全网批量泛搜
- 智能清洗：自动排除B2B平台、广告、黄页等噪音
- 输出高质量目标企业官网列表
- 支持竞对域名对比搜索

**技术实现**:
- 使用Serper API进行Google搜索
- 智能域名过滤算法
- 数据库持久化，状态标记为"Scouted"

### Agent 2: 深度解析器 (Parser Agent)

**作用**: 负责第二阶段"深度解析与穿透"

**功能**:
- 利用Firecrawl解析官网内容，评估业务匹配度
- 调用Apollo/Proxycurl API精准锁定领英上的Key Person
- 通过NeverBounce实时验证商业邮箱与手机号
- 未锁定的数据转入人工池辅助处理

**技术实现**:
- 网站内容解析和业务匹配度评估
- 关键人物定位和信息提取
- 联系信息验证和分类

### Agent 3: 情报研究员 (Researcher Agent)

**作用**: 负责第三阶段"情报调研与1:1定制内容"

**功能**:
- 检索企业近期新闻、动态及财报
- 生成极具个性化的开发信与WhatsApp文案
- 所有情报与文案写入Supabase状态机数据库

**技术实现**:
- 企业情报收集和分析
- AI驱动的个性化内容生成
- 数据持久化和状态管理

### Agent 4: 自动化触达员 (Engager Agent)

**作用**: 负责第四阶段"多渠道自动化触达"

**功能**:
- 通过Instantly API发送首封定制化邮件
- 动态跟进策略：3天内无回复自动触发多渠道策略
- 通过Wati API发送WhatsApp友好跟进信息

**技术实现**:
- 多渠道自动化触达
- 智能跟进策略
- 实时状态监控和调整

### Agent 5: 意向分拣员 (Closer Agent)

**作用**: 负责第五阶段"意向分拣与客服收网"

**功能**:
- 实时监听回复，进行上下文意向分类
- A类(积极)：自动发送Calendly预约链接，飞书/钉钉通知销售
- B类(培育)：标记标签，自动转入CRM长线培育序列
- C类(拒绝)：加入全系统黑名单，停止一切触达

**技术实现**:
- 意向识别和分类
- 自动化后续动作
- CRM集成和状态管理

## 使用流程

1. **配置阶段**: 设置AI模型、发送账号、工作流参数
2. **创建工作流**: 从Skill库拖拽节点到画布，配置参数
3. **执行获客**: 启动工作流，系统自动执行全流程
4. **监控管理**: 通过管理面板实时监控进度和结果
5. **优化调整**: 根据数据反馈调整工作流配置

## 技术特点

- **可插拔Skill架构**: 轻松扩展新的处理能力
- **可视化工作流引擎**: 拖拽式编排业务流程
- **多AI模型支持**: 通义千问、文心一言、OpenAI
- **异步任务队列**: Celery + Redis 实现高性能任务处理
- **实时通信**: WebSocket支持实时数据推送
- **RAG知识库**: 基于本地知识库增强AI回复

## 注意事项

1. 确保所有API密钥正确配置
2. WhatsApp账号需要提前验证
3. 邮件发送需配置正确的SMTP设置
4. 定期检查任务队列状态
5. 监控系统资源使用情况

## 故障排除

- 检查Docker容器状态: `docker-compose ps`
- 查看日志: `docker-compose logs -f`
- 验证API连接: 访问http://localhost:8000/docs
- 检查Celery任务: 访问http://localhost:5555

通过以上步骤，您可以成功启动并运行Trade AI Agent系统，实现外贸B端的自动化获客转化。
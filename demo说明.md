# demo.py 说明文档

## 一、demo.py 是做什么的？

`backend/demo.py` 是一个**完整的 B2B AI 外联管道演示程序**，用于在**无需任何 API 密钥**的情况下，向客户展示 AI 外贸系统中 5 个智能代理（Agent）的端到端工作流程。

### 核心功能

| 功能 | 说明 |
|------|------|
| **演示用途** | 面向客户/内部演示，使用模拟数据完整跑通整个销售外联流程 |
| **零依赖** | 不调用真实 Google、Apollo、Claude、Instantly、Wati 等 API，安全可离线运行 |
| **行业场景** | 以 LED 工业照明行业为例，模拟寻找海外 B2B 分销商并做个性化外联 |

### 5 个智能代理流程

1. **Scout（侦察）** — 通过 Google 搜索发现潜在客户（LED 灯具 B2B 分销商）
2. **Miner（挖掘）** — 抓取企业网站 + 使用 Apollo 获取决策人联系方式
3. **Writer（撰写）** — 用 AI 为每个客户生成个性化开发信和 WhatsApp 文案
4. **Outreach（外联）** — 通过 Instantly（邮件）和 Wati（WhatsApp）发送消息
5. **SDR（销售开发）** — 对客户回复进行意图分类（高意向 / 培育 / 拒绝），并触发相应动作

### 运行方式

```bash
cd /home/shawn/Eric_Frank
python -m backend.demo
```

---

## 二、演示输出（原始运行结果）

以下是 `python -m backend.demo` 的实际终端输出（已去除 ANSI 颜色码）：

```
══════════════════════════════════════════════════════════════
   B2B AI Outreach Pipeline — Live Demo                      
   Product: High-Precision Industrial LED Fixtures            
══════════════════════════════════════════════════════════════

  All 5 AI Agents will run in sequence.
  Watch how the system finds, enriches, and reaches out to leads.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AGENT 1 / 5   Scout — Google Search & Lead Discovery
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Searching Google for B2B distributors of LED fixtures...
  Search query: Find B2B distributors for "LED lighting",
                exclude Alibaba, Made-in-China, -site:competitors

  ✓  [1] Lumex Industrial Lighting GmbH
       → lumex-industrial.de   🇩🇪 Germany
  ✓  [2] NordicLight Distribution AB
       → nordiclight.se   🇸🇪 Sweden
  ✓  [3] Pacific Electrical Wholesale Co.
       → pacificelectrical.com.au   🇦🇺 Australia
  ✓  [4] BrightPath Lighting Solutions Ltd
       → brightpath-lighting.co.uk   🇬🇧 UK
  ✓  [5] AlphaVolt Energy Partners
       → alphavolt.ca   🇨🇦 Canada

  Result: 5 qualified leads found
  Blacklisted domains filtered: alibaba.com, made-in-china.com ...
  All leads saved to DB with status: Scouted

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AGENT 2 / 5   Miner — Website Scrape & Contact Enrichment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scraping each company website + querying Apollo.io for decision makers...

  ▶  Lumex Industrial Lighting GmbH
  Contact :  Klaus Bauer — Head of Procurement
  Email   :  k.bauer@lumex-industrial.de

  ┌─ Company Intel ─────────────────────────────────────┐
  │  Major DACH industrial LED distributor. Recently     │
  │  expanded into smart warehouse lighting. Actively    │
  │  sourcing new OEM suppliers to meet growing demand   │
  │  for high-bay and panel fixtures.                    │
  └──────────────────────────────────────────────────────────┘

  ▶  NordicLight Distribution AB
  Contact :  Anna Lindqvist — Purchasing Manager
  Email   :  anna.lindqvist@nordiclight.se

  ┌─ Company Intel ─────────────────────────────────────┐
  │  Serves Scandinavian retail and hospitality with     │
  │  eco-certified LEDs. Strict quality standards,       │
  │  current focus on dimmable LED strips and panels.    │
  │  Prefers ENEC/RoHS certified products.               │
  └──────────────────────────────────────────────────────────┘

  ▶  Pacific Electrical Wholesale Co.
  Contact :  James Thornton — General Manager
  Email   :  j.thornton@pacificelectrical.com.au

  ┌─ Company Intel ─────────────────────────────────────┐
  │  Top Australian electrical wholesaler with 12        │
  │  branches across NSW & VIC. Supplies lighting to     │
  │  commercial contractors. Looking for competitive     │
  │  pricing on high-bay LED fixtures for large          │
  │  infrastructure projects.                            │
  └──────────────────────────────────────────────────────────┘

  Result: 3 leads fully enriched
  Status updated to: Mined

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AGENT 3 / 5   Writer — AI Personalised Copy (Claude 3.5 Sonnet)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Generating personalised cold email + WhatsApp message per lead...

  ▶  Lumex Industrial Lighting GmbH  (Klaus Bauer)
  Subject  :  30% faster LED supply for Lumex's warehouse projects?

  │  Hi Klaus,
  │  I noticed Lumex recently expanded into smart warehouse lighting
  │  — impressive move given the surge in German logistics infra...
  │  We manufacture ISO 9001-certified LED high-bay fixtures with
  │  a 30% shorter lead time. Would a 15-minute call this week work?
  │  Best regards, Sales Team

  WhatsApp:  Hi Klaus! Saw Lumex is expanding into smart warehouse
             lighting — we make industrial LEDs with 30% faster
             delivery. Worth a quick chat? 💡

  ▶  NordicLight Distribution AB  (Anna Lindqvist)
  Subject  :  ENEC-certified dimmable LEDs for NordicLight's new line?
  │  Hi Anna, NordicLight's focus on eco-certified products caught
  │  my eye — exactly the standard your Scandinavian clients demand...
  │  Happy to send samples this week — would that be helpful?
  │  Best regards, Sales Team

  WhatsApp:  Hi Anna! We make ENEC-certified dimmable LEDs that
             match NordicLight's eco standards. Interested? 🌿

  ▶  Pacific Electrical Wholesale Co.  (James Thornton)
  Subject  :  Bulk LED high-bay pricing for Pacific Electrical's projects?
  │  Hi James, Pacific Electrical's scale across NSW and VIC is
  │  impressive. We supply LED high-bays at bulk pricing with 15-day
  │  delivery, ideal for large infrastructure tenders...
  │  Best regards, Sales Team

  WhatsApp:  Hi James! Bulk LED high-bays with 15-day delivery and
             5yr warranty — great fit for your contractor projects. ⚡

  Result: 3 drafts generated
  Status updated to: Drafted  |  is_approved = False

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⏸  HUMAN REVIEW — Waiting for Manager Approval
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Pipeline paused here.
  Manager reviews the generated copy in the dashboard.
  Call POST /approve_draft to resume.

  [ Simulating manager approval in 2 seconds... ]
  ✓  Draft approved by manager. Pipeline resuming...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AGENT 4 / 5   Outreach — Email + WhatsApp Delivery
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sending approved messages via Instantly (Email) and Wati (WhatsApp)...
  Anti-ban delay: 45–120s between sends (simulated here as 0.5s)

  ▶  Lumex Industrial Lighting GmbH
  📧 Email    :  Sent to k.bauer@lumex-industrial.de   [Instantly API]
  💬 WhatsApp :  Sent to +LUM-XXXXX   [Wati API]

  ▶  NordicLight Distribution AB
  📧 Email    :  Sent to anna.lindqvist@nordiclight.se  [Instantly API]
  💬 WhatsApp :  Sent to +NOR-XXXXX   [Wati API]

  ▶  Pacific Electrical Wholesale Co.
  📧 Email    :  Sent to j.thornton@pacificelectrical.com.au [Instantly API]
  💬 WhatsApp :  Sent to +PAC-XXXXX   [Wati API]

  Result: 3 leads contacted (email + WhatsApp)
  Status updated to: Emailed / WhatsApped
  Daily send counter updated. Limit: 50/day

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AGENT 5 / 5   SDR — Reply Intent Classification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Customer replies are coming in. Classifying each reply...
  A = High intent (quote/meeting/sample)
  B = Nurture (follow up later)
  C = Reject (unsubscribe / not interested)

  ▶  Lumex Industrial GmbH
   "Hi, yes we'd like to get a quote and schedule a call this week."
   → Intent: [A] HIGH INTENT
   → Action: Calendly link sent + Feishu team alert triggered

  ▶  NordicLight Distribution AB
   "Thanks for reaching out. We're reviewing suppliers next quarter
    — follow up then."
   → Intent: [B] NURTURE
   → Action: Tagged for Q2 follow-up sequence

  ▶  Pacific Electrical Wholesale
   "Please remove me from your list. Not interested."
   → Intent: [C] REJECTED
   → Action: Lead blacklisted — removed from pipeline

══════════════════════════════════════════════════════════════
   Pipeline Complete — Summary
══════════════════════════════════════════════════════════════

  Leads Discovered  :  5 companies
  Leads Enriched    :  3 with decision-maker contacts
  Drafts Generated  :  3 personalised emails + WhatsApp
  Messages Sent     :  3 via Email + WhatsApp
  A (High Intent)   :  1 — Calendly sent, team alerted
  B (Nurture)       :  1 — Tagged for Q2 follow-up
  C (Rejected)      :  1 — Blacklisted, pipeline removed

  Full audit trail saved to PostgreSQL database.
  View all leads at: GET /leads

══════════════════════════════════════════════════════════════
```

---

## 三、输出内容中文说明

### 3.1 整体流程说明

演示按照 **Scout → Miner → Writer → 人工审核 → Outreach → SDR** 的顺序依次执行，模拟真实 B2B 外联管道的完整链路。每一步都有停顿，方便边运行边向客户讲解。

---

### 3.2 各阶段输出中文说明

#### ① 开头标题

| 英文输出 | 中文说明 |
|----------|----------|
| B2B AI Outreach Pipeline — Live Demo | 演示标题：B2B AI 外联管道现场演示 |
| Product: High-Precision Industrial LED Fixtures | 演示产品：高精度工业 LED 灯具 |
| All 5 AI Agents will run in sequence | 5 个 AI 代理将依次运行 |
| Watch how the system finds, enriches, and reaches out to leads | 演示系统如何发现、丰富线索并触达客户 |

---

#### ② AGENT 1 — Scout（侦察）

| 英文输出 | 中文说明 |
|----------|----------|
| Searching Google for B2B distributors... | 模拟在 Google 上搜索 LED 灯具的 B2B 分销商 |
| Search query: Find B2B distributors for "LED lighting" | 搜索语句：查找 LED 灯具分销商，并排除阿里巴巴、中国制造等平台 |
| ✓ [1] Lumex Industrial Lighting GmbH 等 | 找到 5 家符合条件的公司：德国 Lumex、瑞典 NordicLight、澳大利亚 Pacific Electrical、英国 BrightPath、加拿大 AlphaVolt |
| Result: 5 qualified leads found | 结果：发现 5 条合格线索 |
| Blacklisted domains filtered | 已过滤黑名单域名（如 alibaba.com、made-in-china.com） |
| All leads saved to DB with status: Scouted | 所有线索已入库，状态为「已侦察」 |

**这一步展示的是：系统如何从零找到潜在客户。** 通过 Google 搜索 + 域名过滤，自动剔除 B2B 平台噪音，只保留真正的企业官网。

---

#### ③ AGENT 2 — Miner（挖掘）

| 英文输出 | 中文说明 |
|----------|----------|
| Scraping each company website + querying Apollo.io | 抓取每家公司的网站，并调用 Apollo.io 查找决策人 |
| Contact : Klaus Bauer — Head of Procurement | 挖到决策人：Klaus Bauer，采购主管 |
| Email : k.bauer@lumex-industrial.de | 获取到其工作邮箱 |
| Company Intel（方框内） | 公司情报：抓取网站后提炼出的公司背景（业务方向、采购需求等） |
| Result: 3 leads fully enriched | 结果：3 条线索完成深度挖掘 |
| Status updated to: Mined | 状态更新为「已挖掘」 |

**这一步展示的是：系统如何拿到决策人的联系方式。** 通过网站抓取 + Apollo 等工具，自动找到 CEO、采购经理等关键联系人及其邮箱。

---

#### ④ AGENT 3 — Writer（撰写）

| 英文输出 | 中文说明 |
|----------|----------|
| Generating personalised cold email + WhatsApp message | 为每个客户生成个性化开发信和 WhatsApp 短消息 |
| Subject : 30% faster LED supply for Lumex's warehouse projects? | 邮件主题：针对 Lumex 业务定制的标题（提到仓库项目、30% 更快交付） |
| │ Hi Klaus, ... │ | 邮件正文：根据 Lumex 的公司情报量身撰写，提及德国物流、高架灯、招标等 |
| WhatsApp: Hi Klaus! Saw Lumex is expanding... | WhatsApp 版本：更简短、口语化，适合即时通讯 |
| Result: 3 drafts generated | 结果：生成 3 份草稿 |
| Status updated to: Drafted \| is_approved = False | 状态为「已起草」，等待人工审核，`is_approved = False` 表示尚未批准 |

**这一步展示的是：系统如何用数据写出有说服力的文案。** AI 根据公司情报和产品卖点，为每家客户生成不同的主题、正文和 WhatsApp 消息，而不是群发统一模板。

---

#### ⑤ HUMAN REVIEW（人工审核）

| 英文输出 | 中文说明 |
|----------|----------|
| Pipeline paused here | 流水线在此暂停 |
| Manager reviews the generated copy in the dashboard | 老板在前端看板中审核生成的文案 |
| Call POST /approve_draft to resume | 调用 `POST /approve_draft` 接口批准后，流程才会继续 |
| [ Simulating manager approval in 2 seconds... ] | 演示中：模拟 2 秒后老板点击批准 |
| ✓ Draft approved by manager. Pipeline resuming... | 草稿已批准，流水线继续执行 |

**这一步展示的是：老板可以在发送前介入审核。** 防止 AI 生成的文案不合适就发出，保证对外沟通质量。

---

#### ⑥ AGENT 4 — Outreach（外联）

| 英文输出 | 中文说明 |
|----------|----------|
| Sending approved messages via Instantly (Email) and Wati (WhatsApp) | 通过 Instantly 发邮件，通过 Wati 发 WhatsApp |
| Anti-ban delay: 45–120s between sends | 防封发：每条消息间隔 45–120 秒随机延迟（演示中压缩为 0.5 秒） |
| 📧 Email : Sent to k.bauer@lumex-industrial.de [Instantly API] | 邮件已发送到 Klaus 的邮箱 |
| 💬 WhatsApp : Sent to +LUM-XXXXX [Wati API] | WhatsApp 已发送（号码脱敏显示为 +LUM-XXXXX） |
| Result: 3 leads contacted (email + WhatsApp) | 结果：3 条线索都完成了邮件 + WhatsApp 双渠道触达 |
| Daily send counter updated. Limit: 50/day | 已更新当日发送计数，日限额 50 封（防封控） |

**这一步展示的是：系统如何自动发送邮件和 WhatsApp。** 使用真实的外联工具（Instantly、Wati），并带有防封策略。

---

#### ⑦ AGENT 5 — SDR（销售开发）

| 英文输出 | 中文说明 |
|----------|----------|
| Customer replies are coming in. Classifying each reply... | 客户开始回复，系统对每条回复进行意图分类 |
| A = High intent \| B = Nurture \| C = Reject | 三类：A 高意向 / B 培育 / C 拒绝 |
| Lumex: "Hi, yes we'd like to get a quote and schedule a call" | Lumex 的回复：明确要报价和预约会议 |
| → Intent: [A] HIGH INTENT | 分类为 A（高意向） |
| → Action: Calendly link sent + Feishu team alert triggered | 动作：发送 Calendly 会议链接，并向飞书群推送提醒 |
| NordicLight: "follow up then" | NordicLight 的回复：下季度再联系 |
| → Intent: [B] NURTURE | 分类为 B（培育） |
| → Action: Tagged for Q2 follow-up sequence | 动作：打上 Q2 跟进标签，进入培育流程 |
| Pacific Electrical: "Please remove me. Not interested" | Pacific Electrical 的回复：明确不感兴趣 |
| → Intent: [C] REJECTED | 分类为 C（拒绝） |
| → Action: Lead blacklisted — removed from pipeline | 动作：拉黑，移出销售管道 |

**这一步展示的是：系统如何智能判断客户意向并自动执行后续动作。** 高意向自动发会议链接并通知团队，培育客户打标签跟进，拒绝客户自动拉黑。

---

#### ⑧ Summary（汇总）

| 英文输出 | 中文说明 |
|----------|----------|
| Leads Discovered : 5 companies | 发现 5 家公司 |
| Leads Enriched : 3 with decision-maker contacts | 其中 3 家完成深度挖掘（拿到决策人） |
| Drafts Generated : 3 personalised emails + WhatsApp | 生成 3 份个性化邮件 + WhatsApp 文案 |
| Messages Sent : 3 via Email + WhatsApp | 发出 3 次双渠道触达 |
| A (High Intent) : 1 — Calendly sent, team alerted | 1 家高意向，已发会议链接并通知团队 |
| B (Nurture) : 1 — Tagged for Q2 follow-up | 1 家培育，已打 Q2 跟进标签 |
| C (Rejected) : 1 — Blacklisted | 1 家拒绝，已拉黑 |
| Full audit trail saved to PostgreSQL database | 全流程审计日志保存在 PostgreSQL 中 |
| View all leads at: GET /leads | 可通过 `GET /leads` 接口查看所有线索 |

---

### 3.3 关键术语对照

| 英文 | 中文 |
|------|------|
| Scout | 侦察 / 线索发现 |
| Miner | 挖掘 / 联系人与公司信息补全 |
| Writer | 撰写 / AI 生成文案 |
| Outreach | 外联 / 邮件 + WhatsApp 发送 |
| SDR (Sales Development Rep) | 销售开发代表 / 回复意图分类 |
| High Intent (A) | 高意向（询价、约会议、要样品） |
| Nurture (B) | 培育（暂不采购，未来跟进） |
| Rejected (C) | 拒绝（明确不感兴趣，需移出管道） |
| Company Intel | 公司情报 / 背景信息 |
| Blacklisted | 拉黑 / 移出销售管道 |
| Lead | 线索 / 潜在客户 |

---

*文档更新时间：2025-03-01*

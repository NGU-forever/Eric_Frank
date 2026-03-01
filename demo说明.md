# backend/demo.py 说明文档

## 一、demo.py 是做什么的？

`backend/demo.py` 是一个**完整的 B2B AI 外联管道演示程序**，用于在**无需任何 API 密钥**的情况下，展示 AI 外贸系统中 5 个智能代理（Agent）的端到端工作流程。

### 核心功能

| 功能 | 说明 |
|------|------|
| **演示用途** | 面向客户/内部演示，使用模拟数据完整跑通整个销售外联流程 |
| **零依赖** | 不调用真实 Google、Apollo、Claude、Instantly、Wati 等 API，安全可离线运行 |
| **行业场景** | 以 LED 工业照明行业为例，模拟寻找海外 B2B 分销商并做个性化外联 |

### 5 个智能代理流程

1. **Scout（侦察）** — 通过“Google 搜索”发现潜在客户（LED 灯具 B2B 分销商）
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
  │  Major DACH industrial LED distributor. Recently       │
  │  expanded into smart warehouse lighting. Actively      │
  │  sourcing new OEM suppliers to meet growing demand for │
  │  high-bay and panel fixtures.                          │
  └──────────────────────────────────────────────────────────┘

  ▶  NordicLight Distribution AB
  Contact :  Anna Lindqvist — Purchasing Manager
  Email   :  anna.lindqvist@nordiclight.se

  ┌─ Company Intel ─────────────────────────────────────┐
  │  Serves Scandinavian retail and hospitality with eco-  │
  │  certified LEDs. Strict quality standards, current     │
  │  focus on dimmable LED strips and panels. Prefers      │
  │  ENEC/RoHS certified products.                         │
  └──────────────────────────────────────────────────────────┘

  ▶  Pacific Electrical Wholesale Co.
  Contact :  James Thornton — General Manager
  Email   :  j.thornton@pacificelectrical.com.au

  ┌─ Company Intel ─────────────────────────────────────┐
  │  Top Australian electrical wholesaler with 12 branches │
  │  across NSW & VIC. Supplies lighting to commercial     │
  │  contractors. Looking for competitive pricing on high- │
  │  bay LED fixtures for large infrastructure projects.   │
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
  │  
  │  I noticed Lumex recently expanded into smart warehouse lighting — impressive move given the surge in German logistics infrastructure investment.
  │  
  │  We manufacture ISO 9001-certified LED high-bay fixtures with a 30% shorter lead time than market average (15 days vs. 21+). Several DACH distributors already use us to win time-sensitive tenders.
  │  
  │  Would a 15-minute call this week work to see if there's a fit?
  │  
  │  Best regards,
  │  Sales Team

  WhatsApp:  Hi Klaus! Saw Lumex is expanding into smart warehouse lighting — we make industrial LEDs with 30% faster delivery. Worth a quick chat? 💡
  ────────────────────────────────────────────────────────
  ▶  NordicLight Distribution AB  (Anna Lindqvist)
  Subject  :  ENEC-certified dimmable LEDs for NordicLight's new line?

  │  Hi Anna,
  │  
  │  NordicLight's focus on eco-certified products caught my eye — exactly the standard your Scandinavian hospitality clients demand.
  │  
  │  Our dimmable LED panel range carries CE, RoHS, and ENEC certification. We also offer private-label packaging under your own brand.
  │  
  │  Happy to send samples this week — would that be helpful?
  │  
  │  Best regards,
  │  Sales Team

  WhatsApp:  Hi Anna! We make ENEC-certified dimmable LEDs that match NordicLight's eco standards. Can send samples this week — interested? 🌿
  ────────────────────────────────────────────────────────
  ▶  Pacific Electrical Wholesale Co.  (James Thornton)
  Subject  :  Bulk LED high-bay pricing for Pacific Electrical's projects?

  │  Hi James,
  │  
  │  Pacific Electrical's scale across NSW and VIC is impressive — especially the volume of commercial contractor work you handle.
  │  
  │  We supply LED high-bay fixtures at bulk pricing with 15-day delivery, ideal for large infrastructure tenders. Our fixtures come with 5-year warranty and local compliance certification.
  │  
  │  Could we schedule a quick call to discuss your upcoming project pipeline?
  │  
  │  Best regards,
  │  Sales Team

  WhatsApp:  Hi James! We supply bulk LED high-bays with 15-day delivery and 5yr warranty — great fit for your contractor projects. Quick chat? ⚡
  ────────────────────────────────────────────────────────
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
  ────────────────────────────────────────────────────────
  ▶  NordicLight Distribution AB
  📧 Email    :  Sent to anna.lindqvist@nordiclight.se   [Instantly API]
  💬 WhatsApp :  Sent to +NOR-XXXXX   [Wati API]
  ────────────────────────────────────────────────────────
  ▶  Pacific Electrical Wholesale Co.
  📧 Email    :  Sent to j.thornton@pacificelectrical.com.au   [Instantly API]
  💬 WhatsApp :  Sent to +PAC-XXXXX   [Wati API]
  ────────────────────────────────────────────────────────

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
  ────────────────────────────────────────────────────────
  ▶  NordicLight Distribution AB
   "Thanks for reaching out. We're reviewing suppliers next quarter — follow up then."

   → Intent: [B] NURTURE
   → Action: Tagged for Q2 follow-up sequence
  ────────────────────────────────────────────────────────
  ▶  Pacific Electrical Wholesale
   "Please remove me from your list. Not interested."

   → Intent: [C] REJECTED
   → Action: Lead blacklisted — removed from pipeline
  ────────────────────────────────────────────────────────

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

演示按照 **Scout → Miner → Writer → 人工审核 → Outreach → SDR** 的顺序依次执行，模拟真实 B2B 外联管道的完整链路。

---

### 3.2 各阶段中文说明

| 阶段 | 输出内容 | 中文说明 |
|------|----------|----------|
| **开头** | B2B AI Outreach Pipeline — Live Demo | 演示标题：B2B AI 外联管道现场演示，产品为工业 LED 灯具 |
| **AGENT 1 - Scout** | 5 个潜在客户被发现 | 通过模拟的 Google 搜索找到 5 家 LED 分销商（德国、瑞典、澳洲、英国、加拿大），排除阿里等平台，线索状态为「已侦察」 |
| **AGENT 2 - Miner** | 3 条线索被深度挖掘 | 为其中 3 家公司抓取网站并获取决策人：Klaus Bauer、Anna Lindqvist、James Thornton，附带公司背景（Company Intel），状态更新为「已挖掘」 |
| **AGENT 3 - Writer** | 3 封个性化邮件 + WhatsApp | AI 为每家客户生成定制化开发信和 WhatsApp 短消息，内容贴合其业务（如仓库照明、环保认证、批发项目），状态为「已起草」 |
| **人工审核** | Pipeline paused here / Draft approved |  pipeline 在此暂停，等待管理员在后台审核文案；审核通过后流程继续（演示中 2 秒后自动通过） |
| **AGENT 4 - Outreach** | 3 条线索被联系 | 通过 Instantly 发送邮件、通过 Wati 发送 WhatsApp，每条线索都完成双渠道触达，并遵守防封发的发送间隔 |
| **AGENT 5 - SDR** | 3 条回复被分类 | Lumex 表示要报价和预约会议 → **高意向 (A)**；NordicLight 表示下季度再联系 → **培育 (B)**；Pacific Electrical 明确拒绝 → **拒绝 (C)** |
| **总结** | Pipeline Complete — Summary | 汇总：发现 5 家、深度挖掘 3 家、生成 3 份草稿、发出 3 次外联；高意向 1 家、培育 1 家、拒绝 1 家；全程记录保存在 PostgreSQL，可通过 `GET /leads` 查询 |

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

---

*文档生成时间：2025-03-01*

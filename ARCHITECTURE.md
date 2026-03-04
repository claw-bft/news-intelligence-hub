# 新闻情报聚合系统 - 产品架构设计

## 核心愿景
构建一个自动化、多维度的新闻沉淀与聚合平台，通过时间维度榜单 + 语义关联网络，帮助用户快速把握信息脉络。

---

## 时间维度榜单体系

### 1. 实时榜单（小时级）
- **更新频率**: 每30分钟
- **数据量**: 最近24小时
- **核心指标**: 
  - 热度分 = 传播速度 × 权威源权重 × 情感极性
  - 突发度 = 同比前一时段增长倍数
- **展示**: 滚动热榜 + 突发标签

### 2. 日榜
- **更新频率**: 每日 00:00/12:00
- **数据量**: 当日0-24时
- **核心指标**:
  - 日热度 = Σ(小时热度 × 时间衰减因子)
  - 持久度 = 持续出现在小时榜的时长
- **展示**: TOP 20 + 分类子榜

### 3. 周榜
- **更新频率**: 每周一 00:00
- **数据量**: 近7天
- **核心指标**:
  - 周热度 = 日热度加权平均 + 跨天延续性奖励
  - 影响力 = 引发后续报道的数量
- **展示**: 周度大事记时间轴

### 4. 月榜
- **更新频率**: 每月1日
- **数据量**: 近30天
- **核心指标**:
  - 月度热度 = 周热度趋势积分
  - 里程碑标记 = 重大政策/事件节点
- **展示**: 月度关键词云 + 趋势曲线

### 5. 年度榜单
- **更新频率**: 每年1月1日
- **数据量**: 全年
- **核心指标**:
  - 年度影响力 = 跨月持续性 + 历史引用次数
  - 领域突破 = 技术/政策/社会变革标记
- **展示**: 年度十大事件 + 领域专题

---

## 新闻关联度系统

### 关联维度

| 维度 | 算法 | 权重 |
|------|------|------|
| **语义相似** | BERT embeddings + 余弦相似度 | 40% |
| **时间邻近** | 发布时间在24h内 | 20% |
| **实体共现** | 共享关键词/人名/地名/机构 | 25% |
| **因果推断** | 事件序列分析（A发生后B发生） | 10% |
| **情感共振** | 情感极性一致性 | 5% |

### 关联强度分级
- **强关联** (0.8-1.0): 同一事件的不同报道
- **中关联** (0.5-0.8): 相关事件/背景关联
- **弱关联** (0.3-0.5): 主题相近/行业相关
- **无关联** (<0.3): 独立事件

### 关联可视化
- **力导向图**: 节点=新闻，边=关联强度
- **时间轴簇**: 同一事件的时间演进
- **主题河流**: 话题热度随时间流动

---

## 数据沉淀架构

### 存储分层

```
┌─────────────────────────────────────────────────┐
│  L1: 热数据 (Redis)                              │
│  - 当前小时榜单                                  │
│  - 实时关联计算                                  │
│  TTL: 24h                                       │
├─────────────────────────────────────────────────┤
│  L2: 温数据 (PostgreSQL)                         │
│  - 日/周榜单                                     │
│  - 新闻全文 + 元数据                             │
│  - 关联关系表                                    │
├─────────────────────────────────────────────────┤
│  L3: 冷数据 (对象存储)                            │
│  - 月/年榜单归档                                 │
│  - 原始抓取数据                                  │
│  - 历史关联网络快照                              │
└─────────────────────────────────────────────────┘
```

### 数据模型

```sql
-- 新闻表
CREATE TABLE news (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    source VARCHAR(100),
    published_at TIMESTAMP,
    category VARCHAR(50),
    heat_score FLOAT,
    impact_social INT,  -- 0-100
    impact_economic INT,
    impact_political INT,
    impact_tech INT,
    embedding VECTOR(768),  -- 语义向量
    created_at TIMESTAMP DEFAULT NOW()
);

-- 关联表
CREATE TABLE news_relations (
    source_id UUID REFERENCES news(id),
    target_id UUID REFERENCES news(id),
    relation_type VARCHAR(50),  -- semantic/temporal/entity/causal
    strength FLOAT,  -- 0-1
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (source_id, target_id)
);

-- 榜单表
CREATE TABLE rankings (
    id UUID PRIMARY KEY,
    rank_type VARCHAR(20),  -- hour/day/week/month/year
    rank_date DATE,
    news_id UUID REFERENCES news(id),
    rank_position INT,
    heat_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 定时任务调度

```yaml
# cron-jobs.yaml
jobs:
  # 实时抓取
  - name: news-scraper
    schedule: "*/30 * * * *"  # 每30分钟
    task: scrape_news
    
  # 小时榜单
  - name: hourly-ranking
    schedule: "0 * * * *"  # 每小时
    task: generate_hourly_ranking
    
  # 日榜
  - name: daily-ranking
    schedule: "0 0,12 * * *"  # 每天 00:00, 12:00
    task: generate_daily_ranking
    
  # 周榜
  - name: weekly-ranking
    schedule: "0 0 * * 1"  # 每周一 00:00
    task: generate_weekly_ranking
    
  # 月榜
  - name: monthly-ranking
    schedule: "0 0 1 * *"  # 每月1日 00:00
    task: generate_monthly_ranking
    
  # 年榜
  - name: yearly-ranking
    schedule: "0 0 1 1 *"  # 每年1月1日 00:00
    task: generate_yearly_ranking
    
  # 关联计算
  - name: relation-analysis
    schedule: "*/30 * * * *"  # 每30分钟
    task: analyze_news_relations
    
  # 数据归档
  - name: data-archival
    schedule: "0 2 * * *"  # 每天 02:00
    task: archive_old_data
```

---

## 前端展示规划

### 页面结构

```
/
├── /                    # 首页 - 实时热榜
├── /hourly              # 小时榜单
├── /daily               # 日榜
├── /weekly              # 周榜
├── /monthly             # 月榜
├── /yearly              # 年度榜单
├── /news/{id}           # 单条新闻详情
├── /topic/{topic_id}    # 话题聚合页
└── /search              # 搜索页
```

### 核心组件

1. **热榜卡片**
   - 排名 + 热度趋势箭头
   - 标题 + 摘要
   - 分类标签
   - 关联新闻数量

2. **关联网络图**
   - D3.js 力导向图
   - 节点大小 = 热度
   - 边粗细 = 关联强度
   - 点击展开详情

3. **时间轴**
   - 垂直/水平双模式
   - 事件聚类显示
   - 缩放筛选

4. **对比视图**
   - 多新闻并列对比
   - 关联路径高亮

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js + D3.js + ECharts |
| 后端 | Python FastAPI |
| 数据库 | PostgreSQL + pgvector |
| 缓存 | Redis |
| 存储 | MinIO / S3 |
| 调度 | APScheduler / Celery |
| 部署 | Docker + GitHub Actions |

---

## 里程碑

- **M1 (1周)**: 小时榜单 + 基础关联
- **M2 (2周)**: 日/周榜单 + 关联可视化
- **M3 (3周)**: 月/年榜单 + 历史归档
- **M4 (4周)**: 搜索 + 个性化推荐

---

*设计文档版本: v1.0*
*创建时间: 2026-03-04*

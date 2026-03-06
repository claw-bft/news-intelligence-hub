# 美伊冲突监控 - GitHub Pages 部署指南

## 📦 部署包内容

已生成部署包: `iran-conflict-monitor-deploy.tar.gz`

包含文件:
- `index.html` - 美伊冲突监控仪表板
- `data.json` - 实时冲突数据
- `iran_monitor.py` - 数据抓取脚本
- `config-iran.json` - 配置文件

## 🚀 部署步骤

### 方法: 使用 GitHub Pages 部署技能

由于当前环境网络限制，请按以下步骤手动部署:

#### 1. 准备工作
```bash
# 解压部署包
tar -xzf iran-conflict-monitor-deploy.tar.gz
cd deploy-iran
```

#### 2. 创建 GitHub 仓库
```bash
# 使用 GitHub CLI 创建仓库
gh repo create iran-conflict-monitor --public --description "美伊冲突实时监控仪表板"

# 或使用网页创建:
# 访问 https://github.com/new
```

#### 3. 推送到 gh-pages 分支
```bash
# 初始化仓库
git init
git remote add origin https://github.com/YOUR_USERNAME/iran-conflict-monitor.git

# 创建 gh-pages 分支
git checkout --orphan gh-pages

# 添加文件
git add -A
git commit -m "Initial deploy"

# 推送
git push origin gh-pages --force
```

#### 4. 启用 GitHub Pages
```bash
# 使用 GitHub CLI 启用 Pages
gh api repos/YOUR_USERNAME/iran-conflict-monitor/pages --method POST \
  -f source[branch]=gh-pages \
  -f source[path]=/

# 或在网页设置:
# Settings -> Pages -> Source -> Deploy from a branch -> gh-pages
```

#### 5. 访问地址
部署完成后，访问:
```
https://YOUR_USERNAME.github.io/iran-conflict-monitor/
```

---

## 📊 仪表板功能

### 实时数据展示
- 冲突等级: 高/中/低
- 伤亡统计: 伊朗/以色列/平民
- 油价动态: 布伦特/WTI
- 军事事件计数

### 可视化组件
- 新闻时间线 (按类别分类)
- 影响维度雷达图 (军事/外交/经济/人道)
- 事件关联网络图 (D3.js 力导向图)
- 市场影响面板

### 预警系统
- 高风险事件自动标红
- 关键窗口期提醒
- 多维度影响评估

---

## 🔧 自动更新配置

### 设置定时任务
```bash
# 编辑 crontab
crontab -e

# 每10分钟抓取一次数据
*/10 * * * * cd /path/to/deploy-iran && python3 iran_monitor.py

# 每小时部署一次更新
0 * * * * cd /path/to/deploy-iran && bash deploy.sh
```

### 数据更新流程
1. `iran_monitor.py` 抓取最新新闻
2. 生成 `data.json` 数据文件
3. 推送到 GitHub Pages
4. 仪表板自动加载新数据

---

## 🌐 访问链接

部署完成后，可通过以下地址访问:

| 环境 | 地址 |
|------|------|
| GitHub Pages | `https://YOUR_USERNAME.github.io/iran-conflict-monitor/` |
| 本地预览 | `file:///path/to/deploy-iran/index.html` |

---

## 📱 移动端支持

仪表板采用响应式设计，支持:
- iOS Safari
- Android Chrome
- 微信内置浏览器

---

## 🔗 相关资源

- 主技能: `news-intelligence-hub`
- 配置文件: `config-iran.json`
- 部署脚本: `deploy-github-pages.py`
- 数据格式: 兼容 news-intelligence-hub 标准

---

*生成时间: 2026-03-05 13:55*  
*基于 news-intelligence-hub 技能框架*

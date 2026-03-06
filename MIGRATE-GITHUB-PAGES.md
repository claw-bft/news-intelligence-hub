# 新闻情报仪表板 - GitHub Pages 迁移指南

## 🚀 迁移状态

由于当前环境网络限制，自动部署遇到超时。以下是手动迁移步骤，请按指引完成迁移。

---

## 📦 部署包信息

- **文件名**: `news-intelligence-hub-github-pages.tar.gz`
- **大小**: 15KB
- **内容**:
  - `index.html` - 主页面
  - `dashboard.html` - 仪表板页面
  - `data.json` - 新闻数据
  - `.nojekyll` - 禁用 Jekyll 处理（重要）

---

## 🔧 手动迁移步骤

### 步骤 1: 解压部署包

```bash
# 在本地解压
cd /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub
tar -xzf news-intelligence-hub-github-pages.tar.gz
cd github-pages-deploy
ls -la
```

### 步骤 2: 推送到 GitHub

```bash
# 克隆你的仓库（替换 YOUR_USERNAME）
git clone https://github.com/YOUR_USERNAME/news-intelligence-hub.git
cd news-intelligence-hub

# 创建并切换到 gh-pages 分支
git checkout --orphan gh-pages

# 删除所有文件（保留 .git）
git rm -rf .

# 复制部署包文件
cp /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub/github-pages-deploy/* .

# 添加 .nojekyll 文件（重要！禁用 Jekyll）
touch .nojekyll

# 提交
git add -A
git commit -m "Migrate from Vercel to GitHub Pages"

# 推送
git push origin gh-pages --force
```

### 步骤 3: 启用 GitHub Pages

**方法一：使用 GitHub CLI**
```bash
gh api repos/YOUR_USERNAME/news-intelligence-hub/pages --method POST \
  -f source[branch]=gh-pages \
  -f source[path]=/
```

**方法二：网页设置**
1. 打开仓库页面: `https://github.com/YOUR_USERNAME/news-intelligence-hub`
2. 点击 **Settings** 标签
3. 左侧菜单选择 **Pages**
4. **Source** 选择 `Deploy from a branch`
5. **Branch** 选择 `gh-pages` / `/(root)`
6. 点击 **Save**

---

## 🌐 访问地址

部署完成后，访问以下地址：

```
https://YOUR_USERNAME.github.io/news-intelligence-hub/
```

例如：
- 主页面: `https://claw-bft.github.io/news-intelligence-hub/`
- 仪表板: `https://claw-bft.github.io/news-intelligence-hub/dashboard.html`

---

## ⚠️ 重要提示

### 1. .nojekyll 文件
**必须**包含 `.nojekyll` 文件，否则 GitHub Pages 会忽略以 `_` 开头的文件和目录，导致 D3.js 等库无法加载。

### 2. 数据更新
迁移后，需要修改数据更新脚本，将推送目标从 Vercel 改为 GitHub：

```bash
# 原 Vercel 部署命令
# vercel --prod

# 新 GitHub Pages 更新命令
git checkout gh-pages
git pull origin gh-pages
cp data.json .
git add data.json
git commit -m "Update data: $(date)"
git push origin gh-pages
```

### 3. 定时任务更新
修改定时任务配置：

```bash
# 编辑定时任务
crontab -e

# 每30分钟更新数据并推送到 GitHub Pages
*/30 * * * * cd /path/to/news-intelligence-hub && bash update-and-deploy.sh
```

---

## 🔄 更新脚本

创建 `update-and-deploy.sh`：

```bash
#!/bin/bash
set -e

cd /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub

# 1. 抓取最新数据
python3 engine.py

# 2. 切换到 gh-pages 分支
git checkout gh-pages

# 3. 复制新数据
cp data.json .

# 4. 提交并推送
git add data.json
git commit -m "Update data: $(date '+%Y-%m-%d %H:%M')" || true
git push origin gh-pages

echo "✅ 数据已更新到 GitHub Pages"
```

---

## 📊 迁移前后对比

| 项目 | Vercel | GitHub Pages |
|:---|:---|:---|
| 访问地址 | `*.vercel.app` | `*.github.io` |
| 部署方式 | CLI 自动 | Git 推送 |
| 更新频率 | 实时 | 5-10分钟缓存 |
| 自定义域名 | 支持 | 支持 |
| 构建限制 | 无 | 1GB 仓库限制 |
| 服务器端 | 支持 | 纯静态 |

---

## ✅ 验证清单

迁移完成后，请检查：

- [ ] 页面能正常访问（无 404）
- [ ] 数据文件 `data.json` 可正常加载
- [ ] D3.js 图表正常显示
- [ ] 移动端适配正常
- [ ] 定时更新任务正常工作

---

## 🆘 常见问题

### Q1: 页面显示 404
**解决**: 检查 Settings -> Pages 是否已启用，分支是否正确选择 `gh-pages`

### Q2: 图表不显示
**解决**: 确认 `.nojekyll` 文件存在，检查浏览器控制台是否有 JS 错误

### Q3: 数据未更新
**解决**: GitHub Pages 有 5-10 分钟缓存，或强制刷新 `Ctrl+Shift+R`

---

**迁移时间**: 2026-03-05  
**原平台**: Vercel  
**目标平台**: GitHub Pages  
**部署包**: `news-intelligence-hub-github-pages.tar.gz`

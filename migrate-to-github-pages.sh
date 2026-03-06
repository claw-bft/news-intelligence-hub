#!/bin/bash
# 新闻情报仪表板 - GitHub Pages 迁移脚本
# 从 Vercel 迁移到 GitHub Pages

set -e

REPO_NAME="news-intelligence-hub"
REPO_OWNER="claw-bft"
WORK_DIR="/tmp/gh-pages-news-intel"

echo "🚀 开始迁移新闻情报仪表板到 GitHub Pages..."
echo "📦 源项目: $REPO_OWNER/$REPO_NAME"
echo ""

# 步骤 1: 准备构建文件
echo "[1/5] 准备构建文件..."
cd /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub

# 确保 dist 目录存在并包含最新文件
mkdir -p dist
cp index.html dist/
cp dashboard.html dist/
cp data.json dist/

# 创建 .nojekyll 文件（禁用 Jekyll 处理）
touch dist/.nojekyll

echo "✅ 构建文件准备完成"
echo ""

# 步骤 2: 克隆仓库
echo "[2/5] 克隆 GitHub 仓库..."
rm -rf $WORK_DIR
mkdir -p $WORK_DIR
cd $WORK_DIR

gh repo clone $REPO_OWNER/$REPO_NAME . 2>&1 || {
    echo "❌ 克隆失败，请检查仓库是否存在"
    exit 1
}

echo "✅ 仓库克隆完成"
echo ""

# 步骤 3: 创建/切换 gh-pages 分支
echo "[3/5] 准备 gh-pages 分支..."
if git branch -a | grep -q "gh-pages"; then
    echo "🌿 切换到现有 gh-pages 分支..."
    git checkout gh-pages
    # 清空现有文件（保留 .git）
    find . -maxdepth 1 ! -name '.git' ! -name '.' -exec rm -rf {} + 2>/dev/null || true
else
    echo "🌿 创建新的 gh-pages 分支..."
    git checkout --orphan gh-pages
    git rm -rf . 2>/dev/null || true
fi

echo "✅ gh-pages 分支准备完成"
echo ""

# 步骤 4: 复制文件
echo "[4/5] 复制构建文件到 gh-pages..."
cp -r /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub/dist/* .

# 验证文件
if [ ! -f "index.html" ]; then
    echo "❌ index.html 不存在"
    exit 1
fi

echo "✅ 文件复制完成"
echo "   - index.html"
echo "   - dashboard.html"
echo "   - data.json"
echo "   - .nojekyll"
echo ""

# 步骤 5: 提交并推送
echo "[5/5] 提交并推送到 GitHub..."
git config user.email "deploy@github.com"
git config user.name "GitHub Deploy"
git add -A
git commit -m "Migrate from Vercel to GitHub Pages - $(date '+%Y-%m-%d %H:%M')" --allow-empty || true

# 推送
git push origin gh-pages --force || {
    echo "❌ 推送失败"
    exit 1
}

echo "✅ 推送完成"
echo ""

# 步骤 6: 启用 GitHub Pages
echo "🔧 检查 GitHub Pages 状态..."
gh api repos/$REPO_OWNER/$REPO_NAME/pages >/dev/null 2>&1 || {
    echo "📝 启用 GitHub Pages..."
    gh api repos/$REPO_OWNER/$REPO_NAME/pages --method POST \
        -f source[branch]=gh-pages \
        -f source[path]=/ 2>/dev/null || {
        echo "⚠️  自动启用失败，请手动在仓库设置中启用 Pages"
    }
}

echo ""
echo "========================================"
echo "✅ 迁移完成!"
echo "========================================"
echo ""
echo "🌐 新的 GitHub Pages 地址:"
echo "   https://$REPO_OWNER.github.io/$REPO_NAME/"
echo ""
echo "📋 访问路径:"
echo "   - 主页面: https://$REPO_OWNER.github.io/$REPO_NAME/"
echo "   - 仪表板: https://$REPO_OWNER.github.io/$REPO_NAME/dashboard.html"
echo ""
echo "⏰ 部署时间: $(date)"
echo "📝 分支: gh-pages"
echo ""
echo "⚠️  注意:"
echo "   1. DNS 解析可能需要 5-10 分钟生效"
echo "   2. 如果页面显示 404，请检查仓库 Settings -> Pages 是否已启用"
echo "   3. 原 Vercel 地址将在下次部署后失效"
echo "========================================"

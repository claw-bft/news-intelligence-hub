#!/bin/bash
# 美伊冲突监控 GitHub Pages 部署脚本 - 使用现有仓库

set -e

REPO_NAME="news-intelligence-hub"
REPO_OWNER="claw-bft"
DIST_DIR="dist-iran"
WORK_DIR="/tmp/gh-deploy-iran"

echo "🚀 开始部署美伊冲突监控到 GitHub Pages..."

# 清理工作目录
rm -rf $WORK_DIR
mkdir -p $WORK_DIR
cd $WORK_DIR

# 克隆仓库
echo "📦 克隆仓库..."
gh repo clone $REPO_OWNER/$REPO_NAME .

# 创建 gh-pages 分支（如果不存在）
echo "🌿 准备 gh-pages 分支..."
if git branch -a | grep -q "gh-pages"; then
    git checkout gh-pages
else
    git checkout --orphan gh-pages
    git rm -rf . 2>/dev/null || true
fi

# 清空目录（保留 .git）
find . -maxdepth 1 ! -name '.git' ! -name '.' -exec rm -rf {} + 2>/dev/null || true

# 复制构建文件
echo "📋 复制构建文件..."
cp -r /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub/$DIST_DIR/* .

# 创建子目录结构
mkdir -p iran-monitor
cp -r /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub/$DIST_DIR/* iran-monitor/

# 提交并推送
echo "⬆️ 推送到 GitHub..."
git add -A
git config user.email "deploy@github.com"
git config user.name "GitHub Deploy"
git commit -m "Deploy Iran Conflict Monitor - $(date '+%Y-%m-%d %H:%M')" --allow-empty || true
git push origin gh-pages --force

# 启用 GitHub Pages
echo "🔧 检查 GitHub Pages 状态..."
gh api repos/$REPO_OWNER/$REPO_NAME/pages >/dev/null 2>&1 || {
    echo "启用 GitHub Pages..."
    gh api repos/$REPO_OWNER/$REPO_NAME/pages --method POST \
        -f source[branch]=gh-pages \
        -f source[path]=/ 2>/dev/null || echo "Pages 可能已启用或需要手动开启"
}

# 获取 Pages URL
PAGES_URL="https://$REPO_OWNER.github.io/$REPO_NAME/"
IRAN_URL="https://$REPO_OWNER.github.io/$REPO_NAME/iran-monitor/"
echo ""
echo "✅ 部署完成!"
echo "🌐 主访问地址: $PAGES_URL"
echo "🌐 美伊冲突监控: $IRAN_URL"
echo ""
echo "⏰ 部署时间: $(date)"

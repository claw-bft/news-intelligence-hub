#!/bin/bash
# 部署到 claw-bft/news-intelligence-hub 的 GitHub Pages
# 带重试机制

set -e

REPO_NAME="news-intelligence-hub"
REPO_OWNER="claw-bft"
WORK_DIR="/tmp/gh-pages-deploy-retry"
MAX_RETRIES=3
RETRY_DELAY=10

echo "🚀 部署到 $REPO_OWNER/$REPO_NAME 的 GitHub Pages"
echo "📦 带重试机制 (最多 $MAX_RETRIES 次)"
echo ""

# 准备构建文件
echo "[1/4] 准备构建文件..."
cd /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub

# 创建干净的构建目录
rm -rf $WORK_DIR
mkdir -p $WORK_DIR/dist
cp index.html $WORK_DIR/dist/
cp dashboard.html $WORK_DIR/dist/
cp data.json $WORK_DIR/dist/
touch $WORK_DIR/dist/.nojekyll

echo "✅ 构建文件准备完成"
echo ""

# 克隆仓库（带重试）
echo "[2/4] 克隆仓库..."
attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    echo "  尝试 $attempt/$MAX_RETRIES..."
    
    cd $WORK_DIR
    rm -rf repo
    mkdir repo
    cd repo
    
    if git clone https://github.com/$REPO_OWNER/$REPO_NAME.git . 2>&1; then
        echo "  ✅ 克隆成功"
        break
    else
        echo "  ❌ 克隆失败"
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "  ⏳ ${RETRY_DELAY}秒后重试..."
            sleep $RETRY_DELAY
        fi
    fi
    
    attempt=$((attempt + 1))
done

if [ $attempt -gt $MAX_RETRIES ]; then
    echo "❌ 克隆失败，已达到最大重试次数"
    exit 1
fi

echo ""

# 准备 gh-pages 分支
echo "[3/4] 准备 gh-pages 分支..."
cd $WORK_DIR/repo

if git branch -a | grep -q "gh-pages"; then
    echo "  🌿 切换到现有 gh-pages 分支..."
    git checkout gh-pages
    find . -maxdepth 1 ! -name '.git' ! -name '.' -exec rm -rf {} + 2>/dev/null || true
else
    echo "  🌿 创建新的 gh-pages 分支..."
    git checkout --orphan gh-pages
    git rm -rf . 2>/dev/null || true
fi

echo "  ✅ gh-pages 分支准备完成"
echo ""

# 复制文件
echo "[4/4] 复制文件并推送..."
cp -r $WORK_DIR/dist/* .

git config user.email "deploy@github.com"
git config user.name "GitHub Deploy"
git add -A

# 提交（带重试）
attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    echo "  提交尝试 $attempt/$MAX_RETRIES..."
    
    if git commit -m "Deploy to GitHub Pages - $(date '+%Y-%m-%d %H:%M')" --allow-empty 2>&1; then
        echo "  ✅ 提交成功"
        break
    else
        echo "  ⚠️  提交可能为空或失败"
        break
    fi
    
    attempt=$((attempt + 1))
done

# 推送（带重试）
echo ""
echo "  推送到 GitHub..."
attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    echo "  推送尝试 $attempt/$MAX_RETRIES..."
    
    if git push origin gh-pages --force 2>&1; then
        echo "  ✅ 推送成功"
        break
    else
        echo "  ❌ 推送失败"
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "  ⏳ ${RETRY_DELAY}秒后重试..."
            sleep $RETRY_DELAY
        fi
    fi
    
    attempt=$((attempt + 1))
done

if [ $attempt -gt $MAX_RETRIES ]; then
    echo "❌ 推送失败，已达到最大重试次数"
    exit 1
fi

echo ""

# 启用 GitHub Pages
echo "🔧 检查 GitHub Pages 状态..."
gh api repos/$REPO_OWNER/$REPO_NAME/pages >/dev/null 2>&1 || {
    echo "  📝 启用 GitHub Pages..."
    gh api repos/$REPO_OWNER/$REPO_NAME/pages --method POST \
        -f source[branch]=gh-pages \
        -f source[path]=/ 2>/dev/null || {
        echo "  ⚠️  自动启用失败，请手动在仓库设置中启用"
    }
}

echo ""
echo "========================================"
echo "✅ 部署完成!"
echo "========================================"
echo ""
echo "🌐 GitHub Pages 地址:"
echo "   https://$REPO_OWNER.github.io/$REPO_NAME/"
echo ""
echo "📋 访问路径:"
echo "   - 主页面: https://$REPO_OWNER.github.io/$REPO_NAME/"
echo "   - 仪表板: https://$REPO_OWNER.github.io/$REPO_NAME/dashboard.html"
echo ""
echo "⏰ 部署时间: $(date)"
echo "========================================"

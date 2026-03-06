# GitHub Pages 部署技能

## 功能
将新闻情报可视化仪表板部署到 GitHub Pages 静态站点

## 使用方法

### 命令行
```bash
python scripts/deploy-github-pages.py --dist ./dist --repo owner/repo
```

### 参数
- `--dist`: 构建输出目录（默认: dist）
- `--repo`: GitHub 仓库名（格式: owner/repo）
- `--work-dir`: 临时工作目录（默认: /tmp/gh-pages-deploy）

### 示例
```bash
# 部署到 claw-bft/news-intelligence-hub
python scripts/deploy-github-pages.py \
  --dist ./dist \
  --repo claw-bft/news-intelligence-hub
```

## 前置要求
1. GitHub CLI 已安装并认证: `gh auth login`
2. 仓库已存在且有写权限
3. 构建输出目录包含 index.html 和必要资源

## 部署流程
1. 克隆目标仓库
2. 创建/切换到 gh-pages 分支
3. 复制构建文件
4. 提交并强制推送到 gh-pages
5. 启用 GitHub Pages（如未启用）
6. 返回访问 URL

## 访问地址
部署成功后可通过以下地址访问：
```
https://[username].github.io/[repo-name]/
```

## 与 Vercel 对比
| 特性 | GitHub Pages | Vercel |
|------|-------------|--------|
| 托管方 | GitHub | Vercel |
| 自定义域名 | 支持 | 支持 |
| 构建触发 | Git push | Git push / Webhook |
| 缓存刷新 | 5-10分钟 | 即时 |
| 国内访问 | 较慢 | 较快 |
| 数据存储 | 仓库文件 | 无状态 |

## 注意事项
- GitHub Pages 有缓存，更新后可能需要 5-10 分钟生效
- 可通过添加 `?t=123` 参数绕过缓存
- 强制推送会覆盖 gh-pages 分支历史

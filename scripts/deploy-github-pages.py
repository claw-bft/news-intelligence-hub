#!/usr/bin/env python3
"""
GitHub Pages 可视化部署技能
将新闻情报数据部署到 GitHub Pages 静态站点
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None, timeout=120):
    """执行 shell 命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"

def check_gh_auth():
    """检查 GitHub CLI 认证状态"""
    success, stdout, stderr = run_command("gh auth status")
    return success

def create_gh_pages_branch(repo_dir):
    """创建或切换到 gh-pages 分支"""
    # 检查是否有 gh-pages 分支
    success, stdout, _ = run_command("git branch -a", cwd=repo_dir)
    
    if "gh-pages" in stdout:
        # 切换到 gh-pages 分支
        run_command("git checkout gh-pages", cwd=repo_dir)
    else:
        # 创建孤儿分支
        run_command("git checkout --orphan gh-pages", cwd=repo_dir)
        run_command("git rm -rf .", cwd=repo_dir)
    
    return True

def copy_dist_files(dist_dir, repo_dir):
    """复制构建文件到仓库"""
    # 清空当前目录（保留 .git）
    for item in Path(repo_dir).iterdir():
        if item.name == '.git':
            continue
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil
            shutil.rmtree(item)
    
    # 复制 dist 文件
    for item in Path(dist_dir).iterdir():
        if item.is_file():
            import shutil
            shutil.copy2(item, repo_dir / item.name)
        elif item.is_dir():
            import shutil
            shutil.copytree(item, repo_dir / item.name, dirs_exist_ok=True)
    
    return True

def commit_and_push(repo_dir, message=None):
    """提交并推送到 GitHub"""
    if message is None:
        message = f"Deploy: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 配置 git
    run_command('git config user.email "action@github.com"', cwd=repo_dir)
    run_command('git config user.name "GitHub Action"', cwd=repo_dir)
    
    # 添加文件
    run_command("git add -A", cwd=repo_dir)
    
    # 提交
    success, _, stderr = run_command(f'git commit -m "{message}" --allow-empty', cwd=repo_dir)
    
    # 推送
    success, stdout, stderr = run_command("git push origin gh-pages --force", cwd=repo_dir, timeout=180)
    
    return success, stderr

def enable_github_pages(repo_name):
    """启用 GitHub Pages"""
    # 检查是否已启用
    success, stdout, _ = run_command(f"gh api repos/{repo_name}/pages")
    
    if success:
        print("✅ GitHub Pages 已启用")
        return True
    
    # 启用 Pages
    cmd = f'echo \'{{"source":{{"branch":"gh-pages","path":"/"}}}}\' | gh api repos/{repo_name}/pages --method POST --input -'
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ GitHub Pages 启用成功")
        return True
    else:
        print(f"⚠️ 启用 Pages 失败: {stderr}")
        return False

def get_pages_url(repo_name):
    """获取 GitHub Pages URL"""
    success, stdout, _ = run_command(f"gh api repos/{repo_name}/pages")
    
    if success:
        try:
            data = json.loads(stdout)
            return data.get("html_url", "")
        except:
            pass
    
    # 默认格式
    return f"https://{repo_name.split('/')[0]}.github.io/{repo_name.split('/')[-1]}/"

def deploy_to_github_pages(dist_dir, repo_name, repo_dir=None):
    """
    部署到 GitHub Pages
    
    Args:
        dist_dir: 构建输出目录
        repo_name: GitHub 仓库名 (格式: owner/repo)
        repo_dir: 本地仓库目录（可选，默认创建临时目录）
    """
    print(f"🚀 开始部署到 GitHub Pages: {repo_name}")
    
    # 检查认证
    if not check_gh_auth():
        print("❌ GitHub CLI 未认证，请先运行: gh auth login")
        return False
    
    # 设置仓库目录
    if repo_dir is None:
        repo_dir = Path("/tmp/gh-pages-deploy")
    else:
        repo_dir = Path(repo_dir)
    
    # 清理并创建目录
    if repo_dir.exists():
        import shutil
        shutil.rmtree(repo_dir)
    repo_dir.mkdir(parents=True, exist_ok=True)
    
    repo_dir = Path(repo_dir)
    
    # 克隆
    print(f"📦 克隆仓库...")
    clone_url = f"https://github.com/{repo_name}.git"
    success, _, stderr = run_command(f"git clone {clone_url} .", cwd=repo_dir, timeout=60)
    
    if not success:
        print(f"❌ 克隆失败: {stderr}")
        return False
    
    # 创建/切换到 gh-pages 分支
    print(f"🌿 准备 gh-pages 分支...")
    create_gh_pages_branch(repo_dir)
    
    # 复制文件
    print(f"📋 复制构建文件...")
    copy_dist_files(dist_dir, repo_dir)
    
    # 提交推送
    print(f"⬆️ 推送到 GitHub...")
    success, error = commit_and_push(repo_dir)
    
    if not success:
        print(f"❌ 推送失败: {error}")
        return False
    
    # 启用 Pages
    print(f"🔧 启用 GitHub Pages...")
    enable_github_pages(repo_name)
    
    # 获取 URL
    pages_url = get_pages_url(repo_name)
    
    print(f"✅ 部署完成!")
    print(f"🌐 访问地址: {pages_url}")
    
    return pages_url

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy to GitHub Pages")
    parser.add_argument("--dist", default="dist", help="Build output directory")
    parser.add_argument("--repo", required=True, help="GitHub repo (owner/repo)")
    parser.add_argument("--work-dir", default="/tmp/gh-pages-deploy", help="Working directory")
    
    args = parser.parse_args()
    
    dist_dir = Path(args.dist)
    if not dist_dir.exists():
        print(f"❌ 构建目录不存在: {dist_dir}")
        sys.exit(1)
    
    url = deploy_to_github_pages(dist_dir, args.repo, args.work_dir)
    
    if url:
        # 输出到文件供其他工具使用
        with open("/tmp/gh-pages-url.txt", "w") as f:
            f.write(url)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

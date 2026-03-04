#!/usr/bin/env python3
"""
静态站点构建脚本
整合所有数据，生成最终的静态站点
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import glob

def load_json_file(filepath):
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 读取失败 {filepath}: {e}")
        return None

def get_latest_ranking(ranking_type):
    """获取最新的榜单数据"""
    pattern = f"data/{ranking_type}/*.json"
    files = sorted(glob.glob(pattern), reverse=True)
    
    if not files:
        return None
    
    return load_json_file(files[0])

def get_ranking_history(ranking_type, limit=7):
    """获取榜单历史"""
    pattern = f"data/{ranking_type}/*.json"
    files = sorted(glob.glob(pattern), reverse=True)[:limit]
    
    history = []
    for f in files:
        data = load_json_file(f)
        if data:
            history.append({
                "period": data.get('period'),
                "timestamp": data.get('timestamp'),
                "top_news": data.get('news', [])[:5]  # 只保留TOP5
            })
    
    return history

def build_site():
    """构建静态站点"""
    now = datetime.now()
    
    # 创建输出目录
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # 复制静态资源
    if Path("assets").exists():
        shutil.copytree("assets", dist_dir / "assets")
    
    # 加载数据
    print("📊 加载数据...")
    
    hourly = get_latest_ranking("hourly")
    daily = get_latest_ranking("daily")
    weekly = get_latest_ranking("weekly")
    monthly = get_latest_ranking("monthly")
    yearly = get_latest_ranking("yearly")
    relations = load_json_file("data/relations/current.json")
    
    # 构建统一数据文件
    site_data = {
        "meta": {
            "title": "News Intelligence Hub - 热点新闻智能分析",
            "description": "自动化新闻聚合与关联分析平台",
            "updated_at": now.isoformat(),
            "version": "1.0.0"
        },
        "rankings": {
            "hourly": hourly,
            "daily": daily,
            "weekly": weekly,
            "monthly": monthly,
            "yearly": yearly
        },
        "history": {
            "hourly": get_ranking_history("hourly", 24),
            "daily": get_ranking_history("daily", 7),
            "weekly": get_ranking_history("weekly", 4),
            "monthly": get_ranking_history("monthly", 12)
        },
        "relations": relations
    }
    
    # 保存统一数据文件
    with open(dist_dir / "data.json", 'w', encoding='utf-8') as f:
        json.dump(site_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据文件生成: {dist_dir / 'data.json'}")
    
    # 生成首页HTML
    print("🏗️ 生成页面...")
    generate_index_html(dist_dir, site_data)
    generate_hourly_html(dist_dir, site_data)
    generate_daily_html(dist_dir, site_data)
    generate_weekly_html(dist_dir, site_data)
    generate_monthly_html(dist_dir, site_data)
    generate_yearly_html(dist_dir, site_data)
    generate_relations_html(dist_dir, site_data)
    
    print(f"✅ 站点构建完成: {dist_dir}")
    print(f"   文件数: {len(list(dist_dir.rglob('*')))}")

def generate_index_html(dist_dir, data):
    """生成首页"""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Intelligence Hub - 热点新闻智能分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #fff;
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{ text-align: center; padding: 40px 0; border-bottom: 1px solid #333; }}
        h1 {{ font-size: 2.5rem; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .subtitle {{ color: #888; margin-top: 10px; }}
        .update-time {{ color: #666; font-size: 0.9rem; margin-top: 10px; }}
        
        .nav {{ display: flex; justify-content: center; gap: 20px; padding: 20px 0; flex-wrap: wrap; }}
        .nav a {{ 
            color: #888; text-decoration: none; padding: 10px 20px; 
            border-radius: 8px; transition: all 0.3s;
        }}
        .nav a:hover, .nav a.active {{ background: #1a1a25; color: #00d4ff; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-top: 30px; }}
        .card {{ 
            background: #1a1a25; border-radius: 12px; padding: 20px;
            border: 1px solid #2a2a35; transition: transform 0.3s;
        }}
        .card:hover {{ transform: translateY(-5px); border-color: #00d4ff; }}
        .card h2 {{ color: #00d4ff; margin-bottom: 15px; font-size: 1.2rem; }}
        
        .news-item {{ 
            display: flex; align-items: center; padding: 12px 0;
            border-bottom: 1px solid #2a2a35;
        }}
        .news-item:last-child {{ border-bottom: none; }}
        .rank {{ 
            width: 28px; height: 28px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 0.85rem; margin-right: 12px;
        }}
        .rank.top3 {{ background: linear-gradient(135deg, #ffd700, #ff6b6b); color: #000; }}
        .rank {{ background: #2a2a35; color: #888; }}
        
        .news-content {{ flex: 1; }}
        .news-title {{ font-size: 0.95rem; color: #fff; margin-bottom: 4px; }}
        .news-meta {{ font-size: 0.8rem; color: #666; display: flex; gap: 10px; }}
        .heat {{ color: #ff6b6b; font-weight: bold; }}
        .category {{ color: #00d4ff; }}
        
        .view-all {{ 
            display: block; text-align: center; margin-top: 15px;
            color: #00d4ff; text-decoration: none; font-size: 0.9rem;
        }}
        
        footer {{ text-align: center; padding: 40px 0; color: #666; border-top: 1px solid #333; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>News Intelligence Hub</h1>
            <p class="subtitle">热点新闻智能分析 · 时间维度榜单 · 语义关联网络</p>
            <p class="update-time">更新时间: {data['meta']['updated_at'][:19].replace('T', ' ')}</p>
        </header>
        
        <nav class="nav">
            <a href="index.html" class="active">首页</a>
            <a href="hourly.html">小时榜</a>
            <a href="daily.html">日榜</a>
            <a href="weekly.html">周榜</a>
            <a href="monthly.html">月榜</a>
            <a href="yearly.html">年榜</a>
            <a href="relations.html">关联网络</a>
        </nav>
        
        <div class="grid">
            {generate_ranking_card('hourly', data['rankings']['hourly'], '实时热榜')}
            {generate_ranking_card('daily', data['rankings']['daily'], '今日热点')}
            {generate_ranking_card('weekly', data['rankings']['weekly'], '本周精选')}
            {generate_ranking_card('relations', data['relations'], '关联洞察')}
        </div>
        
        <footer>
            <p>News Intelligence Hub · 自动化新闻聚合与分析</p>
            <p style="margin-top: 10px; font-size: 0.85rem;">数据每30分钟更新</p>
        </footer>
    </div>
</body>
</html>'''
    
    with open(dist_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 首页生成: {dist_dir / 'index.html'}")

def generate_ranking_card(ranking_type, data, title):
    """生成榜单卡片HTML"""
    if not data:
        return f'''
        <div class="card">
            <h2>{title}</h2>
            <p style="color: #666; text-align: center; padding: 40px 0;">暂无数据</p>
        </div>'''
    
    if ranking_type == 'relations':
        return generate_relations_card(data, title)
    
    news_list = data.get('news', [])[:5]  # TOP 5
    
    news_html = ''
    for i, news in enumerate(news_list, 1):
        rank_class = 'top3' if i <= 3 else ''
        news_html += f'''
            <div class="news-item">
                <div class="rank {rank_class}">{i}</div>
                <div class="news-content">
                    <div class="news-title">{news['title']}</div>
                    <div class="news-meta">
                        <span class="heat">🔥 {news['heat']}</span>
                        <span class="category">{news.get('category', '其他')}</span>
                    </div>
                </div>
            </div>'''
    
    return f'''
    <div class="card">
        <h2>{title}</h2>
        {news_html}
        <a href="{ranking_type}.html" class="view-all">查看完整榜单 →</a>
    </div>'''

def generate_relations_card(data, title):
    """生成关联卡片"""
    if not data:
        return f'''
        <div class="card">
            <h2>{title}</h2>
            <p style="color: #666; text-align: center; padding: 40px 0;">暂无数据</p>
        </div>'''
    
    stats = data.get('stats', {})
    clusters = data.get('clusters', [])[:3]
    
    clusters_html = ''
    for c in clusters:
        clusters_html += f'''
            <div class="news-item">
                <div class="news-content">
                    <div class="news-title">{c['name']}</div>
                    <div class="news-meta">
                        <span>{c['size']} 条相关新闻</span>
                        <span>密度: {c['density']}</span>
                    </div>
                </div>
            </div>'''
    
    return f'''
    <div class="card">
        <h2>{title}</h2>
        <div style="margin-bottom: 15px; color: #888; font-size: 0.9rem;">
            节点: {stats.get('total_nodes', 0)} · 关联: {stats.get('total_links', 0)} · 聚类: {stats.get('total_clusters', 0)}
        </div>
        {clusters_html}
        <a href="relations.html" class="view-all">查看关联网络 →</a>
    </div>'''

def generate_hourly_html(dist_dir, data):
    """生成小时榜页面"""
    generate_ranking_page(dist_dir, 'hourly', data['rankings']['hourly'], '小时热榜', '每小时更新')

def generate_daily_html(dist_dir, data):
    """生成日榜页面"""
    generate_ranking_page(dist_dir, 'daily', data['rankings']['daily'], '今日热点', '每日 00:00/12:00 更新')

def generate_weekly_html(dist_dir, data):
    """生成周榜页面"""
    generate_ranking_page(dist_dir, 'weekly', data['rankings']['weekly'], '本周精选', '每周一更新')

def generate_monthly_html(dist_dir, data):
    """生成月榜页面"""
    generate_ranking_page(dist_dir, 'monthly', data['rankings']['monthly'], '月度大事', '每月1日更新')

def generate_yearly_html(dist_dir, data):
    """生成年榜页面"""
    generate_ranking_page(dist_dir, 'yearly', data['rankings']['yearly'], '年度榜单', '每年1月1日更新')

def generate_ranking_page(dist_dir, ranking_type, data, title, update_info):
    """生成榜单页面"""
    if not data:
        data = {"news": [], "stats": {}}
    
    news_list = data.get('news', [])
    
    news_html = ''
    for i, news in enumerate(news_list, 1):
        rank_class = 'top3' if i <= 3 else ''
        impact = news.get('impact', {})
        impact_html = f'''<div style="margin-top: 8px; display: flex; gap: 10px; font-size: 0.75rem;">
                <span style="color: #888;">社会影响: {impact.get('social', 0)}</span>
                <span style="color: #888;">经济影响: {impact.get('economic', 0)}</span>
                <span style="color: #888;">政治影响: {impact.get('political', 0)}</span>
                <span style="color: #888;">科技影响: {impact.get('tech', 0)}</span>
            </div>'''
        
        news_html += f'''
            <div class="news-item" style="padding: 20px 0;">
                <div class="rank {rank_class}" style="width: 36px; height: 36px; font-size: 1rem;">{i}</div>
                <div class="news-content">
                    <div class="news-title" style="font-size: 1.1rem;">{news['title']}</div>
                    <div style="color: #888; margin-top: 8px; font-size: 0.9rem;">{news.get('summary', '')}</div>
                    <div class="news-meta" style="margin-top: 10px;">
                        <span class="heat">🔥 {news['heat']}</span>
                        <span class="category">{news.get('category', '其他')}</span>
                        <span style="color: #666;">{news.get('source', '未知')}</span>
                    </div>
                    {impact_html}
                </div>
            </div>'''
    
    if not news_html:
        news_html = '<p style="color: #666; text-align: center; padding: 60px 0;">暂无数据</p>'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - News Intelligence Hub</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #fff;
            line-height: 1.6;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
        header {{ text-align: center; padding: 40px 0; border-bottom: 1px solid #333; }}
        h1 {{ font-size: 2rem; color: #00d4ff; }}
        .subtitle {{ color: #888; margin-top: 10px; }}
        
        .nav {{ display: flex; justify-content: center; gap: 20px; padding: 20px 0; flex-wrap: wrap; }}
        .nav a {{ 
            color: #888; text-decoration: none; padding: 10px 20px; 
            border-radius: 8px; transition: all 0.3s;
        }}
        .nav a:hover, .nav a.active {{ background: #1a1a25; color: #00d4ff; }}
        
        .ranking-list {{ margin-top: 30px; }}
        .news-item {{ 
            display: flex; align-items: flex-start; padding: 20px 0;
            border-bottom: 1px solid #2a2a35;
        }}
        .news-item:last-child {{ border-bottom: none; }}
        .rank {{ 
            width: 36px; height: 36px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 1rem; margin-right: 16px;
            flex-shrink: 0;
        }}
        .rank.top3 {{ background: linear-gradient(135deg, #ffd700, #ff6b6b); color: #000; }}
        .rank {{ background: #2a2a35; color: #888; }}
        
        .news-content {{ flex: 1; }}
        .news-title {{ font-size: 1.1rem; color: #fff; margin-bottom: 8px; }}
        .news-meta {{ font-size: 0.85rem; color: #666; display: flex; gap: 15px; flex-wrap: wrap; }}
        .heat {{ color: #ff6b6b; font-weight: bold; }}
        .category {{ color: #00d4ff; }}
        
        footer {{ text-align: center; padding: 40px 0; color: #666; border-top: 1px solid #333; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p class="subtitle">{update_info}</p>
        </header>
        
        <nav class="nav">
            <a href="index.html">首页</a>
            <a href="hourly.html" {'class="active"' if ranking_type == 'hourly' else ''}>小时榜</a>
            <a href="daily.html" {'class="active"' if ranking_type == 'daily' else ''}>日榜</a>
            <a href="weekly.html" {'class="active"' if ranking_type == 'weekly' else ''}>周榜</a>
            <a href="monthly.html" {'class="active"' if ranking_type == 'monthly' else ''}>月榜</a>
            <a href="yearly.html" {'class="active"' if ranking_type == 'yearly' else ''}>年榜</a>
            <a href="relations.html">关联网络</a>
        </nav>
        
        <div class="ranking-list">
            {news_html}
        </div>
        
        <footer>
            <p>News Intelligence Hub · 自动化新闻聚合与分析</p>
        </footer>
    </div>
</body>
</html>'''
    
    with open(dist_dir / f"{ranking_type}.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ {title}页面生成: {dist_dir / f'{ranking_type}.html'}")

def generate_relations_html(dist_dir, data):
    """生成关联网络页面"""
    relations_data = data.get('relations', {})
    nodes = relations_data.get('nodes', [])
    links = relations_data.get('links', [])
    clusters = relations_data.get('clusters', [])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>关联网络 - News Intelligence Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #fff;
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{ text-align: center; padding: 40px 0; border-bottom: 1px solid #333; }}
        h1 {{ font-size: 2rem; color: #00d4ff; }}
        .subtitle {{ color: #888; margin-top: 10px; }}
        
        .nav {{ display: flex; justify-content: center; gap: 20px; padding: 20px 0; flex-wrap: wrap; }}
        .nav a {{ 
            color: #888; text-decoration: none; padding: 10px 20px; 
            border-radius: 8px; transition: all 0.3s;
        }}
        .nav a:hover, .nav a.active {{ background: #1a1a25; color: #00d4ff; }}
        
        #network-chart {{ width: 100%; height: 600px; margin-top: 30px; }}
        
        .stats {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-top: 30px;
        }}
        .stat-card {{ 
            background: #1a1a25; padding: 20px; border-radius: 12px;
            text-align: center; border: 1px solid #2a2a35;
        }}
        .stat-value {{ font-size: 2rem; color: #00d4ff; font-weight: bold; }}
        .stat-label {{ color: #888; margin-top: 8px; }}
        
        footer {{ text-align: center; padding: 40px 0; color: #666; border-top: 1px solid #333; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>新闻关联网络</h1>
            <p class="subtitle">基于语义相似度、实体共现、时间邻近度的多维关联分析</p>
        </header>
        
        <nav class="nav">
            <a href="index.html">首页</a>
            <a href="hourly.html">小时榜</a>
            <a href="daily.html">日榜</a>
            <a href="weekly.html">周榜</a>
            <a href="monthly.html">月榜</a>
            <a href="yearly.html">年榜</a>
            <a href="relations.html" class="active">关联网络</a>
        </nav>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(nodes)}</div>
                <div class="stat-label">新闻节点</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(links)}</div>
                <div class="stat-label">关联关系</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(clusters)}</div>
                <div class="stat-label">话题聚类</div>
            </div>
        </div>
        
        <div id="network-chart"></div>
        
        <footer>
            <p>News Intelligence Hub · 自动化新闻聚合与分析</p>
        </footer>
    </div>
    
    <script>
        const chart = echarts.init(document.getElementById('network-chart'));
        
        const nodes = {json.dumps(nodes, ensure_ascii=False)};
        const links = {json.dumps(links, ensure_ascii=False)};
        
        const option = {{
            backgroundColor: 'transparent',
            tooltip: {{
                trigger: 'item',
                formatter: function(params) {{
                    if (params.dataType === 'node') {{
                        return params.data.full_title + '<br/>热度: ' + params.data.heat;
                    }}
                    return params.data.source + ' → ' + params.data.target + '<br/>关联度: ' + params.data.strength;
                }}
            }},
            series: [{{
                type: 'graph',
                layout: 'force',
                data: nodes.map(n => ({{
                    id: n.id,
                    name: n.title,
                    value: n.heat,
                    symbolSize: Math.sqrt(n.heat) * 3,
                    itemStyle: {{
                        color: n.category === '科技' ? '#00d4ff' : 
                               n.category === '经济' ? '#7c3aed' :
                               n.category === '政治' ? '#ff6b6b' : '#ffd700'
                    }}
                }})),
                links: links.map(l => ({{
                    source: l.source,
                    target: l.target,
                    value: l.strength,
                    lineStyle: {{
                        width: l.strength * 5,
                        opacity: l.strength,
                        color: l.type === 'strong' ? '#ff6b6b' :
                               l.type === 'medium' ? '#ffd700' : '#888'
                    }}
                }})),
                roam: true,
                label: {{
                    show: true,
                    position: 'right',
                    formatter: '{{b}}',
                    color: '#fff',
                    fontSize: 10
                }},
                force: {{
                    repulsion: 300,
                    edgeLength: [50, 200],
                    gravity: 0.1
                }}
            }}]
        }};
        
        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    </script>
</body>
</html>'''
    
    with open(dist_dir / "relations.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 关联网络页面生成: {dist_dir / 'relations.html'}")

def main():
    """主函数"""
    build_site()

if __name__ == "__main__":
    main()

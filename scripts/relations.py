#!/usr/bin/env python3
"""
新闻关联分析脚本
计算新闻之间的关联度，生成关联网络
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import glob
from collections import defaultdict

def calculate_semantic_similarity(news1, news2):
    """计算语义相似度（简化版：基于关键词重叠）"""
    keywords1 = set(news1.get('keywords', []))
    keywords2 = set(news2.get('keywords', []))
    
    if not keywords1 or not keywords2:
        return 0.0
    
    intersection = keywords1 & keywords2
    union = keywords1 | keywords2
    
    return len(intersection) / len(union) if union else 0.0

def calculate_entity_overlap(news1, news2):
    """计算实体共现度"""
    # 从标题和摘要中提取实体（简化处理）
    text1 = f"{news1['title']} {news1.get('summary', '')}".lower()
    text2 = f"{news2['title']} {news2.get('summary', '')}".lower()
    
    # 简单分词（实际应使用NLP工具）
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    # 过滤停用词
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    words1 = words1 - stopwords
    words2 = words2 - stopwords
    
    intersection = words1 & words2
    
    return len(intersection) / max(len(words1), len(words2)) if max(len(words1), len(words2)) > 0 else 0.0

def calculate_temporal_proximity(news1, news2):
    """计算时间邻近度"""
    try:
        t1 = datetime.fromisoformat(news1['published_at'].replace('Z', '+00:00'))
        t2 = datetime.fromisoformat(news2['published_at'].replace('Z', '+00:00'))
        diff_hours = abs((t1 - t2).total_seconds()) / 3600
        
        # 24小时内为1.0，超过72小时为0
        if diff_hours <= 24:
            return 1.0
        elif diff_hours >= 72:
            return 0.0
        else:
            return 1.0 - (diff_hours - 24) / 48
    except:
        return 0.0

def calculate_category_match(news1, news2):
    """计算类别匹配度"""
    return 1.0 if news1.get('category') == news2.get('category') else 0.0

def calculate_relation_strength(news1, news2):
    """计算综合关联强度"""
    # 权重配置
    weights = {
        'semantic': 0.40,
        'entity': 0.25,
        'temporal': 0.20,
        'category': 0.15
    }
    
    semantic = calculate_semantic_similarity(news1, news2)
    entity = calculate_entity_overlap(news1, news2)
    temporal = calculate_temporal_proximity(news1, news2)
    category = calculate_category_match(news1, news2)
    
    strength = (
        weights['semantic'] * semantic +
        weights['entity'] * entity +
        weights['temporal'] * temporal +
        weights['category'] * category
    )
    
    return round(strength, 3)

def get_relation_type(strength, news1, news2):
    """根据关联强度判断关系类型"""
    if strength >= 0.8:
        return "strong"
    elif strength >= 0.5:
        return "medium"
    elif strength >= 0.3:
        return "weak"
    else:
        return "none"

def analyze_relations():
    """分析新闻关联"""
    now = datetime.now()
    
    # 读取最近24小时的新闻
    pattern = "data/hourly/*.json"
    hourly_files = sorted(glob.glob(pattern), reverse=True)[:24]
    
    all_news = {}
    for f in hourly_files:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                for news in data.get('news', []):
                    all_news[news['id']] = news
        except Exception as e:
            print(f"⚠️ 读取失败 {f}: {e}")
    
    if len(all_news) < 2:
        print("⚠️ 新闻数量不足，无法分析关联")
        return
    
    print(f"📊 分析 {len(all_news)} 条新闻的关联关系...")
    
    # 计算关联
    nodes = []
    links = []
    news_list = list(all_news.values())
    
    # 构建节点
    for news in news_list:
        nodes.append({
            "id": news['id'],
            "title": news['title'][:30] + "..." if len(news['title']) > 30 else news['title'],
            "heat": news['heat'],
            "category": news.get('category', '其他'),
            "full_title": news['title']
        })
    
    # 构建边（只保留强关联）
    threshold = 0.3
    for i, news1 in enumerate(news_list):
        for j, news2 in enumerate(news_list):
            if i >= j:
                continue
            
            strength = calculate_relation_strength(news1, news2)
            
            if strength >= threshold:
                relation_type = get_relation_type(strength, news1, news2)
                links.append({
                    "source": news1['id'],
                    "target": news2['id'],
                    "strength": strength,
                    "type": relation_type
                })
    
    # 聚类分析（简化版：基于连通分量）
    clusters = detect_clusters(nodes, links)
    
    result = {
        "timestamp": now.isoformat(),
        "nodes": nodes,
        "links": links,
        "clusters": clusters,
        "stats": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "total_clusters": len(clusters),
            "strong_relations": sum(1 for l in links if l['type'] == 'strong'),
            "medium_relations": sum(1 for l in links if l['type'] == 'medium'),
            "weak_relations": sum(1 for l in links if l['type'] == 'weak')
        }
    }
    
    # 保存当前关联
    output_file = Path("data/relations/current.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 归档历史关联
    archive_file = Path(f"data/relations/archive/{now.strftime('%Y%m%d%H')}.json")
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 关联分析完成: {output_file}")
    print(f"   节点: {len(nodes)}, 边: {len(links)}, 聚类: {len(clusters)}")
    
    return result

def detect_clusters(nodes, links):
    """检测聚类（基于连通分量）"""
    # 构建邻接表
    adj = defaultdict(set)
    for link in links:
        adj[link['source']].add(link['target'])
        adj[link['target']].add(link['source'])
    
    # BFS找连通分量
    visited = set()
    clusters = []
    
    for node in nodes:
        node_id = node['id']
        if node_id in visited:
            continue
        
        # BFS
        cluster_nodes = []
        queue = [node_id]
        visited.add(node_id)
        
        while queue:
            current = queue.pop(0)
            cluster_nodes.append(current)
            
            for neighbor in adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        if len(cluster_nodes) >= 2:  # 至少2个节点才算一个聚类
            # 提取聚类名称（使用热度最高的新闻标题）
            cluster_news = [n for n in nodes if n['id'] in cluster_nodes]
            top_news = max(cluster_news, key=lambda x: x['heat'])
            
            clusters.append({
                "id": f"cluster-{len(clusters)+1}",
                "name": top_news['title'][:20] + "..." if len(top_news['title']) > 20 else top_news['title'],
                "nodes": cluster_nodes,
                "size": len(cluster_nodes),
                "density": calculate_cluster_density(cluster_nodes, links)
            })
    
    return clusters

def calculate_cluster_density(node_ids, links):
    """计算聚类密度"""
    node_set = set(node_ids)
    internal_links = sum(
        1 for l in links 
        if l['source'] in node_set and l['target'] in node_set
    )
    
    n = len(node_ids)
    max_links = n * (n - 1) / 2
    
    return round(internal_links / max_links, 2) if max_links > 0 else 0.0

def main():
    """主函数"""
    analyze_relations()

if __name__ == "__main__":
    main()

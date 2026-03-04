#!/usr/bin/env python3
"""
新闻抓取脚本 - 每30分钟执行一次
输出: data/raw/YYYY-MM-DD-HH.json
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def scrape_news():
    """抓取新闻数据"""
    now = datetime.now()
    
    # 模拟新闻数据（实际使用时替换为真实抓取逻辑）
    news_items = [
        {
            "id": f"news-{now.strftime('%Y%m%d%H')}-001",
            "title": "AGI安全框架全球协议达成",
            "summary": "全球42个国家签署首个具有法律约束力的AGI开发安全协议...",
            "source": "Reuters",
            "category": "科技",
            "heat": 98.5,
            "impact": {"social": 95, "economic": 88, "political": 92, "tech": 99},
            "keywords": ["AGI", "人工智能监管", "安全协议"],
            "published_at": now.isoformat(),
            "url": "https://example.com/news/001"
        },
        {
            "id": f"news-{now.strftime('%Y%m%d%H')}-002",
            "title": "亚洲数字货币联盟正式启动",
            "summary": "15个亚太经济体共同推出基于区块链的跨境结算系统...",
            "source": "Bloomberg",
            "category": "经济",
            "heat": 95.2,
            "impact": {"social": 72, "economic": 98, "political": 85, "tech": 90},
            "keywords": ["数字货币", "CBDC", "区块链"],
            "published_at": (now - timedelta(minutes=15)).isoformat(),
            "url": "https://example.com/news/002"
        },
        {
            "id": f"news-{now.strftime('%Y%m%d%H')}-003",
            "title": "北极资源开发国际公约签署",
            "summary": "北极理事会成员国就资源开发环境保护达成历史性协议...",
            "source": "The Guardian",
            "category": "政治",
            "heat": 92.0,
            "impact": {"social": 85, "economic": 90, "political": 95, "tech": 60},
            "keywords": ["北极", "资源开发", "环境保护"],
            "published_at": (now - timedelta(minutes=30)).isoformat(),
            "url": "https://example.com/news/003"
        },
        {
            "id": f"news-{now.strftime('%Y%m%d%H')}-004",
            "title": "全球首例脑机接口商业应用获批",
            "summary": "FDA批准Neuralink开展人体临床试验，脑机接口进入商用阶段...",
            "source": "TechCrunch",
            "category": "科技",
            "heat": 89.5,
            "impact": {"social": 90, "economic": 75, "political": 60, "tech": 98},
            "keywords": ["脑机接口", "Neuralink", "医疗科技"],
            "published_at": (now - timedelta(minutes=45)).isoformat(),
            "url": "https://example.com/news/004"
        },
        {
            "id": f"news-{now.strftime('%Y%m%d%H')}-005",
            "title": "量子计算破解RSA加密演示",
            "summary": "IBM展示1000量子比特计算机成功破解2048位RSA加密...",
            "source": "MIT Technology Review",
            "category": "科技",
            "heat": 87.3,
            "impact": {"social": 70, "economic": 85, "political": 80, "tech": 99},
            "keywords": ["量子计算", "网络安全", "RSA"],
            "published_at": (now - timedelta(minutes=60)).isoformat(),
            "url": "https://example.com/news/005"
        }
    ]
    
    return {
        "timestamp": now.isoformat(),
        "news": news_items,
        "stats": {
            "total": len(news_items),
            "categories": {"科技": 3, "经济": 1, "政治": 1}
        }
    }

def main():
    """主函数"""
    now = datetime.now()
    
    # 确保目录存在
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # 抓取数据
    data = scrape_news()
    
    # 保存到文件
    filename = raw_dir / f"{now.strftime('%Y-%m-%d-%H')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 抓取完成: {filename}")
    print(f"   共 {len(data['news'])} 条新闻")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
榜单生成脚本
生成小时榜、日榜、周榜、月榜、年榜
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import glob

def load_recent_files(pattern, hours=24):
    """加载最近N小时的文件"""
    files = sorted(glob.glob(pattern), reverse=True)
    data = []
    for f in files[:hours]:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data.append(json.load(fp))
        except Exception as e:
            print(f"⚠️ 读取失败 {f}: {e}")
    return data

def generate_hourly_ranking():
    """生成小时榜"""
    now = datetime.now()
    current_hour = now.strftime('%Y-%m-%d-%H')
    
    # 读取当前小时数据
    raw_file = Path(f"data/raw/{current_hour}.json")
    if not raw_file.exists():
        print(f"⚠️ 无数据: {raw_file}")
        return
    
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 按热度排序
    news = sorted(raw_data['news'], key=lambda x: x['heat'], reverse=True)
    
    # 添加排名
    for i, item in enumerate(news, 1):
        item['rank'] = i
        # 计算趋势（与上一小时对比）
        item['heat_trend'] = '+0.0'  # 简化处理
    
    result = {
        "type": "hourly",
        "timestamp": now.isoformat(),
        "period": current_hour,
        "news": news,
        "stats": {
            "total": len(news),
            "high_impact": sum(1 for n in news if n['heat'] >= 90)
        }
    }
    
    # 保存
    output_file = Path(f"data/hourly/{current_hour}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 小时榜生成: {output_file}")
    return result

def generate_daily_ranking():
    """生成日榜"""
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    
    # 读取今日所有小时数据
    pattern = f"data/raw/{today}-*.json"
    hourly_data = load_recent_files(pattern, hours=24)
    
    if not hourly_data:
        print(f"⚠️ 无今日数据")
        return
    
    # 合并并去重
    all_news = {}
    for data in hourly_data:
        for news in data['news']:
            news_id = news['id']
            if news_id in all_news:
                # 保留最高热度
                all_news[news_id]['heat'] = max(all_news[news_id]['heat'], news['heat'])
            else:
                all_news[news_id] = news.copy()
    
    # 按热度排序
    news_list = sorted(all_news.values(), key=lambda x: x['heat'], reverse=True)
    
    # 添加排名
    for i, item in enumerate(news_list, 1):
        item['rank'] = i
    
    result = {
        "type": "daily",
        "timestamp": now.isoformat(),
        "period": today,
        "news": news_list[:50],  # TOP 50
        "stats": {
            "total": len(news_list),
            "high_impact": sum(1 for n in news_list if n['heat'] >= 90)
        }
    }
    
    # 保存
    output_file = Path(f"data/daily/{today}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 日榜生成: {output_file}")
    return result

def generate_weekly_ranking():
    """生成周榜"""
    now = datetime.now()
    week = now.strftime('%Y-W%W')
    
    # 读取本周日榜
    start_of_week = now - timedelta(days=now.weekday())
    dates = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    all_news = {}
    for date in dates:
        daily_file = Path(f"data/daily/{date}.json")
        if daily_file.exists():
            with open(daily_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for news in data['news']:
                    news_id = news['id']
                    if news_id in all_news:
                        all_news[news_id]['heat'] = max(all_news[news_id]['heat'], news['heat'])
                    else:
                        all_news[news_id] = news.copy()
    
    if not all_news:
        print(f"⚠️ 无本周数据")
        return
    
    news_list = sorted(all_news.values(), key=lambda x: x['heat'], reverse=True)
    for i, item in enumerate(news_list, 1):
        item['rank'] = i
    
    result = {
        "type": "weekly",
        "timestamp": now.isoformat(),
        "period": week,
        "news": news_list[:30],
        "stats": {
            "total": len(news_list),
            "high_impact": sum(1 for n in news_list if n['heat'] >= 90)
        }
    }
    
    output_file = Path(f"data/weekly/{week}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 周榜生成: {output_file}")
    return result

def generate_monthly_ranking():
    """生成月榜"""
    now = datetime.now()
    month = now.strftime('%Y-%m')
    
    # 读取当月日榜
    pattern = f"data/daily/{month}-*.json"
    daily_files = sorted(glob.glob(pattern))
    
    all_news = {}
    for f in daily_files:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            for news in data['news']:
                news_id = news['id']
                if news_id in all_news:
                    all_news[news_id]['heat'] = max(all_news[news_id]['heat'], news['heat'])
                else:
                    all_news[news_id] = news.copy()
    
    if not all_news:
        print(f"⚠️ 无本月数据")
        return
    
    news_list = sorted(all_news.values(), key=lambda x: x['heat'], reverse=True)
    for i, item in enumerate(news_list, 1):
        item['rank'] = i
    
    result = {
        "type": "monthly",
        "timestamp": now.isoformat(),
        "period": month,
        "news": news_list[:20],
        "stats": {
            "total": len(news_list),
            "high_impact": sum(1 for n in news_list if n['heat'] >= 90)
        }
    }
    
    output_file = Path(f"data/monthly/{month}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 月榜生成: {output_file}")
    return result

def generate_yearly_ranking():
    """生成年榜"""
    now = datetime.now()
    year = now.strftime('%Y')
    
    # 读取当年月榜
    pattern = f"data/monthly/{year}-*.json"
    monthly_files = sorted(glob.glob(pattern))
    
    all_news = {}
    for f in monthly_files:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            for news in data['news']:
                news_id = news['id']
                if news_id in all_news:
                    all_news[news_id]['heat'] = max(all_news[news_id]['heat'], news['heat'])
                else:
                    all_news[news_id] = news.copy()
    
    if not all_news:
        print(f"⚠️ 无本年数据")
        return
    
    news_list = sorted(all_news.values(), key=lambda x: x['heat'], reverse=True)
    for i, item in enumerate(news_list, 1):
        item['rank'] = i
    
    result = {
        "type": "yearly",
        "timestamp": now.isoformat(),
        "period": year,
        "news": news_list[:10],
        "stats": {
            "total": len(news_list),
            "high_impact": sum(1 for n in news_list if n['heat'] >= 90)
        }
    }
    
    output_file = Path(f"data/yearly/{year}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 年榜生成: {output_file}")
    return result

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['hourly', 'daily', 'weekly', 'monthly', 'yearly', 'all'], 
                       default='all', help='榜单类型')
    args = parser.parse_args()
    
    if args.type == 'all' or args.type == 'hourly':
        generate_hourly_ranking()
    
    if args.type == 'all' or args.type == 'daily':
        # 只在特定时间生成日榜（00:00, 12:00）
        hour = datetime.now().hour
        if hour in [0, 12] or args.type == 'daily':
            generate_daily_ranking()
    
    if args.type == 'all' or args.type == 'weekly':
        # 只在周一生成周榜
        if datetime.now().weekday() == 0 or args.type == 'weekly':
            generate_weekly_ranking()
    
    if args.type == 'all' or args.type == 'monthly':
        # 只在1日生成月榜
        if datetime.now().day == 1 or args.type == 'monthly':
            generate_monthly_ranking()
    
    if args.type == 'all' or args.type == 'yearly':
        # 只在1月1日生成年榜
        if datetime.now().month == 1 and datetime.now().day == 1 or args.type == 'yearly':
            generate_yearly_ranking()

if __name__ == "__main__":
    main()

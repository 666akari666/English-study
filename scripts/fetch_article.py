import urllib.request
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

def fetch_bbc_business():
    # BBC 商业新闻 RSS 源
    url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        # 解析 XML 数据
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        if not items:
            print("未找到文章")
            return
            
        # 获取最新的一篇文章
        latest_item = items[0]
        title = latest_item.find('title').text
        description = latest_item.find('description').text
        link = latest_item.find('link').text
        pub_date = latest_item.find('pubDate').text
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 组装文章详情数据
        article_detail = {
            "date": today_str,
            "title": title,
            "description": description,
            "content": f"{description}\n\n(Note: This is a preview. Read full article at: {link})",
            "source": "BBC Business",
            "pubDate": pub_date
        }
        
        # 组装索引数据
        article_index = {
            "date": today_str,
            "title": title,
            "summary": description
        }
        
        # 保存详情文件
        os.makedirs('data/articles', exist_ok=True)
        with open(f"data/articles/{today_str}.json", 'w', encoding='utf-8') as f:
            json.dump(article_detail, f, ensure_ascii=False, indent=2)
            
        # 更新索引文件
        index_path = 'data/index.json'
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                index_list = json.load(f)
        else:
            index_list = []
            
        # 避免重复添加同一天的文章
        if not any(item['date'] == today_str for item in index_list):
            index_list.insert(0, article_index)
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_list, f, ensure_ascii=False, indent=2)
                
        print(f"成功获取今日文章: {title}")
        
    except Exception as e:
        print(f"获取文章失败: {e}")

if __name__ == "__main__":
    fetch_bbc_business()
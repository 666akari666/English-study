import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
from datetime import datetime
# 引入 BeautifulSoup 用于解析 HTML 全文
from bs4 import BeautifulSoup

def get_full_article_text(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 寻找 BBC 网页中的所有正文段落
        # BBC 新闻的段落通常在带有特定属性的 div 或 article 中，这里提取所有文章段落
        paragraphs = soup.find_all('p')
        
        valid_paragraphs = []
        for p in paragraphs:
            text = p.get_text().strip()
            # 过滤掉过短的段落、导航栏文字或分享提示
            if len(text) > 40 and not text.startswith("Read more") and not text.startswith("Share this"):
                valid_paragraphs.append(text)
        
        # 将所有段落用换行符连接起来
        if valid_paragraphs:
            return "\n\n".join(valid_paragraphs)
        else:
            return "未能提取到完整正文，请点击原文链接阅读。"
    except Exception as e:
        print(f"提取全文失败: {e}")
        return "提取全文时发生错误。"

def fetch_bbc_business():
    url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        if not items:
            print("未找到文章")
            return
            
        latest_item = items[0]
        title = latest_item.find('title').text
        description = latest_item.find('description').text
        link = latest_item.find('link').text
        pub_date = latest_item.find('pubDate').text
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        print("正在顺着链接爬取完整文章正文...")
        full_text = get_full_article_text(link)
        
        article_detail = {
            "date": today_str,
            "title": title,
            "description": description,
            "content": full_text, # 这里已经替换成了抓取到的全文
            "source": "BBC Business",
            "pubDate": pub_date,
            "link": link
        }
        
        article_index = {
            "date": today_str,
            "title": title,
            "summary": description
        }
        
        os.makedirs('data/articles', exist_ok=True)
        with open(f"data/articles/{today_str}.json", 'w', encoding='utf-8') as f:
            json.dump(article_detail, f, ensure_ascii=False, indent=2)
            
        index_path = 'data/index.json'
        # 即使今天已经运行过，我们也强制更新它以获取全文
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                index_list = json.load(f)
        else:
            index_list = []
            
        # 移除旧的今日数据，避免重复
        index_list = [item for item in index_list if item['date'] != today_str]
        index_list.insert(0, article_index)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_list, f, ensure_ascii=False, indent=2)
                
        print(f"成功获取今日全文文章: {title}")
        
    except Exception as e:
        print(f"获取文章失败: {e}")

if __name__ == "__main__":
    fetch_bbc_business()
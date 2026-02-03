import urllib.parse
import requests
import sys
import os
import io
from bs4 import BeautifulSoup

# 定义生成文件的根目录
OUTPUT_DIR = "/usr/app/html/"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def fetch_html(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    try:
        rep = requests.get(url, headers=headers, timeout=30)  # 增加超时，避免阻塞
        rep.raise_for_status()
        rep.encoding = rep.apparent_encoding
        return rep.text
    except requests.exceptions.RequestException as e:
        print(f"抓取URL失败: {e}", file=sys.stderr)
        sys.exit(1)

def extract_clean_content(html: str) -> str:
    """
    针对腾讯新闻等门户优化：
    - 优先匹配常见内容容器
    - 删除广告、脚本等噪音
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 常见正文容器选择器（按优先级）
    content_selectors = [
        '.content-article',      
        '.article-content',
        'div[bosszone="content"]',
        '#ArticleContent',
        'article',
    ]
    
    article = None
    for selector in content_selectors:
        article = soup.select_one(selector)
        if article:
            break
    
    if not article:
        article = soup.body or soup
    
    # 删除噪音元素
    for tag in article.select('script, style, iframe, nav, header, footer, aside, .ad, .advertisement, .share-bar'):
        tag.decompose()

    title_tag = soup.find('h1', id='article-title')
    if title_tag:
       print(title_tag.get_text())
    else:
      print("未找到文章标题")
    
    return str(article)

def save_as_html(content: str, task_id: str, original_url: str):
    """
    保存为指定任务ID的HTML文件
    :param content: 清洗后的正文内容
    :param task_id: 任务ID（作为文件名）
    :param original_url: 原始URL（嵌入到HTML中）
    """
    # 确保输出目录存在，不存在则创建
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # 拼接输出文件路径
    output_file = os.path.join(OUTPUT_DIR, f"{task_id}.html")
    
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>保存文章</title>
    <style>
        body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif; line-height: 1.7; margin: 0 auto; padding: 20px; color: #333; }}
        img {{ max-width: 100%; height: auto; }}
        a {{ color: #0066cc; text-decoration: none; }}
        .article-info {{ color: #999; font-size: 0.9em; margin-bottom: 20px; }}
    </style>
</head>
<body>
<header class="article-info">
    <p>本文件由工具自动生成，原链接：<a href="{original_url}" target="_blank">{original_url}</a></p>
</header>
<main>
{content}
</main>
</body>
</html>"""
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
    except Exception as e:
        sys.exit(1)

if __name__ == '__main__':
    # 校验命令行参数：需要传入 任务ID 和 URL
    if len(sys.argv) != 3:
        print("❌ 参数错误！使用方式：python3 bs.py <任务ID> <目标URL>", file=sys.stderr)
        sys.exit(1)
    
    # 获取命令行参数
    task_id = sys.argv[1]
    original_url = sys.argv[2]
    
    # 校验URL格式（简单校验）
    if not original_url.startswith(("http://", "https://")):
        print("❌ URL格式错误！必须以http://或https://开头", file=sys.stderr)
        sys.exit(1)
    

    html = fetch_html(original_url)
    
    clean_content = extract_clean_content(html)
    
    save_as_html(clean_content, task_id, original_url)
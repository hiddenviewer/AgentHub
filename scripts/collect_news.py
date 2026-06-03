import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

# 데이터 저장 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_FILE_PATH = os.path.join(BASE_DIR, "data", "news.json")

# 검색할 RSS 피드 쿼리 URL 구성 (국내/해외)
query_ko = urllib.parse.quote("AI 에이전트 OR 인공지능 에이전트")
query_en = urllib.parse.quote('"AI Agent" OR "Agentic AI"')

FEEDS = [
    # 국내 (AI 에이전트 / AI Agent 관련)
    {
        "url": f"https://news.google.com/rss/search?q={query_ko}&hl=ko&gl=KR&ceid=KR:ko",
        "lang": "ko"
    },
    # 해외 (AI Agent / Agentic AI 관련)
    {
        "url": f"https://news.google.com/rss/search?q={query_en}&hl=en-US&gl=US&ceid=US:en",
        "lang": "en"
    }
]

def fetch_rss_news(feed_info):
    url = feed_info["url"]
    lang = feed_info["lang"]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Error fetching RSS from {url}: {e}")
        return []
        
    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"Error parsing XML from {url}: {e}")
        return []
        
    articles = []
    
    # RSS channel -> item 파싱
    for item in root.findall(".//item"):
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        pub_date_str = item.find("pubDate").text if item.find("pubDate") is not None else ""
        source = item.find("source").text if item.find("source") is not None else "Google News"
        
        # 날짜 포맷 변경
        iso_date = ""
        display_date = ""
        if pub_date_str:
            try:
                dt = parsedate_to_datetime(pub_date_str)
                iso_date = dt.isoformat()
                display_date = dt.strftime("%Y-%m-%d")
            except Exception:
                iso_date = datetime.now().isoformat()
                display_date = datetime.now().strftime("%Y-%m-%d")
                
        # Google News 제목은 보통 "제목 - 언론사" 형태이므로 실제 제목만 분리 시도
        clean_title = title
        if " - " in title:
            clean_title = " - ".join(title.split(" - ")[:-1])
            
        articles.append({
            "title": clean_title,
            "link": link,
            "pubDate": iso_date,
            "displayDate": display_date,
            "source": source,
            "lang": lang
        })
        
    return articles

def main():
    print("Starting news collection...")
    
    # 기존 데이터 로드
    existing_news = []
    if os.path.exists(NEWS_FILE_PATH):
        try:
            with open(NEWS_FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    existing_news = json.loads(content)
        except Exception as e:
            print(f"Error reading existing news file: {e}")
            
    # 새로운 뉴스 수집
    new_articles = []
    for feed in FEEDS:
        print(f"Fetching RSS: {feed['url'][:60]}...")
        new_articles.extend(fetch_rss_news(feed))
        
    # 데이터 병합 및 중복 제거 (링크 기준)
    all_news_dict = {}
    
    # 기존 뉴스 먼저 담기
    for item in existing_news:
        link = item.get("link")
        if link:
            all_news_dict[link] = item
            
    # 신규 뉴스 덮어쓰기/추가 (더 최신 정보가 있을 수 있으므로)
    for item in new_articles:
        link = item.get("link")
        if link:
            all_news_dict[link] = item
            
    # 리스트로 변환 후 날짜 기준 내림차순 정렬
    merged_news = list(all_news_dict.values())
    merged_news.sort(key=lambda x: x.get("pubDate", ""), reverse=True)
    
    # 최대 150개 보관
    final_news = merged_news[:150]
    
    # 저장
    try:
        with open(NEWS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(final_news, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved {len(final_news)} articles to {NEWS_FILE_PATH}")
    except Exception as e:
        print(f"Error saving final news: {e}")

if __name__ == "__main__":
    main()

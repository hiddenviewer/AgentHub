import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
from datetime import datetime
from email.utils import parsedate_to_datetime

# 구글 뉴스 URL 디코딩 라이브러리 로드 시도
try:
    from googlenewsdecoder import new_decoderv1
    HAS_DECODER = True
except ImportError:
    HAS_DECODER = False

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
    existing_titles = set()
    existing_news_dict = {}
    
    if os.path.exists(NEWS_FILE_PATH):
        try:
            with open(NEWS_FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    existing_news = json.loads(content)
                    
                    # 중복 판별을 위해 제목 세트 및 매핑 딕셔너리 구축
                    for item in existing_news:
                        title = item.get("title", "").strip()
                        if title:
                            existing_titles.add(title)
                            existing_news_dict[title] = item
        except Exception as e:
            print(f"Error reading existing news file: {e}")
            
    # 새로운 뉴스 수집
    new_articles = []
    for feed in FEEDS:
        print(f"Fetching RSS: {feed['url'][:60]}...")
        new_articles.extend(fetch_rss_news(feed))
        
    # 기존에 없던 진짜 '신규 뉴스'만 필터링 (제목 기준)
    new_unique_articles = []
    for item in new_articles:
        title = item.get("title", "").strip()
        # 이미 수집된 뉴스면 건너뜀
        if title in existing_titles:
            continue
        new_unique_articles.append(item)
        
    print(f"Found {len(new_unique_articles)} new unique articles.")
    
    # 신규 뉴스 디코딩 (최종 기사 원본 URL 찾기)
    if HAS_DECODER and new_unique_articles:
        # 안전장치: 과도한 요청으로 인한 429 차단을 막기 위해 한 회에 최대 25개까지만 디코딩을 진행합니다.
        # 디코딩되지 못한 건 일단 원래 RSS 주소를 가지고 리스트에 추가됩니다.
        decode_limit = 25
        decode_targets = new_unique_articles[:decode_limit]
        remain_targets = new_unique_articles[decode_limit:]
        
        print(f"Decoding actual URLs for the first {len(decode_targets)} new articles...")
        
        decoded_articles = []
        for idx, item in enumerate(decode_targets):
            raw_url = item["link"]
            print(f" -> [{idx+1}/{len(decode_targets)}] Decoding: {item['title'][:40]}...")
            
            try:
                # 1초 대기 후 호출하여 안정성 확보
                time.sleep(1)
                decoded_res = new_decoderv1(raw_url, interval=1)
                
                if decoded_res.get("status"):
                    item["link"] = decoded_res["decoded_url"]
                    print(f"    Success: {item['link'][:60]}")
                else:
                    print(f"    Failed: {decoded_res.get('message')}")
            except Exception as e:
                print(f"    Error during decoding: {e}")
                
            decoded_articles.append(item)
            
        # 디코딩 완료된 기사 + 디코딩 제한에 의해 미뤄진 기사들 합치기
        processed_new_articles = decoded_articles + remain_targets
    else:
        if not HAS_DECODER:
            print("Decoder library is not installed. Skipping URL decoding.")
        processed_new_articles = new_unique_articles

    # 기존 뉴스에 신규 가공 뉴스 병합
    for item in processed_new_articles:
        title = item.get("title", "").strip()
        existing_news_dict[title] = item  # 기존 데이터가 있으면 신규 데이터로 교체/없으면 새로 추가
        
    # 정렬 및 최대 보관 수(150개) 제한
    final_news = list(existing_news_dict.values())
    final_news.sort(key=lambda x: x.get("pubDate", ""), reverse=True)
    final_news = final_news[:150]
    
    # 저장
    try:
        with open(NEWS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(final_news, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved {len(final_news)} articles to {NEWS_FILE_PATH}")
    except Exception as e:
        print(f"Error saving final news: {e}")

if __name__ == "__main__":
    main()

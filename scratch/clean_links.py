import os
import json
import time
from googlenewsdecoder import new_decoderv1

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_FILE_PATH = os.path.join(BASE_DIR, "data", "news.json")

def main():
    print("Starting full URL decoding cleanup...")
    
    if not os.path.exists(NEWS_FILE_PATH):
        print("news.json does not exist!")
        return

    with open(NEWS_FILE_PATH, "r", encoding="utf-8") as f:
        news_data = json.load(f)
        
    undecoded_articles = [item for item in news_data if "news.google.com" in item.get("link", "")]
    print(f"Total articles: {len(news_data)}")
    print(f"Undecoded articles (Google News links): {len(undecoded_articles)}")
    
    if not undecoded_articles:
        print("All URLs are already decoded!")
        return
        
    print("Decoding Google News links to original URLs...")
    success_count = 0
    fail_count = 0
    
    try:
        for idx, item in enumerate(undecoded_articles):
            title = item.get("title", "")
            raw_url = item.get("link", "")
            
            print(f"[{idx+1}/{len(undecoded_articles)}] Decoding: {title[:40]}...")
            
            # 1.5초 딜레이로 429 우회
            time.sleep(1.5)
            
            try:
                res = new_decoderv1(raw_url, interval=1.5)
                if res.get("status"):
                    item["link"] = res["decoded_url"]
                    success_count += 1
                    print(f" -> Success: {item['link'][:60]}")
                else:
                    fail_count += 1
                    print(f" -> Failed: {res.get('message')}")
                    # 만약 지속적으로 실패하거나 차단 메시지가 뜨면 중지
                    if "429" in str(res.get("message")) or "block" in str(res.get("message")).lower():
                        print("Rate limited or blocked by Google. Stopping for safety.")
                        break
            except Exception as e:
                fail_count += 1
                print(f" -> Error: {e}")
                
            # 매 성공할 때마다 데이터를 저장해서 유실 방지
            with open(NEWS_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
                
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        
    print(f"\nCleanup complete. Success: {success_count}, Failed/Skipped: {fail_count}")

if __name__ == "__main__":
    main()

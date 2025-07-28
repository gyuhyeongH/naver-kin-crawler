from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# =====================================
# Google Sheets 인증
# =====================================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("naver_kin_log").sheet1

# 이미 저장된 제목 목록 (중복 방지)
existing_titles = [row[1] for row in sheet.get_all_values()[1:]]  # 첫 행은 헤더 제외

# =====================================
# 네이버 지식인 인기 Q&A 크롤러
# =====================================
def crawl_kin_popular():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    driver.get("https://kin.naver.com")
    time.sleep(5)

    items = driver.find_elements(By.CSS_SELECTOR, "li.ranking_item")
    base_url = "https://kin.naver.com"

    for item in items:
        try:
            # 제목
            title_elem = item.find_element(By.CSS_SELECTOR, "a.ranking_title")
            title = title_elem.get_attribute("textContent").strip()

            # 중복 체크
            if title in existing_titles:
                continue

            # 조회수
            views = item.find_element(By.CSS_SELECTOR, "span.recommend_num").get_attribute("textContent")
            views = views.replace("조회수", "").strip()

            # 답변수
            replies = item.find_element(By.CSS_SELECTOR, "span.reply_num").get_attribute("textContent")
            replies = replies.replace("답변수", "").strip()

            # URL
            url = title_elem.get_attribute("href")

            # 저장 시간
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Google Sheets에 저장
            sheet.append_row([now, title, views, replies, url])
            existing_titles.append(title)

            print(f"✅ 저장됨: {title} | 조회수 {views} | 답변수 {replies}")

        except Exception as e:
            print("❌ 항목 처리 중 오류:", e)

    driver.quit()
    print("크롤링 완료!")

# 실행
crawl_kin_popular()

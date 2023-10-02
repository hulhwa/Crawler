import chromedriver_autoinstaller
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ChromeDriver 자동 설치
chromedriver_autoinstaller.install()

# Chrome 웹드라이버 시작
driver = webdriver.Chrome()

# 주어진 URL 열기
driver.get("https://www.flightconnections.com/")

# 8초 대기
time.sleep(8)

# '#airline-options > div.custom-cursor-default-hover > div.all-airline-options' 아래에 있는 a 태그들을 수집
a_tags = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#airline-options > div:nth-child(3) > div.all-airline-options a"))
)

# 각 a 태그의 href 속성 수집
links = [a.get_attribute('href') for a in a_tags]

# 웹드라이버 종료
driver.quit()

# 수집한 링크를 links.txt 파일에 저장
with open("links.txt", "w", encoding="utf-8") as file:
    for link in links:
        file.write(link + "\n")

print("Links have been saved to links.txt.")
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import chromedriver_autoinstaller
import requests
import json
import time

def fetch_info(iata_code):
    base_url = "https://www.airportal.go.kr/knowledge/airlines/KbAirline01.jsp?PAGENO=1&PAGEROWS=10&START=&keyword1=&keyword2=&gubun=&sortvalue=&order=&area=code&target=iata_code&search="
    url = base_url + iata_code
    
    chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists and if not, download it automatically.
    browser = webdriver.Chrome()
    browser.get(url)
    time.sleep(3)
    try:
        css_selector = "body > table > tbody > tr:nth-child(5) > td:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2) > table > tbody > tr:nth-child(6) > td > table > tbody > tr:nth-child(2) > td:nth-child(5) > a"
        element = browser.find_element(By.CSS_SELECTOR, css_selector)
        IATA_CODE_BROWSER = element.text
    except NoSuchElementException:
        with open('error_log.txt', 'a') as log_file:  # 'error_log.txt'라는 로그 파일에 추가 모드로 기록
            log_file.write(f"not found for IATA code: {iata_code}\n")
    main_window = browser.current_window_handle
    
    
    try:
        link = browser.find_element(By.CSS_SELECTOR, "body > table > tbody > tr:nth-child(5) > td:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2) > table > tbody > tr:nth-child(6) > td > table > tbody > tr:nth-child(2) > td:nth-child(4) > a")
        link.click()
        time.sleep(0.5)
        # 새 창의 핸들을 얻는다
        new_window = [window for window in browser.window_handles if window != main_window][0]
        browser.switch_to.window(new_window)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        details = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td:nth-child(1)")[0]
        
        name = details.contents[0].strip()
        ko = details.contents[2].strip()
        link = details.contents[4]['href']

        data = {
            'IATA': IATA_CODE_BROWSER,
            'name': name,
            'ko': ko,
            'link': link,
        }

        # ICAO
        icao_elem = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(5) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td.text_color_blue02_b")
        data['ICAO'] = icao_elem[0].text if icao_elem else "NULL"

        # status
        status_elem = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(5) > td:nth-child(4)")
        data['status'] = status_elem[0].text if status_elem else "NULL"

        # callsign
        callsign_elem = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(9) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(1)")
        data['callsign'] = callsign_elem[0].text if callsign_elem else "NULL"

        # city
        city_elem = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(12) > td:nth-child(2)")
        data['city'] = city_elem[0].text if city_elem else "NULL"

        # capital
        capital_elem = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(12) > td:nth-child(4)")
        data['capital'] = capital_elem[0].text if capital_elem else "NULL"

        # country
        country_elem = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(15) > td:nth-child(2)")
        data['country'] = country_elem[0].text if country_elem else "NULL"

        # era
        era_elem = soup.select("body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(15) > td:nth-child(4)")
        data['era'] = era_elem[0].text if era_elem else "NULL"

        img_tag = soup.select_one('body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td:nth-child(3) > table > tbody > tr > td > img')
        img_url = img_tag['src']
        current_url = browser.current_url
        img_url_absolute = urljoin(browser.current_url, img_url)
        img_data = requests.get(img_url_absolute).content
        # 이미지 파일로 저장
        with open(fr"img\{iata_code}.jpg", 'wb') as handler:
            handler.write(img_data)
        
        # Convert to JSON
        json_data = json.dumps(data, ensure_ascii=False)
        print(json_data)

        # 데이터를 JSON 파일에 추가
        append_to_json(data)
    except:
        with open("logfile.txt", "a") as f:
            f.write(f"No data found for IATA code: {iata_code}\n")

    browser.quit()

def main():
    print("hi")
    # links.txt에서 링크를 읽고 IATA 코드 추출
    with open("links.txt", "r") as file:
        lines = file.readlines()
        iata_codes = [line.strip().split("-")[-1].split('/')[-1].upper() for line in lines]
    
    # 모든 IATA 코드에 대해 fetch_info 함수 호출
    for iata_code in iata_codes:
        fetch_info(iata_code)

    print("All data fetched successfully!")
def append_to_json(data):
    try:
        with open("airline.json", "r") as file:
            existing_data = json.load(file)
            if not isinstance(existing_data, list):  # 데이터가 리스트가 아닐 경우 리스트로 변환
                existing_data = [existing_data]
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open("airline.json", "w") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
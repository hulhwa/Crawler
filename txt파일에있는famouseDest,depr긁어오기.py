import chromedriver_autoinstaller
import json
import requests
from bs4 import BeautifulSoup

def log_error(url, message):
    with open("error_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"URL: {url}\nError: {message}\n\n")

def crawl_data(url):
    if "flightconnections.com" not in url:
        print(f"Invalid URL: {url}")
        return

    chromedriver_autoinstaller.install()
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    data = []
    # 세 번째 div.airline-destinations-list만 선택
    destinations_list = soup.select("div.airline-destinations-list")[2]
    
    links = destinations_list.find_all("a")
    for link in links:
        description = link.contents[0].strip()
        if link.find("span"):
            span_text = link.find("span").get_text(strip=True)
            if " to " in span_text:
                departure, destination = span_text.split(" to ")
            else:
                log_error(url, f"Unexpected format for span text: {span_text}")
                continue
        else:
            log_error(url, "Span element not found")
            continue
        
        data.append({
            "description": description,
            "departure": departure,
            "destination": destination
        })

    filename = url.split("/")[-1] + ".json"
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"Data saved to {filename}!")

# links.txt 파일에서 링크를 읽어들입니다.
with open("links.txt", "r") as file:
    urls = file.readlines()

# 각 URL을 크롤링합니다.
for url in urls:
    crawl_data(url.strip())
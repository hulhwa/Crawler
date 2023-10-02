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
    destinations_lists = soup.select("div.airline-destinations-list")[:2]

    labels = ["destination", "departure"]
    for idx, destinations_list in enumerate(destinations_lists):
        links = destinations_list.find_all("a")
        for link in links:
            main_text = link.get_text(strip=True).split("\n")[0]
            span_text = link.find("span", class_="float-right").get_text(strip=True) if link.find("span", class_="float-right") else ""
            
            if not main_text or not span_text:
                log_error(url, f"Missing data for country: {main_text} or code: {span_text}")
            
            data.append({
                "flight": labels[idx],
                "country": main_text,
                "code": span_text
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
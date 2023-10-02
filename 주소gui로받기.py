import tkinter as tk
from tkinter import Entry, Button, Label
from selenium import webdriver
import chromedriver_autoinstaller
import json
import requests
from bs4 import BeautifulSoup

def log_error(url, message):
    with open("error_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"URL: {url}\nError: {message}\n\n")

def crawl_data():
    url = url_entry.get()

    if "flightconnections.com" not in url:
        result_label.config(text="Invalid URL!")
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

    result_label.config(text=f"Data saved to {filename}!")

app = tk.Tk()
app.title("Flightconnections Crawler")

Label(app, text="Enter URL:").pack(pady=10)
url_entry = Entry(app, width=50)
url_entry.pack(pady=10)
Button(app, text="Execute", command=crawl_data).pack(pady=10)
result_label = Label(app, text="")
result_label.pack(pady=10)

app.mainloop()
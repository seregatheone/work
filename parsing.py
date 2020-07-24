import csv
import os
import time

import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver

host = "https://vk.com/"
url = "https://vk.com/@yvkurse"
filename = input("Название файла : ")
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.77",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}


# get html from site
def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


# Load all content(doesn't work)
# вк работает по другим принципам, поэтому селениум решил, что не нужно прогружать всё
def get_all_content():
    driver = webdriver.Chrome(executable_path="C:\webdrivers\chromedriver.exe")
    driver.get(url)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    SCROLL_PAUSE_TIME = 3
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    try:
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            driver.refresh()
        return driver.page_source
    except:
        print("err")


# main algorithm
def parse():
    html = get_html(url)
    if html.status_code == 200:
        get_all_content()
        save_file(get_content(html.text))
        os.startfile(filename + ".csv")
    else:
        print("Ошибка на сервере")


# parsing
def get_content(html):
    soup = BS(html, "html.parser")
    articles = []
    items = soup.find_all("div", class_="author_page_grid_article")
    for item in items:
        b = item.find("div", class_="author_page_bottom_info__date_and_views").get_text()
        articles.append({
            "title": item.find("div", class_="author_page_grid_article__title author_page_article_title").get_text(),
            "info": item.find("div", class_="author_page_grid_article__subtitle").get_text(),
            "image": item.find("div", class_="author_page_grid_article__image author_page_article_image").get("style")[
                     22:-1],
            "date": item.find("div", class_="author_page_bottom_info__date_and_views").get_text()[:b.index(":") + 3],
            "views": item.find("span", class_="dvd").get_text(),
            "link": host + item.find("a").get("href")
        })
    return articles


# saving file
def save_file(items, path=(filename + ".csv")):
    with open(path, "w", newline="", encoding="utf16")as file:
        writter = csv.writer(file, delimiter="\t")
        writter.writerow(["Название", "Информация", "Картинку", "Дата", "Просмотры", "Ссылка"])
        for item in items:
            writter.writerow([item["title"], item["info"], item["image"], item["date"], item["views"], item["link"]])


parse()

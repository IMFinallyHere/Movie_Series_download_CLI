import os
import time

from bs4 import BeautifulSoup as bs4
import requests as rq
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re


# noinspection PyBroadException
class Movieflix:
    def __init__(self):
        self.website_url = ''
        self.query_found = False
        self.refined_results = []
        self.search_results = []
        self.name = []
        self.diff = False
        self.link_broken = False
        self.chrome_driver_path = 'C:\\Users\\Priyansh\\PycharmProjects\\auto-download\\chromedriver.exe'
        self.options = Options()
        self.options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        self.options.add_experimental_option('detach', True)
        # fdm
        self.options.add_extension('C:\\Users\\Priyansh\\PycharmProjects\\auto-download\\extension_3_0_57_0.crx')

    def search(self):
        os.system('cls')
        while True:
            movie_type = input('Bollywood or Hollywood??, H/B: ').upper()
            if movie_type == 'H':
                self.website_url = 'https://themoviezflix.org'
                break
            elif movie_type == 'B':
                self.website_url = 'https://hdmoviezflix.org'
                break
            else:
                print('Wrong input')

        user_looking_for = input('Enter name of movie u r looking for 😎:').replace(' ', '+')
        print('Searching....')
        response = rq.get(f'{self.website_url}/?s={user_looking_for}')
        soup = bs4(response.text, 'html.parser')
        search_results = soup.select('#content_box .latestPost h2 a')
        if len(search_results) != 0:
            self.query_found = True
            self.search_results = search_results

        else:
            print('¯\_(ツ)_/¯')
            print('Not found')
            again = input('Want to download another...Y/N:')
            if again.lower() == 'y':
                os.system('cls')
                print('Feature comming soon...')

    def refine_search(self):
        for item in self.search_results:
            a = item.getText().replace('Download', '')
            a = re.sub('\|.*', '', a)
            a = re.sub("WEB.*|WeB.*|BRRip.*|BluRay.*|Bluray.*|360p.*|480p.*|720p.*|1080p.*|Web.*", '', a)
            self.refined_results.append(a)

    def find_correct_choice(self):
        if not self.query_found:
            return

        i = 1
        print('Enter:')
        for item in self.refined_results:
            print(f'{i} for -> {item}')
            i += 1
        if input('Is ur choice in the list??Y/N: ').lower() != 'n':
            n = [int(i) - 1 for i in input(
                'Enter number from list above, u can also download multiple just seperate number by "," : ').split(',')]
            media_page = []
            for i in n:
                media_page.append(self.search_results[i].get('href'))
                self.name.append(self.refined_results[i])
            return media_page
        else:
            os.system('cls')
            print('Sorry...')
            if input('Want to download another...Y/N: ').lower() == 'y':
                self.search()
            else:
                self.query_found = False
            return

    def down_pg_1(self, media_pg):
        if not self.query_found:
            return

        res = rq.get(media_pg)
        soup = bs4(res.text, 'html.parser')
        try:
            a = soup.select('.maxbutton-post-button-1')[-1].get('href')
        except Exception:
            a = soup.select('.maxbutton-post-button')[-1].get('href')
        return a

    def down_pg_2(self, link):
        if not self.query_found:
            return

        driver = webdriver.Chrome(options=self.options, service=Service(self.chrome_driver_path))
        driver.minimize_window()
        driver.get(link)

        try:
            a = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'maxbutton-fast-server-g-direct-2')))
        except Exception:
            try:
                a = WebDriverWait(driver, 11).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'maxbutton-fast-server-g-direct')))
            except Exception:
                a = WebDriverWait(driver, 11).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'maxbutton-g-direct')))
                self.diff = True
        a = a.get_attribute('href')
        if 'https://' not in a:
            driver.quit()
            self.link_broken = True
            return

        driver.quit()
        return a

    def down_pg_3(self, link):
        if not self.query_found:
            return
        if self.link_broken:
            return

        soup = bs4((rq.get(link)).text, 'html.parser')
        a = soup.select_one('#editPrivacyBtn').get('onclick')[15:-2]
        return a

    def final_pg(self, link, name):
        if not self.query_found:
            return
        if self.link_broken:
            return
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"
        driver = webdriver.Chrome(options=self.options, service=Service(self.chrome_driver_path),
                                  desired_capabilities=capa)
        driver.minimize_window()
        driver.get(link)
        try:
            a = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.LINK_TEXT, 'Download Now')))
            a.click()
            while len(driver.window_handles) > 1:
                pass
            os.system('cls')
            print(f'{name}download success...😀😀😀😀')
        except Exception:
            os.system('cls')
            print('Movie link broken..cant download...')
            driver.quit()
            return

        driver.quit()
        return


mf = Movieflix()
mf.search()
mf.refine_search()
for i, name in zip(mf.find_correct_choice(), mf.name):
    os.system('cls')
    print(f'Downloading --> {name}')
    link = mf.down_pg_2(mf.down_pg_1(i))
    if mf.link_broken:
        mf.link_broken = False
        print('Movie link broken..cant download...')
        continue
    if mf.diff:
        mf.final_pg(link, name)
        mf.diff = False
    else:
        mf.final_pg(mf.down_pg_3(link), name)

print('Thanks for using PServices..🤪🤪🤪')

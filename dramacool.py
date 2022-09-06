import os
import time
from bs4 import BeautifulSoup as bs4
import requests as rq
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# noinspection PyBroadException,PyMethodMayBeStatic
class DramaCool:
    def __init__(self):
        self.website_url = 'https://dramacool.cr'
        self.query_found = False
        self.ep_to_download = []
        self.ep_number = []
        self.movie = False

    def search(self):
        os.system('cls')
        user_looking_for = input('Enter name of series/movie u r looking for 😎:').replace(' ', '+')
        print('Searching....')
        response = rq.get(f'{self.website_url}/search?type=movies&keyword={user_looking_for}')
        soup = bs4(response.text, 'html.parser')
        search_results = soup.select('ul li a h3')
        if len(search_results) != 0:
            self.query_found = True
            return search_results
        else:
            print('¯\_(ツ)_/¯')
            print('Not found')
            print('Sorry')

        return

    def find_correct_choice(self, search_results):
        if not self.query_found:
            return
        i = 1
        print('Enter:')
        for item in search_results:
            print(f'{i} for -> {item.getText()}')
            i += 1
        media_page = (
            (search_results[int(input('Which:')) - 1].get('onclick')).replace('window.location = \'', '')).replace('\'',
                                                                                                                   '')
        return self.website_url + media_page

    def get_all_ep_pg(self, media_page):
        if not self.query_found:
            return

        response = rq.get(media_page)
        soup = bs4(response.text, 'html.parser')
        some_useless_data = soup.select('.all-episode li a h3')
        ep_pg = [self.website_url + ((ep.get('onclick')).replace('window.location = \'', '').replace('\'', '')) for ep
                 in some_useless_data]
        ep_pg.reverse()
        if len(ep_pg) > 1:
            os.system('cls')
            print(f'There are {len(ep_pg)} episodes')
            ep_numbers = input('Enter episode numbers separated by "," or\nspecify start til end using 1-7 :')
            if '-' in ep_numbers:
                ep_numbers = ep_numbers.split('-')
                lis = []
                for i in range(int(ep_numbers[0]), int(ep_numbers[1]) + 1):
                    lis.append(i)
                ep_numbers = lis
            else:
                ep_numbers = ep_numbers.split(',')
            self.ep_number = [int(i) - 1 for i in ep_numbers]
        else:
            self.ep_number = [0]
            print('Got ur movie...✌✌')
            self.movie = True

        for i in self.ep_number:
            self.ep_to_download.append(ep_pg[i])

        return

    def get_ep_download_links(self):
        if not self.query_found:
            return

        ep_download = []
        for ep in self.ep_to_download:
            response = rq.get(ep)
            soup = bs4(response.text, 'html.parser')
            some_useless_data = soup.select('.download a')
            for i in some_useless_data:
                ep_download.append("https://" + str(i).split('\n')[0][11:-18])
        return ep_download

    def downloading(self, ep_download):
        if not self.query_found:
            return

        chrome_driver_path = '.\\chromedriver.exe'

        options = Options()
        # browser location
        options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        # fdm
        options.add_extension('.\\fdm.crx')
        # buster
        options.add_extension('.\\buster.crx')

        options.add_experimental_option('detach', True)

        for link, n in zip(ep_download, self.ep_number):
            os.system('cls')
            if self.movie:
                print(f'Downloading ur movie...')
            else:
                print(f'Downloading episode {n + 1}...😊')

            driver = webdriver.Chrome(options=options, service=Service(chrome_driver_path))
            driver.minimize_window()
            driver.get(link)
            if self.check_captcha(driver):
                driver.maximize_window()
                WebDriverWait(driver, 10000).until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
                WebDriverWait(driver, 1000).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
                WebDriverWait(driver, 1000).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[@id='recaptcha-anchor' and @aria-checked='true']")))
                driver.switch_to.default_content()
                driver.find_element(By.ID, 'btn-submit').click()
                driver.minimize_window()
                time.sleep(5)

            for i in range(4, 0, -1):
                try:
                    btn = driver.find_element(By.XPATH, f'/html/body/section/div/div[2]/div/div[4]/div[1]/div[{i}]')
                except Exception:
                    pass
                else:
                    btn.click()
                    driver.minimize_window()
                    break

            time.sleep(1)
            driver.quit()
            print('Browser closed')

        return

    def check_captcha(self, driver):
        """Returns true if captcha found on page"""
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "captcha-v2"))
            )
        except Exception:
            return False
        else:
            return True


if __name__ == '__main__':
    dc = DramaCool()
    dc.get_all_ep_pg(dc.find_correct_choice(dc.search()))
    dc.downloading(dc.get_ep_download_links())
    os.system('cls')
    if not dc.query_found:
        print('¯\_(ツ)_/¯')
        print('Not found')
        print('Sorry')
    print('Thanks for using PServices..🤪🤪🤪')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
import sys
import yaml


def parse_ad(ad_file):
    try:
        with open(ad_file) as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except Exception:
        sys.exit("Please use the correct filename")


def dump_html(html):
    with open("dump.html", 'w') as f:
        f.write(html)
        f.close()


def validate(html, url):
    good_message = "You have successfully posted your ad!"
    if good_message in html:
        print("Looks like the ad was posted succesfully")
        print(f"ad URL: {url}")
    else:
        print("I think we got an error uploading.")
        dump_html(html)


class Bot:

    def __init__(self, **kwargs):
        self.headless = kwargs.get("headless", True)

        if self.headless is True:
            options = Options()
            options.headless = self.headless
            self.bot = webdriver.Firefox(options=options)
        else:
            self.bot = webdriver.Firefox()

    def login(self, username, password):
        bot = self.bot
        self.username = username
        self.password = password
        bot.get("https://www.kijiji.ca/t-login.html")
        uname_field = bot.find_element_by_id("LoginEmailOrNickname")
        uname_field.send_keys(self.username)
        pword_feild = bot.find_element_by_id('login-password')
        pword_feild.send_keys(self.password)
        bot.find_element_by_xpath('//*[@id="SignInButton"]').click()
        time.sleep(5)

    def create_service_post(self, **kwargs):
        bot = self.bot
        self.ad_title = kwargs.get("ad_title")
        self.ad_desc = kwargs.get("ad_desc")
        self.address = kwargs.get("address")
        self.ad_url = kwargs.get("ad_url")
        self.photo = kwargs.get("photo")
        bot.get(self.ad_url)
        
        time.sleep(8)
        print(bot.current_url)
        # enter ad title
        WebDriverWait(bot, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="postad-title"]'))).send_keys(self.ad_title)

        # ad desc
        WebDriverWait(bot, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="pstad-descrptn"]'))).send_keys(self.ad_desc)
        
        # ad address
        WebDriverWait(bot, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="pstad-map-address"]'))).send_keys(self.address)

        time.sleep(1)
        # lets make sure to ad a photo
        bot.execute_script("""
            document.addEventListener('click', function(evt) {
            if (evt.target.type === 'file')
                evt.preventDefault();
            }, true)
            """)
        elem = bot.find_element_by_css_selector('input[type=file]').send_keys('/Users/getty/personal/KijijiReposter/1.jpeg')
        
        time.sleep(15)  # Wait for file to upload
        
        # Since the package section has a few popups, we need to use the execute script on the elem
        element = WebDriverWait(bot, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="MainForm"]/div[6]/div/div/div/div[1]/div[1]/div[1]/div/button')))
        bot.execute_script("arguments[0].click();", element)

        time.sleep(1)
        WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainForm"]/div[10]/button[1]'))).click()
        print("We've sent the request in!")
        
        # run validate to parse the html source
        validate(bot.page_source, bot.current_url)
        
    def create_buysell_post(self, **kwargs):
        bot = self.bot
        self.ad_title = kwargs.get("ad_title")
        self.ad_desc = kwargs.get("ad_desc")
        self.address = kwargs.get("address")
        url_title = self.ad_title.replace(' ', '+')
        url = f"https://www.kijiji.ca/p-admarkt-post-ad.html?categoryId=29324001&adTitle={url_title}"
        bot.get(url)
        WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pstad-descrptn"]'))).send_keys(self.ad_desc)
        #WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pstad-map-address"]'))).send_keys(self.address)

        WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainForm"]/div[7]/div/div/li/div/div[2]/div[3]/label'))).click()
        time.sleep(1)
        WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainForm"]/div[10]/button[1]'))).click()
        time.sleep(10) # Wait 10 seconds for page to load once ad is posted
        html = bot.page_source
        check_for_errors(html)
        url = bot.current_url
        check_success(html, url)

    def delete_all_ads(self, **kwargs):
        bot = self.bot
        
        def delete(delete_url):
            current_ads =[]
            bot.get(delete_url)
            time.sleep(3)
            ads = bot.find_element_by_xpath('//*[@id="mainPageContent"]/div/div/div/div[4]/ul')
            for elem in ads.find_elements_by_css_selector('li'):
                for i in elem.find_elements_by_css_selector('a'):
                    if len(i.text) > 8:
                        ad_title = i.text
                        ad_link = i.get_attribute('href')
                        current_ads.append({
                            "title": ad_title,
                            "url": ad_link
                            })
                if "Delete" in elem.text:
                    elem.click()      
            return current_ads  
        
        inactive = delete('https://www.kijiji.ca/m-my-ads/inactive/1')
        active = delete('https://www.kijiji.ca/m-my-ads/active/1')
        print("Deleting ads")
        print(f"  inactive: {inactive}")
        print(f"  active  : {active}")
        
    def nuke_ads(self):
        bot = self.bot
        bot.get('https://www.kijiji.ca/m-my-ads/')
        elem = bot.find_element_by_xpath('/html/body/div[2]/div[4]/div/div/div/div[4]/ul/li')
        for i in elem:
            print(i.text)

    def teardown(self):
        bot = self.bot
        bot.quit()


# ad = parse_ad("ad.yaml")
ad = parse_ad("alex_ad.yaml")
automate = Bot(headless=False)
automate.login(ad['username'], ad['password'])
automate.create_service_post(
    ad_title=ad['name'],
    ad_desc=ad['description'],
    address=ad['address'],
    ad_url=ad['create_ad_url'],
    photo="/Users/getty/personal/KijijiReposter/1.jpeg")
#automate.teardown()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

from huepy import good, bad, info
from geopy.geocoders import Nominatim
import logging
import time
logging.basicConfig(filename="backend.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
import time
import sys
import yaml

def getgeo(city, province):
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    location = geolocator.geocode(f"{city}, {province}")
    return location.latitude, location.longitude
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
def get_url_by_city(city):
    url = {
        "calgary": "https://www.kijiji.ca/b-calgary/l1700199?ll=51.044733%2C-114.071883&address=Calgary%2C+AB&radius=50.0&dc=true",
        "edmonton": "https://www.kijiji.ca/b-edmonton/e/k0l1700203?ll=53.546125%2C-113.493823&address=Edmonton%2C+AB&radius=50.0&dc=true",
        "vancouver": "https://www.kijiji.ca/b-vancouver/e/k0l1700287?ll=49.282729%2C-123.120738&address=Vancouver%2C+BC&radius=50.0&dc=true",
        "victoria": "https://www.kijiji.ca/b-victoria-bc/e/k0l1700173?ll=48.428421%2C-123.365644&address=Victoria%2C+BC&radius=50.0&dc=true",
        "winnipeg": "https://www.kijiji.ca/b-winnipeg/e/k0l1700192?ll=49.895136%2C-97.138374&address=Winnipeg%2C+MB&radius=50.0&dc=true"
    }
    return url[city.lower()]


def validate(html, url, bot):
    good_message = "You have successfully posted your ad!"
    if good_message in html:
        print(good("Ad was posted succesfully"))
        print(info(f"Ad URL: {url}"))
    else:
        print(bad("There was an error posting the ad. Dumping HTML file."))
        dump_html(html)
        bot.get_screenshot_as_file('output.png') 


def handle_region(city, prov, bot):
    WebDriverWait(bot, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="SearchLocationPicker"]'))).click()


    WebDriverWait(bot, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="downshift-2-input"]'))).click()
    
    for i in range(50):
        bot.find_element_by_xpath('//*[@id="downshift-2-input"]').send_keys(Keys.BACKSPACE)
    
    WebDriverWait(bot, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="downshift-2-input"]'))).send_keys(f"{city}, {prov}")
    time.sleep(1)
    
    WebDriverWait(bot, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="downshift-2-input"]'))).send_keys(Keys.ENTER)

    try:
        
        WebDriverWait(bot, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[11]/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/button'))).click()
    except TimeoutException: 
        WebDriverWait(bot, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[10]/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/button'))).click()
    except TimeoutException:
        WebDriverWait(bot, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[12]/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/button'))).click()
    except:
        print("Well, we couldnt find the 'Apply' button when setting the location")
class Bot:
    def __init__(self, **kwargs):
        self.headless = kwargs.get("headless", True)

        # Setup profile
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("geo.enabled", False);
        firefox_profile.set_preference("geo.prompt.testing", True)
        firefox_profile.set_preference("geo.prompt.testing.allow", False)
        
        if self.headless is True:
            options = Options()
            options.headless = self.headless
            self.bot = webdriver.Firefox(firefox_profile=firefox_profile, options=options)
            print(info(f"Bot Initialized headless"))
        else:
            self.bot = webdriver.Firefox(firefox_profile=firefox_profile)
            print(info("Bot initialized."))

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
        # If we're logged in, the text "Register should not be visible"
        assert "Register" not in bot.page_source, "Failed to login."
        print(good(f"Succesfully logged into {self.username}"))
        logging.info(f"We're logged in to: {self.username}")

    def create_service_post(self, **kwargs):
        bot = self.bot
        self.ad_title = kwargs.get("ad_title")
        self.ad_desc = kwargs.get("ad_desc")
        self.address = kwargs.get("address")
        self.ad_url = kwargs.get("ad_url")
        self.photo = kwargs.get("photo")
        self.province = kwargs.get("province")
        self.city = kwargs.get("city")
        logging.info("Trying to create services post witht he following arguments.")
        logging.info(kwargs)
        time.sleep(3)
        print(info(f"Clicking the right buttons to post an ad in {self.city}, {self.province}"))
        bot.get("https://www.kijiji.ca")
        handle_region(self.city, self.province, bot)
        
       
        time.sleep(10)
        bot.get(self.ad_url)
        
        time.sleep(8)
        logging.info("Waited for some time, and now we're going to post an ad.")
        # Check to see if we get in coprrectly 
        assert 'p-post-ad.html' in bot.current_url
        
        logging.info("Trying to send data to ad title")
        # enter ad title
        WebDriverWait(bot, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="postad-title"]'))).send_keys(self.ad_title)
        logging.info("Trying to send data to ad description")
        # ad desc
        WebDriverWait(bot, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="pstad-descrptn"]'))).send_keys(self.ad_desc)
        
        logging.info("Trying to send data to ad address")
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
        logging.info("Trying to send data to ad photo")
        elem = bot.find_element_by_css_selector('input[type=file]').send_keys(self.photo)
        
        time.sleep(15)  # Wait for file to upload
        
        # Since the package section has a few popups, we need to use the execute script on the elem
        logging.info("We're clicking on the basic package.")
        element = WebDriverWait(bot, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="MainForm"]/div[6]/div/div/div/div[1]/div[1]/div[1]/div/button')))
        bot.execute_script("arguments[0].click();", element)

        time.sleep(1)
        
        logging.info("We're clicking on the submit button.")
        WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainForm"]/div[10]/button[1]'))).click()
        print(info("Ad has been submitted, running validation."))
        
        # run validate to parse the html source
        
        validate(bot.page_source, bot.current_url, bot)
        
        
    def nuke_ads(self):
        bot = self.bot
        bot.get('https://www.kijiji.ca/m-my-ads/active')
        try:
            
            elem = bot.find_element_by_xpath('/html/body/div[3]/div[4]/div/div/div/div[4]/ul')
            for i in elem.find_elements_by_css_selector('li'):
                if i.text == "Delete":
                    i.click()
                    print(info("Deleting an active ad."))
                    time.sleep(3)
        except:
            pass
                
        bot.get('https://www.kijiji.ca/m-my-ads/inactive')
        try:
            
            elem = bot.find_element_by_xpath('/html/body/div[3]/div[4]/div/div/div/div[4]/ul')
            for i in elem.find_elements_by_css_selector('li'):
                if i.text == "Delete":
                    i.click()
                    print(info("Deleting an active ad."))
                    time.sleep(3)
        except:
            pass

    def teardown(self):
        bot = self.bot
        bot.quit()


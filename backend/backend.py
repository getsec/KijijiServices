from sql import *
from bot import Bot
from huepy import bad, good, info
import logging
import time
logging.basicConfig(filename="backend.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

logging.info("Initialized the backend script")


photo_dir = "/Users/getty/personal/KijijiReposter/frontend"
table_name = "my-flask-app-dev"
all_items = scan_table_allpages(table_name)
logging.info(f"Gathered items from database. Count {len(all_items)}")

# For eaach ad
for ad in all_items:
    ad_title = ad['ad_title']
    ad_desc = ad['ad_desc']
    password = ad['password']
    username = ad['uuid']
    province = ad['province']
    city = ad['city']
    category = ad['category']
    photo =  photo_dir + '/' + ad['photo_path']
    logging.info(f"Deleting ads for {username}")
    # # Delete ads associated with user
    # automate = Bot(headless=True)
    # automate.login(username, password)
    # automate.nuke_ads()
    # automate.teardown()
    
    # print(info("Teardown succesful, sleeping for 2 minutes then reposting it."))
    # time.sleep(60)
    # print(info("    --> sleeping for another minute! "))
    # time.sleep(60)
    # logging.info(f"creating ads for {username}")
    # logging.info(ad)
    # print(info(f"Time over. Running ad creation for {username}"))
    if province == "MB":
        automate = Bot(headless=False)
        automate.login(username, password)
        automate.create_service_post(
            ad_title=ad_title,
            ad_desc=ad_desc,
            province=province,
            city=city,
            address="Tanya Cres, Winnipeg MB",
            ad_url=category,
            photo=photo)
        automate.teardown()

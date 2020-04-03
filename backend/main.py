from KijijiReposter.bot import Bot
from KijijiReposter.bot import parse_ad

import click

@click.command("post")
@click.option('-u', "user", help="Kijiji Username")
@click.option('-p', "password", help="Kijiji Password")
@click.option('-f', "file", help="Path to Ad File")
def post_ad(user, password, file):
    ad = parse_ad(file)
    automate = Bot(headless=True)
    automate.login(ad['username'], ad['password'])
    automate.create_service_post(
        ad_title=ad['name'],
        ad_desc=ad['description'],
        address=ad['address'],
        ad_url=ad['create_ad_url'],
        photo=ad['image_path'])
    automate.teardown()
    
@click.command("delete")
@click.option('-u', "user", help="Kijiji Username")
@click.option('-p', "password", help="Kijiji Password")
def delete_ads(user, password):
    automate = Bot(headless=True)
    automate.login(user, password)
    automate.delete_all_ads()
    
if __name__ in "__main__":
    post_ad()
import json
import os
import re

import requests
from bs4 import BeautifulSoup
from pyfuncs import *


# Download links for insexsity are just http://insexsity.com/$VERSION_$OS_64_(U).zip
# so they can be easily generated.
# Note: insexsity calls the OS "windows" "PC"
def update_insexsity_download_links(old_version, new_version):
    json_list = []
    for sub_array in load_json():
        if sub_array["game"].lower() == "insexsity":
            for opsys in ["windows", "mac", "android"]:
                sub_array["download_link_{}".format(opsys)] = sub_array["download_link_{}".format(opsys)].replace(old_version, new_version)
        json_list.append(sub_array)
    write_json_game_db(json_list)

def get_page(page):
    return requests.get(page)

def get_page_to_check(game_name):
    for i in load_json():
        if i["game"].lower() == game_name.lower():
            return i["public_build"]
    print("Could not get page")
    return None

def get_game_latest_version(game_name):
    for i in load_json():
        if i["game"].lower() == game_name.lower():
            return str(i["latest_version"])

def insexsity():
    r = get_page(get_page_to_check("insexsity"))
    soup = BeautifulSoup(r.text, "lxml")
    version = soup.find("div", {"class": "container-fluid"}).find("div", {"class": "warringText"}).get_text().replace("Current version- ", "")
    version_on_disk = get_game_latest_version("insexsity")
    if str(version) != version_on_disk:
        print("There is a new version of insexsity")
        update_json_version("insexsity", version)
        update_insexsity_download_links(version_on_disk, version)

def trials_in_tainted_space():
    game_name = "trials in tainted space"
    link = get_current_download_link(game_name, "linux")
    if link is None:
        print("Unable to get download link for: {}".format(game_name))
    r = requests.get(link, stream=True)
    version = get_game_download_title(r).replace("TiTS_", "").replace(".swf", "")
    get_game_latest_version(game_name)
    if str(version) != get_game_latest_version(game_name):
        print("There is a new version of {}".format(game_name))
        update_json_version(game_name, version)

def summer_time_sage():
    # As the summertime saga site uses JS we need to use selenium
    game_name = "Summertime Saga"
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import time
    driver = webdriver.Firefox()
    driver.get("https://summertimesaga.com/download")
    time.sleep(4)
    for i in range(1,4):
        link = driver.find_element_by_xpath("(//a[contains(text(),'mega')])[{}]".format(i)).get_attribute("href")
        if i is 1:
            if get_current_download_link(game_name, "windows") != link:
                print("Updating Windows link to {}".format(link))
                update_current_download_link(game_name, "windows", link)
                print("Updating Linux link to {}".format(link))
                update_current_download_link(game_name, "linux", link)
        elif i is 2:
            if get_current_download_link(game_name, "mac") != link:
                print("Updating Mac link to {}".format(link))
                update_current_download_link(game_name, "mac", link)
        elif i is 3:
            if get_current_download_link(game_name, "android") != link:
                print("Updating android link to {}".format(link))
                update_current_download_link(game_name, "android", link)

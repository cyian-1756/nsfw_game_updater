import re
from bs4 import BeautifulSoup
import requests


def get_release(post):
	# match mega links
	r = re.findall("https://mega\S*", post)
	r += re.findall("version ?\S*", post)
	return r

def is_release(post):
	r = re.findall("release", post)
	r += re.findall("version", post)
	r += re.findall("https://mega\S*", post)
	return len(r) >= 2

def get_post(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	post = soup.findall('div', class_="text")
	return post

page = requests.get("https://www.patreon.com/summertimesaga")
soup = BeautifulSoup(page.content, "html.parser")
print(soup.prettify())
post = soup.find_all('div', class_="text")
print(post)

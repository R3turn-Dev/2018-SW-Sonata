import requests

from bs4 import BeautifulSoup

req = requests.get("https://www.naver.com", verify=False)

print(req.status_code, len(req.text))

soup = BeautifulSoup(req.text, 'html.parser')
print(soup.select("div"))
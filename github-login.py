from requests import session
from bs4 import BeautifulSoup as bs

USER = 'wushuzhen1975@icloud.com'
PASSWORD = input("Type password:")

URL1 = 'https://github.com/session'
URL2 = 'https://github.com/'


with session() as s:
    req = s.get(URL1).text
    html = bs(req, "lxml")
    token = html.find("input", {"name": "authenticity_token"}).attrs['value']
    com_val = html.find("input", {"name": "commit"}).attrs['value']

    login_data = {'login': USER,
        'password': PASSWORD,
        'commit' : com_val,
        'authenticity_token' : token}

    print("===1")

    r1 = s.post(URL1, data = login_data)

    print("===2")

    r2 = s.get(URL2)
    print("===3")
    data2 = r2.content

    page_html = data2

    print(page_html)

    page_soup = bs(page_html, "html.parser")

    containers = page_soup.findAll("div", {"class":"mb-1"})
    print("On this page, there are how many projects listed? \n")
    print(len(containers))

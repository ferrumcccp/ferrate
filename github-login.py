"""DEPRECATED. USE API INSTEAD
"""

from requests import session
from bs4 import BeautifulSoup as bs

if False:
    user_mail = 'wushuzhen1975@icloud.com'
    username = "ferrumcccp"
    password = input("Type password:")

    url_session = 'https://github.com/session'
    url_test = 'https://github.com/'


    with session() as s:
        req = s.get(url_session).text
        html = bs(req, "lxml")
        token = html.find("input", {"name": "authenticity_token"}).attrs['value']
        com_val = html.find("input", {"name": "commit"}).attrs['value']

        login_data = {'login': user_mail,
            'password': password,
            'commit' : com_val,
            'authenticity_token' : token}

        print("===1")

        r1 = s.post(url_session, data = login_data)

        print("===2")

        r2 = s.get(url_test)
        print("===3")
        data2 = r2.content

        page_html = data2

        if username in str(page_html):
            print("Github login successful.")
        else:
            print("Github login failed.")
            sys.exit(0)

        r3 = s.get("https://gitter.im/login/github?action=login&amp;source=intro-login")
        data3 = r3.content
        page2 = str(data3)

        if ("All conversations" in page2) and (username in page2):
            print("Gitter login successful.")
        else:
            print("Gitter login failed.")
            sys.exit(0)

        r4 = s.post("https://gitter.im/api/v1/rooms/5f2ac5cdd73408ce4feb7088/chatMessages", json = {"text": "**机器人消息**\n\ntest\n\nhttps://github.com/ferrumcccp/ferrate"})

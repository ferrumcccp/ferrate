"""
Ferrate Bot [WIP]
"""


import queue
import requests
import logging
import json
import time


"""Global data"""


username = None
token = None
room_name = "ferrate/community"
room_id = None


""" Network
"""

def get_room():
    """ Get room id
    """
    global token

    logging.info("Fetching room id.")

    r_room = requests.get("https://api.gitter.im/v1/rooms"
        , headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer %s" % token
        })

    res = json.loads(r_room.content)
    logging.info("Result: %s" % r_room.content)
    for i in res:
        if i["name"] == room_name:
            return i["id"]

    raise Exception("Room ID not found!")

def send_msg_1try(msg):
    msg = "**机器人消息**\n\n" + msg

    try:
        r_send = requests.post("https://api.gitter.im/v1/rooms/%s/chatMessages"
            % room_id
            , data = json.dumps({
                "text": msg
            }),headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer %s" % token
            })
    except requests.RequestException:
        return False
    return True

def send_msg(msg):
    if send_msg_1try(msg) or send_msg_1try(msg):
        logging.info("Message sent: '%s'" % msg)
    else:
        logging.error("Failed to send message: '%s'" % msg)

def main_loop():
    logging.basicConfig(level="INFO")

    global username, token
    token = input("口令：")
    global room_id
    room_id = get_room()

    send_msg("""
我是Ferrumcccp暑假划水写的Bot。仅在周末、假期等主人有空接触手机
的时间段内开放。

目前支持：
- 自动复读
""")

    cnt = 0
    while True:
        if cnt > 0:
            logging.error("Streaming API connection broken. Retrying in 20s.")
            time.sleep(20)
        cnt += 1

        r_stream = None
        try:
            r_stream = requests.get(
                "https://stream.gitter.im/v1/rooms/%s/chatMessages" % room_id
                , headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer %s" % token
                }
                , stream = True)
        except requests.RequestException:
            r_stream = None

        if r_stream == None:
            logging.error("Request failed.")
            continue

        fudu = ""
        fudu_cnt = 0
        
        for i in r_stream.iter_lines(decode_unicode = True):
            if len(i) >= 5:
                logging.info("Read stream data: %s" % i)
                i_dec = json.loads(i)

                if (str.startswith(i_dec['text'], "**机器人消息**")
                    or str.startswith(i_dec['text'],"no_bot")):
                    logging.info("Message filtered.")
                    continue

                if i_dec['text'] == fudu:
                    fudu_cnt += 1
                else:
                    fudu_cnt = 1
                    fudu = i_dec['text']
                if fudu_cnt == 2:
                    send_msg(i_dec['text'])

                suicide_kw = ["suicide"
                    , "want to die"
                    , "kill myself"
                    , "end it all"
                    , "自杀"
                    , "想死"
                    , "跳楼"
                    , "上吊"
                    , "服毒"
                    , "割腕"
                    , "不想活"] #应该够用了
                for kw in suicide_kw:
                    if kw in i_dec['text']:
                        send_msg("""
虽然我无法理解人类的情感，但是我知道你身处挣扎中。
不要怕，你并不孤单，有_人_能帮助你。

- 北京危机热线：[01082951332](tel:01082951332)
- 福州第四医院心理咨询热线：[059185666661](tel:059185666661)
""")
                        break
            else:
                logging.info("Non-message: %s" % i)


if __name__ == "__main__":
    main_loop()

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
room_name = "Oriental Sakura/community"
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
    if send_msg_1try(msg) or send_msg_1try(msg) or send_msg_1try(msg):
        logging.info("Message sent: '%s'" % msg)
    else:
        logging.error("Failed to send message: '%s'" % msg)

def main_loop():
    logging.basicConfig(level="INFO")
    test_msg="""POST TEST"""

    global username, token
    token = input("口令：")
    global room_id
    room_id = get_room()

    send_msg(test_msg)

    cnt = 0
    while True:
        if cnt > 0:
            logging.error("Streaming API connection broken. Retrying in 5s.")
            time.sleep(5)
        cnt += 1

        r_stream = None
        try:
            r_stream = requests.get("https://api.gitter.im/v1/rooms"
                , headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer %s" % token
                }
                , streaming = True)
        except requests.RequestException:
            r_stream = None

        if r_stream == None:
            pass


if __name__ == "__main__":
    main_loop()

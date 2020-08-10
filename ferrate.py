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

    send_msg("""测试stream API，我是复读机""")

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
        
        for i in r_stream.iter_lines(decode_unicode = True):
            if len(i) >= 5:
                logging.info("Read stream data: %s" % i)
                i_dec = json.loads(i)

                if (str.startswith(i_dec['text'], "**机器人消息**")
                    or str.startswith(i_dec['text'],"no_bot")):
                    logging.info("Data filtered.")
                    continue
                
                send_msg(i_dec['text'])
            else:
                logging.info("Invalid line: %s" % i)


if __name__ == "__main__":
    main_loop()

""" Ferrate - A Huashui Bot

Python 3 only
"""

import collections
import threading
import requests
import logging
import json
import time

#mutex = 0 # Mutual Exclusion Lock, 0 = Unloct 1 = Backend 2 = Frontend
mutex = threading.Lock() # Mutual Exclusion Lock
iqueue = collections.deque() # Input(FerrateInput-s)
oqueue = collections.deque() # Output(strs)
bot_name = "ferrate"

class FerrateInput:
    """A ferrate input"""
    def __init__(self, sender = "testman", msg = "", command = None):
        """init

        str sender: username of the sender
        str msg: message text
        list command: command and its args (auto parsed if not specified)
            If the message begins with /, then the first line is treated
            as command and splitted with spaces. Only te rest of the lines
            remain to be the message body.
        """
        self.sender = sender
        msg = msg.strip(' \n\t')
        if command or (msg and msg[0] != "/"):
            self.msg = msg
            self.command = command
        else:
            p = msg.find('\n')
            if p < 0: # One line
                self.command = msg
                self.msg = ''
            else: # One line command + Msg body
                self.command = msg[0: p]
                self.msg = msg[p + 1:]

            self.command = self.command.split()

class FerrateModule:
    """A ferrate module"""
    def __init__(self):
        pass

    def printmsg(self, msg):
        """Write to output queue"""
        mutex.acquire()
        oqueue.append(msg)
        mutex.release()

    def routine(self):
        """Routine work run repeatedly

        Override this"""
        pass

    def input(self, x):
        """Process input. Called only once for each module each input

        FerrateInput x: input
        Override this"""
        pass

class Ceshi(FerrateModule):
    """For testing only do not use it in production"""
    def __init__(self):
        self.cnt = 0
    def routine(self):
        self.cnt += 1
        if self.cnt % 10000000 == 0:
            self.printmsg("Tick %d" % self.cnt)
    def input(self, x):
        self.printmsg("Input:\n\n\tSender: %s\n\n\tMsg: %s\n\n\tCommand: %s\n\n\t"
                % (x.sender, x.msg, x.command))

modules = [
        Ceshi()]

def run_modules():
    global mutex
    while True:
        for i in modules:
            i.routine()
        while True: # clear the input queue
            mutex.acquire()
            if not len(iqueue):
                mutex.release()
                break
            x = iqueue.popleft()
            mutex.release()
            for i in modules:
                i.input(x)
         
# Queue funcs for frontend
def msg_receive(sender, msg):
    """After receiving a message, put it in the input queue
    so that it can be processed by backend"""
    mutex.acquire()
    iqueue.append(FerrateInput(sender, msg))
    mutex.release()

def msg_send():
    """Get the message 2 be sent"""
    mutex.acquire()
    if not len(oqueue):
        mutex.release()
        return None
    x = oqueue.popleft()
    mutex.release()
    return x

def test_app():
    print("""This is Ferrate test mode. Type your message to test the bot.
Type RETURN twice to finish message.
Your default username is 'testman'. To change, type "username:<RETURN>"
    """)
    msg = ""
    sender = 'testman'
    while True:
        while True:
            y = msg_send()
            if y:
                print(y)
            else:
                break

        x = input('> ')
        if x == '':
            if msg != '':
                msg_receive(sender, msg)
            msg = ''
        elif x[-1] == ':':
            sender = x[:-1]
            print("Current username : %s" % sender)
        elif msg == '':
            msg = x
        else:
            msg = msg + '\n' + x
        time.sleep(.25)

if __name__ == "__main__":
    th = threading.Thread(target = run_modules)
    th.start()
    test_app()

"""EMMMMMM, here comes networking"""


"""Global data"""


#username = None # = bot_name
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
    #msg = "**机器人消息**\n\n" + msg

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

    global bot_name, token
    token = input("口令：")
    global room_id
    room_id = get_room()

    send_msg("""
我是Ferrumcccp划水写的Bot。仅在周末、假期等主人有空接触手机
的时间段内开放。

Fork me on Github: [Repo](https://github.com/ferrumcccp/ferrate)

目前支持：
- 自动复读
""")

    cnt = 0
    while True:
        if cnt > 0:
            logging.error("Connection broken. Retrying in 20s.")
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
        try:
            for i in r_stream.iter_lines(decode_unicode = True):
                if len(i) >= 5:
                    logging.info("Read stream data: %s" % i)
                    i_dec = json.loads(i)

                    if (str.startswith(i_dec['text'], "**机器人消息**")
                        or str.startswith(i_dec['text'],"no_bot")):
                        logging.info("Message filtered.")
                        continue

                    # 复读
                    if i_dec['text'] == fudu:
                        fudu_cnt += 1
                    else:
                        fudu_cnt = 1
                        fudu = i_dec['text']
                    if fudu_cnt == 2:
                        send_msg(i_dec['text'])

                    # 危机干预
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

                    # Process Command

                else:
                    logging.info("Non-message: %s" % i)
        except requests.RequestException:
            logging.error("Stream broken.")


if __name__ == "__main__":
    main_loop()

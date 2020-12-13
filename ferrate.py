""" Ferrate - A Huashui Bot

Python 3 only
"""

import collections
import threading
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

"""EMMMMMM"""

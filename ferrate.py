"""
Ferrate Bot [WIP]
"""


import queue
import requests


"""Global data"""


username = None
token = None
room_name = "Oriental-Sakura"
room_id = None


""" Network
"""


def main_loop():
    global username, token
    username = input("用户名：")
    token = input("口令：")

if __name__ == "__main__":
    main_loop()

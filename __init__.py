""" Network
"""


import requests

import global_data

def main_loop():
    global_data.username = input("用户名：")
    global_data.token = input("口令：")

if __name__ == "__main__":
    main_loop()

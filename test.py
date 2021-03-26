import sys
import platform
import time
import base64
import hashlib
import hmac
import urllib.request as urllib2
import json
import csv
import pandas as pd


class Test:

    def __init__(self):
        self.buy_price = 6
        self.sell_price = 5

    def determineSellPrice(self):
        new_sell_price = self.sell_price + 1
        return new_sell_price


# a = Test()
# print(a.determineSellPrice())

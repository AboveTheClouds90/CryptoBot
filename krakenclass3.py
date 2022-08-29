from dataclasses import asdict
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
import numpy as np
import math


'''
This class is handling the kraken api. For further information on the kraken Api visit  https://docs.kraken.com/rest/.
'''
class Kraken:

    
    def __init__(self):
        #Apikeys
        self.api_key = "STdsVRArlAEFg36dmQqFqG9ujAKVwBWeLSWHk6wbtswOcqzaIIhs92QA"
        self.api_secret = base64.b64decode(
            "11urJofpMdWEVxmCAEK81jCfzU1tCGP8LOeECxZEiuAGkW6mSpeCQFrA1/P3Igo4ILkGOlveF1fqYtj2piEfBQ==")
        self.api_nonce = str(int(time.time()*1000))
        self.api_domain = "https://api.kraken.com"
        self.api_path = {"private": "/0/private/", "public": "/0/public/"}
        self.api_endpoint = {"Balance": "Balance", "DepositStatus": "DepositStatus", "DepositMethods": "DepositMethods",
                             "AddOrder": "AddOrder", "Ticker": "Ticker", "OpenOrders": "OpenOrders", "TradesHistory": "TradesHistory", "ClosedOrders": "ClosedOrders"}
        self.api_parameters = {"none": ""}
        self.asset = {"Cardano": "ADA", "Bitchoincash": "BCH",
                      "Algorand": "ALGO", "Monero": "XMR"}
        self.asset_pair = {"Cardano": "ADAEUR", "Bitcoincash": "BCHEUR",
                           "Algorand": "ALGOEUR", "Monero": "XMREUR"}
        self.buy_price =np.array([])
        self.sell_price = np.array([])
        self.df_sell = ""
        self.df_buy = ""

    def callEndpoint(self, my_api_key, my_api_secret, endpoint, parameters, api_path_self, api_domain_self):
        api_key = my_api_key
        api_secret = my_api_secret
        api_endpoint = endpoint
        api_parameters = parameters
        api_endpoint = endpoint
        api_parameters = parameters
        api_domain = api_domain_self
        api_path = api_path_self
        if api_path == "/0/private/":
            api_nonce = str(int(time.time()*1000))
            api_postdata = api_parameters + "&nonce=" + api_nonce
            api_postdata = api_postdata.encode('utf-8')
            api_sha256Data = api_nonce.encode('utf-8') + api_postdata
            api_sha256 = hashlib.sha256(api_sha256Data).digest()
            api_hmacSha512Data = api_path.encode(
                'utf-8') + api_endpoint.encode('utf-8') + api_sha256
            api_hmacsha512 = hmac.new(
                api_secret, api_hmacSha512Data, hashlib.sha512)
            api_sig = base64.b64encode(api_hmacsha512.digest())
            api_url = api_domain + api_path + api_endpoint
            api_request = urllib2.Request(api_url, api_postdata)
            api_request.add_header("API-Key", api_key)
            api_request.add_header("API-Sign", api_sig)
            api_request.add_header("User-Agent", "Kraken REST API")
            api_reply = urllib2.urlopen(api_request).read()
            api_reply = self.api_reply(api_request)
            api_reply = api_reply.decode()
            api_reply = json.loads(api_reply)
            return api_reply
        else:
            api_url = api_domain + api_path + api_endpoint + api_parameters
            api_request = urllib2.Request(api_url)
            api_reply = self.api_reply(api_url) #urllib2.urlopen(api_url).read()
            api_reply = api_reply.decode()
            api_reply = json.loads(api_reply)
            return api_reply

    def api_reply(self, api_request):
        while True:
            try:
                
                api_reply = urllib2.urlopen(api_request).read()
                return api_reply
            except:# urllib2.URLError: -> handles disconnects
                time.sleep(2)
                pass

    def apiBalance(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["Balance"],
                                 self.api_parameters["none"],
                                 self.api_path["private"],
                                 self.api_domain)
    # determines all availabe funds(euro)
    #helpfunction to round down numbers. 
    #needed because API outputs an insufficient fund error. 
    #Problem is on new kraken api since assets can still be bought/sold
    def round_down_string(self,s):    
        for i in range(len(s)):
            if s[i] == ".":
                return float(s[:i+3])
    #AddBuyOrder
    def eurVolume(self):
        balance = self.apiBalance()
        euro_balance = balance['result']['ZEUR']
        euro_balance = self.round_down_string(euro_balance) - 1
        print(euro_balance)
        ask_price = self.getAskprice()
        ask_price = self.round_down_string(ask_price)
        print(ask_price)
        #ask_price = ask_price
        volume = euro_balance/ask_price
        print(volume)
        volume = str(self.round_down_string(str(volume)))
        print(volume)
        return volume
    # determines all available funds(asset)
    #sellAddOrder:
    def volume(self):
        balance = self.apiBalance()
        asset_balance = balance['result'][f'{self.asset}']
        asset_balance = str(self.round_down_string(asset_balance))
        #asset_balance = str(self.round_down_string(asset_balance))
        print(asset_balance)
        return asset_balance

    def sellAddOrderParameters(self):
        # sells all available funds
        parameter = f"pair={self.asset_pair}&type=sell&ordertype=market&volume=" + \
            self.volume()+"&trading_agreement=agree"
        return parameter

    def sellAddOrder(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["AddOrder"],
                                 self.sellAddOrderParameters(),
                                 self.api_path["private"],
                                 self.api_domain)

    def buyAddOrderParameters(self):
        # buys bch worth of all available eur funds
        parameter = f"pair={self.asset_pair}&type=buy&ordertype=market&volume=" + \
            str(self.eurVolume())+"&trading_agreement=agree"
        return parameter

    def buyAddOrder(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["AddOrder"],
                                 self.buyAddOrderParameters(),
                                 self.api_path["private"],
                                 self.api_domain)

    def getOpenOrders(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["OpenOrders"],
                                 self.sellAddOrderParameters(),
                                 self.api_path["private"],
                                 self.api_domain)

    def tickerParameters(self):
        parameter = f"?pair={self.asset_pair}"
        return parameter

    def getTickerInformation(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["Ticker"],
                                 self.tickerParameters(),
                                 self.api_path["public"],
                                 self.api_domain)

    def getBidprice(self):
        bidprice = self.getTickerInformation()
        bidprice = bidprice["result"][f"{self.asset_pair}"]["b"][0]
        return bidprice

    def getAskprice(self):
        askprice = self.getTickerInformation()
        askprice = askprice["result"][f"{self.asset_pair}"]["a"][0]
        return askprice

    # def tradesHistoryParameters(self):
    #     return "type=buy&closed%20position=buy&ofs=offset"

    # def getTradesHistory(self):
    #     return self.callEndpoint(self.api_key,
    #                              self.api_secret,
    #                              self.api_endpoint["TradesHistory"],
    #                              self.tradesHistoryParameters(),
    #                              self.api_path["private"],
    #                              self.api_domain)

    def closedOrdersParameters(self):
        return ""

    def getClosedOrders(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["ClosedOrders"],
                                 self.closedOrdersParameters(),
                                 self.api_path["private"],
                                 self.api_domain)

    def depositStatusParameters(self):
        return "asset=BCH&method=Bitcoin%Cash"

    def depositStatus(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["DepositStatus"],
                                 self.depositStatusParameters(),
                                 self.api_path["private"],
                                 self.api_domain)

    def depositMethodsParameters(self):
        return "asset=BCH"

    def depositMethods(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["DepositMethods"],
                                 self.depositMethodsParameters(),
                                 self.api_path["private"],
                                 self.api_domain)
    def setAsset(self, asset):
        self.asset = self.asset[f"{asset}"]
        self.asset_pair = self.asset_pair[f"{asset}"]
        print(self.asset)
        




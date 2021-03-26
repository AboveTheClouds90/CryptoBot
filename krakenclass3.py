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


class Kraken:
    def __init__(self):
        self.api_key = "STdsVRArlAEFg36dmQqFqG9ujAKVwBWeLSWHk6wbtswOcqzaIIhs92QA"
        self.api_secret = base64.b64decode(
            "11urJofpMdWEVxmCAEK81jCfzU1tCGP8LOeECxZEiuAGkW6mSpeCQFrA1/P3Igo4ILkGOlveF1fqYtj2piEfBQ==")
        self.api_nonce = str(int(time.time()*1000))
        self.api_domain = "https://api.kraken.com"
        self.api_path = {"private": "/0/private/", "public": "/0/public/"}
        self.api_endpoint = {"Balance": "Balance", "DepositStatus": "DepositStatus", "DepositMethods": "DepositMethods",
                             "AddOrder": "AddOrder", "Ticker": "Ticker", "OpenOrders": "OpenOrders", "TradesHistory": "TradesHistory", "ClosedOrders": "ClosedOrders"}
        # ; "AddOrder": {"pair": "BCHEUR","type": "buy", "sell", "ordertype": "market"}}
        self.api_parameters = {"none": ""}
        self.asset = {"Cardano": "ADA", "Bitchoincash": "BCH",
                      "Algorand": "ALGO", "Monero": "XMR"}
        self.asset_pair = {"Cardano": "ADAEUR", "Bitcoincash": "BCHEUR",
                           "Algorand": "ALGOEUR", "Monero": "XMREUR"}
        self.algo_args = {"buy_price": 0, "additional": 0,
                          "sell_price": 0, "counter": 0}
        self.df = ""
        self.args_counter = 0

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
            api_reply = api_reply.decode()
            api_reply = json.loads(api_reply)
            return api_reply
        else:
            api_url = api_domain + api_path + api_endpoint + api_parameters
            api_request = urllib2.Request(api_url)
            api_reply = urllib2.urlopen(api_url).read()
            api_reply = api_reply.decode()
            api_reply = json.loads(api_reply)
            return api_reply

    def apiBalance(self):
        return self.callEndpoint(self.api_key,
                                 self.api_secret,
                                 self.api_endpoint["Balance"],
                                 self.api_parameters["none"],
                                 self.api_path["private"],
                                 self.api_domain)
    # determines all availabe funds(euro)

    def eurVolume(self):
        balance = self.apiBalance()
        euro_balance = balance['result']['ZEUR']
        ask_price = self.getAskprice()
        volume = float(euro_balance)/float(ask_price)
        volume = format(volume, '.3f')
        return volume
    # determines all available funds(BCH)

    def volume(self):
        balance = self.apiBalance()
        bch_balance = balance['result'][f'{self.asset}']
        return bch_balance

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


# --------------------------------------------------------------LOG
# ---------------------------panda csv
    # 1. programm run loadLog() to load the log in dataframe
    # 2.  call loadLastEntry() to extract last algoArgs from log/dataframe
    # 3. checkLastEntry() checks the last entry and returns where the programm stoped. Is it a cash or crypto position, also set counter. PURPOSE OF COUNTER: So the program nows when to write data to dataframe with algoArgsTODataframe()
    # 4. Depending if its cash or crypto.TODO: Check with checkAlgoArgs() cash position -> buyAlgo()
    # 5. After buying, self.algo_args["buyprice"] = buyprice # counter +1
    # between 5. and 6. check if funding is available
    # 6. Call sellAlgo(), after sell, self.algoargs["sellprice"] = sellprice ;coutner +1TODO this probably needs to be done with algoArgs toDATAframe function because of counter -> cycle is over at this point, write to dataframe, safe csv
    # 7. Go back to step 4 and repeat everything agian
    # 4.4. If crypto position -> sellAlgo() -> call sellAlgo(),
    # 4.5 after sell, self.algoargs["sellprice"] = sellprice #coutner +1
    # prolly check funding
    # 4.6. call buyAlgo(), after buy self.algo_args["buyprice" = buyproce] ;counter +1; same TODO as in 6.
    # 4.7 go back and repeat 4.4.
    # loads Log to programm
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# ----------------------------NOT NEEDED ANYMORE, NOW IN "Krakencontrol.py"------
# ----------------------------------------->NEEDS TESTING------------------------

#     def loadLog(self):
#         data_frame = pd.read_csv("log.csv")
#         self.df = data_frame

#     # function to fill self.algo_args and writes it to csv after one trading cycle.With arg_name is the key from self.algo-args
#     # and arg the value

#     # should check current algo arg, with counter and return where we are at, maybe call algo functions
#     def checkAlgoArgs(self):
#         pass

#     def getCounterLastEntry(self):
#         # self.df in actual programm
#         last_entry = self.df.iloc[-1].to_dict()
#         return last_entry["counter"]

#     def callAlgo(self):
#         loop = True
#         self.loadLog()
#         # needs to be replaced with something else in program n.
#         while loop == True:
#             last_entry = self.df.iloc[-1].to_dict()
#             if last_entry["buy_price"] == 0:
#                 # self.testBuyAlgo()
#                 self.buyAlgo()
#             else:
#                 # self.testSellAlgo()
#                 self.sellAlgo()
#             print(last_entry)
#             user_input = int(input("Enter 0 to exit program:"))
#             print(user_input)
#             if user_input == 0:
#                 self.df.to_csv("log.csv", index=False)
#                 loop = False

#     def setParameter(self, arg):
#         # gets current counter
#         counter = self.getCounterLastEntry()
#         # gets counter length. However the substracts -1 because the counter itself is not an argument
#         counter_length = len(self.df.iloc[-1].to_dict().keys())-1
#         # checks if it's the last entry
#         if counter < counter_length:
#             # counter represents a value from algo_args from left to right with the most left item represented by coutner = 0
#             self.df.iloc[-1, counter] = arg
#             self.df.iloc[-1, counter_length] = self.df.iloc[-1,
#                                                             counter_length] + 1
#         # else case: last entry
#         # sets the arg for last entry and appends new algo args to dataframe
#         else:
#             self.df.iloc[-1, counter] = arg
#             self.df.iloc[-1, counter_length] = self.df.iloc[-1,
#                                                             counter_length] + 1
#             self.algo_args = {"buy_price": 0, "additional": 0,
#                               "sell_price": 0, "counter": 0}
#             self.df = self.df.append(
#                 self.algo_args, ignore_index=True)
#     # --------------------test functions

#     # def testBuyAlgo(self):
#     #     buyprice = 1
#     #     additional = 9
#     #     self.setParameter(buyprice)
#     #     # adding more parameters:
#     #     # algo_args = {"buy_price": 0,"additional":0 "sell_price": 0, "counter": 0}
#     #     # additional parameters need to be added consecutively to maintain order since counter represents argument form algo args
#     #     self.setParameter(additional)
#     #     self.algo_args["additional"] = additional
#     #     self.algo_args["buyprice"] = buyprice

# # # -----------------------------------------------------------CONTROL
#     # returns an array with values down from 0.9 in 0.025 intervals
#     # purpose of this function is to guarantee that the asset is bought 10% or more below the price it was sold.
#     # the buy_limit and sell_limit functions are desgined to return parameters to handle a trailing stop loss order.
#     def setAsset(self, asset):
#         self.asset = self.asset[f"{asset}"]
#         self.asset_pair = self.asset_pair[f"{asset}"]
#         print(self.asset)

#     def buy_limit(self, price):
#         const = 0.95
#         limit = [0.95]
#         while (const > 0.1):
#             limit.append(const*price)
#             const = const - 0.02
#         return limit
#     # retruns an array with values up from 1.1 in 0.025 intervarls
#     # same purpose as the buy_limit function but only for selling respective asset.

#     def sell_limit(self, price):
#         const = 1.05
#         limit = [1.05]
#         while (const < 3):
#             limit.append(const*price)
#             const = const + 0.02
#         return limit

#     # TODO last_entry should be its own function to check if it should start with buy/sellAlgo function

#     def buyAlgo(self):
#         last_entry = self.df.iloc[-1].to_dict()
#         old_sellprice = last_entry["sell_price"]
#         loop_one = True
#         # limit presents an array of prices which it would be profitable to buy as in regard to the last sellprice
#         limit = self.buy_limit(old_sellprice)
#         # highest limit is old_sellprice*0.9 at the start. For refererence check buy_limit function
#         highest_limit = limit[0]
#         while(loop_one == True):
#             time.sleep(1.2)
#             print("checking buyprice")
#             # gets current ask price
#             check_buyprice = float(self.getAskprice())
#             print(check_buyprice)
#             # compares current askprice with the the price at which the asset would be a buy.
#             # Smaller check_buyprice -> more profit.
#             if (check_buyprice < highest_limit):
#                 highest_limit = check_buyprice
#             # if the esset is above the buyprice then resume the loop and start again
#             elif (check_buyprice > limit[0]):
#                 pass
#             # this is the case if the current askprice is between the highest_limit and limit[0]
#             else:
#                 for value in limit:
#                     # TODO is this even necessary? these should be covered thru the other if/else cases
#                     # check_buyprice < value -> must be lower then limit[0]
#                     # check_buyprice > highest limit -> dropped down from anothter limit
#                     if (check_buyprice > value and check_buyprice > highest_limit):
#                         print("buying")
#                         self.buyAddOrder()
#                         # TODO NEEDS WORK SINCE PANDAS CSV CHANGE _--_OLD CODE for reference TODO delete later
#                         # self.setArgsBuyprice(check_buyprice)
#                         # self.setCounter()
#                         # _--_OLD CODE for reference TODO delete later
#                         buy_price = check_buyprice
#                         # logs price at which asset was bought
#                         self.setParameter(buy_price)
#                         # temporarily saves currenz buyprice in algo args.
#                         # TODO needs to be reseted after one cycle
#                         self.argsetter("buy_price", buy_price)
#                         loop_one = False
#                         # not sure if this condition is necassary because this is the only othercase

#     def sellAlgo(self):
#         # loads last enty to get the last buyprice
#         last_entry = self.df.iloc[-1].to_dict()
#         old_buy_price = last_entry["buy_price"]
#         loop_one = True
#         # limit_sell presents an array of prices which it would be profitable to sell as in regard to the last buyprice
#         limit_sell = self.sell_limit(old_buy_price)
#         # highest limit is old_buyprice*1.1 at the start. For refererence check buy_limit function
#         highest_limit_sell = limit_sell[0]
#         while (loop_one == True):
#             time.sleep(1.2)
#             print("checking sellprice")
#             # gets current bidprice
#             check_sellprice = float(self.getBidprice())
#             print(check_sellprice)
#             # compares current bidprice with possible lowest sellprice
#             if(check_sellprice > limit_sell[0]):
#                 # if bidprice is above sellprice it sets it as the highes sellprice
#                 highest_limit_sell = check_sellprice
#             # if the esset is under the sellprice then resume the loop and start again
#             elif(check_sellprice < limit_sell[0]):
#                 pass
#             # this is the case if the current bidprice is between the highest_limit and limit[0]
#             else:
#                 for value in limit_sell:
#                     # TODO same as buyalgo problem
#                     if(check_sellprice < value and check_sellprice < highest_limit_sell):
#                         print("selling")
#                         self.sellAddOrder
#                         # TODO csv pandaas stuff --- OLD CODE
#                         # self.setArgsSellprice(check_sellprice)
#                         # self.setCounter()
#                         # TODO OLDCODE for reference
#                         sell_price = check_sellprice
#                         self.setParameter(sell_price)
#                         self.argsetter("sell_price", sell_price)
#                         loop_one = False
#     # 1.buy/sellalgo
#     # 2. buy algo must return data for sell Algo
#     # 3.sellAlgo must return data for buy algo
#     # 4. data sould be saved in one csv file or thru a different function

#     def argSetter(self, arg_name, arg):
#         self.algo_args[arg_name] = arg
#         print(self.algo_args)


# a = Kraken()
# a.setAsset("Algorand")
# a.callAlgo()

# if bot.getPosition():
#   bot.sellAlgo()
# else:
#   bot.buyAlgo()

# def writeToCsv():
#     ask = a.getAskprice()
#     bid = a.getBidprice()
#     with open('log.csv', 'a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([ask, bid])


# def readFromCsv():
#     data = list()
#     with open('log.csv', 'r') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             data.append(row)
#     print(data)
#     return data[-1][0]


# writeToCsv()
# print(readFromCsv())


# b = a.sellAddOrder()
# apiJSON = CallPrivateEndpoint(
#   api_key, api_secret, api_endpoint, api_parameters)
# print(b)
# b = a.buyAddOrder()
# b = a.eurVolume()
# c = a.getOpenOrders()
# print(c)
# print(b)
# a.getBidprice()
# print(a.getClosedOrders())
# print(apiJSON)

# Additions:
# 1. create Log in txt file with date, loop(1,2,3), relevant values: profit,sell/buyprice
# 1. also to recall last buyprice when restarting programm maybe.
# 2. Create menu to interrupt program. Manually sell/buy

# 0. TODO function to determine buyprice
# 1. TODO buy price = x
# 2. addorder -> buy                     TODO    ->loob1
# 2.1 TODO remember price sold @ = buyprice = x
# 3. check price
# 4. if price == sellprice= buyprice + profit
# 4.1. then sell
# -> wait for the order to go through, maybe check when able to sell again to avoid errors
# 4.2 else 3.
# 5. check price                             ->loop2
# 5.1 if current price == or >buyprice then 2.
# 5.2 else 5

# pseudocode:
# bot = Kraken()
# loop = false
# ---------loop1
# while(loop == true):

# bot.buyAddOrder(buyprice)
# buypricedetermined = false
# sell = false
# buyagain = false
# ---------loop2
# while sell == false:
# check_price = bot.getAskprice()
# if (check_price == sell_price)
# bot.sellAddOrder()
# sell = true
# ---------loop2 end
# ---------loop3begin
# while(buyagain= false):
# if buyprice determined == false:
# buyprice = determineBuyprice()
# elif bot.askprice() == buyprice || bot.askprice()< buyprice:
# buyagain = true
# --------loop3end
# some function to end program
# --------loop1end

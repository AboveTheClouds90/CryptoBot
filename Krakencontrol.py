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
from krakenclass3 import *
import os


def clear():
    return os.system('clear')
# additional


class KrakenControl(Kraken):
    """
    Attributes
    ----------
    super().__int__(): Imports attributes from krakenclass.py


    """

    def __init__(self, parent):
        super().__init__()

    def loadLog(self):
        data_frame = pd.read_csv("log.csv")
        self.df = data_frame

    # function to fill self.algo_args and writes it to csv after one trading cycle.With arg_name is the key from self.algo-args
    # and arg the value

    def getCounterLastEntry(self):
        # self.df in actual programm
        last_entry = self.df.iloc[-1].to_dict()
        last_entry = int(last_entry["counter"])
        return last_entry

    def callAlgo(self):
        loop = True
        self.loadLog()
        # needs to be replaced with something else in program n.
        while loop == True:
            last_entry = self.df.iloc[-1].to_dict()
            if last_entry["buy_price"] == 0:
                # self.testBuyAlgo()
                self.buyAlgo()
            elif last_entry["sell_price"] == 0:
                # self.testSellAlgo()
                self.sellAlgo()
            # TODO exit programm code
            # print(last_entry)
            # user_input = int(input("Enter 0 to exit program:"))
            # print(user_input)
            # if user_input == 0:
            #     self.df.to_csv("log.csv", index=False)
            #     loop = False

    def calcExecLimit(self, limit, highest_limit):
        if limit[0] == highest_limit:
            calculate_execute_limit = 0
            return calculate_execute_limit
        else:
            for i in range(len(limit)):
                if limit[i] == highest_limit:
                    calculate_execute_limit = limit[i-1]
                    return calculate_execute_limit

    def getCurrentData(self, current_state, current_price, highest_limit, limit, next_limit, max_min_price):
        calculate_execute_limit = self.calcExecLimit(limit, highest_limit)
        data = {"current_price": current_price, "highest_limit": highest_limit,
                "next_limit": next_limit, "Highest/lowest_price": max_min_price, "execute_limit": calculate_execute_limit,
                "current_state": current_state}
        return data

    def printData(self, current_state, current_price, highest_limit, limit, next_limit, max_min_price):
        data = self.getCurrentData(
            current_state, current_price, highest_limit, limit, next_limit, max_min_price)
        clear()
        for key in data:
            if data["execute_limit"] == 0 and key == "execute_limit":
                print(f"{key}:  " + f"Not available\n")
            else:
                print(f"{key}:  " + f"{data[key]}\n")

    def setParameter(self, arg):
        # gets current counter
        counter = self.getCounterLastEntry()
        # gets counter length. However the substracts -1 because the counter itself is not an argument
        counter_length = len(self.df.iloc[-1].to_dict().keys())-1
        # checks if it's the last entry
        if counter < (counter_length-1):
            # counter represents a value from algo_args from left to right with the most left item represented by coutner = 0
            self.df.iloc[-1, counter] = arg
            self.df.iloc[-1, counter_length] = self.df.iloc[-1,
                                                            counter_length] + 1
        # else case: last entry
        # sets the arg for last entry and appends new algo args to dataframe
        else:
            self.df.iloc[-1, counter] = arg
            self.df.iloc[-1, counter_length] = self.df.iloc[-1,
                                                            counter_length] + 1
            self.df.to_csv("log.csv", index=False)
            self.algo_args = {"buy_price": 0, "sell_price": 0, "counter": 0}
            self.df = self.df.append(
                self.algo_args, ignore_index=True)
    # --------------------test functions

    # def testBuyAlgo(self):
    #     buyprice = 1
    #     additional = 9
    #     self.setParameter(buyprice)
    #     # adding more parameters:
    #     # algo_args = {"buy_price": 0,"additional":0 "sell_price": 0, "counter": 0}
    #     # additional parameters need to be added consecutively to maintain order since counter represents argument form algo args
    #     self.setParameter(additional)
    #     self.algo_args["additional"] = additional
    #     self.algo_args["buyprice"] = buyprice

# # -----------------------------------------------------------CONTROL
    # returns an array with values down from 0.9 in 0.025 intervals
    # purpose of this function is to guarantee that the asset is bought 10% or more below the price it was sold.
    # the buy_limit and sell_limit functions are desgined to return parameters to handle a trailing stop loss order.
    def setAsset(self, asset):
        self.asset = self.asset[f"{asset}"]
        self.asset_pair = self.asset_pair[f"{asset}"]
        print(self.asset)

    def buy_limit(self, price):
        const = 0.985
        limit = [0.985*price]
        while (const > 0.1):
            const = const - 0.01
            limit.append(const*price)
        return limit
    # retruns an array with values up from 1.1 in 0.025 intervarls
    # same purpose as the buy_limit function but only for selling respective asset.

    # TODO last_entry should be it
    # s own function to check if it should start with buy/sellAlgo function
    def getBuyLimits(self, current_price, limit, highest_limit, next_limit):
        # if highestlimit = limit[0] and is still in intervall between(limt0,limit1)
        if current_price > limit[1] and highest_limit == limit[0]:
            return [highest_limit, limit[1]]
        elif current_price > highest_limit:
            return [highest_limit, next_limit]
        else:
            for idx, value in enumerate(limit):
                # case: highest limit is lower then the checked value and current price is higher then value -> sets highest limit
                # if highest limit = limit [0] this wont trigger and go to else because limit[0] is never smaller then limit[0]
                if current_price <= highest_limit and current_price > value:
                    highest_limit = limit[idx - 1]
                    return [highest_limit, limit[idx + 1]]

    def determineLowestPrice(self, lowest_price, current_price):
        if current_price <= lowest_price:
            return current_price
        else:
            return lowest_price

    def buyAlgo(self):
        last_entry = self.df.iloc[-1].to_dict()
        old_sellprice = last_entry["sell_price"]
        loop_one = True
        # limit presents an array of prices which it would be profitable to buy as in regard to the last sellprice
        limit = self.buy_limit(old_sellprice)
        # highest limit is old_sellprice*0.9 at the start. For refererence check buy_limit function
        highest_limit = limit[0]
        next_limit = limit[1]
        lowest_price = old_sellprice
        while (loop_one == True):
            time.sleep(1.2)
            # print("checking sellprice")
            # gets current bidprice
            current_price = float(self.getAskprice())
            get_limit = self.getBuyLimits(
                current_price, limit, highest_limit, next_limit)
            # print(check_sellprice)
            highest_limit = get_limit[0]
            next_limit = get_limit[1]
            lowest_price = self.determineLowestPrice(
                lowest_price, current_price)
            self.printData("buying", current_price,
                           highest_limit, limit, next_limit, lowest_price)
            # compares current bidprice with possible lowest sellprice
            if highest_limit <= limit[1] and current_price > highest_limit:
                self.buyAddOrder()
                self.setParameter(current_price)
                loop_one = False

                # not sure if this condition is necassary because this is the only othercase
    def sell_limit(self, price):
        const = 1.015
        limit = [1.015*price]
        while (const < 3):
            const = const + 0.01
            limit.append(const*price)
        return limit

    def getSellLimits(self, current_price, limit, highest_limit, next_limit):
        # if highestlimit = limit[0] and is still in intervall between(limt0,limit1)
        if current_price < limit[1] and highest_limit == limit[0]:
            return [highest_limit, limit[1]]
        elif current_price < highest_limit:
            return [highest_limit, next_limit]
        else:
            for idx, value in enumerate(limit):
                # case: highest limit is lower then the checked value and current price is higher then value -> sets highest limit
                # if highest limit = limit [0] this wont trigger and go to else because limit[0] is never smaller then limit[0]
                if current_price >= highest_limit and current_price < value:
                    highest_limit = limit[idx - 1]
                    return [highest_limit, limit[idx + 1]]

    def determineHighestPrice(self, highest_price, current_price):
        if current_price >= highest_price:
            return current_price
        else:
            return highest_price

    def sellAlgo(self):
        # loads last enty to get the last buyprice
        last_entry = self.df.iloc[-1].to_dict()
        old_buy_price = last_entry["buy_price"]
        loop_one = True
        # limit presents an array of prices which it would be profitable to sell as in regard to the last buyprice
        limit = self.sell_limit(old_buy_price)
        # highest limit is old_buyprice*1.1 at the start. For refererence check buy_limit function
        highest_limit = limit[0]
        next_limit = limit[1]
        highest_price = 0
        while (loop_one == True):
            time.sleep(1.2)
            # print("checking sellprice")
            # gets current bidprice
            current_price = float(self.getBidprice())
            get_limit = self.getSellLimits(
                current_price, limit, highest_limit, next_limit)
            highest_limit = get_limit[0]
            next_limit = get_limit[1]
            highest_price = self.determineHighestPrice(
                highest_price, current_price)
           # print(check_sellprice)
            self.printData("selling", current_price,
                           highest_limit, limit, next_limit, highest_price)
            # compares current bidprice with possible lowest sellprice
            if highest_limit >= limit[1] and current_price < highest_limit:
                self.sellAddOrder()
                self.setParameter(current_price)
                loop_one = False

            # if(current_price > highest_limit):
            #     # if bidprice is above sellprice it sets it as the highes sellprice
            #     highest_limit = check_sellprice
            # # if the esset is under the sellprice then resume the loop and start again
            # elif(check_sellprice < limit[0]):
            #     pass
            # # this is the case if the current bidprice is between the highest_limit and limit[0]
            # elif check_sellprice < highest_limit and check_sellprice > limit[0]:
            #     print("selling")
            #     self.sellAddOrder()
            #     sell_price = check_sellprice
            #     self.setParameter(sell_price)
            #     #self.argsetter("sell_price", sell_price)
            #     loop_one = False
            # else:
            #     pass
    # 1.buy/sellalgo
    # 2. buy algo must return data for sell Algo
    # 3.sellAlgo must return data for buy algo
    # 4. data sould be saved in one csv file or thru a different function


a = KrakenControl(Kraken)
a.setAsset("Cardano")
a.callAlgo()

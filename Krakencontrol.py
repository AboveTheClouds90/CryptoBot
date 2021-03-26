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
from test import *
import os


def clear():
    return os.system('clear')


class KrakenControl(Kraken):

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
        return last_entry["counter"]

    def callAlgo(self):
        loop = True
        self.loadLog()
        # needs to be replaced with something else in program n.
        while loop == True:
            last_entry = self.df.iloc[-1].to_dict()
            if last_entry["buy_price"] == 0:
                # self.testBuyAlgo()
                self.buyAlgo()
            else:
                # self.testSellAlgo()
                self.sellAlgo()
            print(last_entry)
            user_input = int(input("Enter 0 to exit program:"))
            print(user_input)
            if user_input == 0:
                self.df.to_csv("log.csv", index=False)
                loop = False

    def calcNextLimit(self, limit, highest_limit):
        for i in range(len(limit)):
            if limit[i] == highest_limit:
                calculate_next_limit = limit[i+1]
                return calculate_next_limit

    def calcExecLimit(self, limit, highest_limit):
        for i in range(len(limit)):
            if limit[i] == highest_limit:
                calculate_execute_limit = limit[i-1]
                return calculate_execute_limit

    def getCurrentData(self, current_state, current_price, highest_limit, limit):
        calculate_next_limit = self.calcNextLimit(limit, highest_limit)
        calculate_execute_limit = self.calcExecLimit(limit, highest_limit)
        data = {"current_price": current_price, "highest_limit": highest_limit,
                "next_limit": calculate_next_limit, "execute_limit": calculate_execute_limit,
                "current_state": current_state}
        return data

    def printData(self, current_state, current_price, highest_limit, limit):
        data = self.getCurrentData(
            current_state, current_price, highest_limit, limit)
        clear()
        for key in data:
            print(f"{key}:  " + f"{data[key]}\n")

    def setParameter(self, arg):
        # gets current counter
        counter = self.getCounterLastEntry()
        # gets counter length. However the substracts -1 because the counter itself is not an argument
        counter_length = len(self.df.iloc[-1].to_dict().keys())-1
        # checks if it's the last entry
        if counter < counter_length:
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
            self.algo_args = {"buy_price": 0, "additional": 0,
                              "sell_price": 0, "counter": 0}
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
        const = 0.95
        limit = [0.95]
        while (const > 0.1):
            limit.append(const*price)
            const = const - 0.02
        return limit
    # retruns an array with values up from 1.1 in 0.025 intervarls
    # same purpose as the buy_limit function but only for selling respective asset.

    def sell_limit(self, price):
        const = 1.05
        limit = [1.05]
        while (const < 3):
            limit.append(const*price)
            const = const + 0.02
        return limit

    # TODO last_entry should be its own function to check if it should start with buy/sellAlgo function

    def buyAlgo(self):
        last_entry = self.df.iloc[-1].to_dict()
        old_sellprice = last_entry["sell_price"]
        loop_one = True
        # limit presents an array of prices which it would be profitable to buy as in regard to the last sellprice
        limit = self.buy_limit(old_sellprice)
        # highest limit is old_sellprice*0.9 at the start. For refererence check buy_limit function
        highest_limit = limit[0]
        while(loop_one == True):
            time.sleep(1.2)

            #print("checking buyprice")
            # gets current ask price
            check_buyprice = float(self.getAskprice())
            # print(check_buyprice)
            self.printData("buying", check_buyprice, highest_limit, limit)
            # compares current askprice with the the price at which the asset would be a buy.
            # Smaller check_buyprice -> more profit.
            if (check_buyprice < highest_limit):
                highest_limit = check_buyprice
            # if the esset is above the buyprice then resume the loop and start again
            elif (check_buyprice > limit[0]):
                pass
            # this is the case if the current askprice is between the highest_limit and limit[0]
            else:
                for value in limit:
                    # TODO is this even necessary? these should be covered thru the other if/else cases
                    # check_buyprice < value -> must be lower then limit[0]
                    # check_buyprice > highest limit -> dropped down from anothter limit
                    if (check_buyprice > value and check_buyprice > highest_limit):
                        print("buying")
                        self.printData("buying", check_buyprice,
                                       highest_limit, limit)
                        self.buyAddOrder()
                        # TODO NEEDS WORK SINCE PANDAS CSV CHANGE _--_OLD CODE for reference TODO delete later
                        # self.setArgsBuyprice(check_buyprice)
                        # self.setCounter()
                        # _--_OLD CODE for reference TODO delete later
                        buy_price = check_buyprice
                        # logs price at which asset was bought
                        self.setParameter(buy_price)
                        # temporarily saves currenz buyprice in algo args.
                        # TODO needs to be reseted after one cycle
                        #self.argsetter("buy_price", buy_price)
                        loop_one = False
                        # not sure if this condition is necassary because this is the only othercase

    def sellAlgo(self):
        # loads last enty to get the last buyprice
        last_entry = self.df.iloc[-1].to_dict()
        old_buy_price = last_entry["buy_price"]
        loop_one = True
        # limit presents an array of prices which it would be profitable to sell as in regard to the last buyprice
        limit = self.sell_limit(old_buy_price)
        # highest limit is old_buyprice*1.1 at the start. For refererence check buy_limit function
        highest_limit = limit[0]
        while (loop_one == True):
            time.sleep(1.2)
            #print("checking sellprice")
            # gets current bidprice
            check_sellprice = float(self.getBidprice())
            # print(check_sellprice)
            self.printData("buying", check_sellprice, highest_limit, limit)
            # compares current bidprice with possible lowest sellprice
            if(check_sellprice > limit[0]):
                # if bidprice is above sellprice it sets it as the highes sellprice
                highest_limit = check_sellprice
            # if the esset is under the sellprice then resume the loop and start again
            elif(check_sellprice < limit[0]):
                pass
            # this is the case if the current bidprice is between the highest_limit and limit[0]
            else:
                for value in limit:
                    # TODO same as buyalgo problem
                    if(check_sellprice < value and check_sellprice < highest_limit):
                        print("selling")
                        self.printData("selling", check_sellprice,
                                       highest_limit, limit)
                        self.sellAddOrder
                        # TODO csv pandaas stuff --- OLD CODE
                        # self.setArgsSellprice(check_sellprice)
                        # self.setCounter()
                        # TODO OLDCODE for reference
                        sell_price = check_sellprice
                        self.setParameter(sell_price)
                        #self.argsetter("sell_price", sell_price)
                        loop_one = False
    # 1.buy/sellalgo
    # 2. buy algo must return data for sell Algo
    # 3.sellAlgo must return data for buy algo
    # 4. data sould be saved in one csv file or thru a different function


a = KrakenControl(Kraken)
a.setAsset("Algorand")
a.callAlgo()

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
import numpy as np

# help function for clearing console -> dataoutput in console, ->d ef printAndLog() 
def clear():
    return os.system('clear')


'''
Using data from kraken api generated with the Kraken class. KrakenControl, handles the trading algorithm, data and gives an output to the console with necessary data and current progress.
'''
class KrakenControl(Kraken):

    #super().__int__(): Imports attributes from krakenclass.py
    def __init__(self, parent):
        super().__init__()


    #----------------------------Mainfunction calling algo functions

    #calls Algo functions, loads data from prev. session
    def callAlgo(self):
        loop = True
        #loading data from last session
        self.loadBuyCsv()
        self.loadSellCsv()
        while loop:
            if self.compareIndex() == True:
                self.sellAlgo()
            else:
                self.buyAlgo()
    #------------------------------algo functions
    '''
    The currently implemented algorithm is similar to a trailing stop-loss order. It is meant to swing trade assets over a span of hours, days or even weeks
    Arrays of thresholds are set by the functions buyLimit() and sellLimit() in certain intervalls. If a threshold is reached the bot will constantly check if it drops 
    below that threshold the bot will buy/sell the asset.
    '''

    def buyAlgo(self):
        loop_one = True
        
        #the last price the assets were sold for
        old_sellprice = self.sell_price[-1]
        
        # limit presents an array of prices which it would be profitable to buy as in regard to the last sellprice
        limit = self.buyLimit(old_sellprice)
        # highest limit is old_sellprice*0.9 at the start. For refererence check buyLimit function
        highest_limit = limit[0]
        next_limit = limit[1]
        lowest_price = old_sellprice
        #will constantly check prices when to buy 
        while (loop_one == True):
            time.sleep(1.2)
            # gets current askprice
            current_price = float(self.getAskprice())
            #checks if new buylimits/thresholds need to be set and gets them
            get_limit = self.getBuyLimits(
                current_price, limit, highest_limit, next_limit)
            highest_limit = get_limit[0]
            next_limit = get_limit[1]
            #setting lowest price reached while buyAlgo is running,
            lowest_price = self.determineLowestPrice(
                lowest_price, current_price)
            self.printAndLog("buying",current_price,highest_limit,limit,next_limit,lowest_price)
            if highest_limit <= limit[1] and current_price > highest_limit:
                self.buyAddOrder()
                #self.setParameter(current_price)
                self.buy_price = np.append(self.buy_price, [current_price])
                self.printAndLog("bought",current_price,highest_limit,limit,next_limit,lowest_price)
                self.safeCsv()
                loop_one = False
    
    def sellAlgo(self):
        # infinite Loop to check price until it reaches threshhold TODO: long-term solution
        loop_one = True
        # Price at which the currency was bought
        old_buy_price = self.buy_price[-1]      
        # limit presents an array with different Price-thresholds. The Intervalls are set with self.sellLimit(old_buyprice)
        limit = self.sellLimit(old_buy_price)
        #highest limit: Highest threshold reached til this point of time. 
        #next limit: next threshold after highes limit
        highest_limit = limit[0]
        next_limit = limit[1]
        highest_price = 0

        while (loop_one == True):
            #sleep -limited API-calls
            time.sleep(1.2)            
            current_price = float(self.getAskprice())
            #getting new sell limits
            current_limits = self.getSellLimits(current_price, limit, highest_limit, next_limit)
            #setting new limits
            highest_limit = current_limits[0]
            next_limit = current_limits[1]
            #setting highest price reached while sellAlgo is running,
            highest_price = self.determineHighestPrice(highest_price, current_price)
            #log functions TODO: more efficient
            self.printAndLog("selling",current_price,highest_limit,limit,next_limit,highest_price)
            # highest_limit >= limit[1] checks if the highest limit isnt still limit[0]
            # current_price < highest_limit checks if the price dropped under a limit(except limit[0] since this is cleared with the first condition)
            # if it did the trade becomes profitable 
            if highest_limit >= limit[1] and current_price < highest_limit:
                #selling
                self.sellAddOrder()
                self.sell_price = np.append(self.sell_price, [current_price])
                self.safeCsv()
                #logging some additional information
                self.printAndLog("sold",current_price,highest_limit,limit,next_limit,highest_price)
                loop_one = False
    #------------------------------Algo methods
    
    #---------------------------------Generating Buy/Sell threshholds as an array
    def buyLimit(self, price):
        const = 0.99
        threshold_intervall= 0.01
        #first threshold (limit[0]) with price being the last sellprice
        #const needs to be set <1
        limit = [0.99*price]
        #creating array with multiple thresholds at certain intervallsintervalls
        while (const > 0.15):
            const = const - threshold_intervall
            limit.append(const*price)
        return limit
    #analogue to buyLimit()
    def sellLimit(self, price):
        const = 1.01
        threshold_intervall= 0.01
        limit = [1.01*price]
        while (const < 3):
            const = const + threshold_intervall
            limit.append(const*price)
        return limit
    #-----------------------------------------
    def calcExecLimit(self, limit, highest_limit):
        if limit[0] == highest_limit:
            calculate_execute_limit = 0
            return calculate_execute_limit
        else:
            for i in range(len(limit)):
                if limit[i] == highest_limit:
                    calculate_execute_limit = limit[i-1]
                    return calculate_execute_limit

    #------------------------------getBuyLimits and getSellLimits are setting new thresholds/limits 
    
    def getBuyLimits(self, current_price, limit, highest_limit, next_limit):
        # If the current price is still in the Intervall between highest_limit = limit[0] and limit[1], it returns those values
        if current_price > limit[1] and highest_limit == limit[0]: #1 anstatt 0 ursprünglich
            return [highest_limit, limit[1]]
        #nothing changes here, no new limits need to be set if the price remains above the potential buyprice
        elif current_price > highest_limit:
            return [highest_limit, next_limit]
        else:
            # enumerates all limits looking for an intervall of two threshholds that includes currents price 
            # -> returns the new highest limit and the next one
            for idx, value in enumerate(limit):
                if current_price <= highest_limit and current_price > value:
                    highest_limit = limit[idx - 1]
                    return [highest_limit, limit[idx + 1]]
    
    #analogue to getBuyLimits
    def getSellLimits(self, current_price, limit, highest_limit, next_limit):
        if current_price < limit[1] and highest_limit == limit[0]:
            return [highest_limit, limit[1]]
        elif current_price < highest_limit:
            return [highest_limit, next_limit]
        else:
            for idx, value in enumerate(limit):
                if current_price >= highest_limit and current_price < value:
                    highest_limit = limit[idx - 1]
                    return [highest_limit, limit[idx + 1]]
    
    #Determining lowest/highest price for this session while sellAlgo() or buyAlgo() is running
    def determineLowestPrice(self, lowest_price, current_price):
        if current_price <= lowest_price:
            return current_price
        else:
            return lowest_price
    
    def determineHighestPrice(self, highest_price, current_price):
        if current_price >= highest_price:
            return current_price
        else:
            return highest_price
    #-----------------------------------------Datahandling

    #creates Dataframe 
    def createDf(self):
        self.df_sell = pd.DataFrame({"Sellprice": self.sell_price})
        self.df_buy = pd.DataFrame({"Buyprice": self.buy_price})
    
    #loads data/sell/buyprices from previous sessions
    def loadSellCsv(self):
        data_sell = pd.read_csv("sell.csv")
        self.sell_price = data_sell["Sellprice"].to_numpy()
    
    def loadBuyCsv(self):
        data_buy = pd.read_csv("buy.csv")
        self.buy_price = data_buy["Buyprice"].to_numpy()
    
    #saving data to csv
    def safeCsv(self):
        self.createDf()
        self.df_buy.to_csv("buy.csv", index = False)
        self.df_sell.to_csv("sell.csv", index = False)
    #getting data for functional purposes
    #-> if  len(self.sell_price) < len(self.buy_price) algo needs to sell its position next
    #-> used and handled by callAlgo() fct
    #len(self.sell_price) > len(self.buy_price) should never occur. If it does, check csv files for manual modifactions.
    def getIndexSell(self):
        return len(self.sell_price)
    
    def getIndexBuy(self):
        return len(self.buy_price)

    def compareIndex(self):
        if self.getIndexBuy() == self.getIndexSell():
            return True
        else:
                return self.getIndexBuy()-self.getIndexSell()



    def getCurrentData(self, current_state, current_price, highest_limit, limit, next_limit, max_min_price):
        calculate_execute_limit = self.calcExecLimit(limit, highest_limit)
        data = {"current_price": current_price, "highest_limit": highest_limit,
                "next_limit": next_limit, "Highest/lowest_price": max_min_price, "execute_limit": calculate_execute_limit,
                "current_state": current_state}
        return data

    def printAndLog(self, current_state, current_price, highest_limit, limit, next_limit, max_min_price):
        data = self.getCurrentData(current_state, current_price, highest_limit, limit, next_limit, max_min_price)
        
        #log:
        df = pd.read_csv("log.csv", index_col=0)
        df = df.append(data, ignore_index = True)
        df.to_csv("log.csv")
        #print:
        clear()
        for key in data:
                if data["execute_limit"] == 0 and key == "execute_limit":
                    print(f"{key}:  " + f"Not yet available\n")
                else:
                    print(f"{key}:  " + f"{data[key]}\n")



 
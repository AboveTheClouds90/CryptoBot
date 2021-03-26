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
from tkinter import *


class Gui():
    def __init__(self, parent):
        # loads object from control class
        self.control = Control()
        # loads object from TKINTER
        #self.root = Tk()
        # self.root.geometry("450x350")
        # creates frames in other frames for structuring purposes
        self.frame_master = Frame(parent, bg="black", bd=6)
        self.frame_master_second = Frame(self.frame_master, bg="red")
        self.frame_master_third = Frame(self.frame_master, bg="yellow")
        # frame 1 is the left frame of the left frame(master second)
        self.frame1 = Frame(self.frame_master_second, bg="grey")
        # names of the variables that will be displayed on the right side
        self.label_name_selling = Label(self.frame1, text="Selling", bg="grey")
        self.label_name_current_price_sell = Label(
            self.frame1, text="Current Price", bg="grey")
        self.label_name_highest_limit_sell = Label(
            self.frame1, text="Highest Limit", bg="grey")
        self.label_name_next_limit_sell = Label(
            self.frame1, text="Next limit", bg="grey")
        self.label_name_sell_limit_sell = Label(
            self.frame1, text="Sell limit", bg="grey")
        self.label_name_buying = Label(self.frame1, text="Buying", bg="grey")
        self.label_name_current_price_buy = Label(
            self.frame1, text="Current Price", bg="grey")
        self.label_name_highest_limit_buy = Label(
            self.frame1, text="Highest Limit", bg="grey")
        self.label_name_next_limit_buy = Label(
            self.frame1, text="Next limit", bg="grey")
        self.label_name_sell_limit_buy = Label(
            self.frame1, text="Sell limit", bg="grey")
        # variables that will be displayed on the right side
        # functions get values from Krakencontrol() and load them into respective inputs
        self.frame2 = Frame(self.frame_master_second, bg="#414141")
        self.label_buyprice_input = StringVar()
        self.label_buyprice = Label(
            self.frame2, textvariable=self.label_buyprice_input, bg="#414141")
        self.label_sellprice_input = StringVar()
        self.label_sellprice = Label(
            self.frame2, textvariable=self.label_sellprice_input, bg="#414141")
        self.setLabel()
        self.packWidgets()

    def setLabel(self):
        buyprice = self.control.setBuyprice()
        sellprice = self.control.setSellprice()
        #self.label_buyprice_input = str(buyprice)
        self.label_buyprice_input.set(str(buyprice))
        self.label_sellprice_input.set(str(sellprice))
        self.label_buyprice.after(1000, self.setLabel)
        # n = self.label_buyprice_input
        # self.label_buyprice.configure(textvariable=n)

    def packWidgets(self):
        self.frame_master.pack(fill=BOTH)
        self.frame_master_second.pack(side=LEFT)
        self.frame_master_third.pack(side=RIGHT, expand=True, fill=BOTH)
        self.frame1.pack(side=LEFT, expand=True)

        self.label_name_selling.grid(row=0, column=0)
        self.label_name_current_price_sell.grid(row=1, column=0, sticky=W)
        self.label_name_highest_limit_sell.grid(row=2, column=0, sticky=W)
        self.label_name_next_limit_sell.grid(row=3, column=0, sticky=W)
        self.label_name_sell_limit_sell.grid(row=4, column=0, sticky=W)
        self.label_name_buying.grid(row=5, column=0)
        self.label_name_current_price_buy.grid(row=6, column=0, sticky=W)
        self.label_buyprice.grid(row=6, column=1, sticky=E)
        self.label_name_highest_limit_buy.grid(row=7, column=0, sticky=W)
        self.label_name_next_limit_buy.grid(row=8, column=0, sticky=W)
        self.label_name_sell_limit_buy.grid(row=9, column=0, sticky=W)

        self.frame2.pack(side=RIGHT, fill=BOTH)
        self.label_buyprice.grid(row=6, column=1, sticky=E)
        self.label_sellprice.grid(row=7, column=1, sticky=E)

    # def createGui(self):


class Control:
    def __init__(self):
        # self.control = Model()
        self.number = 1
        self.sell = 2

    def setBuyprice(self):
        self.number = self.number + 1
        print(self.number)
        return self.number

    def setSellprice(self):
        self.sell = self.sell + 0.5
        return self.sell

# class Model:
#     def __init__(self):
#         self.number = 1


root = Tk()
a = Gui(root)
# a.runExe()
#root.after(1000, a.setLabel())
# a.setLabel()
root.mainloop()

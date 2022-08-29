from krakenclass3 import *
from Krakencontrol import *


bot = KrakenControl(Kraken)
#set asset to whatever the bot is supposed to trade.
bot.setAsset("Cardano")
bot.callAlgo()

# CryptoBot

Use the bot at your own risk. I will not be responsible for any losses. This is just a small project not fully tested to make "profit".

1. For further information on the API check https://docs.kraken.com/rest/
2. To get started create an API-key on kraken.com and insert in krakenclass3.py constructor.
3. Buy an asset on the kraken exchange. Check API documentation for further information on the asset, like minimum trade limit, fees etc.
4. Insert at which price you bought the asset in buy.csv
5. Otherwise do not change formats of buy.csv, log.csv or sell.csv. 
6. Insert your asset in runbot.py -> bot.setAsset("....")
7. Open Krakencontrol.py.Set variable threshhold_intervalls from functions buyLimit() and sellLimit() to your liking.
8. run runbot.py


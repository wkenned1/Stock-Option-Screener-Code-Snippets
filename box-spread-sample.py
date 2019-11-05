from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib.request
import datetime as dt
from optionable_list_imp import *

#robinhood login
import robin_stocks as r
login = r.login("""email""", """password""")
#get list of ticker symbols which were scraped from the web
tickers = big_ticker_list
file = open("boxes_spreads.txt", "w+")

short_call = None
long_call = None
short_put = None
long_put = None

##finding opportunities for each stock in the list
for t in tickers:
    file.write(t + "\n")
    print(t)
    
    temp_short = None
    temp_long = None

    try:
    
        expirations = r.options.get_chains(t)['expiration_dates']
        #selecting the second soonest expiration date for options (usually two weeks out)
        calls = r.options.find_options_for_stock_by_expiration(t, str(expirations[1]), 'call')
        puts = r.options.find_options_for_stock_by_expiration(t, str(expirations[1]), 'put')
        latest_price = r.stocks.get_latest_price(t)
        strikes = []
        p_strikes = []
        call_prices = []
        put_prices = []
        first_strike_above = -1

        #get strike prices
        for i in range(0, len(calls)):
            strikes.append(float(calls[i]['strike_price']))
        for i in range(0, len(puts)):
            p_strikes.append(float(puts[i]['strike_price']))

        
        temp = zip(strikes, calls)
        sorted_calls = [x for _, x in sorted(temp)]

        temp_p = zip(p_strikes, puts)
        sorted_puts = [x for _, x in sorted(temp_p)]
        strikes.sort()

        for index in range(0, len(strikes)):
            if(float(strikes[index]) > float(latest_price[0])):
               first_strike_above = index;
               break

        first_strike_below = first_strike_above - 1

        #finding call spread
        low_strike = first_strike_below
        while low_strike > 0:
            
            high_strike = first_strike_above
            
            while high_strike < len(strikes) - 1:
                
                max_gain = strikes[high_strike] - strikes[low_strike]

                temp_long_call = sorted_calls[low_strike]
                temp_short_put = sorted_puts[low_strike]
                temp_short_call = sorted_calls[high_strike]
                temp_long_put = sorted_puts[high_strike]
                
                debit_calls = float(temp_long_call['high_fill_rate_buy_price']) - float(temp_short_call['high_fill_rate_sell_price'])
                debit_puts = float(temp_long_put['high_fill_rate_buy_price']) - float(temp_short_put['high_fill_rate_sell_price'])

                if(float(temp_long_call['open_interest']) > 100 and float(temp_short_call['open_interest']) > 100 and float(temp_long_put['open_interest']) > 100 and float(temp_short_put['open_interest']) > 100):
                    open_interest = True
                #check for high volume    
                if(open_interest == True and (debit_calls + debit_puts) <= (max_gain - .01) and float(temp_long_call['volume']) > 100 and float(temp_short_call['volume']) > 100 and float(temp_long_put['volume']) > 100 and float(temp_short_put['volume']) > 100):
                    long_call = temp_long_call
                    short_call = temp_short_call
                    long_put = temp_long_put
                    short_put = temp_short_put
                    #check for profitable box spread opportunity
                    file.write((t + " Exp " + temp_long_call['expiration_date'] + " Strikes " + str(strikes[low_strike]) + " " + str(strikes[high_strike])+ " "+ "Max debit "+ str(max_gain)+ " "+ str(debit_calls)+ " "+ str(debit_puts) + " Return " + str(max_gain - debit_calls - debit_puts) + "\n"))
                high_strike = high_strike + 1
                
            low_strike = low_strike - 1

        #search opposite strike prices from previous loop
        low_strike = first_strike_below
        while low_strike > 0:
            
            high_strike = first_strike_above
            
            while high_strike < len(strikes) - 1:
                
                max_loss = strikes[high_strike] - strikes[low_strike]

                temp_long_call = sorted_calls[high_strike]
                temp_short_put = sorted_puts[high_strike]
                temp_short_call = sorted_calls[low_strike]
                temp_long_put = sorted_puts[low_strike]
                
                credit_calls = float(temp_short_call['high_fill_rate_sell_price']) - float(temp_long_call['high_fill_rate_buy_price'])
                credit_puts = float(temp_short_put['high_fill_rate_sell_price']) - float(temp_long_put['high_fill_rate_buy_price'])

            
                open_interest = False
                if(float(temp_long_call['open_interest']) > 100 and float(temp_short_call['open_interest']) > 100 and float(temp_long_put['open_interest']) > 100 and float(temp_short_put['open_interest']) > 100):
                    open_interest = True      
                #filtering out low volume options
                if(open_interest == True and (credit_calls + credit_puts) >=  (max_loss + .01)  and float(temp_long_call['volume']) > 100 and float(temp_short_call['volume']) > 100 and float(temp_long_put['volume']) > 100 and float(temp_short_put['volume']) > 100):
                    long_call = temp_long_call
                    short_call = temp_short_put
                    long_put = temp_long_put
                    short_put = temp_short_put
                    #identifying profitable box spread opportunities
                    file.write((t + " Exp " + temp_long_call['expiration_date'] + " Strikes " + str(strikes[low_strike]) + " " + str(strikes[high_strike])+ " "+"Max credit "+ str(max_loss)+ " "+ str(credit_calls)+ " "+ str(credit_puts) + " Return " + str(credit_calls + credit_puts - max_loss) + "\n"))
                high_strike = high_strike + 1
                
            low_strike = low_strike - 1
        
    except:
        print("Error on ", t)

file.close()


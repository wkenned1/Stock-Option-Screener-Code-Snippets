from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib.request
import datetime as dt

#read New York Stock Exchange website
fp = urllib.request.urlopen("https://www.nyse.com/products/options-nyse-american-short-term")
mybytes = fp.read()

#get ticker symbols from table
soup = BeautifulSoup(mybytes, features="lxml")
table = soup.find("table", attrs={"class":"table table-data"})
table = table.find("tbody")
table = table.get_text().split("\n")
#create list of ticker symbols
tickers = []
for i in range(2, len(table)):
    if((i-2) % 4 == 0):
        tickers.append(table[i])
print(tickers)
print(len(tickers))

mystr = mybytes.decode("utf8")
fp.close()

#print(mystr)

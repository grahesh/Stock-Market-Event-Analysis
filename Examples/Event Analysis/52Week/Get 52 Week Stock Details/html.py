#-------------------------------------------------------------------------------
# Name:        Fifty Two Week Parser for www.nseindia.com
# Purpose:     Fetch the 52 week high & low dates from the NSE website
#
# Author:      Ashwin
#
# Created:     22/01/2013
# Copyright:   (c) Ashwin 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import requests
import csv
import json
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class FiftyTwoWeekParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = 0
        self.data = ""


    def handle_starttag(self, tag, attrs):
        if tag == 'div':

            if self.flag == 1:
                self.flag = 0
            for name,value in attrs:
                if name == "id" and value == "responseDiv":
                    self.flag = 1



    def handle_data(self, data):
        if self.flag == 1:
            self.data += data


#################################
#################################
##                             ##
##          Main Code          ##
##                             ##
#################################
#################################

# Reading the Symbols of CNX 100 from the File using csv lib
CNX100 = open("ind_cnx100list.csv","r")
CNX100Reader = csv.reader(CNX100,delimiter=",")

flag = 1
##csvData = "flag|symbol|52 week High date|52 week High price|52 week low date|52 week low price\n"
csvData = "flag|symbol|52 week High date|52 week low date\n"


for row in CNX100Reader:
    if flag == 1:
        flag = 0
        continue

    try :

        # HTML Parser Object
        html = FiftyTwoWeekParser()
        symbol = row[2]

        #print symbol


        # Getting the Request Object For the URL
        requestObj = requests.get("http://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol="+symbol)
        content = requestObj.content

        print symbol

        # Feeding the HTML Parser with the requested Content i.e HTML of the URL
        html.feed(content)


        # Removing the Extra White Spaces
        data = html.data.strip()

        #print data

        # Converting to JSON Object
        jsonObj = json.loads(data)

        print symbol

        # Fetching the Data From the JSON Object
        highDate = jsonObj['data'][0]['cm_adj_high_dt']
##        highValue = jsonObj['data'][0]['cm_adj_high']
        lowDate = jsonObj['data'][0]['cm_adj_low_dt']
##        lowValue = jsonObj['data'][0]['cm_adj_low']


##        csvData += "Y|"+symbol+"|"+highDate+"|"+highValue+"|"+lowDate+"|"+lowValue+"\n"
        csvData += "Y|"+symbol+'.NS'+"|"+highDate+"|"+lowDate+"\n"


    except Exception as ex:
        print "Error Message : ", ex




# print csvData

#Writing data to csv file

try:
    outputFile = open("52Week.csv","w")
    outputFile.write(csvData)
    print "File Sucessuflly Written to "+outputFile.name
    outputFile.close()
    CNX100.close()
except Exception as ex:
    print "Error Message : ", ex



# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 10:55:19 2013

@author: Grahesh Parkar
"""

import pandas
from qstkutil import DataAccess as da
import numpy as np
import math
import copy
import qstkutil.qsdateutil as du
import datetime as dt
import qstkutil.DataAccess as da
import qstkutil.tsutil as tsu
import qstkstudy.EventProfiler as ep
import qstkstudy.Event_Analysis as ea
import requests


# formats the raw stock details file data into an array

def formatData(rawData):
    formattedData=[]
    rows=rawData.split('\n')
    for row in rows:
        cellData=[]
        cells=row.split(',')
        for cell in cells:
            if(cell!=''):
                cellData.append(cell)
        formattedData.append(cellData)
    return formattedData


##def formatConfigData(rawData):
##    formattedData = dict()
##    rows=rawData.split('\n')
##    for row in rows:
##        cells=row.split(',')
##        if(cells[0]=='Columns'):
##            cellData=[]
##            for i in range(1,len(cells)):
##                if(cells[i]!=''):
##                    cellData.append(cells[i])
##            formattedData[cells[0]]=cellData
##        else:
##            formattedData[cells[0]]=cells[1]
##    return formattedData


# formats the raw configuration file details data into an a dictionary

def formatConfigData(rawData):
    conditions=[]
    formattedData = dict()
    rows=rawData.split('\n')
    for row in rows:
        cells=row.split(',')
        if(cells[0]=='END'):
            conditions.append(formattedData)
            formattedData=dict()
        else:
            if(cells[0]=='Columns'):
                cellData=[]
                for i in range(1,len(cells)):
                    if(cells[i]!=''):
                        cellData.append(cells[i])
                formattedData[cells[0]]=cellData
            else:
                formattedData[cells[0]]=cells[1]
    return conditions


#################################################
################ MAIN CODE ######################
#################################################

##configFileKey=raw_input("Enter The Configuration File Key.")

### config file with columns
##configFileKey='0AjoNUMfP67sMdDh2THZXb2xjRjN6WXY2Zm8xM3hRbFE'

### config file without columns
##configFileKey='0AjoNUMfP67sMdHY0OG9yTjZuR0oyUnhUYUZwOVBzQnc'

### config file without columns ignored
##configFileKey='0AjoNUMfP67sMdEVXdGMwRW9yVnVGNkRSUnluTG0xcUE'

# config file two entries
configFileKey='0AjoNUMfP67sMdHpHS3ZNSHJxRWVBSlZ2NFhocjdDNEE'

# gets data from configuration file in google docs using key
configResponse = requests.get('https://docs.google.com/spreadsheet/ccc?key='+configFileKey+'&output=csv')
config_data=formatConfigData(configResponse.text)


# loops through different event analysis scenarios mentioned in config file
for condition in config_data:
    stockFileResponse = requests.get('https://docs.google.com/spreadsheet/ccc?key='+condition["File_Key"]+'&output=csv') # gets raw data from stock details file in google docs
    stockFileData=formatData(stockFileResponse.text)

# creates object of Event_Analysis Class and passes config data and formatted stock file data
    eventAnalysis=ea.EventAnalysis(condition, stockFileData)
    eventAnalysis.AnalyseEvents()





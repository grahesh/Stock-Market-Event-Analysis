# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 10:55:19 2013

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


# config file with columns
configFileKey='0AjoNUMfP67sMdDVSdlJvM29XcHhWMGVtekxJeUlyRFE'

configResponse = requests.get('https://docs.google.com/spreadsheet/ccc?key='+configFileKey+'&output=csv')
config_data=formatConfigData(configResponse.text)
##print config_data

for condition in config_data:
    stockFileResponse = requests.get('https://docs.google.com/spreadsheet/ccc?key='+condition["File_Key"]+'&output=csv')
    stockFileData=formatData(stockFileResponse.text)

    eventAnalysis=ea.EventAnalysis(condition, stockFileData)
    eventAnalysis.AnalyseEvents()





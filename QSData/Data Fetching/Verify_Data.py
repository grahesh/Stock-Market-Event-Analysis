import csv

# reads symbola from symbols.txt file
def read_symbols(s_symbols_file):
    ls_symbols=[]
    file = open(s_symbols_file, 'r')
    for f in file.readlines():
        j = f[:-1]
        ls_symbols.append(j)
    file.close()
    return ls_symbols


path = 'C:/QSTK/QSData/Data Pull/NSEData/'
ls_symbols = read_symbols('symbols.txt')
outputFile=open('Stock_Data_Debug.csv','wb')
cot=csv.writer(outputFile)
j=1

for stock in ls_symbols:
    print 'Reading Data...',stock
    stockPath=path+stock+'.csv'
    inp=open(stockPath,'r')
    symbol_data=inp.readlines()

    for i in range(1,len(symbol_data)-1):
        todayRow = symbol_data[i].split(",") # row contaning curent day's data
        prevRow = symbol_data[i+1].split(",") # row contaning yesterday's data (i+1 because dates in csv file are in reverse order)
        todayPrice = todayRow[4] # current day's closig price
        prevPrice = prevRow[4]  # yesterday's closing price

        if(int(todayRow[0].split('-')[0])>=2007):   # condition to check the year

            ret=((float(todayPrice.replace("\n",""))/float(prevPrice.replace("\n","")))-1)*100  # total return (yesterday and current day)

            if(float(todayRow[1])<1.0 or float(todayRow[2])<1.0 or float(todayRow[3])<1.0 or float(todayRow[4])<1.0 or
                float(todayRow[5])<1.0 or float(todayRow[6].replace("\n",""))<1.0): # (condition to check if any value is less than 1)
                cot.writerow([j,stock])
                cot.writerow(['Previous Date',prevRow])
                cot.writerow(['Today',todayRow])
                cot.writerow(['Returns ',ret])
                cot.writerow('\n')
                j=j+1

            if(ret<-25.0 or ret>25.0):  # condition to check if return value is <-25% or >25%
                cot.writerow([j,stock])
                cot.writerow(['Previous Date',prevRow])
                cot.writerow(['Today',todayRow])
                cot.writerow(['Returns ',ret])
                cot.writerow('\n')
                j=j+1

outputFile.close()
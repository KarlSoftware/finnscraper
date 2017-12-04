import numpy as np
import sys
import pandas as pd
import json
import matplotlib.pyplot as plt


Price = []
Square = []
TravelTime = []
lat = []
lng = []
SquarePrice = []
TestDict = {}
TestDict['W'] = {}
TestDict['E'] = {}

if len(sys.argv) >= 2:
    print(sys.argv)
    with open(sys.argv[1],'r') as infile:
        houses = json.load(infile)
else:
    print('Add argument of json to read')
    sys.exit(0)

for house in houses:
    try:
        t_price = int(houses[house]['price'].replace(',-',''))
        t_square = int(houses[house]['kvadrat'])
        t_travelTime = int(houses[house]['traveltime'].replace(' mins', ''))
        t_lat = float(houses[house]['lat'])
        t_lng = float(houses[house]['lng'])

        if(t_lng >= 10.764459):
            #testing
            if t_travelTime not in TestDict['E']:
                TestDict['E'][t_travelTime] = {}
                TestDict['E'][t_travelTime]['sum'] = 0
                TestDict['E'][t_travelTime]['count'] = 0
            TestDict['E'][t_travelTime]['sum'] += t_price / t_square
            TestDict['E'][t_travelTime]['count'] += 1
        else:
            #testing
            if t_travelTime not in TestDict['W']:
                TestDict['W'][t_travelTime] = {}
                TestDict['W'][t_travelTime]['sum'] = 0
                TestDict['W'][t_travelTime]['count'] = 0
            TestDict['W'][t_travelTime]['sum'] += t_price / t_square
            TestDict['W'][t_travelTime]['count'] += 1
        # assigning



        Price.append(t_price)
        Square.append(t_square)
        SquarePrice.append(t_price / t_square / t_travelTime)
        TravelTime.append(t_travelTime)
        lat.append(t_lat)
        lng.append(t_lng)
    except ValueError:
        print("valueError")

frame = {}
frame['E'] = {'Travel':[],  'Avg':[]}
frame['W'] = {'Travel':[],  'Avg':[]}
for r in TestDict:
    print(len(TestDict[r]))
    for t in TestDict[r]:
        frame[r]['Travel'].append(t)
        frame[r]['Avg'].append(TestDict[r][t]['sum'] / TestDict[r][t]['count'])
#frame = {'Price':Price, 'Square':Square, 'TravelTime':TravelTime, 'lat':lat,  'lng':lng}
#frame = {'SquarePrice':SquarePrice, 'TravelTime':TravelTime}
#df = df.cumsum()
#plt.figure()


df = pd.DataFrame(data=frame['E'])
print(df)
ax = df['Avg'].plot(x='Avg', y='Travel', label='East of Oslo Centrum', legend=True, title="TravelTime SquarePrice East/West Oslo")
ax.set_xlabel("TravelTime collective")
ax.set_ylabel("Square meter price")

df = pd.DataFrame(data=frame['W'])
ax = df['Avg'].plot(x='Avg', y='Travel', label='West of Oslo Centrum', legend=True)
ax.set_xlabel("TravelTime collective")
ax.set_ylabel("Square meter price")

#df['E']['Avg'].hist(by=df['Travel'])
#df.plot.box()
plt.savefig('osloPris.png', dpi=600)
plt.show()

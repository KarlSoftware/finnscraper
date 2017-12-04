from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import googlemaps
from datetime import datetime
import requests
import json
import requests
import gmplot
import collections

#Write inn your API key here
gmaps = googlemaps.Client(key='API_KEY')

# This dict will be populated with scraped information from Finn.no
houses = {}

'''
This will scrape finn with the url sent in as argument
Go to finn, select you area and copy the url
NOTE: Please remove the **&page=1 at the end, as the script will add that
'''
def scrapeFinn(url):
    r  = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, fromEncoding="utf-8")
    try:
        for house in soup.find_all("div", {"class":"unit flex align-items-stretch result-item"}):
            try:
                adress = house.find_all("div", {"class":"licorice valign-middle"})[0].text
                price = house.find_all("p", {"class":"t5 word-break mhn"})[0].find_all("span")[1].text
                kvadrat = house.find_all("p", {"class":"t5 word-break mhn"})[0].find_all("span")[0].text
                gecode_result = gmaps.geocode(adress)
                latetude = gecode_result[0]['geometry']['location']['lat']
                longtitude = gecode_result[0]['geometry']['location']['lng']
                now = datetime.now()
                try:
                    directions_result = gmaps.directions(adress,
                                                         "Oslo Sentralstasjon",
                                                         mode="transit",
                                                         departure_time=now)
                    travelTime = directions_result[0]['legs'][0]['duration']['text']
                    # adding to dict
                    houses[adress] = {}
                    houses[adress]['price'] = price.replace(u"\u00a0", '')
                    houses[adress]['adress'] = adress
                    houses[adress]['kvadrat'] = kvadrat.replace("m\u00b2", '')
                    houses[adress]['lat'] = latetude
                    houses[adress]['lng'] = longtitude
                    houses[adress]['traveltime'] = travelTime
                    print('Successfully addded ' + adress)
                except googlemaps.exceptions.ApiError:
                    print("Error in getting travel time")
            except IndexError:
                print("IndexError in geolocation or finnScraping")
    except googlemaps.exceptions._RetriableRequest:
        print("RetriableRequest error")
        return 0
    except googlemaps.exceptions.Timeout:
        print("Error timeout!")
        return 0


'''
This will get the new data
it will loop over 100 pages of finn
and dump the output as json to file
'''
def getNewData():
    for i in range(0, 100):
        print("\n\n Getting page ", i)
        print("Houses ", len(houses))
        scrapeFinn("https://www.finn.no/realestate/homes/search.html?location=0.20003&location=0.20007&location=0.20061&page=" + str(i))
        with open('dataOslo++.json', 'w') as outfile:
            json.dump(houses, outfile)


def createHeatMapTravelTime():
    heatLat = []
    heatLng = []
    for house in houses:
        for i in range(0, int(houses[house]['traveltime'].replace(' mins', ''))):
            heatLat.append(float(houses[house]['lat']))
            heatLng.append(float(houses[house]['lng']))
    gmap = gmplot.GoogleMapPlotter(59.9019315,10.764459, 11.17)
    #gmap.plot(latitudes, longitudes, 'cornflowerblue', edge_width=10)
    #gmap.scatter(more_lats, more_lngs, '#3B0B39', size=40, marker=False)
    #gmap.scatter(marker_lats, marker_lngs, 'k', marker=True)
    gmap.heatmap(heatLat, heatLng, radius=10)
    gmap.draw("mymap.html")

def createHeatMapOfHouses():
    heatLat = []
    heatLng = []
    for house in houses:
        heatLat.append(float(houses[house]['lat']))
        heatLng.append(float(houses[house]['lng']))
    gmap = gmplot.GoogleMapPlotter(59.9019315,10.764459, 11.17)
    #gmap.plot(latitudes, longitudes, 'cornflowerblue', edge_width=10)
    #gmap.scatter(more_lats, more_lngs, '#3B0B39', size=40, marker=False)
    #gmap.scatter(marker_lats, marker_lngs, 'k', marker=True)
    gmap.heatmap(heatLat, heatLng, threshold=10, radius=30, dissipating=False, gradient=[(30,30,30,0), (30,30,30,1), (50, 50, 50, 1)])
    gmap.heatmap(heatLat, heatLng, threshold=5, radius=10)
    gmap.scatter(heatLat, heatLng, marker=False)
    gmap.draw("finnHouses.html")

def interpolateColor(inputdata, max, min):
    return float( inputdata / (max - min)) * 255

def createHeatMapOfHousesPrice():
    heatLat = []
    heatLng = []

    highLat = []
    highLng = []

    kvadratPris = []

    kvadPris = {}

    kvadPris['0'] = {}
    kvadPris['0']['lat'] = []
    kvadPris['0']['lng'] = []
    kvadPris['1'] = {}
    kvadPris['1']['lat'] = []
    kvadPris['1']['lng'] = []
    kvadPris['2'] = {}
    kvadPris['2']['lat'] = []
    kvadPris['2']['lng'] = []
    kvadPris['3'] = {}
    kvadPris['3']['lat'] = []
    kvadPris['3']['lng'] = []

    minKP = 0
    maxKP = 0
    for house in houses:
        try:
            price = int(houses[house]['price'].replace(',-',''))
            kvadrat = int(houses[house]['kvadrat'])
            kvPris = float(price / kvadrat)
            kvadratPris.append(kvPris)

            if kvPris < minKP:
                minKP = kvPris

            if kvPris > maxKP:
                maxKP = kvPris
            klasse = int(kvPris / 20000)
            if klasse <= 3:
                kvadPris[str(klasse)]['lat'].append(float(houses[house]['lat']))
                kvadPris[str(klasse)]['lng'].append(float(houses[house]['lng']))
        except ValueError:
            print('error parsing')
    gmap = gmplot.GoogleMapPlotter(59.9019315,10.764459, 11.17)

    for klass in kvadPris:
        colorInput = interpolateColor(int(klass), 3, 0)
        print(colorInput)
        grd = [(colorInput, 255 - colorInput, 0, 0), (colorInput, 255 - colorInput, 0, 1)]
        gmap.heatmap(kvadPris[klass]['lat'],kvadPris[klass]['lng'], radius=50, gradient=grd)

    gmap.draw("finnHousesPrices.html")

def distancePriceGraph():
    x = []
    y = []
    relation = []
    test = {}
    counter = 0
    for house in houses:
        try:
            tmpx = (int(houses[house]['price'].replace(',-','')))
            tmpy = (int(houses[house]['traveltime'].replace(' mins', '')))
            y.append(tmpy)
            x.append(tmpx)
            relation.append(float(tmpx/tmpy))
            test[counter] = {}
            test[counter]['price'] = tmpx
            test[counter]['traveltime'] = tmpy
            counter += 1
        except ValueError:
            print('error parsing')


    od = collections.OrderedDict(sorted(test.items()))

    plt.plot(relation)
    plt.ylabel('Travel time')
    plt.xlabel('Price')
    plt.show()


def simpleHeatMap():
    heatLat = []
    heatLng = []
    for house in houses:
        heatLat.append(float(houses[house]['lat']))
        heatLng.append(float(houses[house]['lng']))
    gmap = gmplot.GoogleMapPlotter(59.9019315,10.764459, 11.17)
    gmap.heatmap(heatLat, heatLng, radius=10)
    gmap.draw("mymap.html")
getNewData()





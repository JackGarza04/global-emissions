from flask import Flask, request, Markup
from flask import render_template, flash, Markup

import os
import json

app = Flask(__name__)

@app.route("/")
def render_main():
    return render_template('index.html') # 'index.html'

@app.route("/p1")
def render_page1():
    if "startYear" in request.args:
        return render_template('page1.html', points = format_dict_as_graph(get_sector_data()), options = get_country_names()) # 'page1.html', points = format_dict_as_graph(get_sector_data())
    else:
        return render_template('page1.html', options = get_country_names())

def get_country_names():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    
    country_list = []
    options = ""
    for i in countries:
        country = i["Country"]
        if country not in country_list:
            country_list.append(country)
    country_list.sort()
    for c in country_list:
        options += Markup("<option value=\"" + c + "\">" + c + "</option>")
    return options
    
def get_sector_data():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    emissions_by_sector = {}
    targetCountry = request.args['targetCountry']
    startYear = float(request.args['startYear'])
    endYear = float(request.args['endYear'])
    power = 0.0
    buildings = 0.0
    transport = 0.0
    otherI = 0.0
    otherS = 0.0
    total = 0.0
    for country in countries:
        if country["Country"] == targetCountry and country["Year"] > startYear and country["Year"] < endYear:
            power += country["Emissions"]["Sector"]["Power Industry"]
            buildings += country["Emissions"]["Sector"]["Buildings"]
            transport += country["Emissions"]["Sector"]["Transport"]
            otherI += country["Emissions"]["Sector"]["Other Industry"]
            otherS += country["Emissions"]["Sector"]["Other sectors"]
        else: #ADD STATEMENT TO HANDLE START YEAR > END YEAR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            pass
    if (endYear-startYear) > 0 and endYear > startYear:
        power = power/(endYear-startYear) #End year minus start year to get averages
        buildings = buildings/(endYear-startYear)
        transport = transport/(endYear-startYear)
        otherI = otherI/(endYear-startYear)
        otherS = otherS/(endYear-startYear)
    elif (endYear-startYear) == 0 or endYear == startYear:
        power = power #If user inputs a range where the years are equal do not average
        buildings = buildings
        transport = transport
        otherI = otherI
        otherS = otherS
    else:
        power = power #Safety measure if the start year is greater then end year
        buildings = buildings
        transport = transport
        otherI = otherI
        otherS = otherS
        
    
    total = power + buildings + transport + otherI + otherS # Express the data in terms of percentage distribution between the 5 sectors
    power = 100 * round((power/total), 2) 
    buildings = 100 * round((buildings/total), 2)
    transport = 100 * round((transport/total), 2)
    otherI = 100 * round((otherI/total), 2)
    otherS = 100 * round((otherS/total), 2)
    
    emissions_by_sector.update({'Power Industry': power, 'Buildings': buildings, 'Transport': transport, 'Other Industry': otherI, 'Other sectors': otherS}) #appends all attributes to the dictionary
    return emissions_by_sector

    
def format_dict_as_graph(data):
    graph_points = ""
    for key in data:
        # { y: 20, name: "Medical Aid" }
        graph_points = graph_points + Markup('{ y: ' + str(data[key]) + ', name: "' + key + '" }, ')
    graph_points = graph_points[:-2]
    print(graph_points)
    return graph_points
    

if __name__ == '__main__':
    app.run(debug=False) # change to False when running in production
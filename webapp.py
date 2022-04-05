from flask import Flask, request, Markup
from flask import render_template, flash, Markup

import os
import json

app = Flask(__name__)

@app.route("/")
def render_main():
    return render_template('index.html')

@app.route("/p1")
def render_page1():
    if "startYear" in request.args:
        return render_template('page1.html', points = format_dict_as_graph(get_sector_data()), options = get_country_names(), splineData = format_dict_as_spline_graph(get_total_emissions_change()))
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
        if country["Country"] == targetCountry and country["Year"] >= startYear and country["Year"] <= endYear:
            power += country["Emissions"]["Sector"]["Power Industry"]
            buildings += country["Emissions"]["Sector"]["Buildings"]
            transport += country["Emissions"]["Sector"]["Transport"]
            otherI += country["Emissions"]["Sector"]["Other Industry"]
            otherS += country["Emissions"]["Sector"]["Other sectors"]
        elif country["Country"] == targetCountry and startYear > endYear: # Statement to handle if startYear > endYear (only count the start year's data)
            if country["Year"] == startYear:
                power += country["Emissions"]["Sector"]["Power Industry"]
                buildings += country["Emissions"]["Sector"]["Buildings"]
                transport += country["Emissions"]["Sector"]["Transport"]
                otherI += country["Emissions"]["Sector"]["Other Industry"]
                otherS += country["Emissions"]["Sector"]["Other sectors"]
            else:
                pass
        else:
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
    
def get_total_emissions_change():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    targetCountry = request.args['targetCountry']
    startYear = float(request.args['startYear'])
    endYear = float(request.args['endYear'])
    totalCarbonPerYear = 0.0
    targetYear = 0
    totalCarbon = 0.0
    emissionsPerYear = {}
    for country in countries:
        if country["Country"] == targetCountry and country["Year"] >= startYear and country["Year"] <= endYear and startYear != endYear:
            totalCarbonPerYear = (country["Emissions"]["Type"]["CO2"] + country["Emissions"]["Type"]["N2O"] + country["Emissions"]["Type"]["CH4"])
            targetYear = country["Year"]
            emissionsPerYear.update({targetYear: totalCarbonPerYear})
            totalCarbon = totalCarbon + totalCarbonPerYear
            totalCarbonPerYear = 0.0
            targetYear = 0
        elif country["Country"] == targetCountry and startYear > endYear:# if the user inputs a start year thats greater than the end year, then flip the start and end years to make the function valid
            newEndYear = startYear 
            newStartYear = endYear
            if country["Country"] == targetCountry and country["Year"] >= newStartYear and country["Year"] <= newEndYear and startYear != endYear:
                totalCarbonPerYear = (country["Emissions"]["Type"]["CO2"] + country["Emissions"]["Type"]["N2O"] + country["Emissions"]["Type"]["CH4"])
                targetYear = country["Year"]
                emissionsPerYear.update({targetYear: totalCarbonPerYear})
                totalCarbon = totalCarbon + totalCarbonPerYear
                totalCarbonPerYear = 0.0
                targetYear = 0
            else:
                pass
        elif country["Country"] == targetCountry and startYear == endYear: #If the user inputs a year range of 0, then add 5 to the end year to make the graph readable
            endYear = endYear + 5
            if country["Country"] == targetCountry and country["Year"] >= startYear and country["Year"] <= endYear:
                totalCarbonPerYear = (country["Emissions"]["Type"]["CO2"] + country["Emissions"]["Type"]["N2O"] + country["Emissions"]["Type"]["CH4"])
                targetYear = country["Year"]
                emissionsPerYear.update({targetYear: totalCarbonPerYear})
                totalCarbon = totalCarbon + totalCarbonPerYear
                totalCarbonPerYear = 0.0
                targetYear = 0
            else:
                pass
        else:
            pass
    return emissionsPerYear
    
def format_dict_as_spline_graph(data):
    graphPoints = ""
    for key in data:
        # {x: new Date(2012, 0), y: 2009000}, 
        graphPoints = graphPoints + Markup('{x: new Date(' + str(key) + ', 0), y: ' + str((data[key])) + '}, ')
    graphPoints = graphPoints[:-2]
    print(graphPoints)
    return graphPoints
    

if __name__ == '__main__':
    app.run(debug=False) # change to False when running in production
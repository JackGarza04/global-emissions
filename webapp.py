from flask import Flask, request, Markup
from flask import render_template, flash, Markup

import os
import json

app = Flask(__name__)

@app.route("/")
def render_main():
    return render_template('page1.html', points = format_dict_as_graph(get_sector_data())) # 'index.html'

@app.route("/p1")
def render_page1():
    return render_template('index.html') # 'page1.html', points = format_dict_as_graph(get_sector_data())
    
def get_sector_data():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    emissions_by_sector = {}
    power = 0.0
    buildings = 0.0
    transport = 0.0
    otherI = 0.0
    otherS = 0.0
    total = 0.0
    for country in countries:
        if country["Country"] == "Afghanistan" and country["Year"] >= 1990:
            power += country["Emissions"]["Sector"]["Power Industry"]
            buildings += country["Emissions"]["Sector"]["Buildings"]
            transport += country["Emissions"]["Sector"]["Transport"]
            otherI += country["Emissions"]["Sector"]["Other Industry"]
            otherS += country["Emissions"]["Sector"]["Other sectors"]
        else:
            pass
    power = power/(2012.0-1990.0) #end year minus start year to get averages AND limit each result to 2 decimal places (for readability)
    buildings = buildings/(2012.0-1990.0)
    transport = transport/(2012.0-1990.0)
    otherI = otherI/(2012.0-1990.0)
    otherS = otherS/(2012.0-1990.0)
    
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
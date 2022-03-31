from flask import Flask, request, Markup
from flask import render_template, flash, Markup

import os
import json

app = Flask(__name__)

@app.route("/")
def render_main():
    print(get_sector_data())
    return render_template('page1.html') # !!FLIP WHEN DONE WITH GRAPH TESTING!!

@app.route("/p1")
def render_page1():
    return render_template('index.html')
    
def get_sector_data():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    emissions_by_sector = {}
    power = 0.0
    buildings = 0.0
    transport = 0.0
    otherI = 0.0
    otherS = 0.0
    for country in countries:
        if country["Country"] == "Afghanistan" and country["year"] >= 1990:
            power += country["Power Industry"]
            buildings += country["Buildings"]
            transport += country["Transport"]
            otherI += country["Other Industry"]
            otherS += country["Other sectors"]
        else:
            pass
    power = power/(2012.0-1990.0) #end year minus start year to get averages
    buildings = buildings/(2012.0-1990.0)
    transport = transport/(2012.0-1990.0)
    otherI = otherI/(2012.0-1990.0)
    otherS = otherS/(2012.0-1990.0)
    
    emissions_by_sector.update({'Power Industry': power, 'Buildings': buildings, 'Transport': transport, 'Other Industry': otherI, 'Other sectors': otherS}) #appends all attributes to the dictionary
    return emissions_by_sector
    

if __name__ == '__main__':
    app.run(debug=False) # change to False when running in production
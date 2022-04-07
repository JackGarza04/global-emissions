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
        return render_template('page1.html', points = format_dict_as_graph(get_sector_data()), options = get_country_names(), splineData = format_dict_as_spline_graph(get_total_emissions_change()), average = get_total_emissions_average(get_total_emissions_change()), country = get_target_country(), yearRange = get_year_range())
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
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    power = 0.0
    buildings = 0.0
    transport = 0.0
    other_industry = 0.0
    other_sectors = 0.0
    total = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year:
            power += country["Emissions"]["Sector"]["Power Industry"]
            buildings += country["Emissions"]["Sector"]["Buildings"]
            transport += country["Emissions"]["Sector"]["Transport"]
            other_industry += country["Emissions"]["Sector"]["Other Industry"]
            other_sectors += country["Emissions"]["Sector"]["Other sectors"]
        elif country["Country"] == target_country and start_year > end_year: # Statement to handle if start_year > end_year (flip the two points and then calculate with the flipped values)
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and country["Year"] >= new_start_year and country["Year"] <= new_end_year:
                power += country["Emissions"]["Sector"]["Power Industry"]
                buildings += country["Emissions"]["Sector"]["Buildings"]
                transport += country["Emissions"]["Sector"]["Transport"]
                other_industry += country["Emissions"]["Sector"]["Other Industry"]
                other_sectors += country["Emissions"]["Sector"]["Other sectors"]
            else:
                pass
        else:
            pass

    if (end_year-start_year) > 0 and end_year > start_year:
        power = power/(end_year-start_year) #End year minus start year to get averages
        buildings = buildings/(end_year-start_year)
        transport = transport/(end_year-start_year)
        other_industry = other_industry/(end_year-start_year)
        other_sectors = other_sectors/(end_year-start_year)
    elif end_year < start_year:
        new_start_year = end_year #If the given start year is larger than the given end year, then flip the two values (since they are also flipped above)
        new_end_year = start_year
        power = power/(new_end_year-new_start_year) 
        buildings = buildings/(new_end_year-new_start_year)
        transport = transport/(new_end_year-new_start_year)
        other_industry = other_industry/(new_end_year-new_start_year)
        other_sectors = other_sectors/(new_end_year-new_start_year)
    elif (end_year-start_year) == 0 or end_year == start_year:
        power = power #If user inputs a range where the years are equal do not average
        buildings = buildings
        transport = transport
        other_industry = other_industry
        other_sectors = other_sectors
    else:
        pass        

    total = power + buildings + transport + other_industry + other_sectors # Express the data in terms of percentage distribution between the 5 sectors
    power = 100 * round((power/total), 2) 
    buildings = 100 * round((buildings/total), 2)
    transport = 100 * round((transport/total), 2)
    other_industry = 100 * round((other_industry/total), 2)
    other_sectors = 100 * round((other_sectors/total), 2)
    
    #Since the values are not present, the update function populates the empty dictionary with new key:value pairs
    emissions_by_sector.update({'Power Industry': power, 'Buildings': buildings, 'Transport': transport, 'Other Industry': other_industry, 'Other sectors': other_sectors}) #appends all attributes to the dictionary
    return emissions_by_sector

    
def format_dict_as_graph(data):
    graph_points = ""
    for key in data:
        # { y: 20, name: "Medical Aid" }
        graph_points = graph_points + Markup('{ y: ' + str(data[key]) + ', name: "' + key + '" }, ')
    graph_points = graph_points[:-2] #Remove the last comma and space
    return graph_points
    
def get_total_emissions_change():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_carbon_per_year = 0.0
    target_year = 0
    emissions_per_year = {}
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and start_year != end_year:
            total_carbon_per_year = (country["Emissions"]["Type"]["CO2"] + country["Emissions"]["Type"]["N2O"] + country["Emissions"]["Type"]["CH4"])
            target_year = country["Year"]
            emissions_per_year.update({target_year: total_carbon_per_year}) #Write in new key:value pairs for each iteration (year) within the json file that satisfies the range
            total_carbon_per_year = 0.0
            target_year = 0
        elif country["Country"] == target_country and start_year > end_year:# if the user inputs a start year thats greater than the end year, then flip the start and end years to make the function valid
            new_end_year = start_year 
            new_start_year = end_year
            if country["Country"] == target_country and country["Year"] >= new_start_year and country["Year"] <= new_end_year and start_year != end_year:
                total_carbon_per_year = (country["Emissions"]["Type"]["CO2"] + country["Emissions"]["Type"]["N2O"] + country["Emissions"]["Type"]["CH4"])
                target_year = country["Year"]
                emissions_per_year.update({target_year: total_carbon_per_year})
                total_carbon_per_year = 0.0
                target_year = 0
            else:
                pass
        elif country["Country"] == target_country and start_year == end_year: #If the user inputs a year range of 0, then add 4 to the end year & start year to make the graph readable
            end_year = end_year + 4
            start_year = start_year - 4
            if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year:
                total_carbon_per_year = (country["Emissions"]["Type"]["CO2"] + country["Emissions"]["Type"]["N2O"] + country["Emissions"]["Type"]["CH4"])
                target_year = country["Year"]
                emissions_per_year.update({target_year: total_carbon_per_year})
                total_carbon_per_year = 0.0
                target_year = 0
            else:
                pass
        else:
            pass
    return emissions_per_year
    
def get_year_range():
    start_year = str(request.args['startYear'])
    end_year = str(request.args['endYear'])
    response = ""
    if start_year > end_year:
        new_start_year = end_year
        new_end_year = start_year
        response = "(" + new_start_year + " - " + new_end_year + ")"
    elif start_year == end_year:
        response = "(" + start_year + ")"
    else:
        response = "(" + start_year + " - " + end_year + ")"
    return response
        
    
def get_target_country():
    target_country = request.args['targetCountry']
    return target_country
    
def get_total_emissions_average(data):
    average_emissions = 0 
    total_emissions = 0
    for year in data: #Helper function to display the average on the spline chart for the user's inputted data
        total_emissions = total_emissions + data[year]
    average_emissions = round((total_emissions / (len(data))), 2)
    return average_emissions
        
def format_dict_as_spline_graph(data):
    graph_points_spline = ""
    for key in data:
        # {x: new Date(2012, 0), y: 2009000}, 
        graph_points_spline = graph_points_spline + Markup('{x: new Date(' + str(key) + ', 0), y: ' + str((data[key])) + '}, ')
    graph_points_spline = graph_points_spline[:-2] #Remove the last comma and space
    return graph_points_spline
    

if __name__ == '__main__':
    app.run(debug=False) # change to False when running in production
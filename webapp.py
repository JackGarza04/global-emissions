from flask import Flask, request, Markup
from flask import render_template, flash, Markup

import os
import json
import statistics

app = Flask(__name__)

@app.route("/")
def render_main():
    return render_template('index.html')

@app.route("/p1")
def render_page1():
    if "startYear" in request.args:
        return render_template('page1.html', points = format_dict_as_graph(get_sector_data()), options = get_country_names(), splineData = format_dict_as_spline_graph(get_total_emissions_change()), average = get_total_emissions_average(get_total_emissions_change()), country = get_target_country(), yearRange = get_year_range(), averageCarbon = get_average_carbon(), averageNitrous = get_average_nitrous(), averageMethane = get_average_methane(), minCarbon = get_min_carbon(), maxCarbon = get_max_carbon(), minNitrous = get_min_nitrous(), maxNitrous = get_max_nitrous(), minMethane = get_min_methane(), maxMethane = get_max_methane(), carbonDeviation = get_standard_deviation_carbon(), nitrousDeviation = get_standard_deviation_nitrous(), methaneDeviation = get_standard_deviation_methane(), totalCarbon = get_total_for_CO2(), totalNitrous = get_total_for_N2O(), totalMethane = get_total_for_CH4(), percentOfWorld = get_percent_of_world(), startYearInput = save_start_year(), endYearInput = save_end_year())
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
        if "targetCountry" in request.args:
            targetCountry = request.args['targetCountry']
            if c == targetCountry: #When the user inputs, save the input and make the option selected for ease of use
                options += Markup("<option value=\"" + c + "\" selected>" + c + "</option>")
            else:
                options += Markup("<option value=\"" + c + "\">" + c + "</option>")
        else:
            options += Markup("<option value=\"" + c + "\">" + c + "</option>")
    return options
    
def save_start_year():
    start_year = int(request.args['startYear'])
    end_year = int(request.args['endYear'])
    start_value = ""
    if start_year >= 1970 and start_year < end_year:
        start_value = start_year
    elif start_year > end_year:
        new_start_year = end_year
        start_value = new_start_year
    else:
        start_vaule = start_year
        
    if start_value != 0:
        return start_value
    else:
        pass

def save_end_year():
    start_year = int(request.args['startYear'])
    end_year = int(request.args['endYear'])
    end_value = 0
    if end_year <= 2012 and start_year < end_year:
        end_value = end_year
    elif start_year > end_year:
        new_end_year = start_year
        end_value = new_end_year
    else:
        end_value = end_year
    
    if end_value != 0:
        return end_value
    else:
        pass
    
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
    
def get_percent_of_world():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_for_target = 0.0
    total_for_world = 0.0
    percent_of_world = 0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_for_target = total_for_target + (country["Emissions"]["Type"]["CO2"]) + (country["Emissions"]["Type"]["N2O"]) + (country["Emissions"]["Type"]["CH4"])
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_for_target = total_for_target + (country["Emissions"]["Type"]["CO2"]) + (country["Emissions"]["Type"]["N2O"]) + (country["Emissions"]["Type"]["CH4"])
            else:
                pass
        else:
            pass
    for country in countries:
        if country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_for_world = total_for_world + (country["Emissions"]["Type"]["CO2"]) + (country["Emissions"]["Type"]["N2O"]) + (country["Emissions"]["Type"]["CH4"])
        elif start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_for_world = total_for_world + (country["Emissions"]["Type"]["CO2"]) + (country["Emissions"]["Type"]["N2O"]) + (country["Emissions"]["Type"]["CH4"])
            else:
                pass
        else:
            pass
    percent_of_world = round(((total_for_target / total_for_world) * 100), 2)
    return percent_of_world
    
# def get_average(gas):
    # with open('emissions.json') as emissions_data:
        # countries = json.load(emissions_data)
    # target_country = request.args['targetCountry']
    # start_year = float(request.args['startYear'])
    # end_year = float(request.args['endYear'])
    # target_pollutant = gas
    # total_pollutant = 0.0
    # avg_pollutant = 0.0
    # for country in countries:
        # if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            # total_pollutant = total_pollutant + country["Emissions"]["Type"][target_pollutant]
        # elif country["Country"] == target_country and start_year > end_year:
            # new_start_year = end_year
            # new_end_year = start_year
            # if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                # total_pollutant = total_pollutant + country["Emissions"]["Type"][target_pollutant]
            # else:
                # pass
        # else:
            # pass
    # if start_year != end_year:
        # avg_pollutant = round((total_pollutant / abs(start_year - end_year)), 2)
    # else:
        # avg_pollutant = round((total_pollutant), 2)
    # avg_pollutant = "{:,}".format(avg_pollutant)
    # return avg_pollutant



def get_average_carbon():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_CO2 = 0.0
    avg_CO2 = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_CO2 = total_CO2 + country["Emissions"]["Type"]["CO2"]
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_CO2 = total_CO2 + country["Emissions"]["Type"]["CO2"]
            else:
                pass
        else:
            pass
    if start_year != end_year:
        avg_CO2 = round((total_CO2 / abs(start_year - end_year)), 2)
    else:
        avg_CO2 = round((total_CO2), 2)
    avg_CO2 = "{:,}".format(avg_CO2)
    return avg_CO2
    
def get_average_nitrous():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_N2O = 0.0
    avg_N2O = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_N2O = total_N2O + country["Emissions"]["Type"]["N2O"]
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_N2O = total_N2O + country["Emissions"]["Type"]["N2O"]
            else:
                pass
        else:
            pass
    if start_year != end_year:
        avg_N2O = round((total_N2O / abs(start_year - end_year)), 2)
    else:
        avg_N2O = round((total_N2O), 2)
    avg_N2O = "{:,}".format(avg_N2O)
    return avg_N2O

def get_average_methane():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_CH4 = 0.0
    avg_CH4 = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_CH4 = total_CH4 + country["Emissions"]["Type"]["CH4"]
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_CH4 = total_CH4 + country["Emissions"]["Type"]["CH4"]
            else:
                pass
        else:
            pass
    if start_year != end_year:
        avg_CH4 = round((total_CH4 / abs(start_year - end_year)), 2)
    else:
        avg_CH4 = round((total_CH4), 2)
    avg_CH4 = "{:,}".format(avg_CH4)
    return avg_CH4
    
def get_min_carbon():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    lowest_CO2 = 10000000.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            if country["Emissions"]["Type"]["CO2"] < lowest_CO2:
                lowest_CO2 = country["Emissions"]["Type"]["CO2"]
            else:
                pass
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                if country["Emissions"]["Type"]["CO2"] < lowest_CO2:
                    lowest_CO2 = country["Emissions"]["Type"]["CO2"]
                else:
                    pass
            else:
                pass
        else:
            pass
    lowest_CO2 = "{:,}".format(lowest_CO2)
    return lowest_CO2

def get_min_nitrous():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    lowest_N2O = 10000000.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            if country["Emissions"]["Type"]["N2O"] < lowest_N2O:
                lowest_N2O = country["Emissions"]["Type"]["N2O"]
            else:
                pass
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                if country["Emissions"]["Type"]["N2O"] < lowest_N2O:
                    lowest_N2O = country["Emissions"]["Type"]["N2O"]
                else:
                    pass
            else:
                pass
        else:
            pass
    lowest_N2O = "{:,}".format(lowest_N2O)
    return lowest_N2O
    
def get_min_methane():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    lowest_CH4 = 10000000.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            if country["Emissions"]["Type"]["CH4"] < lowest_CH4:
                lowest_CH4 = country["Emissions"]["Type"]["CH4"]
            else:
                pass
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                if country["Emissions"]["Type"]["CH4"] < lowest_CH4:
                    lowest_CH4 = country["Emissions"]["Type"]["CH4"]
                else:
                    pass
            else:
                pass
        else:
            pass
    lowest_CH4 = "{:,}".format(lowest_CH4)
    return lowest_CH4

def get_max_carbon():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    highest_CO2 = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            if country["Emissions"]["Type"]["CO2"] > highest_CO2:
                highest_CO2 = country["Emissions"]["Type"]["CO2"]
            else:
                pass
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                if country["Emissions"]["Type"]["CO2"] > highest_CO2:
                    highest_CO2 = country["Emissions"]["Type"]["CO2"]
                else:
                    pass
            else:
                pass
        else:
            pass
    highest_CO2 = "{:,}".format(highest_CO2)
    return highest_CO2

def get_max_nitrous():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    highest_N2O = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            if country["Emissions"]["Type"]["N2O"] > highest_N2O:
                highest_N2O = country["Emissions"]["Type"]["N2O"]
            else:
                pass
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                if country["Emissions"]["Type"]["N2O"] > highest_N2O:
                    highest_N2O = country["Emissions"]["Type"]["N2O"]
                else:
                    pass
            else:
                pass
        else:
            pass
    highest_N2O = "{:,}".format(highest_N2O)
    return highest_N2O
    
def get_max_methane():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    highest_CH4 = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            if country["Emissions"]["Type"]["CH4"] > highest_CH4:
                highest_CH4 = country["Emissions"]["Type"]["CH4"]
            else:
                pass
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                if country["Emissions"]["Type"]["CH4"] > highest_CH4:
                    highest_CH4 = country["Emissions"]["Type"]["CH4"]
                else:
                    pass
            else:
                pass
        else:
            pass
    highest_CH4 = "{:,}".format(highest_CH4)
    return highest_CH4
    
def get_standard_deviation_carbon():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    data = []
    carbon_deviation = 0.0
    for country in countries: 
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            data.append(country["Emissions"]["Type"]["CO2"])
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                data.append(country["Emissions"]["Type"]["CO2"])
            else:
                pass
        else:
            pass
    carbon_deviation = round((statistics.stdev(data)), 2)
    carbon_deviation = "{:,}".format(carbon_deviation)
    return carbon_deviation

def get_standard_deviation_nitrous():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    data = []
    nitrous_deviation = 0.0
    for country in countries: 
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            data.append(country["Emissions"]["Type"]["N2O"])
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                data.append(country["Emissions"]["Type"]["N2O"])
            else:
                pass
        else:
            pass
    nitrous_deviation = round((statistics.stdev(data)), 2)
    nitrous_deviation = "{:,}".format(nitrous_deviation)
    return nitrous_deviation

def get_standard_deviation_methane():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    data = []
    methane_deviation = 0.0
    for country in countries: 
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            data.append(country["Emissions"]["Type"]["CH4"])
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                data.append(country["Emissions"]["Type"]["CH4"])
            else:
                pass
        else:
            pass
    methane_deviation = round((statistics.stdev(data)), 2)
    methane_deviation = "{:,}".format(methane_deviation)
    return methane_deviation
    
def get_total_for_CO2():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_c = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_c = total_c + (country["Emissions"]["Type"]["CO2"])
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_c = total_c + (country["Emissions"]["Type"]["CO2"])
            else:
                pass
        else:
            pass
    total_c = round(total_c, 2)
    total_c = "{:,}".format(total_c)
    return total_c

def get_total_for_N2O():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_n = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_n = total_n + (country["Emissions"]["Type"]["N2O"])
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_n = total_n + (country["Emissions"]["Type"]["N2O"])
            else:
                pass
        else:
            pass
    total_n = round(total_n, 2)
    total_n = "{:,}".format(total_n)
    return total_n

def get_total_for_CH4():
    with open('emissions.json') as emissions_data:
        countries = json.load(emissions_data)
    target_country = request.args['targetCountry']
    start_year = float(request.args['startYear'])
    end_year = float(request.args['endYear'])
    total_m = 0.0
    for country in countries:
        if country["Country"] == target_country and country["Year"] >= start_year and country["Year"] <= end_year and not start_year > end_year:
            total_m = total_m + (country["Emissions"]["Type"]["CH4"])
        elif country["Country"] == target_country and start_year > end_year:
            new_start_year = end_year
            new_end_year = start_year
            if country["Country"] == target_country and new_start_year <= country["Year"] and new_end_year >= country["Year"]:
                total_m = total_m + (country["Emissions"]["Type"]["CH4"])
            else:
                pass
        else:
            pass
    total_m = round(total_m, 2)
    total_m = "{:,}".format(total_m)
    return total_m

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
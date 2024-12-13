# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to measurement and station tables.
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
# Initialize the Flask app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/") # Main route of the API
def welcome():
    return (
        f"Welcome to Hawaii API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/hawaii_precipitation<br/>"
        f"/api/v1.0/hawaii_stations<br/>"
        f"/api/v1.0/hawaii_tobs<br/>"
        f"/api/v1.0/hawaii_temp/start_date<br/>"
        f"/api/v1.0/hawaii_temp/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/hawaii_precipitation") # Route to get precipitation data
def hawaii_percipitation():
    # Create a new session to query the database
    session = Session(engine)

    # Defining the start and end dates for the query
    start_date = "2016-08-23"  
    end_date = "2017-08-23" 

    # Query the database to get precipitation data within the date range
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date, 
                                                     measurement.date <= end_date).all()

    session.close() # Close the session after querying

    # Convert the query results into a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data) # Return the data in JSON format

@app.route("/api/v1.0/hawaii_stations") # Route to get station information
def hawaii_stations():
    session = Session(engine) # Create a new session to query the database
   
    # Query the database to get station information
    results = session.query(station.station, station.name, 
                            station.latitude, station.longitude, 
                            station.elevation).all()
    session.close() # Close the session after querying

    # Convert the query results into a list of dictionaries
    stations = [
        {
            "station": s[0],
            "name": s[1],
            "latitude": s[2],
            "longitude": s[3],
            "elevation": s[4]
        }
        for s in results
    ]
    return jsonify(stations) # Return the data in JSON format

@app.route("/api/v1.0/hawaii_tobs") # Route to get temperature observations
def hawaii_tobs():
    session = Session(engine) # Create a new session to query the database
 
    station_id = "USC00519281" # Station ID for the station of interest
    start_date = "2016-08-23"  # End Date
    end_date = "2017-08-23"    # Start Date

    # Query the database to get temperature observations within the date range
    results = session.query(measurement.id, measurement.station, 
                            measurement.date, measurement.prcp, 
                            measurement.tobs).filter(measurement.station == station_id, 
                                                     measurement.date >= start_date, 
                                                     measurement.date <= end_date).all()

    session.close() # Close the session after querying

    # Convert the query results into a list of dictionaries
    tobs_data = [
        {
            "id": s[0],
            "station": s[1],
            "date": s[2],
            "prcp": s[3],
            "tobs": s[4]
        }
        for s in results
    ]
    return jsonify(tobs_data) # Return the data in JSON format

@app.route("/api/v1.0/hawaii_temp/<start_date>") # Route to get temperature stats after a specific start date
def hawaii_temperature(start_date):
    session = Session(engine) # Create a new session to query the database

    # Convert the start_date from string to datetime object
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    
    # Retrieve data to get max, min, and average temperatures from the start date
    temp_stats = session.query(
        func.max(measurement.tobs), # Highest Temperature
        func.min(measurement.tobs), # Lowest Temperature
        func.avg(measurement.tobs)  # Average Temperature
    ).filter(measurement.date >= start_date_obj).first() # Establishing the Start Date for URL

    session.close() # Close the session after querying

    # Extract the temperature statistics from the query result
    max_temp, min_temp, avg_temp = temp_stats

    # Return the data in JSON format
    return jsonify({
        "temperature_statistics": {
            "max_temperature": max_temp,
            "min_temperature": min_temp,
            "avg_temperature": avg_temp
        }
    })

# Route to get temperature stats for a date range
@app.route("/api/v1.0/hawaii_temp/<start_date>/<end_date>") 
def hawaii_temp(start_date, end_date):
    session = Session(engine) # Create a new session to query the database
    
    # Convert the start_date and end_date strings to datetime objects
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    
    # Retrieve data to get max, min, and average temperatures from the start and end dates
    temp_stats = session.query(
        func.max(measurement.tobs), 
        func.min(measurement.tobs), 
        func.avg(measurement.tobs)
    ).filter(measurement.date >= start_date_obj).first()

    session.close() # Close the session after querying


    # Extract the temperature statistics from the query result
    max_temp, min_temp, avg_temp = temp_stats

    # Return the data in JSON format
    return jsonify({
        "temperature_statistics": {
            "max_temperature": max_temp,
            "min_temperature": min_temp,
            "avg_temperature": avg_temp
        }
    })

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
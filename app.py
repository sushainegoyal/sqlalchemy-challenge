import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"<br>"
        f"Below you can query Temperature Min, Avg, and Max for your desired date or date range.<br>"
        f"Enter a start/end dates in the format %Y-%m-%d<br>"
        f"/api/v1.0/start/<start><br>"
        f"/api/v1.0/start<start>/end<end>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    """Return JSON representation of Date and Precipitation."""
    
    # Query precipitation
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the results data and append to a list of precip
    precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip.append(precip_dict)

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return JSON representation list of stations."""
    
    # Query stations
    
    session = Session(engine)
    stations = session.query(Station.station, Station.name).all()
    stations = list(np.ravel(stations))
    
    # Create a JSON list of stations

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    
    # Query stations
    
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = list(last_date)

    recent_year = []
    recent_mon = []
    recent_day = []
    for date in last_date:
        recent_year.append(date[:4])
        recent_mon.append(date[5:7])
        recent_day.append(date[8:10])

#     print(recent_year[0]) 
#     print(recent_mon[0]) 
#     print(recent_day[0]) 

    year_ago = dt.date(int(recent_year[0]), int(recent_mon[0]), int(recent_day[0])) - dt.timedelta(days=365)
#     print(year_ago)

    date_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= str(year_ago)).all()
#     print(date_tobs)
    
    
    # Create a JSON list of stations

    return jsonify(date_tobs)

@app.route("/api/v1.0/<start>")
def temps_start(start):
    
    session = Session(engine)
    
    
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    return jsonify(query)

@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    
    session = Session(engine)
    
    
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    return jsonify(query)

    

if __name__ == '__main__':
    app.run(debug=True)


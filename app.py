# import
from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



engine = create_engine("sqlite:///hawaii.sqlite")


Base = automap_base()

Base.prepare(engine, reflect=True)


measurement = Base.classes.measurement
station = Base.classes.station


# setup Flask
app = Flask(__name__)



@app.route("/")
def home():
    return(
        f"Welcome to the Climate App.<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date"
    )



@app.route("/api/v1.0/precipitation")
def precip(): 
    
    session = Session(engine)

    
    recent_date  = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    recent_date1 = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    one_year_ago = recent_date1 - dt.timedelta(days=365)
    query = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()
    
    
    final_results = []
    for date, precip in query:
        final_results.append({date: precip})

    session.close()
    return jsonify(final_results)


@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    
    results = session.query(station.station).all()

    session.close()

    
    final_results = list(np.ravel(results))

    return jsonify(final_results)


@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)

    
    recent_date  = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    recent_date1  = dt.datetime.strptime(recent_date , '%Y-%m-%d')
    one_year_ago = recent_date1 - dt.timedelta(days=365)

    active_stations  = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).\
        order_by(func.count(measurement.station).desc())
    most_active_id = active_stations[0][0]
    active_year = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_id).\
        filter(measurement.date > one_year_ago).all()
    
    
    results_dict = []
    for date, temp in active_year:
        tob_dict = {}
        tob_dict['date'] = date
        tob_dict['tobs'] = temp
        results_dict.append(tob_dict)

    session.close()

    return jsonify(results_dict)


@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    
    start_obs = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()

    
    results = [
        {'min': start_obs[0][0]},
        {'max': start_obs[0][1]},
        {'average': start_obs[0][2]}
    ]
    
    session.close()

    return jsonify(results)


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    
    session = Session(engine)

    
    
    start_end_obs = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

     
    
    results = [
        {'min': start_end_obs[0][0]},
        {'max': start_end_obs[0][1]},
        {'average': start_end_obs[0][2]}
    ]
   
    session.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
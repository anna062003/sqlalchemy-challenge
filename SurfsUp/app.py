# Import the dependencies.
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
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes. station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    sel = [Measurement.date, Measurement.prcp]
    recent_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(recent_data_point[0], '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    results = session.query(*sel).filter(Measurement.date >= one_year_ago).all()
    session.close()
    
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Find the most active station's ID
    station_id = session.query(Measurement.station).\
                 group_by(Measurement.station).\
                 order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year from the last date in the dataset
    recent_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(recent_data_point[0], '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == station_id).\
              filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Create a dictionary for each temperature observation
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {"date": date, "tobs": tobs}
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).all()
    session.close()
    
    temp_data = []
    for tmin, tmax, tavg in results:
        temp_dict = {"TMIN": tmin,
                    "TMAX": tmax,
                    "TAVG": tmax
                   }
        temp_data.append(temp_dict)
    return jsonify(temp_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()
    
    session.close()
    
    temp_range_data = []
    for tmin, tmax, tavg in results:
        temp_range_dict = {"TMIN": tmin,
                            "TMAX": tmax,
                            "TAVG": tmax
                   }
        temp_range_data.append(temp_range_dict)
    return jsonify(temp_range_data)
    
    
    
if __name__ == "__main__":
    app.run(debug=True)
    





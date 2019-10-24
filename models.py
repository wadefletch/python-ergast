# sqlalchemy implementation of ergast schema as defined at
# http://ergast.com/schemas/f1db_schema.txt

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class Circuit(Base):
    __tablename__ = 'circuits'

    id = Column(Integer, primary_key=True)
    circuitRef = Column(String(255))
    name = Column(String(255))
    location = Column(String(255), nullable=True, default=None)
    country = Column(String(255), nullable=True, default=None)
    lat = Column(Float, nullable=True, default=None)
    lng = Column(Float, nullable=True, default=None)
    alt = Column(Integer, nullable=True, default=None)
    url = Column(String(255), unique=True)


class ConstructorResult(Base):
    __tablename__ = 'constructor_results'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    race = relationship("Race")
    constructor_id = Column(Integer, ForeignKey('constructors.id'))
    constructor = relationship("Constructor")
    points = Column(Float, nullable=True, default=None)
    status = Column(String(255), nullable=True, default=None)


class ConstructorStanding(Base):
    __tablename__ = 'constructor_standings'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    race = relationship("Race")
    constructor_id = Column(Integer, ForeignKey('constructors.id'))
    constructor = relationship("Constructor")
    points = Column(Float, default=0)
    position = Column(Integer, nullable=True, default=None)
    positionText = Column(String(255), nullable=True, default=None)
    wins = Column(Integer, default=0)


class Constructor(Base):
    __tablename__ = 'constructors'

    id = Column(Integer, primary_key=True)
    constructorRef = Column(String(255))
    name = Column(String(255), unique=True)
    nationality = Column(String(255), nullable=True, default=None)
    url = Column(String(255))


class DriverStanding(Base):
    __tablename__ = 'driver_standings'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    race = relationship("Race")
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    driver = relationship("Driver")
    points = Column(Float, default=0)
    position = Column(Integer, nullable=True, default=None)
    positionText = Column(String(255), nullable=True, default=None)
    wins = Column(Integer, default=0)


class Driver(Base):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True)
    driverRef = Column(String(255))
    number = Column(Integer, default=None)
    code = Column(String(3), nullable=True, default=None)
    forename = Column(String(255))
    surname = Column(String(255))
    dob = Column(Date, nullable=True, default=None)
    nationality = Column(String(255), nullable=True, default=None)
    url = Column(String(255), unique=True)


class LapTime(Base):
    __tablename__ = 'lap_times'

    race_id = Column(Integer, ForeignKey('races.id'), primary_key=True)
    race = relationship("Race")
    driver_id = Column(Integer, ForeignKey('drivers.id'), primary_key=True)
    driver = relationship("Driver")
    lap = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=True, default=None)
    time = Column(String(255), nullable=True, default=None)
    milliseconds = Column(Integer, nullable=True, default=None)


class PitStop(Base):
    __tablename__ = 'pit_stops'

    race_id = Column(Integer, ForeignKey('races.id'), primary_key=True)
    race = relationship("Race")
    driver_id = Column(Integer, ForeignKey('drivers.id'), primary_key=True)
    driver = relationship("Driver")
    stop = Column(Integer, primary_key=True)
    lap = Column(Integer)
    time = Column(Time)
    duration = Column(String(255), nullable=True, default=None)
    milliseconds = Column(Integer, nullable=True, default=None)


class Qualifying(Base):
    __tablename__ = 'qualifying'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'), primary_key=True)
    race = relationship("Race")
    driver_id = Column(Integer, ForeignKey('drivers.id'), primary_key=True)
    driver = relationship("Driver")
    constructor_id = Column(Integer, ForeignKey('constructors.id'))
    constructor = relationship("Constructor")
    number = Column(Integer)
    position = Column(Integer, nullable=True, default=None)
    q1 = Column(String(255), nullable=True, default=True)
    q2 = Column(String(255), nullable=True, default=True)
    q3 = Column(String(255), nullable=True, default=True)

class Race(Base):
    __tablename__ = 'races'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, default=0)
    round = Column(Integer, default=0)
    name = Column(String(255))
    date = Column(Date, nullable=True, default=None)
    time = Column(Time, nullable=True, default=None)
    url = Column(String(255), nullable=True, unique=True, default=None)

    circuit_id = Column(Integer, ForeignKey('circuits.id'))
    circuit = relationship("Circuit")


class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    race = relationship("Race")
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    driver = relationship("Driver")
    constructor_id = Column(Integer, ForeignKey('constructors.id'))
    constructor = relationship("Constructor")
    number = Column(Integer, nullable=True, default=None)
    grid = Column(Integer, default=0)
    position = Column(Integer, nullable=True, default=None)
    position_text = Column(String(255))
    position_order = Column(Integer, default=0)
    points = Column(Float, default=0)
    laps = Column(Integer, default=0)
    time = Column(String(255), nullable=True, default=None)
    milliseconds = Column(Integer, nullable=True, default=None)
    fastest_lap = Column(Integer, nullable=True, default=None)
    rank = Column(Integer, nullable=True, default=0)
    fastest_lap_time = Column(String(255), nullable=True, default=None)
    fastest_lap_speed = Column(String(255), nullable=True, default=None)
    status_id = Column(Integer, ForeignKey('status.id'))
    status = relationship("Status")


class Season(Base):
    __tablename__ = 'seasons'

    year = Column(Integer, primary_key=True)
    url = Column(String(255), unique=True)



class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True)
    status = Column(String(255))

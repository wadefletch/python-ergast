import pandas as pd
import numpy as np
import os.path
from models import *

CSV_DIR = 'f1db_csv/'
REGISTERED_LOADERS = []

# I took inspiration from Django class-based views to implement DRY for each individual file associated schema

# TODO: Standardize order of assingment in each subclass
# TODO: Add a nice way to process dates and other things that require typecasting, but in the meantime:
# Filter out columns we don't know how to handle but don't need
FILTERED_COLUMNS = ['dob']

class ErgastCSVLoaderMixin():
    csv_file = None
    column_names = None
    model = None
    foreign_keys = None
    index = 0

    def __init_subclass__(cls, **kwargs):
        '''Adds the subclass to a global registry of loaders (REGISTERED_LOADERS) that can then be iterated over upon init.'''
        super().__init_subclass__(**kwargs)
        REGISTERED_LOADERS.append(cls)

    def _get_csv_path(self, filename):
        '''Returns a relative path to a csv file in the global CSV_DIR'''
        return os.path.abspath(os.path.join(os.path.dirname(__file__), CSV_DIR, filename))

    def get_df(self):
        '''Returns a pandas DataFrame with data from self.csv_file'''
        # Serialize the defined csv file to a pandas DataFrame
        df = pd.read_csv(self._get_csv_path(self.csv_file), header=None)

        # If column_names is assigned in the subclass, use those names in the DataFrame
        if self.column_names:
            df.columns = self.column_names

        # If index is assigned in the subclass, use it, otherwise keep first column
        if self.index:
            i = df[self.index]
            df = df.set_index(i)
            self.index = i.name
        
        # Replace the weird NaN replacement ergast uses with numpy NaN objects
        df.replace(to_replace=['\\N'], value=np.nan, inplace=True)

        self.df = df
        return df

    def populate_db(self, db):
        '''Populates df from a given reader into its associated model.'''  # TODO: rewrite this docstring
        df = self.get_df()
        df_dict = self.df.to_dict(orient='records')
        for entry in df_dict:
            # make a copy bc we need to reference later
            just_the_basic_entry_items = dict(entry)

            for name in FILTERED_COLUMNS:
                just_the_basic_entry_items.pop(name, None)

            # Remove the index column from object if it exists
            if self.index:
                just_the_basic_entry_items.pop(self.index)

            # Remove foreign keys, because we need to query them before adding
            if self.foreign_keys:
                for key in self.foreign_keys.keys():
                    just_the_basic_entry_items.pop(key)

            # create a model prototype with just the "vanilla" (mostly str) columns
            m = self.model(**just_the_basic_entry_items)

            # find foreign key references and create relationships
            if self.foreign_keys:
                for attr, model in self.foreign_keys.items():
                    i = db.query(model).get(entry[attr])
                    setattr(m, attr, i)

            # add to the db
            # TODO: Maybe optimize this to hold entries in memory to add all at once and minimize database writes
            db.add(m)
        db.commit()
        print('Populated:', self.__class__.__name__)

class CircuitsLoader(ErgastCSVLoaderMixin):
    csv_file = 'circuits.csv'
    column_names = ['circuitId', 'circuitRef', 'name', 'location', 'country', 'lat', 'lng', 'alt', 'url']
    index = 'circuitId'
    model = Circuit


class ConstructorResultsLoader(ErgastCSVLoaderMixin):
    csv_file = 'constructor_results.csv'
    column_names = ['constructorResultsId', 'raceId', 'constructorId', 'points', 'status']
    model = ConstructorResult
    foreign_keys = {'raceId': Race, 'constructorId': Constructor}
    index = 'constructorResultsId'


class ConstructorStandingsLoader(ErgastCSVLoaderMixin):
    csv_file = 'constructor_standings.csv'
    column_names = ['constructorStandingsId', 'raceId', 'constructorId', 'points', 'position', 'positionText', 'wins']
    model = ConstructorStanding
    foreign_keys = {'raceId': Race, 'constructorId': Constructor}
    index = 'constructorStandingsId'


class ConstructorsLoader(ErgastCSVLoaderMixin):
    csv_file = 'constructors.csv'
    column_names = ['constructorId', 'constructorRef', 'name', 'nationality', 'url']
    model = Constructor
    index = 'constructorId'


class DriverStandingsLoader(ErgastCSVLoaderMixin):
    csv_file = 'driver_standings.csv'
    column_names = ['driverStandingsId', 'raceId', 'driverId', 'points', 'position', 'positionText', 'wins']
    model = DriverStanding
    foreign_keys = {'raceId': Race, 'driverId': Driver}
    index = 'driverStandingsId'


class DriversLoader(ErgastCSVLoaderMixin):
    csv_file = 'driver.csv'
    column_names = ['driverId', 'driverRef', 'number', 'code', 'forename', 'surname', 'dob', 'nationality', 'url']
    model = Driver
    index = 'driverId'


class LapTimesLoader(ErgastCSVLoaderMixin):
    # TODO: raceId not null constraint failing, probably need to ensure this is below races
    csv_file = 'lap_times.csv'
    column_names = ['raceId', 'driverId', 'lap', 'position', 'time', 'milliseconds']
    model = LapTime
    foreign_keys = {'raceId': Race, 'driverId': Driver}
    index = None


class PitStopsLoader(ErgastCSVLoaderMixin):
    csv_file = 'pit_stops.csv'
    column_names = ['raceId', 'driverId', 'stop', 'lap', 'time', 'duration', 'milliseconds']
    model = PitStop
    foreign_keys = {'raceId': Race, 'driverId': Driver}
    index = None


class QualifyingLoader(ErgastCSVLoaderMixin):
    csv_file = 'qualifying.csv'
    column_names = ['qualifyId', 'raceId', 'driverId', 'consructorId', 'number', 'position', 'q1', 'q2', 'q3']
    foreign_keys = {'raceId': Race, 'driverId': Driver, 'constructorId': Constructor}
    model = Qualifying
    index = 'qualifyId'


class RacesLoader(ErgastCSVLoaderMixin):
    csv_file = 'races.csv'
    column_names = ['raceId', 'year', 'round', 'circuitId', 'name', 'date', 'time', 'url']
    foreign_keys = {'circuitId': Circuit}
    index = 'raceId'


class ResultsLoader(ErgastCSVLoaderMixin):
    csv_file = 'results.csv'
    column_names = ['resultId', 'raceId', 'driverId', 'constructorId', 'number', 'grid', 'position', 'positionText', 'positionOrder', 'points', 'laps', 'time', 'milliseconds', 'fastestLap', 'rank', 'fastestLapTime', 'fastestLapSpeed', 'statusId']
    model = Result
    foreign_keys = {'raceId': Race, 'driverId': Driver, 'constructorId': Constructor, 'statusId': Status}
    index = 'resultId'


class SeasonsLoader(ErgastCSVLoaderMixin):
    csv_file = 'seasons.csv'
    column_names = ['year', 'url']
    model = Season
    index = None


class StatusLoader(ErgastCSVLoaderMixin):
    csv_file = 'status.csv'
    column_names = ['statusId', 'status']
    index = 'statusId'
    model = Status


if __name__ in '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    db_file = 'sqlite://'

    engine = create_engine(db_file)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    # TODO: This isn't working in order, which it needs to to build foreign keys. Explore strategies to build this from foreign_keys attribute.
    for l in REGISTERED_LOADERS:
        li = l()
        li.populate_db(session)

    print(session.query(Circuit).all())
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Circuit


db_file = 'sqlite://'

engine = create_engine(db_file)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
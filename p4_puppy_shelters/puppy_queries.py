import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Query all of the puppies and return the results in asc alphabetical order
def names_alpha():
    for instance in session.query(Puppy).order_by(Puppy.name):
        print(instance.name)


# Query all puppies that are > 6 months old organized by the youngest first
def less_than_six():
    today = datetime.date.today()
    age = datetime.timedelta(weeks=20)
    six_months = today - age
    for instance in session.query(Puppy).filter(
                            Puppy.dateOfBirth > six_months):
        print instance.name, instance.dateOfBirth


# Query all puppies by ascending weight
def puppies_by_weight():
    for instance in session.query(Puppy).order_by(Puppy.weight):
        print instance.name, instance.weight


# Query all puppies grouped by the shelter in which they are staying
def puppies_by_shelter():
    for shelter, puppy in session.query(Shelter, Puppy).all():
        print shelter.name, puppy.name


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Index, String, DateTime, Integer, Float, \
    PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB

import datetime

from generators import MovRGenerator

#@todo: add interleaving
#@todo: restore FKs and "relationship' functionality after this is fixed: https://github.com/cockroachdb/cockroach/issues/36859

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID, default=MovRGenerator.generate_uuid)
    city = Column(String)
    name = Column(String)
    address = Column(String)
    credit_card = Column(String)
    PrimaryKeyConstraint(city, id)
    #promo_codes = relationship("UserPromoCode")

    def __repr__(self):
        return "<User(city='%s', id='%s', name='%s')>" % (self.city, self.id, self.name)

#@todo: sqlalchemy fails silently if compound fks are in the wrong order.
class Ride(Base):
    __tablename__ = 'rides'
    id = Column(UUID, default=MovRGenerator.generate_uuid)
    city = Column(String)
    vehicle_city = Column(String, CheckConstraint('vehicle_city=city')) #@todo: annoying workaround for https://github.com/cockroachdb/cockroach/issues/23580
    rider_id = Column(UUID)
    vehicle_id = Column(UUID)
    start_address = Column(String)
    end_address = Column(String)
    start_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime)
    revenue = Column(DECIMAL(10,2))
    PrimaryKeyConstraint(city, id)
    __table_args__ = (ForeignKeyConstraint([city, rider_id], ["users.city", "users.id"]),) #this requires an index or it fails silently:  https://github.com/cockroachdb/cockroach/issues/22253
    __table_args__ = (ForeignKeyConstraint([vehicle_city, vehicle_id], ["vehicles.city", "vehicles.id"]),)


    def __repr__(self):
        return "<Ride(city='%s', id='%s', rider_id='%s', vehicle_id='%s')>" % (self.city, self.id, self.rider_id, self.vehicle_id)

class VehicleLocationHistory(Base):
    __tablename__ = 'vehicle_location_histories'
    city = Column(String)
    ride_id = Column(UUID)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    lat = Column(Float)
    long = Column(Float)
    PrimaryKeyConstraint(city, ride_id, timestamp)
    #__table_args__ = (ForeignKeyConstraint([city, ride_id], ["rides.city", "rides.id"]),) #@todo: cut until FK performance improves in 19.2

    def __repr__(self):
        return "<VehicleLocationHistory(city='%s', ride_id='%s', timestamp='%s', lat='%s', long='%s')>" % \
               (self.city, self.ride_id, self.timestamp, self.lat, self.long)

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(UUID, default=MovRGenerator.generate_uuid)
    city = Column(String)
    type = Column(String)
    owner_id = Column(UUID)
    creation_time = Column(DateTime, default=datetime.datetime.now)
    status = Column(String)
    current_location = Column(String)
    ext = Column(JSONB)
    PrimaryKeyConstraint(city, id)
    __table_args__ = (ForeignKeyConstraint([city, owner_id], ["users.city", "users.id"]),)
    
    def __repr__(self):
        return "<Vehicle(city='%s', id='%s', type='%s', status='%s', ext='%s')>" % (self.city, self.id, self.type, self.status, self.ext)

class PromoCode(Base):
    __tablename__ = 'promo_codes'
    code = Column(String)
    description = Column(String)
    creation_time = Column(DateTime, default=datetime.datetime.now)
    expiration_time = Column(DateTime)
    rules = Column(JSONB)

    PrimaryKeyConstraint(code)
    def __repr__(self):
        return "<PromoCode(code='%s', description='%s', creation_time='%s', expiration_time='%s', rules='%s')>" % \
               (self.code, self.description, self.creation_time, self.expiration_time, self.rules)


class UserPromoCode(Base):
    __tablename__ = 'user_promo_codes'
    city = Column(String)
    user_id = Column(UUID)
    code = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    usage_count = Column(Integer, default=0)
    #promo_code = relationship("PromoCode")

    PrimaryKeyConstraint(city, user_id, code)

    __table_args__ = (ForeignKeyConstraint([city, user_id], ["users.city",
                                                              "users.id"]),)
    #__table_args__ = (ForeignKeyConstraint([code], ["promo_codes.code"]),)

    def __repr__(self):
        return "<UserPromoCode(city='%s', user_id='%s', code='%s', timestamp='%s')>" % \
               (self.user_city, self.user_id, self.code, self.timestamp)

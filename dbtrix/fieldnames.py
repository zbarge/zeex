# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:09:50 2016

@author: Zeke
"""
import os
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, DateTime, create_engine)
from sqlalchemy.orm import sessionmaker
from config import config


Base = declarative_base()
db_path = "sqlite:///" + os.path.join(config['DATA_DIR'], "fieldnames.db")
engine = create_engine(db_path)
Session = sessionmaker(bind=engine)

class Field(Base):
     """Access for orig_name & new_name"""
     __tablename__ = 'users'
    
     id = Column(Integer, primary_key=True)
     
     orig_name = Column(String(45), unique=True)
     new_name = Column(String(45))
     insertdate = Column(DateTime, default=datetime.datetime.now())
     updatedate = Column(DateTime, default=datetime.datetime.now())
     source = Column(String(30))
        
     def __repr__(self):
        return "<Field(orig_name='%s', new_name='%s', source='%s')>" % (
                             self.orig_name, self.new_name, self.source)
        
class FieldNames:
    def __init__(self):
        self.base = Base
        self.engine = engine
        self.base.metadata.create_all(self.engine)
        self.session = Session()
        self.Field = Field
        
    def add_entry(self, name, newname, source=None):
        field = Field(orig_name=name, new_name=newname, source=source)
        self.session.add(field)
        self.session.commit()
        return field
        
    def add_entries(self, names: dict, source=None):
        for oname, nname in names.items():
            self.session.add(Field(orig_name=oname, new_name=nname, source=source))
        self.session.commit()
        
    def get_renames(self, names: list):
        renames = {}
        for n in names:
            try:
                field = self.session.query(Field).filter(Field.orig_name.ilike("{}".format(n))).one()
                renames[n] = field.new_name
            except Exception as e:
                print("Ignored exception getting rename for {}: {}".format(n, e))
                renames[n] = n
        renames = {key: (value if value is not None else key) for key, value in renames.items()}
        return renames
        
    def delete_entry(self, orig_name: str):
        entry = self.session.query(Field).filter(Field.orig_name == orig_name).one()
        if entry:
            self.session.delete(entry)
            self.session.commit()
            
    def delete_entries(self, orig_names: list):
        entries = self.session.query(Field).filter(Field.orig_name.in_(orig_names)).all()
        for entry in entries:
            self.session.delete(entry)
        if entries:
            self.session.commit()
        
        
def test_fieldnames():
    renames = {"first name-dv":"first_name",
               "last name-dv":"last_name"}
    
    fns = FieldNames()
    
    fns.delete_entries(renames.keys())
    
    try:
        fns.add_entries(renames)
    except Exception as e:
        print("ignored exception : {}".format(e))
        fns.session.rollback()
    
    
    gots = fns.get_renames(renames.keys())
    
    for key, value in gots.items():
        print("{}:{}".format(key, value))
        assert renames[key] == value
    
    
    fns.delete_entries(renames.keys())
    print("tests passed")

                
if __name__ == "__main__":
    test_fieldnames()                
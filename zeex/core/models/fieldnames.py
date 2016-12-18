# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:09:50 2016
MIT License

Copyright (c) 2016 Zeke Barge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import datetime
from PySide import QtGui
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, DateTime, create_engine)
from sqlalchemy.orm import sessionmaker
from core.models.config import config


Base = declarative_base()
db_path = "sqlite:///" + os.path.join(config['DATA_DIR'], "fieldnames.db")
engine = create_engine(db_path)
Session = sessionmaker(bind=engine)


class Field(Base):
     """Storage for orig_name & new_name"""
     __tablename__ = 'users'
    
     id = Column(Integer, primary_key=True)
     
     orig_name = Column(String(45), unique=True)
     new_name = Column(String(45))
     dtype = Column(String(45))
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
        
    def add_entries(self, names: dict, source=None) -> list:
        entries = []
        for oname, nname in names.items():
            field = Field(orig_name=oname, new_name=nname, source=source)
            self.session.add(field)
            entries.append(field)
        self.session.commit()
        return entries
        
    def get_renames(self, names: list, fill_missing=False) -> dict:
        """
        Returns all names in the list
        as a dictionary like:
        {name:new_name}
        the value is None if no match is found.
        """
        renames = {}
        
        for n in names:
            try:
                field = self.session.query(Field).filter(
                        Field.orig_name.ilike("{}".format(n))
                        ).one()
                renames[n] = field.new_name
            except:
                renames[n] = (field if fill_missing is True else None)
                   
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


class FieldRenameModel(QtGui.QStandardItemModel):
    def __init__(self, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        self.setHorizontalHeaderLabels(['original_name', 'new_name'])
        self.db = FieldNames()

    def set_renames(self, columns: list, fill_missing=True, include_found=False, clear_current=True):
        if clear_current:
            self.clear()

        renames = self.db.get_renames(columns, fill_missing=False)

        if include_found is False:
            renames = {key: value for key, value in renames.items() if value is None}

        if fill_missing is True:
            renames = {key: (value if value is not None else key) for key, value in renames.items()}

        idx = 0
        for orig_name, new_name in renames.items():
            oitem = QtGui.QStandardItem(orig_name)
            nitem = QtGui.QStandardItem(new_name)
            self.setItem(idx, 0, oitem)
            self.setItem(idx, 1, nitem)
            idx += 1

    def set_case(self, method):
        for idx in range(self.rowCount()):
            item = self.item(idx, 1)
            item.setText(method(item.text()))

    def set_lower(self):
        self.set_case(str.lower)

    def set_upper(self):
        self.set_case(str.upper)

    def set_proper(self):
        self.set_case(str.title)

    def clear(self):
        super(FieldRenameModel, self).clear()
        self.setHorizontalHeaderLabels(['original_name', 'new_name'])

    def get_renames_dict(self):
        renames = {}
        for i in range(self.rowCount()):
            renames[self.item(i, 0).text()] =  self.item(i, 1).text()
        return renames


class FieldModel(QtGui.QStandardItemModel):
    def __init__(self):
        QtGui.QStandardItemModel.__init__(self)
        self.db = FieldNames()
        self.setHorizontalHeaderLabels(['orig_name', 'new_name', 'dtype'])
        self._original_info = {}

    def sync_database(self):
        pass

    def reset_to_original(self):
        self.clear()
        self.setHorizontalHeaderLabels(['orig_name', 'new_name', 'dtype'])
        for f, d in self._original_info.items():
            self.set_field(f, d[0], d[1])

    def request_fields(self, fields: list):
        pass

    def set_field(self, field_name, new_name=None, dtype=None):
        """
        Use this method to add fields to the model.
        Stores the original data allowing the reset_to_original to work.

        :param field_name: the name of the column in the data
        :param new_name: the new name of the column
        :param dtype: the data type of the column
        :return: None
        """
        match = self.findItems(field_name)
        if match:
            ct = match[0].row()
            # Pass along existing values instead of nulls
            # But don't override the new set.
            new_name = (self.item(ct, 1).text() if new_name is None else new_name)
            dtype = (self.item(ct, 2).text() if dtype is None else dtype)
        else:
            ct = self.rowCount()
            new_name = (field_name if new_name is None else new_name)
            dtype = ('object' if dtype is None else dtype)

        self.setItem(ct, 0, self._handle_field_name(field_name))
        self.setItem(ct, 1, self._handle_new_name(new_name))
        self.setItem(ct, 2, self._handle_dtype(dtype))
        self._store_original(field_name, new_name, dtype)

    def apply_new_name(self, method):
        """
        Applies the method across all rows
        of the new_name column in the model.
        :param method: str.lower, str.upper, str.title
        :return: None
        """
        for idx in range(self.rowCount()):
            item = self.item(idx, 1)
            item.setText(method(item.text()))

    def _handle_dtype(self, dtype):
        return QtGui.QStandardItem(str(dtype))

    def _handle_field_name(self, name):
        return QtGui.QStandardItem(name)

    def _handle_new_name(self, name):
        return QtGui.QStandardItem(name)

    def _get_duplicate_indexes(self):
        return []

    def _store_original(self, field_name, new_name=None, dtype=None):
        self._original_info[field_name] = [new_name, dtype]


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
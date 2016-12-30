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


from core.ctrls.sql import AlchemyConnection, AlchemyConnectionManager
from tests.main import MainTestClass
from core.compat import QtGui


class TestAlchemyConnection(MainTestClass):
    def test_general_configuration(self):
        from core.models.fieldnames import connection_info as ci
        a = AlchemyConnection('field_names', **ci)
        a.configure(reset=False)
        assert a.inspector is not None
        assert a.engine is not None
        assert a.meta is not None
        assert a.Session is not None
        assert 'fields' in a.get_table_names()
        assert 'id' in a.get_column_names('fields')
        print(a.engine.url)
        print(a.engine.driver)
        print(a.engine.name)
        assert isinstance(a.get_standard_item(), QtGui.QStandardItem)


class TestAlchemyConnectionManager(MainTestClass):
    def test_general_configuration(self):
        from core.models.fieldnames import connection_info as ci
        name = 'field_names'
        a = AlchemyConnectionManager()
        assert not a._connections
        a.add_connection(name, **ci)
        assert a.connection(name) is not None
        assert isinstance(a.get_standard_item_model(), QtGui.QStandardItemModel)
        assert a._connections
        con = a.remove_connection(name)
        assert isinstance(con, AlchemyConnection)
        assert not a._connections

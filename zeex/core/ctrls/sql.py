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
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from core.compat import QtGui
from core.utility.widgets import create_standard_item
from core.models.dataframe import DataFrameModel

class AlchemyConnection(object):
    """
    A container for a SQLAlchemy connection.
    Makes available the core compontents from
    SQLAlchemy in an easy way all grouped in with the connection.
    Dialogs & Windows should use this connection to conveniently
    gather the information they need.
    """
    def __init__(self, name, *args, **kwargs):
        """
        Provide a name for the connection and optional
        args/kwargs for creating the engine/connection.

        :param name: (str) The label associated with the connection.
        :param args: AlchemyConnection.configure(*args)
        :param kwargs:

            The following pre-configured objects can be passed
            and will not be overwritted unless you call configure
            with reset=False. If any of these objects are not passed, they
            will be generated if the **engine is passed.

                :param Session: (sqlalchemy.orm.session.sessionmaker)
                    For creating sessions from the class.
                :param engine: (sqlalchemy.engine.base.Engine)
                    For managing the core connection.
                :param inspector: (sqlalchemy.engine.reflection.Inspector)
                    For reflecting database properties.
                :param meta: (sqlalchemy.MetaData)
                    For reflecting database properties.

            :param (sqlalchemy.create_engine(**kwargs))
                Can be passed to the constructor if no engine.
        """
        self.name = name
        self.args = None
        self.kwargs = None
        self._engine = kwargs.pop('engine', None)
        self._Session = kwargs.pop('Session', None)
        self._meta = kwargs.pop('meta', None)
        self._inspector = kwargs.pop('inspector', None)
        if args or kwargs or self._engine is not None:
            # Force reset to false if
            # we're setting the connection on __init__.
            kwargs.pop('reset', None)
            self.configure(*args, reset=False, **kwargs)

    def configure(self, *args, reset=True, **kwargs):
        """
        Configures the connection based on the current engine
        or on the engine created from the details in *args/**kwargs

        :param args: (sqlalchemy.create_engine(*args))
            Optional when reset is False and an engine is already set
        :param reset: (bool, default True)
            True resets the entire connection creating a new engine
            and all associated objects (Session, meta, inspector, etc)
            False will set the associated objects using the engine as
            long as the engine is valid and the associated objects are None.

            It is recommended to create new AlchemyConnections rather than
            using old ones to eliminate confusion.
        :param kwargs: (sqlalchemy.create_engine(**kwargs))
            Optional when reset is False and the engine is already set.
        :return: None
        """
        if reset:
            self._engine = create_engine(*args, **kwargs)
            self.args = args
            self.kwargs = kwargs
            self._meta = MetaData(bind=self.engine)
            self._meta.reflect()
            self._inspector = inspect(self.engine)
            self._Session = sessionmaker(bind=self.engine)

        else:
            if self._engine is None:
                self._engine = create_engine(*args, **kwargs)
                self.args = args
                self.kwargs = kwargs

            if self._meta is None:
                self._meta = MetaData(bind=self.engine)

            if not self.get_table_names():
                self._meta.reflect()

            if self._inspector is None:
                self._inspector = inspect(self.engine)

            if self._Session is None:
                self._Session = sessionmaker(bind=self.engine)

    @property
    def Session(self) -> sqlalchemy.orm.session.sessionmaker:
        """
        The sessionmaker factory for the connection.
        :return: (sqlalchemy.orm.session.sessionmaker)
        """
        return self._Session

    @property
    def engine(self) -> sqlalchemy.engine.base.Engine:
        """
        The Engine class for the
        sqlalchemy connection.
        :return: (sqlalchemy.engine.base.Engine)
        """
        return self._engine

    @property
    def inspector(self) -> sqlalchemy.engine.reflection.Inspector:
        """
        The inspector object for the sqlalchemy connection.
        :return: (sqlalchemy.engine.reflection.Inspector)
        """
        return self._inspector

    @property
    def meta(self) -> sqlalchemy.MetaData:
        """
        The MetaData for the connection that has already been reflected.
        :return: (sqlalchemy.MetaData)
        """
        return self._meta

    def get_column_names(self, table):
        """
        Returns a list of column names for the given table.
        :param table: (str)
            A table that exists in the database.
        :return: (list)
            Of column names.
        """
        return [c['name'] for c in self.inspector.get_columns(table)]

    def get_table_names(self):
        """
        Returns a list of table names for the connection.
        :return: (list)
            Of table names.
        """
        return list(self.meta.tables.keys())

    def get_standard_item(self) -> QtGui.QStandardItem:
        """
        Creates a QStandardItem for the connection
        with the following information:
        - Database Name (parent)
            - Table1 (child1)
                - Column1 (child1.child1)
                - Column2... (child1.child2)
            - Table2 (child2)
                - Column1 (child2.child1)
                - Column2... (child2.child2)
            - etc...
        :return: (QtGui.QStandardItem)
        """
        # Create top database item.
        name_item = create_standard_item(self.name, editable=False, checkable=False)
        for row, table in enumerate(self.meta.tables.keys()):
            # Get a dict of all columns in the table.
            columns = self.inspector.get_columns(table)
            table = create_standard_item(table, editable=False, checkable=False)

            # Add all columns to the table's item.
            cnames = [c['name'] for c in columns]
            for crow, c in enumerate(cnames):
                c = create_standard_item(c)
                table.setChild(crow, c)

            # Add the table to the database's item
            name_item.setChild(row, table)
        return name_item

    def read_sql(self, sql, **kwargs) -> pd.DataFrame:
        """
        Returns a Pandas DataFrame based on given SQL-SELECT query
        and kwargs.
        :param sql: (str)
        :param kwargs: (pd.read_sql(**kwargs))
        :return: (pd.DataFrame)
        """
        return pd.read_sql(sql, self.engine.connect(), **kwargs)

    def get_df_model(self, df, **kwargs) -> DataFrameModel:
        """
        Accessor for creating a DataFrameModel.
        :param df:
        :param kwargs:
        :return: (DataFrameModel)
        """
        kwargs['dataFrame'] = df
        return DataFrameModel(**kwargs)

    def read_sql_df_model(self, sql, filePath=None, **kwargs) -> DataFrameModel:
        """
        Returns a DataFrameModel based on given SQL-SELECT query
        and kwargs.
        :param sql: (str)
        :param filePath: (str, default None)
        :param kwargs: (pd.read_sql(**kwargs))
        :return: (DataFrameModel)
        """
        df = self.read_sql(sql, **kwargs)
        return self.get_df_model(df, copyDataFrame=False, filePath=filePath)

    def execute_sql(self, sql, **kwargs) -> DataFrameModel:
        """
        Executes SQL returning a DataFrameModel based on the given
        SQL query.
        The following statement types are defined:
            - ALTER
            - CREATE
            - DELETE
            - SELECT
            - UPDATE
        :param sql:
        :param kwargs: (pd.read_sql(**kwargs) or
                        sqlalchemy.engine.base.Engine.execute(**kwargs))
        :return: (DataFrameModel)
        """
        direction = sql[:10].lower()
        if 'select' in direction:
            dfm = self.read_sql_df_model(sql, **kwargs)
        else:
            bit = dict(params=kwargs.pop('params', None),
                       multiparams=kwargs.pop('multiparams', None))
            res = self.engine.execute(sql, **bit)
            if 'delete' in direction or 'update' in direction:
                note = "SQLite RowCount (& others) may be inaccurate."
                dfm = self.get_df_model(pd.DataFrame([[res.rowcount, sql, note]],
                                                    columns=['Row Count', 'Statement', 'Note'],
                                                    index=[0]),
                                       filePath=kwargs.get('filePath'))

            elif 'create' in direction or 'alter' in direction:
                dfm = self.get_dfm_model(pd.DataFrame([[sql, 'OK']], index=[0],
                                                      columns=['Statement', 'Status']),
                                         filePath=kwargs.get('filePath') )
            else:
                raise NotImplementedError("Not sure how to handle statement: {}".format(sql))
        return dfm


class DuplicateConnectionError(Exception):
    pass


class AlchemyConnectionManager(object):
    """
    A global container for AlchemyConnection objects.
    QMainWindows & dialogs, if interacting with SQL, should
    store a reference to this container and use it to store
    and retrieve AlchemyConnections & their sessions.
    """
    def __init__(self):
        self._connections = {}

    def add_connection(self, *args, name=None,
                       connection: AlchemyConnection=None,
                       allow_duplicate=False,
                       **kwargs):
        """
        Registers a new AlchemyConnection by name.

        :param name: (str, default None)
            the name of the connection, required if :param connection is None.
        :param connection: (AlchemyConnection, default None)
            Nothing else is required to add a connection if this is provided.
        :param args: (AlchemyConnection.__init__(*args))
            Required if :param connection is None
        :param allow_duplicate (bool, default False)
            False raises DuplicateConnectionError if the name or connection url
            has already been registered.
            True overwrites the existing connection entry if the name is the same.
                A unique name will add the duplicate connection without overwriting
                the original name/connection pair.
        :param kwargs: (AlchemyConnection.__init__(**kwargs))
            Used if :param connection is None.
        :return: None
        """
        valid_entry_parameters = name is not None or connection is not None
        assert valid_entry_parameters, "name and connection parameters cannot both be None!"
        if connection is None:
            valid_new_parameters = args or kwargs.get('engine')
            assert valid_new_parameters, "must provide AlchemyConnection args or an existing engine"
            if not allow_duplicate:
                try:
                    self._connections[name]
                    raise DuplicateConnectionError("error - duplicate connection '{}'".format(
                        name))
                except KeyError:
                    pass
            connection = AlchemyConnection(name, *args, **kwargs)
        elif not isinstance(connection, AlchemyConnection):
            raise TypeError("connection parameter must be an AlchemyConnection, not {}".format(
                type(connection)))
            name = connection.name
        if not allow_duplicate:
            duplicate = (name in self._connections.keys()
                         or connection.engine.url in self.get_connection_urls())
            if duplicate:
                raise DuplicateConnectionError("error - duplicate connection '{}': '{}'".format(
                    name, connection.engine.url))
        self._connections[name] = connection

    def remove_connection(self, name) -> AlchemyConnection:
        """
        Pop's the connection off the registered
        connection's and returns it.
        :param name: (str)
            The name of the AlchemyConnection.
        :return: (AlchemyConnection)
        """
        return self._connections.pop(name, None)

    def connection(self, name) -> AlchemyConnection:
        """
        Returns a reference to a registered
        AlchemyConnection object.
        :param name: (str)
            The name of the AlchemyConnection.
        :return: (AlchemyConnection)
        """
        return self._connections[name]

    def get_connection_urls(self) -> list:
        """
        Returns a list of current connection urls registered.
        :return: list(url1, url2...)
        """
        return [self.connection(c).engine.url for c in self._connections.keys()]

    def get_standard_item_model(self, model=None, replace=True) -> QtGui.QStandardItemModel:
        """
        Returns a QStandardItemModel with all databases.
        :param model: (QStandardItemModel)
            An optional existing model to add/replace rows on.
        :return: (QtGui.QStandardItemModel)
            - connection_name1
                - Table1
                    - Column1
                    - Column2..
                - ...
            - connection_name2
                - ...
                    - ...
        """
        if model is None:
            model = QtGui.QStandardItemModel()

        if replace is True:
            model.clear()
            [model.appendRow(self.connection(name).get_standard_item())
             for name in self._connections.keys()]
        else:
            for name in self._connections.keys():
                item = self.connection(name).get_standard_item()
                match = model.findItems(name)
                if match:
                    model.setItem(match[0].row(), item)
                else:
                    model.appendRow(item)
        model.setHorizontalHeaderLabels(['databases'])
        model.sort(0)
        return model




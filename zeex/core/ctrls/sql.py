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
import pandas as pd
import sqlalchemy
import logging
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from zeex.core.compat import QtGui
from zeex.core.utility.widgets import create_standard_item
from zeex.core.models.dataframe import DataFrameModel
from zeex.core.utility.collection import DictConfig, get_default_config_directory
from zeex.core.models.sql import AlchemyTableModel


class AlchemyConnection(object):
    """
    A container for a SQLAlchemy connection.
    Makes available the core compontents from
    SQLAlchemy in an easy way all grouped in with the connection.
    Dialogs & Windows should use these connections to conveniently
    communicate with the SQLAlchemy connection.
    """
    def __init__(self, name, *args, **kwargs):
        """
        Provide a name for the connection and optional
        args/kwargs for creating the engine/connection.

        :param name: (str) The label associated with the connection.
        :param args: AlchemyConnection.configure(*args)
        :param kwargs:

            The following pre-configured objects can be passed
            and will not be overwritten unless you call configure
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
        self._Base = kwargs.pop('Base', None)
        if args or kwargs or self._engine is not None:
            # Force reset to false if
            # we're setting the connection on __init__.
            kwargs.pop('reset', None)
            self.configure(*args, reset=False, **kwargs)
        self._query_editor_windows = dict()

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

            It is recommended to create a unique AlchemyConnection
            for each Server (or database) being connected to.
        :param kwargs: (sqlalchemy.create_engine(**kwargs))
            Optional when reset is False and the engine is already set.
        :return: None
        """
        if reset:

            self._engine = create_engine(*args, **kwargs)
            if args:
                self.args = args
            if kwargs:
                self.kwargs = kwargs
            self._meta = MetaData(bind=self.engine)
            self._meta.reflect()
            self._inspector = inspect(self.engine)
            self._Session = sessionmaker(bind=self.engine)
            self._Base = automap_base(metadata=self.meta)
            self._Base.prepare()

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

            if self._Base is None:
                self._Base = automap_base(metadata=self.meta)
                self._Base.prepare()

    def configure_from_url(self, url):
        try:
            engine = create_engine(url)
        except TypeError as e:
            raise TypeError("Error creating engine: {}, {}".format(url, e))
        self._engine = engine
        self.configure(reset=False)

    @property
    def Session(self) -> sqlalchemy.orm.session.sessionmaker:
        """
        The sessionmaker factory for the connection.
        Use it like:
            sess = AlchemyConnection.Session()
            sess.query(Class)...etc.
            sess.close()
        :return: (sqlalchemy.orm.session.sessionmaker)
        """
        return self._Session

    @property
    def Base(self):
        return self._Base

    @property
    def engine(self) -> sqlalchemy.engine.base.Engine:
        """
        The Engine class for the
        sqlalchemy connection.
        Use it outside of a session like:
            statement = "UPDATE table SET...etc"
            AlchemyConnection.engine.execute(statement)
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
        The MetaData for the connection.
        :return: (sqlalchemy.MetaData)
        """
        return self._meta

    def get_class_by_tablename(self, table):
        """Return class reference mapped to table.

        :param tablename: String with name of table.
        :return: Class reference or None.
        """
        return self.meta.tables[table]

    def get_table_class(self, name):
        return self.meta.tables[name]

    def get_column_names(self, table) -> list:
        """
        Returns a list of column names for the given table.
        :param table: (str)
            A table that exists in the database.
        :return: (list)
            Of column names.
        """
        return [c['name'] for c in self.inspector.get_columns(table)]

    def get_table_names(self) -> list:
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
        return pd.read_sql(sql, self.engine, **kwargs)

    def get_alchemy_model(self, session, query, columns):
        return AlchemyTableModel(session, query, columns)

    def get_alchemy_query_editor_window(self, table_name, session=None, query=None,
                                        model=None, columns=None, reset=False, parent=None):
        table = self.meta.tables[table_name]
        if reset:
            self._query_editor_windows.pop(table_name, None)

        try:
            return self._query_editor_windows[table_name]
        except KeyError:
            if session is None:
                session = self.Session()
            if query is None:
                query = session.query(table)
            if columns is None:
                columns = self.get_column_names(table_name)
            if model is None:
                model = self.get_alchemy_model(session, query, columns)
            window = AlchemyQueryEditorWindow(model, parent=parent)
            self._query_editor_windows[table_name] = window
            return window

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

    def execute_sql(self, sql, force=False, **kwargs) -> DataFrameModel:
        """
        Executes SQL query returning a DataFrameModel.

        The following statement-types are identified:
            - ALTER
            - CREATE
            - DELETE
            - SELECT
            - UPDATE

        :param sql: (str)
            The statement to be executed.

        :param force (bool, default False)
            Let's the method run without error even if the statement-type is not identified.
            NOTE: This does not override SQL SYNTAX errors or anything else SQLAlchemy
            would normally raise if an invalid statement is passed.

        :param kwargs: (pd.read_sql(**kwargs) or
                        sqlalchemy.engine.base.Engine.execute(**kwargs))

        :return: (DataFrameModel)

        :raises (NotImplementedError)
            When a statement cannot be identified & force is False.
        """
        direction = str(sql[:6]).lower().lstrip().rstrip()
        if direction == 'select':
            # Select queries should contain all data queried
            # From the database in a dataframe.
            dfm = self.read_sql_df_model(sql, **kwargs)
        else:
            # Any other query should have a 1-row dataframe
            # Containing results from the execution.
            bit = dict(params=kwargs.pop('params', None),
                       multiparams=kwargs.pop('multiparams', None))
            res = self.engine.execute(sql, **bit)

            if direction in ['update', 'delete']:
                note = "SQLite RowCount (& others) may be inaccurate."
                dfm = self.get_df_model(pd.DataFrame([[res.rowcount, sql, note]],
                                                    columns=['Row Count', 'Statement', 'Note'],
                                                    index=[0]),
                                       filePath=kwargs.get('filePath'))

            elif direction in ['alter', 'create'] or force is True:
                dfm = self.get_df_model(pd.DataFrame([[sql, 'OK']], index=[0],
                                                      columns=['Statement', 'Status']),
                                         filePath=kwargs.get('filePath') )
            else:
                raise NotImplementedError("Not sure how to handle statement: {}".format(sql))
        return dfm

    def refresh_schemas(self):
        """
        Clears existing metadata,
        resets the engine inspector
        and re-reflects metadata.
        :return: (None)
        """
        self.meta.clear()
        self._inspector = inspect(self.engine)
        self.meta.reflect(bind=self.engine)


class DuplicateConnectionError(Exception):
    pass


class AlchemyConnectionManager(object):
    """
    A global container for AlchemyConnection objects.
    QMainWindows & dialogs, if interacting with SQL, should
    store a reference to this container and use it to store
    and retrieve AlchemyConnections & their sessions.
    """
    def __init__(self, dict_config=None):
        self._connections = {} # AlchemyConnections stored as key/value pairs here
        self._config = dict_config # connection configuration object stored here

    @property
    def connections(self) -> dict:
        """
        Public accessor to the connections dictionary.
        :return:
        """
        return self._connections

    @property
    def config(self) -> DictConfig:
        """
        Public accessor to the DictConfig object.
        :return: (DictConfig)
        """
        if self._config is None:
            self._config = self.get_default_config()
        return self._config

    @property
    def config_path(self) -> str:
        """
        An accessor to the DictConfig object's filename.
        Defaults to "zeex.configs.databases.ini"

        :return: (str)
            Config path.

        """
        return self.config.filename

    @staticmethod
    def get_default_config(dictionary:dict = None) -> DictConfig:
        """
        Returns a DictConfig object that contains data from
        zeex.configs.databases.ini if the path exists.

        :param dictionary: (dict, default None)
            An optional dictionary of compiled settings to load.
        :return: (DictConfig)
            With compiled settings.
        """
        filename = os.path.join(get_default_config_directory(), "databases.ini")
        c = DictConfig(filename=filename)
        if os.path.exists(filename):
            c.read(filename)
        if dictionary:
            c.read_dict(dictionary)
        return c

    def add_connection(self, *args, name: str=None,
                       connection: AlchemyConnection=None,
                       allow_duplicate: bool=False, **kwargs) -> AlchemyConnection:
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


        :return: (AlchemyConnection)
            Either the existing connection is returned,
            or the newly created connection is returned.
        """
        valid_entry_parameters = name is not None or connection is not None
        assert valid_entry_parameters, "name and connection parameters cannot both be None!"

        # Try to create a connection based on passed *args/**kwargs
        if connection is None:
            # Find args or a pre-generated engine.
            valid_new_parameters = args or kwargs.get('engine')
            assert valid_new_parameters, "must provide AlchemyConnection args or an existing engine"

            # Make sure to fail if a duplicate connection is
            # Being added when not allowed.
            if not allow_duplicate:
                try:
                    self._connections[name]
                    raise DuplicateConnectionError("error - duplicate connection '{}'".format(
                        name))
                except KeyError:
                    pass
            # No fails so far, create the connection.
            connection = AlchemyConnection(name, *args, **kwargs)

        elif not hasattr(connection, 'engine'):
            # Don't allow non-AlchemyConnections to be passed in here.
            raise TypeError("connection parameter must be an AlchemyConnection, not {}".format(
                type(connection)))

        elif name is None:
            # Don't allow no-name connections in here.
            name = connection.name
            assert name is not None, "You can't add a connection with no name!"

        elif name is not None and name != connection.name:
            # Don't allow a connection name to be different
            # than it's key.
            connection.name = name

        # Check for duplicate connection URLs now
        # Fail only if not allowed.
        if not allow_duplicate:
            duplicate = (name in self._connections.keys()
                         or connection.engine.url in self.get_connection_urls())
            if duplicate:
                raise DuplicateConnectionError("error - duplicate connection '{}': '{}'".format(
                    name, connection.engine.url))

        # Add the connection and be done...finally.
        self._connections[name] = connection
        return self._connections[name]

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
            # Clear the model and append all standard items.
            model.clear()
            [model.appendRow(self.connection(name).get_standard_item())
             for name in self._connections.keys()]
        else:
            # Go through each item in the existing model and
            # Replace it with an updated connection
            for name in self._connections.keys():
                item = self.connection(name).get_standard_item()
                match = model.findItems(name)
                if match:
                    model.setItem(match[0].row(), item)
                else:
                    # No match found, append the item to the end.
                    model.appendRow(item)
        model.setHorizontalHeaderLabels(['Connections'])
        model.sort(0)
        return model

    def save_settings(self, file_path=None):
        """
        Saves all current connection details to a file path, securely stores
        passwords using the method::zeex.core.utility.collection.BaseConfig.set_password
        this method wraps the keyring library to store credentials.

        :param file_path: (str, default None)
            None will save the settings to zeex.configs.databases.ini

        :return: (DictConfig)
            Containing the details of the configurations (sans passwords).
        """
        if file_path is None:
            file_path = self.config_path
        config = self.config

        for name in self.connections.keys():
            con = self.connection(name)
            section = con.name
            args, kwargs = con.args, con.kwargs
            url = None
            if args:
                try:
                    url = sqlalchemy.engine.url.make_url(args[0])
                except Exception:
                    pass

            if url is None:
                url = sqlalchemy.engine.url.make_url(con.engine.url)

            con_args = url.translate_connect_args()
            password = con_args.get('password', None)
            if password is not None:
                # Securely store the password.
                # Remove from connection arguments.
                config.set_password(section,
                                    con_args.pop('username'),
                                    con_args.pop('password'))

            for key, value in con_args.items():
                config.set_safe(section, key, value)

            if 'drivername' not in config.options(section):
                drivername = "{}+{}".format(con.engine.name, con.engine.driver)
                config.set_safe(section, 'drivername', drivername)

        config.save_as(file_path, set_self=True)
        return config

    def add_connections_from_settings(self, settings: DictConfig=None, sections=None,
                                      raise_on_error=False) -> list:
        """
        Adds database connections from a DictConfig (ConfigParser) object.

        List of configuration options available from SQLAlchemy:
        (http://docs.sqlalchemy.org/en/latest/core/engines.html)
        ========================================================
            drivername – the name of the database backend.
                         This name will correspond to a module in sqlalchemy/databases
                         or a third party plug-in.
            username – The user name.
            password – database password.
            host – The name of the host.
            port¶ – The port number.
            database – The database name.
            query – A dictionary of options to be passed to the
                    dialect and/or the DBAPI upon connect.
        ========================================================

        :param settings: (DictConfig, default None)
            None uses the last saved zeex.configs.databases.ini file
            example configuration setup:
                [connection name1]
                database=C:/Users/User/database1.db
                drivername=sqlite+pysqlite
            The above example could be accessed like:
                alchemy_connection = AlchemyConnectionManager.connection('connection name1')

        :param sections: (list, default None)
            An optional list of connection names to connect to.
            None uses all available sections in the :param settings object

        :param raise_on_error: (bool, default False)
            True raises errors when a connection fails to add
            False prints that the connection failed to add on the console.

        :return: (list)
            Of connection names that were successfully added
        """
        if settings is None:
            settings = self.config
        if sections is None:
            sections = settings.sections()
        else:
            sections = [s for s in settings.sections() if s in sections]
        added = []
        if sections:
            for s in sections:
                options = settings.options(s)
                if 'database' in options and s not in self.connections:
                    # should be a valid section
                    try:
                        info = {o: settings.get(s, o) for o in options}
                        username = info.get('username')
                        if username is not None:
                            info['password'] = settings.get_password(s, username=username)
                        url = sqlalchemy.engine.url.URL(info.pop('drivername'), **info)
                        con = AlchemyConnection(name=s)
                        con.configure_from_url(url)
                        self.add_connection(connection=con)
                        added.append(s)
                    except Exception as e:
                        if raise_on_error:
                            raise
                        else:
                            logging.error("Error adding connection: {}, {}".format(s, e))
        return added








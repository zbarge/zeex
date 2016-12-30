from ...ui.sql.main_ui import Ui_DatabasesMainWindow
from ...compat import QtGui
from ...models.fieldnames import connection_info as fieldnames_connection_info
from sqlalchemy import inspect, MetaData
from ...utility.widgets import create_standard_item_model, create_standard_item
CONNECTIONS = {'field_names': fieldnames_connection_info}


class DatabasesMainWindow(QtGui.QMainWindow, Ui_DatabasesMainWindow):
    def __init__(self, *args, **kwargs):
        db_model = kwargs.pop('databases_model', None)
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.connect_database_treeview(model=db_model)

    def connect_database_treeview(self, model=None):
        if model is None:
            model = self.treeView.model()
            if not model:
                model = QtGui.QStandardItemModel()
        self.treeView.setModel(model)
        for db_name in CONNECTIONS.keys():
            self.load_engine(db_name, engine=CONNECTIONS[db_name]['engine'])
        model.setHorizontalHeaderLabels(['databases'])

    def connect_actions(self):
        pass

    def load_engine(self, name, engine=None):
        """
        Inspects an engine via SQLAlchemy
        and adds it to the "databases" treeview.
        :param name: The name of the database.
        :param engine: The engine to the database
        :return: None
        """
        meta = MetaData()
        if engine is None:
            engine = CONNECTIONS[name]['engine']
        # Load engine data into object
        meta.reflect(bind=engine)
        inspector = inspect(engine)

        # Get the treeView's model
        model = self.treeView.model()

        # Try to find an existing database/table item
        # in the model to replace
        indexes = model.findItems(name)
        if indexes:
            idx = indexes[0]
            db_name = model.itemFromIndex(idx).text()
        else:
            idx = None
            db_name = name

        # Create a new item
        # to load table/column information into.
        new_item = create_standard_item(db_name, editable=False, checkable=False)
        for row, table in enumerate(meta.tables.keys()):
            # Get a dict of all columns in the table.
            columns = inspector.get_columns(table)
            table = create_standard_item(table)

            # Add all columns to the table's item.
            cnames = [c['name'] for c in columns]
            for crow, c in enumerate(cnames):
                c = create_standard_item(c)
                table.setChild(crow, c)

            # Add the table to the database's item
            new_item.setChild(row, table)

        # Replace or append the table item
        if idx:
            model.setItem(idx.row(), new_item)
        else:
            model.appendRow(new_item)




















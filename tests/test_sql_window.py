import os
import pytest
import pandas as pd
from tests.main import MainTestClass
from zeex.core.views.sql.main import DatabasesMainWindow
from zeex.core.ctrls.sql import AlchemyConnectionManager, AlchemyConnection
from zeex.core.ctrls.dataframe import DataFrameModelManager


fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
sqlite_db_path = os.path.join(fixtures_dir, "test_sql.db")
sqlite_db_path2 = os.path.join(fixtures_dir, "test_sql2.db")
dump_path1 = os.path.join(fixtures_dir, "sql_dump1.csv")
query_txt_path = os.path.join(fixtures_dir, "sample_query.txt")


class TestDatabasesMainWindowAndAssociates(MainTestClass):
    """
    Holds test-cases covering the following:
        - zeex.core.views.sql.main.DatabasesMainWindow
        - zeex.core.views.sql.add_connection.AlchemyConnectionDialog
        - zeex.core.views.sql.table_import.AlchemyTableImportDialog
    """

    @pytest.fixture
    def sqlite_db_path(self):
        return sqlite_db_path

    @pytest.fixture
    def main_window(self, qtbot, sqlite_db_path):
        """
        Creates & returns a DatabasesMainWindow object loaded with one test sqlite connection
        named "con1" - any existing tables are dropped.
        :param qtbot:
        :param sqlite_db_path:
        :return:
        """
        c = AlchemyConnection(name="con1")
        c.configure("sqlite:///" + sqlite_db_path, reset=True)
        c.meta.drop_all()
        cm = AlchemyConnectionManager()
        cm.add_connection(connection=c)
        window = DatabasesMainWindow(df_manager=DataFrameModelManager(), connection_manager=cm)
        qtbot.addWidget(window)
        return window

    def test_general_functionality(self, main_window: DatabasesMainWindow, df:pd.DataFrame):
        """
        Covers the following cases:
            - TreeView/TreeModel are in sync with the AlchemyConnectionManager's connections
            - Refreshing schemas will actually show you newly added tables/data.
            - Entering queries via the text edit can execute against the database
            - Connection activation occurs when expanding the treeview - the combo box will stay in sync.
            - Queries in the text edit can save to disk
            - Queries saved to disk can import into the text edit
        :param main_window:
        :param df:
        :return:
        """
        first_item = main_window.tree_model.item(0)
        table_name = 'test_table'

        # Valid connection exists in the connection manager.
        assert first_item.text() in main_window.con_manager.connections.keys()

        main_window.treeView.setExpanded(first_item.index(), True)
        # Combo box should've picked up the treeView expanded signal.
        assert main_window.comboBoxCurrentDatabase.currentText() == first_item.text()

        # Load the test dataframe into a SQL table.
        df.to_sql(table_name, main_window.connection.engine, index=False)

        # Ensure that, after refreshing schemas,
        # the table exists in the connection's meta data
        main_window.actionRefreshSchemas.trigger()
        assert table_name in main_window.connection.meta.tables.keys()

        # Also confirm the newly created table made it into the treeView/model
        first_item = main_window.tree_model.item(0)
        check_table = first_item.child(0)
        assert check_table.text() == table_name

        # Load a query into the text edit and execute it
        first_col = df.columns.tolist()[0]
        first_val = df.loc[0, first_col]
        query = "SELECT * FROM {} WHERE {} = {}".format(table_name, first_col, first_val)
        main_window.textEdit.document().setPlainText(query)
        main_window.actionExecuteQuery.trigger()

        # A DataFrameModel should've been inserted into the tableView.
        model = main_window.tableView.model()
        df_back = model.dataFrame()

        # Prove this is the same value from the dataframe.
        assert df_back.loc[0, first_col] == first_val

        # Make sure we can open the dataframe to a FileView window
        assert not main_window.df_manager.file_table_windows
        main_window.open_query_fileview(save_path=dump_path1)
        assert main_window.df_manager.file_table_windows

        # Save the query to file
        if os.path.exists(query_txt_path):
            os.remove(query_txt_path)
        main_window.comboBoxCurrentFile.addItem(query_txt_path)
        main_window.actionSaveText.trigger()
        assert os.path.exists(query_txt_path)

        # Clear the query out and load the file back in
        main_window.textEdit.document().setPlainText('')
        main_window.open_sql_text(query_txt_path)

        # Prove the query stayed the same.
        assert main_window.textEdit.document().toPlainText() == query
        main_window.con_manager.connections.clear()

    def test_table_import_dialog(self, main_window: DatabasesMainWindow, example_file_path):
        """
        Covers case of importing a new table into a database via the DatabasesMainWindow.dialog_import
        :param main_window:
        :param example_file_path:
        :return:
        """
        df = pd.read_csv(example_file_path)
        # Activate the first connection
        con_item = main_window.tree_model.item(0)
        main_window.treeView.setExpanded(con_item.index(), True)

        # Set the path/table & execute the import.
        table_name = "test_import_table"
        dialog = main_window.dialog_import
        dialog.lineEditSourcePath.setText(example_file_path)
        dialog.lineEditTableName.setText(table_name)
        dialog.import_table()

        # Refresh the schemas and check for the new table.
        main_window.actionRefreshSchemas.trigger()
        con_item = main_window.tree_model.item(0)
        table_item = con_item.child(0)
        assert table_item.text() == table_name

        # Query the data back out of the database.
        main_window.textEdit.document().setPlainText("SELECT * FROM {}".format(table_name))
        main_window.actionExecuteQuery.trigger()
        df_back = main_window.tableView.model().dataFrame()

        assert df_back.index.size == df.index.size

        # Verify that the imported data queried out of the
        # database is an exact match to the original dataframe.
        for i in list(df_back.index):
            for c in df_back.columns:
                assert df.loc[i, c] == df_back.loc[i, c]
        main_window.con_manager.connections.clear()

    def test_add_sqlite_connection(self, main_window: DatabasesMainWindow):
        """
        Covers case of adding a SQLite connection via the DatabasesMainWindow.dialog_add_con.
        :param main_window:
        :return:
        """
        con_name = "sample_sqlite_connection2"
        dialog = main_window.dialog_add_con

        # Insert connection info into the dialog
        dialog.lineEditHost.setText(sqlite_db_path2)
        dialog.comboBoxDatabaseType.setCurrentIndex(dialog.comboBoxDatabaseType.findText("sqlite"))
        dialog.lineEditConnectionName.setText(con_name)

        # Execute what the buttonBox.OK is connected to
        dialog.register_connection()

        # The new table should now be in the main_window's treeView/model.
        names = [main_window.tree_model.item(i).text()
                 for i in range(main_window.tree_model.rowCount())]
        assert con_name in names

        # The connection should available in the AlchemyConnectionManager.
        con = dialog.con_manager.connection(con_name)
        assert os.path.basename(sqlite_db_path2) == os.path.basename(con.engine.url.database)
        main_window.con_manager.connections.clear()

    def test_edit_fields_dialog(self, main_window: DatabasesMainWindow, example_file_path):

        # Prepare to import SQL table.
        # Activate the connection in the window.
        df = pd.read_csv(example_file_path)
        table_name = "edit_fields_sample_table"
        con_item = main_window.tree_model.item(0)
        con_name = con_item.text()
        main_window.treeView.setCurrentIndex(con_item.index())
        main_window.treeView.setExpanded(con_item.index(), True)
        # Do the import
        df.to_sql(table_name, main_window.connection.engine, if_exists='replace', index=False)

        # Refresh schemas and find/select the newly created table
        main_window.refresh_schemas()
        con_item = main_window.tree_model.findItems(con_name)[0]
        table_item = con_item.child(0)

        # Open the table description dialog & get the tableView.model
        main_window.open_table_description_dialog(table_item.index())
        model = main_window._table_desc_dialog.tableView.model()

        # Compare columns from the model and ensure they're in the dataframe
        for i in range(model.rowCount()):
            col = model.item(i, 0).text()
            assert col in df.columns

        main_window.con_manager.connections.clear()

    def test_alchemy_table_view_window(self, main_window: DatabasesMainWindow):
        pytest.skip()

    def teardown_class(self):
        for p in [sqlite_db_path, dump_path1, query_txt_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass





# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:47:27 2016

@author: Zeke
"""
import os
from functools import partial
from core.compat import QtGui, QtCore
from core.models.main import FieldsListModel
from core.ui.settings_ui import Ui_settingsDialog
from core.utility.collection import SettingsINI
from core.utility.widgets import configureComboBox


def normpath(dirname, filename=None):
    if filename is not None:
        dirname = os.path.join(dirname, filename)
    return os.path.normpath(dirname).replace("\\","/")


VIEWS = normpath(os.path.dirname(__file__))
CORE = os.path.dirname(VIEWS)
ZEEX = os.path.dirname(CORE)
THEMES_DIR = normpath(CORE, 'themes')
CONFIG_DIR = normpath(ZEEX, 'configs')
DEFAULT_SETTINGS_PATH = normpath(CONFIG_DIR, 'default.ini')
THEME_NAME1 = 'theme1.qss'
THEME_NAME2 = 'theme2.qss'
THEME_NAME3 = 'theme3.qss'
DEFAULT_THEME = THEME_NAME3
DEFAULT_THEME_OPTIONS = [THEME_NAME1, THEME_NAME2, THEME_NAME3]
DEFAULT_CODECS = ['UTF_8', 'ASCII', 'ISO-8895-1']
DEFAULT_SEPARATORS = [',','|',r'\t',';']
DEFAULT_FLAVORS = ['SQLite', 'PostgreSQL', 'MySQL']
DEFAULT_FILE_FORMATS = ['.xlsx', '.csv', '.txt']


class SettingsDialog(QtGui.QDialog, Ui_settingsDialog):
    signalSettingsExported = QtCore.Signal(SettingsINI, str)
    signalSettingsImported = QtCore.Signal(SettingsINI, str)
    _themes_dir = THEMES_DIR

    def __init__(self, settings=None):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)

        if isinstance(settings, SettingsINI):
            self.Config = settings
        else:
            self.Config = SettingsINI(settings)

        self.configure_settings(self.Config)
        self.connect_buttons()

    @property
    def _settings_filename(self):
        return self.Config._filename

    def connect_buttons(self):
        new_path = os.path.splitext(self.Config._default_path)[0] + "-test.ini"
        func = partial(self.save_settings, new_path)
        self.btnSave.clicked.connect(func)
        self.btnExport.clicked.connect(self.export_settings)
        self.btnImport.clicked.connect(self.import_settings)
        self.btnLogDirectory.clicked.connect(self.open_log_directory)
        self.btnRootDirectory.clicked.connect(self.open_root_directory)

    def configure_settings(self, config):
        """
        Configures settings based on a SettingsINI object.
        Defaults are contained in here.
        Top-level configurations read from.:
            GENERAL
            INPUT
            OUTPUT
            DATABASE
            FIELDS
        """
        if not isinstance(config, SettingsINI):
            raise NotImplementedError("config must be a SettingsINI object.")
            
        try:
            genconfig = config['GENERAL']
            inconfig  = config['INPUT']
            outconfig = config['OUTPUT']
            dbconfig  = config['DATABASE']
        except KeyError as e:
            raise KeyError("SettingsINI object missing config option '{}'".format(e))
            
        # Get items/set defaults.
        ROOT_DIR =        genconfig.get('ROOT_DIRECTORY',  "C:/Zeex Projects")
        LOG_DIR =         genconfig.get('LOG_DIRECTORY',   "C:/Zeex Projects/logs")
        LOG_LEVEL =       genconfig.get('LOG_LEVEL',       "Low")
        CLOUD_PROVIDER =  genconfig.get('CLOUD_PROVIDER',  "S3")
        THEME_NAME     =  genconfig.get('THEME',           DEFAULT_THEME)
        HEADER_CASE =     inconfig.get('HEADER_CASE',      "Lower")
        HEADER_SPACE =    inconfig.get('HEADER_SPACE',     "_")
        AUTO_SORT =       inconfig.get('AUTO_SORT',        False)
        AUTO_DEDUPE =     inconfig.get('AUTO_DEDUPE',      False)
        OUTPUT_FORMAT =   outconfig.get('OUTPUT_FORMAT',   ".csv")
        FILENAME_PFX =    outconfig.get('FILENAME_PREFIX', "z_")
        CHART_FILE =      outconfig.get('CHART_FILENAME',  "")
        SEPARATOR =       outconfig.get('SEPARATOR', ",")
        ENCODING =        outconfig.get('ENCODING', "UTF_8")
        DB_FLAVOR =       dbconfig.get('FLAVOR',           "SQLITE")
        DB_URL =          dbconfig.get('URL',              "")
        DB_NAME =         dbconfig.get('DEFAULT_DATABASE', None)
        DB_USERNAME =     dbconfig.get('USERNAME',         None)
        DB_PASSWORD =     dbconfig.get('PASSWORD',         None)
        DB_PORT =         dbconfig.get('PORT',             None)


        DEDUPE_FIELDS =   config.get_safe('FIELDS', 'DEDUPE', fallback=[])
        SORT_FIELDS   =   config.get_safe('FIELDS', 'SORT',   fallback=['updatedate', 'insertdate'])
        STRING_FIELDS =   config.get_safe('FIELDS', 'STRING', fallback=['address1','firstname','lastname',
                                                              'city','state','zipcode', 'fullname',
                                                              'email','homephone','cellphone'])
        INTEGER_FIELDS =  config.get_safe('FIELDS', 'INTEGER',fallback=['id','users_id'])
        DATE_FIELDS   =   config.get_safe('FIELDS', 'DATE',   fallback=['insertdate','updatedate'])
        FLOAT_FIELDS =    config.get_safe('FIELDS', 'FLOAT',   fallback=[])

        self.autoSortCheckBox.setCheckable(True)
        self.autoDedupeCheckBox.setCheckable(True)

        if AUTO_SORT:
            self.autoSortCheckBox.setChecked(True)

        if AUTO_DEDUPE:
            self.autoSortCheckBox.setChecked(True)
        
        #LINE EDITS
        self.rootDirectoryLineEdit.setText(      ROOT_DIR)
        self.logDirectoryLineEdit.setText(       LOG_DIR)
        self.fileNamePrefixLineEdit.setText(     FILENAME_PFX)
        self.chartSettingsFileLineEdit.setText(  CHART_FILE)
        self.urlLineEdit.setText(                DB_URL)
        self.defaultDatabaseLineEdit.setText(    DB_NAME)
        self.usernameLineEdit.setText(           DB_USERNAME)
        self.passwordLineEdit.setText(           DB_PASSWORD)
        self.portLineEdit.setText(               DB_PORT)
        
        #COMBO BOXES
        configureComboBox(self.logLevelComboBox,      ['Low', 'Medium', 'High'],         LOG_LEVEL)
        configureComboBox(self.cloudProviderComboBox, ['Google Drive', 'S3', 'DropBox'], CLOUD_PROVIDER)
        configureComboBox(self.headerCaseComboBox,    ['lower', 'UPPER', 'Proper'],      HEADER_CASE)
        configureComboBox(self.headerSpacesComboBox,  [' ', '_'],                        HEADER_SPACE)
        configureComboBox(self.fileFormatComboBox,    DEFAULT_FILE_FORMATS,              OUTPUT_FORMAT)
        configureComboBox(self.flavorComboBox,        DEFAULT_FLAVORS,                   DB_FLAVOR)
        configureComboBox(self.separatorComboBox,     DEFAULT_SEPARATORS,                SEPARATOR)
        configureComboBox(self.encodingComboBox,      DEFAULT_CODECS,                    ENCODING)
        configureComboBox(self.themeComboBox,         DEFAULT_THEME_OPTIONS,             THEME_NAME)
        self.set_theme(THEME_NAME)
        
        #Field Models
        self.dedupeFieldsModel = FieldsListModel(items=DEDUPE_FIELDS)
        self.sortFieldsModel   = FieldsListModel(items=SORT_FIELDS)
        self.strFieldsModel    = FieldsListModel(items=STRING_FIELDS)
        self.intFieldsModel    = FieldsListModel(items=INTEGER_FIELDS)
        self.dateFieldsModel   = FieldsListModel(items=DATE_FIELDS)
        self.floatFieldsModel  = FieldsListModel(items=FLOAT_FIELDS)
        
        self.dedupeFieldsListView.setModel(self.dedupeFieldsModel)
        self.sortFieldsColumnView.setModel(self.sortFieldsModel)
        self.strFieldsListView.setModel(   self.strFieldsModel)
        self.intFieldsListView.setModel(   self.intFieldsModel)
        self.dateFieldsListView.setModel(  self.dateFieldsModel)
        self.floatFieldsListView.setModel( self.floatFieldsModel)
        
    def save_settings(self, to_path=None, write=False):
        self.set_theme()

        self.Config.set('GENERAL', 'ROOT_DIRECTORY', self.rootDirectoryLineEdit.text())
        self.Config.set('GENERAL', 'LOG_DIRECTORY', self.logDirectoryLineEdit.text())
        self.Config.set('GENERAL', 'LOG_LEVEL', self.logLevelComboBox.currentText())
        self.Config.set('GENERAL', 'CLOUD_PROVIDER', self.cloudProviderComboBox.currentText())
        self.Config.set('GENERAL', 'THEME', self.themeComboBox.currentText())

        self.Config.set('INPUT', 'HEADER_CASE', self.headerCaseComboBox.currentText())
        self.Config.set('INPUT', 'HEADER_SPACE', self.headerSpacesComboBox.currentText())
        self.Config.set_safe('INPUT', 'AUTO_SORT', self.autoSortCheckBox.isChecked())
        self.Config.set_safe('INPUT', 'AUTO_DEDUPE', self.autoDedupeCheckBox.isChecked())

        self.Config.set('OUTPUT', 'OUTPUT_FORMAT', self.fileFormatComboBox.currentText())
        self.Config.set('OUTPUT', 'FILENAME_PREFIX', self.fileNamePrefixLineEdit.text())
        self.Config.set('OUTPUT', 'CHART_FILENAME', self.chartSettingsFileLineEdit.text())

        self.Config.set('DATABASE', 'FLAVOR', self.flavorComboBox.currentText())
        self.Config.set('DATABASE', 'URL', self.urlLineEdit.text())
        self.Config.set('DATABASE', 'DEFAULT_DATABASE', self.defaultDatabaseLineEdit.text())
        self.Config.set('DATABASE', 'USERNAME', self.usernameLineEdit.text())
        self.Config.set('DATABASE', 'PASSWORD', self.passwordLineEdit.text())

        self.Config.set_safe('FIELDS', 'DEDUPE',  self.dedupeFieldsModel.get_data_list())
        self.Config.set_safe('FIELDS', 'SORT',    self.sortFieldsModel.get_data_list())
        self.Config.set_safe('FIELDS', 'STRING',  self.strFieldsModel.get_data_list())
        self.Config.set_safe('FIELDS', 'DATE',    self.dateFieldsModel.get_data_list())
        self.Config.set_safe('FIELDS', 'INTEGER', self.intFieldsModel.get_data_list())
        self.Config.set_safe('FIELDS', 'FLOAT', self.floatFieldsModel.get_data_list())

        if write or to_path is not None:
            if to_path is None:
                to_path = self.Config._filename

            self.Config._filename = to_path

            self.Config.save()

    def clear_settings(self):
        pass

    def export_settings(self, to=None):
        if to is None:
            to = QtGui.QFileDialog.getSaveFileName()[0]
        self.save_settings(to_path=None, write=False)
        self.Config.save_as(to, set_self=False)
        self.signalSettingsExported.emit(self.Config, to)

    def set_theme(self, theme_name=None):
        if theme_name is None:
            theme_name = self.themeComboBox.currentText()
            if isinstance(theme_name, int):
                print("No theme selected.")
                theme_name = THEME_NAME2

        theme_path = normpath(self._themes_dir, theme_name)

        if os.path.exists(theme_path):
            with open(theme_path, "r") as fh:
                app = QtCore.QCoreApplication.instance()
                app.setStyleSheet(fh.read())
        else:
            print("Couldnt find theme {}!".format(theme_path))

    def import_settings(self, filename=None):
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName()

        self.Config.save()
        self.Config.clear()
        self.Config.read(filename)
        self.Config._filename = filename
        self.clear_settings()
        self.configure_settings(self.Config)

    def open_root_directory(self):
        dirname = QtGui.QFileDialog.getExistingDirectory()
        self.rootDirectoryLineEdit.setText(dirname)

    def open_log_directory(self):
        dirname = QtGui.QFileDialog.getExistingDirectory()
        self.logDirectoryLineEdit.setText(dirname)






        
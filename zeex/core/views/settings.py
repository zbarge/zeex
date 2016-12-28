# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:47:27 2016
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
import sys
from functools import partial
from core.compat import QtGui, QtCore
from core.models.main import FieldsListModel
from core.ui.settings_ui import Ui_settingsDialog
from core.utility.collection import SettingsINI, DictConfig
from core.utility.widgets import configureComboBox
from core.ctrls.dataframe import ENCODINGS, SEPARATORS

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
DEFAULT_THEME_OPTIONS = ['', THEME_NAME1, THEME_NAME2, THEME_NAME3]
DEFAULT_CODECS = ['UTF_8', 'ASCII', 'ISO-8859-1']
DEFAULT_SEPARATORS = [',','|',r'\t',';']
DEFAULT_FLAVORS = ['SQLite', 'PostgreSQL', 'MySQL']
DEFAULT_FILE_FORMATS = ['.xlsx', '.csv', '.txt']

DEFAULT_ROOT_DIR = os.path.join(os.environ['HOMEPATH'], "Zeex Projects")
DEFAULT_LOG_DIR = os.path.join(DEFAULT_ROOT_DIR, 'logs')


class SettingsDialog(QtGui.QDialog, Ui_settingsDialog):
    signalSettingsExported = QtCore.Signal(SettingsINI, str)
    signalSettingsImported = QtCore.Signal(SettingsINI, str)
    signalSettingsSaved = QtCore.Signal(SettingsINI, str)
    _themes_dir = THEMES_DIR

    def __init__(self, settings=None, **kwargs):
        QtGui.QDialog.__init__(self, **kwargs)
        self.setupUi(self)

        if isinstance(settings, (SettingsINI, DictConfig)):
            self.settings_ini = settings
        elif isinstance(settings, str) or settings is None:
            if settings is None:
                print("Using default settings - got settings of type {}".format(type(settings)))
            self.settings_ini = SettingsINI(filename=settings)
        elif isinstance(settings, dict):
            self.settings_ini = DictConfig(dictionary=settings)
        else:
            raise NotImplementedError("Unsupported settings type: {}".format(type(settings)))

        self.configure_settings(self.settings_ini)
        self.connect_buttons()

    @property
    def _settings_filename(self):
        return self.settings_ini._filename

    def connect_buttons(self):
        self.btnSave.clicked.connect(self.save_settings)
        self.btnExport.clicked.connect(self.export_settings)
        self.btnImport.clicked.connect(self.import_settings)
        self.btnLogDirectory.clicked.connect(self.open_log_directory)
        self.btnRootDirectory.clicked.connect(self.open_root_directory)
        self.btnSetDefault.clicked.connect(partial(self.export_settings, self.settings_ini.default_path, set_self=True))
        self.btnReset.clicked.connect(self.reset_settings)

    def configure_settings(self, config: SettingsINI):
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

        c = config
        # Get items/set defaults.
        ROOT_DIR =        c.get('GENERAL', 'root_directory',  fallback=DEFAULT_ROOT_DIR)
        LOG_DIR =         c.get('GENERAL', 'log_directory',   fallback=DEFAULT_LOG_DIR)
        LOG_LEVEL =       c.get_safe('GENERAL', 'LOG_LEVEL',       fallback="Low")
        CLOUD_PROVIDER =  c.get_safe('GENERAL', 'CLOUD_PROVIDER',  fallback="S3")
        THEME_NAME     =  c.get_safe('GENERAL', 'THEME',           fallback=DEFAULT_THEME)
        HEADER_CASE =     c.get_safe('INPUT', 'HEADER_CASE',      fallback="Lower")
        HEADER_SPACE =    c.get_safe('INPUT', 'HEADER_SPACE',     fallback="_")
        AUTO_SORT =       c.getboolean('INPUT', 'AUTO_SORT',        fallback=False)
        AUTO_DEDUPE =     c.getboolean('INPUT', 'AUTO_DEDUPE',      fallback=False)
        OUTPUT_FORMAT =   c.get_safe('OUTPUT', 'OUTPUT_FORMAT',   fallback=".csv")
        FILENAME_PFX =    c.get_safe('OUTPUT', 'FILENAME_PREFIX', fallback="z_")
        CHART_FILE =      c.get_safe('OUTPUT', 'CHART_FILENAME',  fallback="")
        SEPARATOR =       c.get_safe('OUTPUT', 'SEPARATOR',       fallback=",")
        ENCODING =        c.get_safe('OUTPUT', 'ENCODING',        fallback="UTF_8")
        DB_FLAVOR =       c.get_safe('DATABASE', 'FLAVOR',           fallback="SQLITE")
        DB_URL =          c.get_safe('DATABASE', 'URL',              fallback="")
        DB_NAME =         c.get_safe('DATABASE', 'DEFAULT_DATABASE', fallback=None)
        DB_USERNAME =     c.get_safe('DATABASE', 'USERNAME',        fallback= None)
        DB_PASSWORD =     c.get_safe('DATABASE', 'PASSWORD',         fallback=None)
        DB_PORT =         c.get_safe('DATABASE', 'PORT',             fallback=None)


        DEDUPE_FIELDS =   c.get_safe('FIELDS', 'DEDUPE', fallback=[])
        SORT_FIELDS   =   c.get_safe('FIELDS', 'SORT',   fallback=['updatedate', 'insertdate'])
        STRING_FIELDS =   c.get_safe('FIELDS', 'STRING', fallback=['address1','firstname','lastname',
                                                              'city','state','zipcode', 'fullname',
                                                              'email','homephone','cellphone'])
        INTEGER_FIELDS =  c.get_safe('FIELDS', 'INTEGER',fallback=['id','users_id'])
        DATE_FIELDS   =   c.get_safe('FIELDS', 'DATE',   fallback=['insertdate','updatedate'])
        FLOAT_FIELDS =    c.get_safe('FIELDS', 'FLOAT',   fallback=[])

        #Make sure the directories exist.
        for fp in [ROOT_DIR, LOG_DIR]:
            try:
                if not os.path.exists(fp):
                    os.mkdir(fp)
            except OSError as e:
                raise OSError("Cannot initialize settings directory {} - {}".format(fp, e))
                sys.exit(1)

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

        self.save_settings(to_path=None, write=False)
        
    def save_settings(self, to_path=None, write=False):
        self.set_theme()

        self.settings_ini.set_safe('GENERAL', 'ROOT_DIRECTORY', self.rootDirectoryLineEdit.text())
        self.settings_ini.set('GENERAL', 'LOG_DIRECTORY', self.logDirectoryLineEdit.text())
        self.settings_ini.set('GENERAL', 'LOG_LEVEL', self.logLevelComboBox.currentText())
        self.settings_ini.set('GENERAL', 'CLOUD_PROVIDER', self.cloudProviderComboBox.currentText())
        self.settings_ini.set('GENERAL', 'THEME', self.themeComboBox.currentText())

        self.settings_ini.set_safe('INPUT', 'HEADER_CASE', self.headerCaseComboBox.currentText())
        self.settings_ini.set('INPUT', 'HEADER_SPACE', self.headerSpacesComboBox.currentText())
        self.settings_ini.set_safe('INPUT', 'AUTO_SORT', self.autoSortCheckBox.isChecked())
        self.settings_ini.set_safe('INPUT', 'AUTO_DEDUPE', self.autoDedupeCheckBox.isChecked())

        self.settings_ini.set_safe('OUTPUT', 'OUTPUT_FORMAT', self.fileFormatComboBox.currentText())
        self.settings_ini.set('OUTPUT', 'FILENAME_PREFIX', self.fileNamePrefixLineEdit.text())
        self.settings_ini.set('OUTPUT', 'CHART_FILENAME', self.chartSettingsFileLineEdit.text())

        self.settings_ini.set_safe('DATABASE', 'FLAVOR', self.flavorComboBox.currentText())
        self.settings_ini.set('DATABASE', 'URL', self.urlLineEdit.text())
        self.settings_ini.set('DATABASE', 'DEFAULT_DATABASE', self.defaultDatabaseLineEdit.text())
        self.settings_ini.set('DATABASE', 'USERNAME', self.usernameLineEdit.text())
        self.settings_ini.set('DATABASE', 'PASSWORD', self.passwordLineEdit.text())

        self.settings_ini.set_safe('FIELDS', 'DEDUPE', self.dedupeFieldsModel.get_data_list())
        self.settings_ini.set_safe('FIELDS', 'SORT', self.sortFieldsModel.get_data_list())
        self.settings_ini.set_safe('FIELDS', 'STRING', self.strFieldsModel.get_data_list())
        self.settings_ini.set_safe('FIELDS', 'DATE', self.dateFieldsModel.get_data_list())
        self.settings_ini.set_safe('FIELDS', 'INTEGER', self.intFieldsModel.get_data_list())
        self.settings_ini.set_safe('FIELDS', 'FLOAT', self.floatFieldsModel.get_data_list())

        if write or to_path is not None:
            if to_path is None:
                to_path = self.settings_ini._filename

            self.settings_ini._filename = to_path

            self.settings_ini.save()

        self.signalSettingsSaved.emit(self.settings_ini, self.settings_ini.filename)

    def clear_settings(self):
        self.cloudProviderComboBox.clear()
        self.encodingComboBox.clear()
        self.fileFormatComboBox.clear()
        self.flavorComboBox.clear()
        self.headerCaseComboBox.clear()
        self.headerSpacesComboBox.clear()
        self.logLevelComboBox.clear()
        self.separatorComboBox.clear()
        self.themeComboBox.clear()


    def export_settings(self, to=None, set_self=False):
        if to is None:
            to = QtGui.QFileDialog.getSaveFileName()[0]
        self.save_settings(to_path=None, write=False)
        self.settings_ini.save_as(to, set_self=set_self)
        self.signalSettingsExported.emit(self.settings_ini, to)

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

        self.settings_ini.save()
        self.settings_ini.clear()
        self.settings_ini.read(filename)
        self.settings_ini._filename = filename
        self.clear_settings()
        self.configure_settings(self.settings_ini)

    def reset_settings(self):
        self.settings_ini.clear()
        self.settings_ini.read(self.settings_ini.backup_path)
        self.settings_ini.save_as(self.settings_ini.default_path, set_self=True)
        self.clear_settings()
        self.configure_settings(self.settings_ini)

    def open_root_directory(self):
        dirname = QtGui.QFileDialog.getExistingDirectory()
        self.rootDirectoryLineEdit.setText(dirname)

    def open_log_directory(self):
        dirname = QtGui.QFileDialog.getExistingDirectory()
        self.logDirectoryLineEdit.setText(dirname)






        
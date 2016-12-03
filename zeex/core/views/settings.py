# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:47:27 2016

@author: Zeke
"""
import os
from PySide import QtGui
from core.views.uis.settings_ui import Ui_settingsDialog 
from core.utility.widgets import configureComboBox
from core.utility.collection import SettingsINI
from core.models.main import FieldsListModel 

here = os.path.dirname(__file__)

class SettingsDialog(QtGui.QDialog, Ui_settingsDialog):

    def __init__(self, filename=None):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.Config = SettingsINI(filename)
        self._settings_filename = filename

        self.configure_settings(self.Config)
        
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
            
        #Get items/set defaults.
        ROOT_DIR =        genconfig.get('ROOT_DIRECTORY',  "C:/Zeex Projects")
        LOG_DIR =         genconfig.get('LOG_DIRECTORY',   "C:/Zeex Projects/logs")
        LOG_LEVEL =       genconfig.get('LOG_LEVEL',       "Low")
        CLOUD_PROVIDER =  genconfig.get('CLOUD_PROVIDER',  "S3")
        HEADER_CASE =     inconfig.get('HEADER_CASE',      "Lower")
        HEADER_SPACE =    inconfig.get('HEADER_SPACE',     "_")
        AUTO_SORT =       inconfig.get('AUTO_SORT',        False)
        AUTO_DEDUPE =     inconfig.get('AUTO_DEDUPE',      False)
        OUTPUT_FORMAT =   outconfig.get('OUTPUT_FORMAT',   ".csv")
        FILENAME_PFX =    outconfig.get('FILENAME_PREFIX', "z_")
        CHART_FILE =      outconfig.get('CHART_FILENAME',  "")
        DB_FLAVOR =       dbconfig.get('FLAVOR',           "SQLITE")
        DB_URL =          dbconfig.get('URL',              "")
        DB_NAME =         dbconfig.get('DEFAULT_DATABASE', None)
        DB_USERNAME =     dbconfig.get('USERNAME',         None)
        DB_PASSWORD =     dbconfig.get('PASSWORD',         None)
        DB_PORT =         dbconfig.get('PORT',             None)

        DEDUPE_FIELDS =   config.getlist('FIELDS', 'DEDUPE', fallback=[])
        SORT_FIELDS   =   config.getlist('FIELDS', 'SORT',   fallback=['updatedate', 'insertdate'])
        STRING_FIELDS =   config.getlist('FIELDS', 'STRING', fallback=['address1','firstname','lastname',
                                                              'city','state','zipcode', 'fullname',
                                                              'email','homephone','cellphone'])
        INTEGER_FIELDS =  config.getlist('FIELDS', 'INTEGER',fallback=['id','users_id'])
        DATE_FIELDS   =   config.getlist('FIELDS', 'INTEGER',fallback=['insertdate','updatedate'])
        
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
        configureComboBox(self.fileFormatComboBox,    ['.xlsx', '.csv', '.txt'],         OUTPUT_FORMAT)
        configureComboBox(self.flavorComboBox,        ['SQLite', 'PostgreSQL', 'MySQL'], DB_FLAVOR)
        
        #Field Models
        self.dedupeFieldsModel = FieldsListModel(items=DEDUPE_FIELDS)
        self.sortFieldsModel   = FieldsListModel(items=SORT_FIELDS)
        self.strFieldsModel    = FieldsListModel(items=STRING_FIELDS)
        self.intFieldsModel    = FieldsListModel(items=INTEGER_FIELDS)
        self.dateFieldsModel   = FieldsListModel(items=DATE_FIELDS)
        
        self.dedupeFieldsListView.setModel(self.dedupeFieldsModel)
        self.sortFieldsColumnView.setModel(self.sortFieldsModel)
        self.strFieldsListView.setModel(   self.strFieldsModel)
        self.intFieldsListView.setModel(   self.intFieldsModel)
        self.dateFieldsListView.setModel(  self.dateFieldsModel)
        
    def save_settings(self):
        self.Config.update('GENERAL', 'ROOT_DIRECTORY', self.rootDirectoryLineEdit.text())
        self.Config.update('GENERAL', 'LOG_DIRECTORY', self.logDirectoryLineEdit.text())
        self.Config.update('GENERAL', 'LOG_LEVEL', self.rootDirectoryLineEdit.text())
        self.Config.update('GENERAL', 'CLOUD_PROVIDER', self.rootDirectoryLineEdit.text())
        self.Config.update('INPUT', 'HEADER_CASE', self.rootDirectoryLineEdit.text())
        self.Config.update('INPUT', 'HEADER_SPACE', self.rootDirectoryLineEdit.text())
        self.Config.update('INPUT', 'AUTO_SORT', self.rootDirectoryLineEdit.text())
        self.Config.update('INPUT', 'AUTO_DEDUPE', self.rootDirectoryLineEdit.text())
        self.Config.update('OUTPUT', 'OUTPUT_FORMAT', self.rootDirectoryLineEdit.text())
        
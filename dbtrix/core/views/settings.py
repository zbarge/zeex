# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:47:27 2016

@author: Zeke
"""
import os
from core.utility.uiloader import loadUiWidget   
from core.utility.widgets import configureComboBox
from core.utility.collection import SettingsINI
from core.models.main import FieldsListModel 

here = os.path.dirname(__file__)

class MainSettings(object):
    ui_path = os.path.join(here, "settings.ui").replace("\\","/")
    def __init__(self, parent=None, defaults=None):
        super(MainSettings, self).__init__()
        self.Config = (SettingsINI() if defaults is None else defaults)
        self._ui = loadUiWidget(self.ui_path, parent)
        self.configure_settings(self.Config)
    
    @property
    def ui(self):
        """The connection to the user interface. """
        return self._ui
        
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
        self.ui.rootDirectoryLineEdit.setText(      ROOT_DIR)
        self.ui.logDirectoryLineEdit.setText(       LOG_DIR)
        self.ui.fileNamePrefixLineEdit.setText(     FILENAME_PFX)
        self.ui.chartSettingsFileLineEdit.setText(  CHART_FILE)
        self.ui.urlLineEdit.setText(                DB_URL)
        self.ui.defaultDatabaseLineEdit.setText(    DB_NAME)
        self.ui.usernameLineEdit.setText(           DB_USERNAME)
        self.ui.passwordLineEdit.setText(           DB_PASSWORD)
        self.ui.portLineEdit.setText(               DB_PORT)
        
        #COMBO BOXES
        configureComboBox(self.ui.logLevelComboBox,      ['Low', 'Medium', 'High'],         LOG_LEVEL)
        configureComboBox(self.ui.cloudProviderComboBox, ['Google Drive', 'S3', 'DropBox'], CLOUD_PROVIDER)
        configureComboBox(self.ui.headerCaseComboBox,    ['lower', 'UPPER', 'Proper'],      HEADER_CASE)
        configureComboBox(self.ui.headerSpacesComboBox,  [' ', '_'],                        HEADER_SPACE)
        configureComboBox(self.ui.fileFormatComboBox,    ['.xlsx', '.csv', '.txt'],         OUTPUT_FORMAT)
        configureComboBox(self.ui.flavorComboBox,        ['SQLite', 'PostgreSQL', 'MySQL'], DB_FLAVOR)
        
        #Field Models
        self.dedupeFieldsModel = FieldsListModel(items=DEDUPE_FIELDS)
        self.sortFieldsModel   = FieldsListModel(items=SORT_FIELDS)
        self.strFieldsModel    = FieldsListModel(items=STRING_FIELDS)
        self.intFieldsModel    = FieldsListModel(items=INTEGER_FIELDS)
        self.dateFieldsModel   = FieldsListModel(items=DATE_FIELDS)
        
        self.ui.dedupeFieldsListView.setModel(self.dedupeFieldsModel)
        self.ui.sortFieldsColumnView.setModel(self.sortFieldsModel)
        self.ui.strFieldsListView.setModel(   self.strFieldsModel)
        self.ui.intFieldsListView.setModel(   self.intFieldsModel)
        self.ui.dateFieldsListView.setModel(  self.dateFieldsModel)
       
        
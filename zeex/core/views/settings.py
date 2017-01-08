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
from functools import partial
from core.compat import QtGui, QtCore
from core.ui.settings_ui import Ui_settingsDialog
from core.utility.collection import SettingsINI, DictConfig
from core.utility.widgets import configure_combo_box


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
        self.settings_ini = settings

        if isinstance(settings, str) or settings is None:
            if settings is None:
                print("Using default settings - got settings of type {}".format(type(settings)))
            self.settings_ini = SettingsINI(filename=settings)
        elif isinstance(settings, dict):
            self.settings_ini = DictConfig(dictionary=settings)
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

        if not hasattr(config, "set_safe"):
            # We'll assume get_safe exists to.
            raise NotImplementedError("Unsupported settings type: {}".format(
                                      type(config)))
        c = config
        # Get items/set defaults.
        ROOT_DIR =        c.get('GENERAL', 'root_directory',  fallback=DEFAULT_ROOT_DIR)
        LOG_DIR =         c.get('GENERAL', 'log_directory',   fallback=DEFAULT_LOG_DIR)
        LOG_LEVEL =       c.get_safe('GENERAL', 'LOG_LEVEL',       fallback="Low")
        CLOUD_PROVIDER =  c.get_safe('GENERAL', 'CLOUD_PROVIDER',  fallback="S3")
        THEME_NAME     =  c.get_safe('GENERAL', 'THEME',           fallback=DEFAULT_THEME)
        HEADER_CASE =     c.get_safe('INPUT', 'HEADER_CASE',      fallback="Lower")
        HEADER_SPACE =    c.get_safe('INPUT', 'HEADER_SPACE',     fallback="_")
        SEPARATOR =       c.get_safe('OUTPUT', 'SEPARATOR',       fallback=",")
        ENCODING =        c.get_safe('OUTPUT', 'ENCODING',        fallback="UTF_8")

        if not os.path.exists(ROOT_DIR):
            try:
                os.mkdir(ROOT_DIR)
            except OSError:
                msg = "Defaulting root and log directories because the root directory '{}' was invalid.".format(
                      ROOT_DIR)
                ROOT_DIR = DEFAULT_ROOT_DIR
                LOG_DIR = DEFAULT_LOG_DIR
                print(msg)

        #Make sure the directories exist.
        for fp in [ROOT_DIR, LOG_DIR]:
            try:
                if not os.path.exists(fp):
                    os.mkdir(fp)
            except OSError as e:
                raise OSError("Cannot initialize settings directory {} - {}".format(fp, e))
        
        #LINE EDITS
        self.rootDirectoryLineEdit.setText(ROOT_DIR)
        self.logDirectoryLineEdit.setText(LOG_DIR)
        
        #COMBO BOXES
        configure_combo_box(self.logLevelComboBox, ['Low', 'Medium', 'High'], LOG_LEVEL)
        configure_combo_box(self.cloudProviderComboBox, ['Google Drive', 'S3', 'DropBox'], CLOUD_PROVIDER)
        configure_combo_box(self.headerCaseComboBox, ['lower', 'UPPER', 'Proper'], HEADER_CASE)
        configure_combo_box(self.headerSpacesComboBox, [' ', '_'], HEADER_SPACE)
        configure_combo_box(self.separatorComboBox, DEFAULT_SEPARATORS, SEPARATOR)
        configure_combo_box(self.encodingComboBox, DEFAULT_CODECS, ENCODING)
        configure_combo_box(self.themeComboBox, DEFAULT_THEME_OPTIONS, THEME_NAME)
        self.set_theme(THEME_NAME)

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

        if write or to_path is not None:
            if to_path is None:
                to_path = self.settings_ini._filename

            self.settings_ini._filename = to_path

            self.settings_ini.save()

        self.signalSettingsSaved.emit(self.settings_ini, self.settings_ini.filename)

    def clear_settings(self):
        self.cloudProviderComboBox.clear()
        self.encodingComboBox.clear()
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






        
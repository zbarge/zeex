"""
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
import shutil
import pytest
from zeex.core.views.main import ZeexMainWindow
from zeex.core.views.settings import SettingsDialog
from tests.main import MainTestClass
from zeex.core.compat import QtCore, QtTest, QtGui
from zeex.core.ctrls.main import MainController

class TestMainWindow(MainTestClass):

    @pytest.fixture
    def window(self, qtbot) -> ZeexMainWindow:
        window = ZeexMainWindow(MainController())
        window.show()
        qtbot.addWidget(window)
        return window

    @pytest.fixture
    def settings_dialog(self, window: ZeexMainWindow):
        return window.control.dialog_settings_main

    def test_settings_dialog(self, qtbot, window:ZeexMainWindow, settings_dialog: SettingsDialog, fixtures_dir):
        window.actionGeneralSettings.trigger()
        dialog = settings_dialog
        assert dialog.isEnabled()
        qtbot.mouseClick(window.homemenu, QtCore.Qt.LeftButton)
        assert window.homemenu.isEnabled()

        settings_path = os.path.join(fixtures_dir, "main_config_test.ini")
        orig_root = dialog.settings_ini.get('GENERAL', 'ROOT_DIRECTORY')
        orig_log = dialog.settings_ini.get('GENERAL', 'LOG_DIRECTORY')
        root_dir = os.path.join(fixtures_dir, "sample_root_dir")
        log_dir = os.path.join(root_dir, "logs")

        if os.path.exists(root_dir):
            shutil.rmtree(root_dir)

        dialog.settings_ini._filename = settings_path
        dialog.rootDirectoryLineEdit.setText(root_dir)
        dialog.logDirectoryLineEdit.setText(log_dir)

        qtbot.mouseClick(dialog.btnSave, QtCore.Qt.LeftButton)

        assert dialog.settings_ini.get('GENERAL', 'ROOT_DIRECTORY').replace("\\",'/') == root_dir.replace("\\",'/')
        assert dialog.settings_ini.get('GENERAL', 'LOG_DIRECTORY').replace("\\",'/') == log_dir.replace("\\",'/')
        qtbot.mouseClick(dialog.btnReset, QtCore.Qt.LeftButton)

        assert dialog.settings_ini.get('GENERAL', 'ROOT_DIRECTORY').replace("\\",'/') == orig_root.replace("\\",'/')
        assert dialog.settings_ini.get('GENERAL', 'LOG_DIRECTORY').replace("\\",'/') == orig_log.replace("\\",'/')
        dialog.close()

    def test_new_project_dialog(self, qtbot, window: ZeexMainWindow, fixtures_dir):
        window.actionNewProject.trigger()
        dialog = window.control.dialog_new_project
        assert dialog.isEnabled()
        proj_dir = os.path.join(fixtures_dir, "project")
        if os.path.exists(proj_dir):
            shutil.rmtree(proj_dir)
        dialog.set_base_dirname(proj_dir)
        log_dir = os.path.join(proj_dir, "logs")

        dialog.settingsFileLineEdit.setText(window.control.dialog_settings_main.settings_ini.default_path)
        dialog.nameLineEdit.setText(proj_dir)

        button = dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        assert button is not None
        assert button.isVisible()

        qtbot.mouseClick(button, QtCore.Qt.LeftButton )

        assert os.path.exists(proj_dir)
        found = False
        for dirname, subdirs, files in os.walk(proj_dir):
            for f in files:
                if f.endswith('ini'):
                    found = True

        assert found, "Expected dirname {} to contain a .ini file... none exists.".format(proj_dir)
        window.close()












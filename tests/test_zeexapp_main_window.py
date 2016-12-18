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
from core.views.main import ZeexMainWindow
from core.views.settings import SettingsDialog
from tests.main import MainTestClass
from core.compat import QtCore, QtTest, QtGui


class TestMainWindow(MainTestClass):

    @pytest.fixture
    def window(self, qtbot) -> ZeexMainWindow:
        window = ZeexMainWindow()
        window.show()
        qtbot.addWidget(window)
        return window

    @pytest.fixture
    def settings_dialog(self, window):
        return window.SettingsDialog

    def test_settings_dialog(self, qtbot, window, settings_dialog: SettingsDialog, fixtures_dir):
        window.actionSettings.trigger()
        dialog = settings_dialog
        assert dialog.isEnabled()
        qtbot.mouseClick(window.homemenu, QtCore.Qt.LeftButton)
        assert window.homemenu.isEnabled()

        settings_path = os.path.join(fixtures_dir, "main_config_test.ini")
        orig_root = dialog.Config.get('GENERAL', 'ROOT_DIRECTORY')
        orig_log = dialog.Config.get('GENERAL', 'LOG_DIRECTORY')
        root_dir = os.path.join(fixtures_dir, "sample_root_dir")
        log_dir = os.path.join(root_dir, "logs")

        if os.path.exists(root_dir):
            shutil.rmtree(root_dir)

        dialog.Config._filename = settings_path
        dialog.rootDirectoryLineEdit.setText(root_dir)
        dialog.logDirectoryLineEdit.setText(log_dir)

        qtbot.mouseClick(dialog.btnSave, QtCore.Qt.LeftButton)

        assert dialog.Config.get('GENERAL', 'ROOT_DIRECTORY') == root_dir
        assert dialog.Config.get('GENERAL', 'LOG_DIRECTORY') == log_dir
        qtbot.mouseClick(dialog.btnReset, QtCore.Qt.LeftButton)

        assert dialog.Config.get('GENERAL', 'ROOT_DIRECTORY') == orig_root
        assert dialog.Config.get('GENERAL', 'LOG_DIRECTORY') == orig_log
        dialog.close()

    def test_new_project_dialog(self, qtbot, window: ZeexMainWindow, fixtures_dir):
        window.actionNew.trigger()
        dialog = window.NewProjectDialog
        assert dialog.isEnabled()
        proj_dir = os.path.join(fixtures_dir, "project")
        if os.path.exists(proj_dir):
            shutil.rmtree(proj_dir)

        log_dir = os.path.join(proj_dir, "logs")

        dialog.settingsFileLineEdit.setText(window.SettingsDialog.Config.default_path)
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

        assert found
        window.close()












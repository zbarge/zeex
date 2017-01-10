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
from zeex.core.views.settings import SettingsDialog


class ProjectSettingsDialog(SettingsDialog):
    """
    A SettingsDialog with a few items hidden or set to read-only.
    This covers the minor differences between general settings and project settings.
    """
    def __init__(self, settings_ini, project_directory=None, log_directory=None, **kwargs):
        if log_directory is None:
            log_directory = settings_ini.get('GENERAL', 'LOG_DIRECTORY')
        if project_directory is None:
            project_directory = settings_ini.get('GENERAL', 'ROOT_DIRECTORY')

        SettingsDialog.__init__(self, settings=settings_ini, **kwargs)
        self.project_directory = project_directory
        self.log_directory = log_directory

        # Adjust the box to remove irrelevant items.
        self.cloudProviderComboBox.hide()
        self.cloudProviderLabel.hide()
        self.btnLogDirectory.hide()
        self.btnRootDirectory.hide()
        self.themeComboBox.hide()
        self.themeLabel.hide()

        # Override the log/root directory options
        self.logDirectoryLineEdit.setText(self.log_directory)
        self.logDirectoryLineEdit.setReadOnly(True)
        self.rootDirectoryLineEdit.setText(self.project_directory)
        self.rootDirectoryLineEdit.setReadOnly(True)
        self.btnSetDefault.setVisible(False)
        self.sync_project_config_path()

    def sync_project_config_path(self):
        orig_path = self.settings_ini.filename
        cur_path = self.settings_ini.default_path
        cur_dir = os.path.dirname(cur_path).replace("\\", "/")
        proj_dir = self.project_directory.replace("\\", "/")
        if cur_dir != proj_dir:
            cur_path = os.path.join(proj_dir, os.path.basename(cur_path))
            self.settings_ini._default_path = cur_path
            self.settings_ini._filename = cur_path
            self.settings_ini._default_backup_path = cur_path
            self.settings_ini.save()

        if not os.path.exists(cur_path):
            shutil.copy2(orig_path, cur_path)

        self.save_settings()


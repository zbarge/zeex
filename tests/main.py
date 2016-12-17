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
import pytest
import pandas as pd
from core.compat import QtGui, QtCore
from PySide.QtTest import QTest
from core.utility.collection import SettingsINI

class MainTestClass(object):

    @pytest.fixture
    def df(self) -> pd.DataFrame:
        sample_cols = ['id', 'name', 'address', 'updated']
        sample_recs = [[1000, 'zeke', '123 street'],
                       [1001, 'larry', '688 road'],
                       [1002, 'fred', '585 lane']]
        for rec in sample_recs:
            rec.append(pd.NaT)
        return pd.DataFrame(sample_recs, columns=sample_cols)

    @pytest.fixture
    def output_dir(self) -> str:
        fp = os.path.join(os.path.dirname(__file__), "output")
        if not os.path.exists(fp):
            os.mkdir(fp)
        return fp

    @pytest.fixture
    def fixtures_dir(self) -> str:
        fp = os.path.join(os.path.dirname(__file__), "fixtures")
        if not os.path.exists(fp):
            os.mkdir(fp)
        return fp

    @pytest.fixture
    def project_root_dir(self, fixtures_dir):
        return os.path.join(fixtures_dir, "fixed_root_dir/fixed_project")

    @pytest.fixture
    def project_log_dir(self, project_root_dir):
        return os.path.join(project_root_dir, "logs")

    @pytest.fixture
    def project_settings_path(self, project_root_dir):
        return os.path.join(project_root_dir, "sample_project_config.ini")

    @pytest.fixture
    def example_file_path(self, project_root_dir):
        return os.path.join(project_root_dir, "example.csv")

    @pytest.fixture
    def project_settings_ini(self, project_settings_path, project_root_dir, project_log_dir):
        settings = SettingsINI(filename=project_settings_path)
        settings.set('GENERAL', 'ROOT_DIRECTORY', value=project_root_dir)
        settings.set('GENERAL', 'LOG_DIRECTORY', value=project_log_dir)
        settings.save()
        return settings

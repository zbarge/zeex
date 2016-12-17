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
from PySide import QtGui, QtCore
from core.utility.collection import SettingsINI





class ZeexGuiObj(object):
    def _handle_kwargs(*args, **kwargs):
        zeex_kwargs = {'zeex_settings': kwargs.pop('zeex_settings', DEFAULT_SETTINGS_PATH)}
        return (zeex_kwargs, kwargs)

    def __init__(self, *args, **kwargs):
        self._settings_path = kwargs.pop('zeex_settings', DEFAULT_SETTINGS_PATH)
        if not isinstance(self._settings_path, SettingsINI):
            self._settings_ini = SettingsINI(filename=self._settings_path)
        self._configure_defaults()

    def _configure_defaults(self):
        self._theme_options = self._settings_ini.get('GENERAL', 'theme_options', fallback=DEFAULT_THEME_OPTIONS)
        self._theme_default_path = self._settings_ini.get('GENERAL', 'theme_default_path', fallback=DEFAULT_THEME_PATH)
        self._theme_current_path = self._theme_default_path
        self._set_theme()

    def _set_theme(self, to=None):
        obj = (self if to is None else self)
        with open(self._theme_current_path, "r") as fh:
            obj.setStyleSheet(fh.read())

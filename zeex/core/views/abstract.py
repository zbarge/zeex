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

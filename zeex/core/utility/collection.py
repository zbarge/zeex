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
from configparser import ConfigParser
from ast import literal_eval as Eval

DEFAULT_CONFIG_NAME = 'default.ini'
DEFAULT_CONFIG_BACKUP_NAME = 'default_backup.ini'


def get_ini_file(dirname):
    for directory, subdirs, files in os.walk(dirname):
        for f in files:
            if f.endswith('.ini'):
                return os.path.join(directory, f)


def get_default_config_path():
    """
    Points 3 directories back to the
    zeex/configs directory.
    :return: (str)
        filepath to the default config.
    """
    f = __file__
    for i in range(0,3):
        f = os.path.dirname(f)
    f = os.path.join(f, "configs/{}".format(DEFAULT_CONFIG_NAME))
    if not os.path.exists(f):
        raise OSError("Missing default config path, please create it: {}".format(f))
    return f


def get_config_backup_path(default):
    f = os.path.join(os.path.dirname(default), DEFAULT_CONFIG_BACKUP_NAME)
    if not os.path.exists(f):
        shutil.copy2(default, f)
    return f


class BaseConfig(ConfigParser):
    """
    Credits: http://codereview.stackexchange.com/questions/2775/python-subclassing-configparser
    """

    def __init__(self, filename=None, default_path=None, default_backup_path=None):
        ConfigParser.__init__(self, allow_no_value=True)
        self._default_path = default_path
        self._default_backup_path = default_backup_path
        self._filename = filename


    @property
    def filename(self):
        return self._filename

    @property
    def default_path(self):
        return self._default_path

    @property
    def backup_path(self):
        return self._default_backup_path

    def set_safe(self, section, option, value, **kwargs):
        if self.has_section(section):
            self.set(section, option, str(value), **kwargs)
        else:
            self.add_section(section)
            self.set(section, option, str(value), **kwargs)

    def get_safe(self, section, option, **kwargs):
        try:
            option = self.get(section, option, **kwargs)
            return Eval(option)
        except (SyntaxError, ValueError) as e:
            try:
                return self[section][str(option)]
            except (KeyError, AttributeError) as e:
                pass
            return kwargs.pop('fallback', None)

    def get_path(self, section, option, **kwargs):
        return os.path.normpath(self.get_safe(section, option, **kwargs)).replace('\\', '/')

    def set_path(self, section, option, value, **kwargs):
        value = os.path.normpath(value).replace("\\", '/')
        self.set_safe(section, option, value, **kwargs)

    def save(self):
        with open(self._filename, "w") as fh:
            self.write(fh)

    def save_as(self, name, set_self=True):
        orig = self._filename
        self._filename = name
        self.save()
        if set_self is not True:
            self._filename = orig


class FileConfig(BaseConfig):
    _default_path = get_default_config_path()
    _default_backup_path = get_config_backup_path(_default_path)

    def __init__(self, filename=None):
        default = get_default_config_path()
        backup = get_config_backup_path(default)
        if filename is None:
            filename = default
        BaseConfig.__init__(self, filename=filename, default_path=default, default_backup_path=backup)

        try:
            self.read(self._filename)
        except IOError as Err:
            if Err.errno == 2:
                pass
            else:
                raise Err


class DictConfig(BaseConfig):
    """
    Convenient way to get a BaseConfig without needing a filepath.
    """
    def __init__(self, dictionary=None, filename=None, **kwargs):
        if dictionary is not None:
            self.read_dict(dictionary, **kwargs)
        self.filename = filename


class SettingsINI(FileConfig):
    def __init__(self, filename=None):
        FileConfig.__init__(self, filename=filename)

if __name__ == '__main__':
    s = SettingsINI()




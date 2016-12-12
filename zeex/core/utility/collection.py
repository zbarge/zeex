import os
import shutil
from configparser import ConfigParser
from core.compat import string_to_list
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


class _ConfParse(ConfigParser):
    """
    Credits: http://codereview.stackexchange.com/questions/2775/python-subclassing-configparser
    """

    _default_path = get_default_config_path()
    _default_backup_path = get_config_backup_path(_default_path)

    def __init__(self, filename=None):
        ConfigParser.__init__(self)
        if filename is None:
            self._filename = self._default_path
        else:
            self._filename = filename

        try:
            self.read(self._filename)
        except IOError as Err:
            if Err.errno == 2:
                pass
            else:
                raise Err

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
            return Eval(self.get(section, option, **kwargs))
        except:
            return kwargs.pop('fallback', None)

    def save(self):
        with open(self._filename, "w") as fh:
            self.write(fh)

    def save_as(self, name, set_self=True):
        orig = self._filename
        self._filename = name
        self.save()
        if set_self is not True:
            self._filename = orig




    
class SettingsINI(_ConfParse):
    def __init__(self, filename=None):
        _ConfParse.__init__(self, filename=filename)

if __name__ == '__main__':
    s = SettingsINI()




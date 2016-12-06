import os
from configparser import ConfigParser
from core.compat import string_to_list
from ast import literal_eval as Eval


def get_ini_file(dirname):
    for directory, subdirs, files in os.walk(dirname):
        for f in files:
            if f.endswith('.ini'):
                return os.path.join(directory, f)


def get_default_config_path():
    f = __file__
    for i in range(0,3):
        f = os.path.dirname(f)
    f = os.path.join(f, "configs/default.ini")
    if not os.path.exists(f):
        raise OSError("Missing default config path, please create it: {}".format(f))
    return f


class _ConfParse(ConfigParser):
    """
    Credits: http://codereview.stackexchange.com/questions/2775/python-subclassing-configparser
    """

    _default_path = get_default_config_path()

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




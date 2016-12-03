import os
from configparser import ConfigParser
from core.compat.compat import string_to_list

def get_default_config_path():
    f = __file__
    for i in range(0,3):
        f = os.path.dirname(f)
    f = os.path.join(f, "configs/default.ini")
    if not os.path.exists(f):
        raise OSError("Missing default config path, please create it: {}".format(f))
    return f
    
class SettingsINI(ConfigParser):
    
    _default_path = get_default_config_path()
    
    def __init__(self, filename=None):
        ConfigParser.__init__(self)
        if filename is None:
            filename = self._default_path
        self.read(filename)
        
    def getlist(self,*args, **kwargs):
        item = self.get(*args, **kwargs)
        return string_to_list(item)
    def drop_empty_settings(self):
        for header in self.keys():
            for key, value in self.items(section=header):
                if self.has_option(header, key):
                    print("Key {} - Option {}".format(key, value))

s = SettingsINI()
s.drop_empty_settings()

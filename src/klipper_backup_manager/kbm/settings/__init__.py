import logging

import kbm
import yaml


class SettingsFile:
    def __init__(self, name):
        self.name = name
        self.log=logging.getLogger(__name__+'.'+self.name)

    def load(self):
        with open(kbm.kbm_yaml) as file:
            self.log.debug("Opening settings file.")
            self.yamlfile = yaml.safe_load(file)
        self.profile = self.yamlfile.get(self.name)

    def pull_entry(self, entry_name):
        if not self.profile:
            self.load()
        return self.profile[entry_name] if entry_name in self.profile else None

    def update_entry_key(self, entry_name, key, new_value):
        if not self.profile:
            self.load()
        if entry_name not in self.profile:
            return None
        self.profile[entry_name][key] = new_value
        return True


# Commenting this out because I haven't had the time to properly implement it,
# and I changed the way I'm handling this part anyway.
################################################################################
#   def add_recent(self, tag, new_value, delete_old=False):
#       (self.load() if not self.profile else None)
#       if tag not in self.profile:
#           return None
#       if len(self.profile[tag]['recent']) > self.profile[tag]['maxbackups']:
#           t = self.profile[tag]['recent'][-1]
#           if os.path.isfile(t) and delete_old:
#               os.remove(t)
#               self.profile[tag]['recent'].pop(-1)
#       self.profile[tag]['recent'].insert(new_value, 0)
#       return self.profile[tag]['recent'][0]

    def write(self):
        self.yamlfile[self.name] = self.profile
        with open(kbm.kbm_yaml, "w") as file:
            self.log.debug("Writing updated settings to file.")
            yaml.safe_dump(self.profile, file)

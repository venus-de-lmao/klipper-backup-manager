import yaml
import os
import kbm
import logging
class SettingsFile:
    def __init__(self, name):
        self.name = name
        self.log=logging.getLogger('kbm.SettingsFile.'+self.name)

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

    def write(self):
        self.yamlfile[self.name] = self.profile
        with open(kbm.kbm_yaml, "w") as file:
            self.log.debug("Writing updated settings to file.")
            yaml.safe_dump(self.profile, file)

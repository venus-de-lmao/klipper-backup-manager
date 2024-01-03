import os
import yaml
log = kbm.log.getChild(__name__)

class SettingsFile:
    def __init__(self, name):
        self.name = name
        self.mode = (lambda x: 'r' if x not in ['r', 'w'] else x)(mode)
        self.new_file = new_file

    def __enter__(self):
        return self

    def __exit__(self, exctype, excinst, exctb):
            # put this in, eventually
            
    def load(self):
        with open(kbm_yaml, 'r') as file:
            log.debug("Opening settings profile '%s'", self.name)
            self.settings_profile = yaml.safe_load(file)

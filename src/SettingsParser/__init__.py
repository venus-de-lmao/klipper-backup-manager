import yaml
import KBM

log = KBM.log.getChild(__name__)

class SettingsFile:
    def __init__(self, name):
        self.name = name
    def load(self):
        with open(kbm_yaml) as file:
            log.debug("Opening settings file.")
            self.yamlfile = yaml.safe_load(file)
        self.profile = self.yamlfile.get(self.name)
    def pull_entry(self, entry_name):
        if not self.profile:
            self.load()
        return (lambda x: self.profile[entry_name] if x in self.profile.keys() else None)(entry_name)
    def update_entry_key(self, entry_name, key, new_value):
        if not self.profile:
            self.load()
        if entry not in self.profile.keys():
            return None
        self.profile[entry_name][key] = new_value
        return True
    def write(self):
        self.yamlfile[self.name] = self.profile
        with open(kbm_yaml, 'w') as file:
            log.debug('Writing updated settings to file.')
            yaml.safe_dump(self.profile, file)

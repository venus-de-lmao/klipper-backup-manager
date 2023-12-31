import os

import yaml

userhome = os.path.expanduser("~")
kbmlocal = os.path.expanduser("~/.kbmlocal")


class KBMSettings:
    def __init__(self, name):
        os.chdir(kbmlocal)
        self.name = name
        self.filename = ".kbmdefault.yaml"
        if os.path.exists("kbm.yaml"):
            self.filename = "kbm.yaml"
        with open(self.filename) as file:
            self.settings = yaml.safe_load(file)

        try:
            self.profile = self.settings["BackupManagers"][self.name]
        except KeyError:
            self.profile = self.settings["BackupManagers"]["default"]


class BackupManager:
    # I'm pretty sure I only want each instance to have access to its own settings
    def __init__(self, profile_name):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


class Archiver(BackupManager):
    def __init__(self, profile_name, archive_type):
        super().__init__(profile_name)
        self.archive_type = archive_type

    def __repr__(self):
        return f"Archiver('{self.profile_name}', '{self.archive_type}')"


class Unarchiver(BackupManager):
    def __init__(self, profile_name, archive_type):
        super().__init__(profile_name)
        self.archive_type = archive_type

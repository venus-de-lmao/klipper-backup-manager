# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel@proton.me>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#!/usr/bin/env python3
import logging
from logging.handlers import TimedRotatingFileHandler as TRFileHandler
import os
import sys

import yaml

userhome = os.path.expanduser("~")
kbmlocal = os.path.expanduser("~/.kbmlocal")
logdir = os.path.join(kbmlocal, "logs")
backupdir = os.path.join(kbmlocal, "backups")
log = logging.getLogger(__name__)
logfile = os.path.join(logdir, "kbm.log")
kbmdefault_yaml = os.path.join('.kbmdefault.yaml')
kbm_yaml = os.path.join("kbm.yaml")

class KBMSettings:
    def __init__(self, name):
        log.debug("Settings object initialized.")
        os.chdir(kbmlocal)
        self.name = name
        self.filename = kbmdefault_yaml
        if os.path.exists(kbm_yaml):
            self.filename = kbm_yaml
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


if not os.path.isdir(backupdir):
    try:
        os.makedirs(backupdir)
    except FileExistsError:
        log.critical("Something is in the way.")
        log.critical("e")
        sys.exit()
if not os.path.isdir(logdir):
    try:
        os.makedirs(logdir)
    except FileExistsError as e:
        log.critical("Something is in the way.")
        log.critical(e)
        sys.exit()

with KBMSettings("default") as s:
    logsettings = s.profile["logger"]

if logsettings["console"]["enabled"]:
    log.setLevel(logging.DEBUG)
    clog = logging.StreamHandler()
    clog.setLevel(logsettings["console"].setdefault("level", "WARNING"))
    log.addHandler(clog)
    log.debug("Console output initiated.")

if logsettings["file"]["enabled"]:
    flog = TRFileHandler(logfile, when="midnight", interval=1, backupCount=logsettings["file"].setdefault("max", 7))
    timestamped = logging.Formatter(
        fmt="%(asctime)s %(name)-8s %(levelname)-10s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    flog.setLevel(logsettings["file"].setdefault("level", "INFO"))
    flog.setFormatter(timestamped)

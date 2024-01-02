# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#


# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler as TRFileHandler

import yaml


def file_timestamp():
    return datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")

userhome = os.path.expanduser("~")
kbmlocal = os.path.join(userhome, '.kbmlocal')
logdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "logs")
backupdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "backups")
log = logging.getLogger(__name__)
logfile = os.path.join(logdir, "kbm.log")
log.setLevel(logging.DEBUG)
clog = logging.StreamHandler()
clog.setLevel(logging.WARNING)
log.addHandler(clog)
flog = TRFileHandler(logfile, when="midnight", interval=1, backupCount=7)
timestamped = logging.Formatter(fmt="%(asctime)s %(name)-8s %(levelname)-10s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
flog.setLevel(logging.INFO)
flog.setFormatter(timestamped)
log.addHandler(flog)
kbmdefault_yaml = os.path.join(os.path.expanduser("~/.kbmlocal"), ".kbmdefault.yaml")
kbm_yaml = os.path.join(os.path.expanduser("~/.kbmlocal"), "kbm.yaml")
if not os.path.exists(kbmdefault_yaml):
    sys.exit()
if not os.path.exists(kbm_yaml):
    os.copy(kbmdefault_yaml, kbm_yaml)

if not os.path.isdir(backupdir):
    try:
        os.makedirs(backupdir)
    except FileExistsError:
        log.critical("Something is in the way.", exc_info=True) # note to polish this after I merge back to the main branch
        raise

if not os.path.isdir(logdir):
    try:
        os.makedirs(logdir)
    except FileExistsError as e:
        log.critical("Something is in the way.", exc_info=True)
        raise
class SettingsParser:
    def load_settings_file(self, profile_name='default'):
        self.profile_name = profile_name
        with open(kbm_yaml, 'r') as file:
            try:
                self.settings_file = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                log.exception("Error while parsing YAML file:", exc_info=True)
                if hasattr(exc, "problem_mark"):
                    if exc.context:
                        log.exception(
                            "  parser says %s\n  %s %s\nPlease correct data and retry.",
                            str(exc.problem_mark),
                            str(exc.problem),
                            str(exc.context))
                    else:
                        log.exception(
                            "  parser says%s\n%s\n  \nPlease correct data and retry.",
                            str(exc.problem_mark), str(exc.problem))
                else:
                    log.exception("Something went wrong while parsing YAML file.", exc_info=True)
                    raise
            if self.profile_name in self.settings_file:
                return self.settings_file[self.profile_name]
            return self.settings_file['default']

    def __init__(self, profile, mode='r', new_file=None):
        self.profile = self.load_settings_file(profile)
        self.mode = (lambda x: 'r' if x not in ['r', 'w'] else x)(mode)
        self.new_file = new_file

    def push_entry(self, section, key, value):
        if section in self.profile and key in self.profile[section]:
            self.profile[section][key] = value
            self.keyupdate = None
            return True
        return None

    def pull_entry(self, requested):
        if requested in self.profile:
            return self.profile[requested]
        return None

    def update_yaml(self):
        with open(kbm_yaml, 'w') as file:
            self.settings_file[self.profile_name] = self.profile
            yaml.safe_dump(self.settings_file, file)

    def __enter__(self):
        return self

    def __exit__(self, exctype, excinst, exctb):
        log.debug("Exiting settings object.")
        log.debug("Removing old backups:")
            # put this in, eventually

pdata = SettingsParser('default').pull_entry('printer')['printer_data']
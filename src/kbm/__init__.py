# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#

# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler as TRFileHandler

import yaml

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

with open(kbm_yaml) as file:
    try:
        settings_file = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        log.exception("Error while parsing YAML file:")
        if hasattr(exc, "problem_mark"):
            if exc.context:
                log.exception(
                    "  parser says %s\n  %s %s\nPlease correct data and retry.",
                    str(exc.problem_mark),
                    str(exc.problem),
                    str(exc.context),
                )
            else:
                log.exception(
                    "  parser says%s\n%s\n  \nPlease correct data and retry.", str(exc.problem_mark), str(exc.problem)
                )

        else:
            log.exception("Something went wrong while parsing YAML file.")
            sys.exit()
    try:
        settings_profile = settings_file["BackupManagers"]["user1"]
    except KeyError:
        settings_profile = settings_file["BackupManagers"]["default"]
    del settings_file

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

class SettingsParser:
    def __init__(self, request):
        self.requested = request
        if self.requested == "all":
            self.entry = settings_profile
        try:
            self.entry = settings_profile.get(self.requested)
        except KeyError:
            self.entry = None

    def __enter__(self):
        log.debug("Entering KBMSettings object.")
        log.debug("Section '%s' requested.", self.requested)
        return self.entry

    def __exit__(self, exctype, excinst, exctb):
        log.debug("Exiting KBMSettings object.")
        log.debug("Execution type: %s", exctype)
        log.debug("Execution value: %s", excinst)
        log.debug("Traceback: %s", exctb)



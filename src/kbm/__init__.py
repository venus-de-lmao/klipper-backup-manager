# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler as TRFileHandler

import SettingsParser

settings = SettingsParser.SettingsFile("default")
settings.load()


def file_timestamp():
    return datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")


userhome = os.path.expanduser("~")
kbmlocal = os.path.join(userhome, ".kbmlocal")
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
        log.critical("Something is in the way.", exc_info=True)
        raise

if not os.path.isdir(logdir):
    try:
        os.makedirs(logdir)
    except FileExistsError:
        log.critical("Something is in the way.", exc_info=True)
        raise

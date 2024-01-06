# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

def file_timestamp():
    return datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")

scripthome = Path(os.path.realpath(__file__)).parent.resolve()
userhome = os.path.expanduser("~")
kbmlocal = os.path.join(userhome, ".kbmlocal")
logdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "logs")
backupdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "backups")
kbmdefault_yaml = os.path.join(scripthome, ".kbmdefault.yaml")
kbm_yaml = os.path.join(os.path.expanduser("~/.kbmlocal"), "kbm.yaml")
log = logging.getLogger(__name__)
if not os.path.exists(kbmdefault_yaml):
    log.critical('Failed to find %s', kbmdefault_yaml)
    raise FileNotFoundError
if not os.path.exists(kbm_yaml):
    shutil.copy(kbmdefault_yaml, kbmlocal)

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


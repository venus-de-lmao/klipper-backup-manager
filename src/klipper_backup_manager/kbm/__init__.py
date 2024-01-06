# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
import sys
import yaml

def file_timestamp():
    return datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")

userhome = os.path.expanduser("~")
kbmlocal = os.path.join(userhome, ".kbmlocal")
logdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "logs")
backupdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "backups")
kbmdefault_yaml = os.path.join(userhome, ".kbmdefault.yaml")
if not os.path.isfile(kbmdefault_yaml):
    with open(kbmdefault_yaml, 'w') as file:
        yamlsettings = {
            'default':{
                    'printer':{ 
                    'name': 'Ender 3',
                    'printer_data': '~/printer_data'
                    },
                'config': {
                    'location': 'config',
                    'recent': [],
                    'maxbackups': 5
                    },
                'database':{
                    'location': 'database', 
                    'recent': [], 
                    'maxbackups': 5
                    }, 
                'gcodes': {
                    'location': 'gcodes',
                    'recent': [], 
                    'maxbackups': 5
                    }, 
                'remote': {
                    'enabled': False, 
                    'handler': 'rclone', 
                    'rclone':'gdrive', 
                    'path': '.kbmremote'}}}
        yaml.safe_dump(yamlsettings, file)

kbm_yaml = os.path.join(os.path.expanduser("~/.kbmlocal"), "kbm.yaml")
log = logging.getLogger(__name__)
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


# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from shutil import copy

import yaml
from tqdm import tqdm

# To do:
# Rewrite command-line interface w/ option groups
# Reimplement logging and tqdm progress bars.
# Write restore function.
# Look into remote upload options besides rclone.

kbmlocal = Path.home().joinpath('.kbmlocal')
backup_dir = kbmlocal.joinpath('backups')
logdir = kbmlocal.joinpath('logs')
kbmyaml = kbmlocal.joinpath('kbm.yaml')
def directory_files(target):
    top_dir = Path(target)
    outlist = []
    for dirpath, dirs, files in os.walk(top_dir):
        outlist += [str(Path(dirpath).joinpath(f)) for f in files]
    return sorted(outlist)
def directory_size(target):
    file_size = 0
    for f in directory_files(target):
        file_size += f.stat().st_size
    return file_size

if not backup_dir.exists():
    backup_dir.mkdir(parents=True)

if not logdir.exists():
    logdir.mkdir(parents=True)

class Settings:
    def def_settings(self):
        return {
            'printer_data': '~/printer_data',
            'configs': ['config','database'],
            'max_backups': 5,
            'mostrecent': {
                'config': None,
                'gcode': None
            },
            'extras': {
                'kiauh': {
                    'location': '~/kiauh',
                    'git_repo': 'https://github.com/dw-0/kiauh.git'
                    },
                'kamp': {
                    'location': '~/Klipper-Adaptive-Meshing-Purging',
                    'git_repo': 'https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging.git'
                }
            }
        }
    def __init__(self):
        self.profile = self.def_settings() # start with default settings
        if not kbmyaml.exists(): # dump the default profile into a file
            with open(kbmyaml, 'w') as f:
                yaml.safe_dump(self.profile, f)
    def get(self, entry_name, value=None):
        return self.profile.get(entry_name, value)
    def write(self):
        with open(kbmyaml, 'w') as file:
            yaml.safe_dump(self.profile, file)
    def __enter__(self):
        with open(kbmyaml) as file:
            self.profile = yaml.safe_load(file)
        return self
    def __exit__(self, exc_type, exc_value, exc_traceback):
        del self.profile

def arc_cleanup(files: list, maximum: int):
    if len(files) <= maximum:
        return None
    for f in files[maximum::]:
        os.remove(f)

def backup(gcode):
    file_tag = "config" if not gcode else "gcode"
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M")
    backup_filename = f"{file_tag}_backup_{timestamp}.tar.xz"
    backup_file_path = Path(kbmlocal.joinpath(backup_filename))
    with Settings() as cfg:
        maxbackups = cfg.get("max_backups", 5)
        configs = cfg.get("configs", None)
        extras = cfg.get("extras", None)
        printer_data = Path(cfg.get("printer_data")).expanduser()
        pdata_stem = Path(printer_data.stem)
    tgt = [pdata_stem.joinpath(f) for f in configs] if not gcode\
        else [pdata_stem.joinpath("gcodes")]
    os.chdir(printer_data.parent)
    for t in tgt:
        print(f"Backing up: {t}")
        with (tqdm(total=directory_size(t), unit="B", unit_scale=True, unit_divisor=1024) as pbar,
        tarfile.open(backup_file_path, 'w:xz') as tar):
            for f in directory_files(t):
                tqdm.write(f)
                tar.add(f)
                pbar.update(f.stat().st_size)
    cbackups = sorted(backup_dir.glob("config_backup_*.tar*"))
    gbackups = sorted(backup_dir.glob("gcode_backups."))
    arc_cleanup(cbackups, maxbackups)
    arc_cleanup(gbackups, maxbackups)
    with Settings() as cfg:
        cfg.profile["mostrecent"][file_tag].update(backup_filename)
        cfg.write()

def restore(gcode):
    with Settings() as cfg:
        archive_path = backup_dir.joinpath(
            cfg["mostrecent"][("gcode" if gcode else "config")]

        )
        pdata = Path(cfg.get("printer_data"))
    os.chdir(pdata.parent)
    print(f"Extracting: {archive_path}")
    with (
        tqdm(
            total=archive_path.stat().st_size,
            unit="B", unit_scale=True, unit_divisor=1024
        ) as pbar,
        tarfile.open(archive_path, 'r') as tar):
            restore_kamp = False
            for f in tar.members(filter="data"):
                if "KAMP_Settings.cfg" in f.name:
                    restore_kamp = True
                tqdm.write(f.name)
                tar.extract(f)
                pbar.update(f.size)
    if restore_kamp:
        restore_kamp()

# KIAUH and KAMP restores are hardcoded
# because they have specific installation steps
def restore_kiauh():
    os.chdir(Path.home())
    with Settings() as cfg:
        k_repo = cfg.profile["extras"]["kiauh"]["git_repo"]
        pdata = Path(cfg.get("printer_data"))
    gitclone = subprocess.run(["git", "clone", k_repo], check=True)
    if gitclone.returncode:
        sys.exit(gitclone.returncode)
    i = input("Run KIAUH now?").lower()
    if i.startswith("y"):
        kiauh_cmd = str(Path.home().joinpath("kiauh", "kiauh.sh"))
        do_kiauh = subprocess.run([kiauh_cmd], check=True)

def restore_kamp():
    os.chdir(Path.home())
    with Settings() as cfg:
        k_repo = cfg.profile["extras"]["kamp"]["git_repo"]
        pdata = Path(cfg.get("printer_data"))
    gitclone = subprocess.run(["git", "clone", k_repo], check=True)
    if gitclone.returncode:
        sys.exit(gitclone.returncode)
    ln_dest = pdata.joinpath("config", "KAMP")
    kampdir = Path("Klipper-Adaptive-Meshing-Purging")
    os.symlink(kampdir.joinpath("Configuration"), ln_dest, target_is_directory=True)
    # Assuming you have previously installed KAMP, this just restores the symlink 
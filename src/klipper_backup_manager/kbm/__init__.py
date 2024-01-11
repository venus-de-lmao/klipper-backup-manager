# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path

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
        outlist += [Path(dirpath).joinpath(f) for f in files]
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
    # Here we define the default settings YAML that will be dumped
    # into a file the first time KBM is run.
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

def backup(mode):
    mode = mode.lower()[0]
    file_tag = "config" if mode=="c" else "gcode"
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"{file_tag}_backup_{timestamp}.tar.xz"
    backup_file_path = Path(backup_dir.joinpath(backup_filename))
    with Settings() as cfg:
        maxbackups = cfg.get("max_backups", 5)
        configs = cfg.get("configs", None)
        printer_data = Path(cfg.get("printer_data")).expanduser()
        pdata_stem = Path(printer_data.stem)
    tgt = pdata_stem.joinpath("config") if mode=="c"\
        else pdata_stem.joinpath("gcodes")
    os.chdir(printer_data.parent)
    print(f"Backing up: {tgt}")
    with (tqdm(total=directory_size(tgt), unit="B", unit_scale=True, unit_divisor=1024) as pbar,
    tarfile.open(backup_file_path, 'w:xz') as tar):
        for f in directory_files(tgt):
            tqdm.write(str(f))
            tar.add(f)
            pbar.update(f.stat().st_size)
        if mode=="c":
            db_dir = pdata_stem.joinpath("database")
            db_size = directory_size(db_dir)
            db_files = directory_files(db_dir)
            pbar.reset(total=db_size)
            pbar.write(f"Backing up: {db_dir}")
            for f in directory_files(pdata_stem.joinpath("database")):
                tqdm.write(str(f))
                tar.add(f)
                pbar.update(f.stat().st_size)

    cbackups = sorted(backup_dir.glob("config_backup_*.tar.*"))
    gbackups = sorted(backup_dir.glob("gcode_backup_*.tar.*"))
    arc_cleanup(cbackups, maxbackups)
    arc_cleanup(gbackups, maxbackups)
    with Settings() as cfg:
        cfg.profile["mostrecent"][file_tag] = backup_filename
        cfg.write()

def restore(config, gcode):
    tag = "config" if config else "gcode"
    with Settings() as cfg:
        archive_path = backup_dir.joinpath(
            cfg.profile["mostrecent"][tag]
        )
        pdata = Path(cfg.get("printer_data")).expanduser()
    print(pdata)
    os.chdir(pdata.parent)
    t_size = 0
    with tarfile.open(archive_path, "r") as tar:
        for member in tar.getmembers():
            t_size = (t_size+member.size if member.isfile() else t_size)
    print(t_size)
    print(f"Extracting: {archive_path}")
    with (
        tqdm(
            total=t_size,
            unit="B", unit_scale=True, unit_divisor=1024
        ) as pbar,
        tarfile.open(archive_path, 'r') as tar):
            restore_kamp = False
            for f in tar.getmembers():
                # check to see if user has backed up a KAMP cfg file
                # and set a flag to reinstall KAMP
                if "KAMP_Settings.cfg" in f.name:
                    restore_kamp = True
                tqdm.write(f.name)
                pbar.update(f.size)
                tar.extract(f, pdata.parent, filter="data")
    if restore_kamp:
        do_restore_kamp()

# KIAUH and KAMP restores are hardcoded
# because they have specific installation steps
def do_restore_kiauh():
    # Prompt user to reinstall KIAUH. Default is no.
    os.chdir(Path.home())
    with Settings() as cfg:
        if "extras" not in cfg.profile:
            return False
        extras = cfg.get("extras")
        if "kiauh" not in extras:
            return False
        kdir = Path(extras["kiauh"].get("location")).resolve()
        k_repo = extras["kiauh"].get("git_repo")
    if not Path(kdir).exists():
        # Check to see if KIAUH is already installed, and install if not.
        print("KIAUH not detected. Install now?")
        if not input("Install Klipper Install And Update Helper? [yN]: ").lower().startswith("y"):
            return False
    gitclone = subprocess.run(["git", "clone", k_repo], check=True)
    if gitclone.returncode:
        sys.exit(gitclone.returncode)
    i = input("Run KIAUH now? [Yn]: ").lower()
    if i.startswith("y"):
        kiauh_cmd = str(Path.home().joinpath("kiauh", "kiauh.sh"))
        do_kiauh = subprocess.run([kiauh_cmd], check=True)
        if do_kiauh.returncode:
            sys.exit(do_kiauh.returncode)
    return True

def do_restore_kamp():
    # Prompt user to reinstall KAMP; default is yes.
    if input("Reinstall Klipper-Adaptive-Meshing-Purging? [Yn]").lower().startswith("n"):
        return None
    os.chdir(Path.home())
    with Settings() as cfg:
        k_repo = cfg.profile["extras"]["kamp"]["git_repo"]
        pdata = Path(cfg.get("printer_data"))
        kampdir = Path(cfg.profile["extras"]["kamp"]["location"]).resolve().stem
        full_path_kampdir = Path(kampdir).absolute()
    if full_path_kampdir.exists():
        print("KAMP directory {} already exists.".format(full_path_kampdir))
        sys.exit()
    gitclone = subprocess.run(["git", "clone", k_repo], check=True)
    if gitclone.returncode:
        sys.exit(gitclone.returncode)
    ln_dest = pdata.resolve().joinpath("config", "KAMP")
    os.symlink(Path(kampdir).joinpath("Configuration"), ln_dest, target_is_directory=True)
    # Assuming user has previously installed KAMP, this just restores the symlink
    # All of the KAMP settings are in the printer_data/config directory, so we don't
    # want to overwrite those with the default installation


# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import pathlib
import sys
import tarfile
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import kbm
import kbm.config as conf

# To do:
# Look into remote upload options besides rclone.

def friendly_size(num):
    suffix = "B"
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            s = unit + suffix
            n = f"{num:3.1f}"
            return f"{n : >8} {s : >3}"
        num /= 1024.0
    s = "YiB"
    return f"{num:0.1f : <}"+f"{s : >}"

def directory_files(target):
    top_dir = Path(target)
    outlist = []
    outsize = 0
    exc_suffixes = (".bkp", ".bak", ".tmp", ".log")
    for dirpath, _, files in os.walk(top_dir):
        for f in files:
            outpath = Path(Path(dirpath).joinpath(f))
            if (not outpath.is_symlink()) and (outpath.suffix not in exc_suffixes):
                outlist.append(outpath)
                outsize += outpath.stat().st_size
    return (sorted(outlist), outsize)

if not conf.backup_dir.exists():
    conf.backup_dir.mkdir(parents=True)

if not conf.logdir.exists():
    conf.logdir.mkdir(parents=True)

def cleanup(files: list, maximum: int):
    if len(files) <= maximum:
        return None
    for f in files[maximum::]:
        os.remove(f)

def most_recent(files: list) -> os.PathLike:
    for f in sorted(files, reverse=True):
        p = (f if isinstance(f, pathlib.PurePath) else Path(f))
        if p.exists():
            return p

def do_archive(tag: str):
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"{tag}_backup_{timestamp}.tar.xz"
    backup_file_path = Path(conf.backup_dir.joinpath(backup_filename))
    with conf.Settings() as cfg:
        maxbackups = cfg.get("max_backups", 5)
        printer_data = Path(cfg.get("printer_data")).expanduser()
        pdata_stem = Path(printer_data.stem)
    if tag == "config":
        tgt = pdata_stem.joinpath("config")
    elif tag == "gcode":
        tgt = pdata_stem.joinpath("gcodes")
    elif tag == "database":
        tgt = pdata_stem.joinpath("database")
    else:
        print("This code should never execute!")
        sys.exit(1)
    os.chdir(printer_data.parent)
    dfiles = directory_files(tgt)
    tgt_files = dfiles[0]
    tgt_size = dfiles[1]
    if not tgt_files: # this should prevent accidentally creating empty tarballs
        print(f"No {tag} files to back up!")
        return None
    print(f"Backing up {tag} files to: \x1b[33m{backup_file_path}\x1b[39m")
    with (tqdm(total=tgt_size, unit="B", unit_scale=True, unit_divisor=1024) as pbar,
    tarfile.open(backup_file_path, 'w:xz') as tar):
        for f in tgt_files:
            tqdm.write(str(f))
            tar.add(f)
            pbar.update(f.stat().st_size)

    backups = sorted(conf.backup_dir.glob(f"{tag}_backup_*.tar.*z"), reverse=True)
    cleanup(backups, maxbackups)

def do_unarchive(tag: str):
    with conf.Settings() as cfg:
        pdata = Path(cfg.get("printer_data")).expanduser()
        pdata_stem = Path(pdata).stem
    backups = sorted(conf.backup_dir.glob(f"{tag}_backup_*.tar.*"), reverse=True)
    archive_path = most_recent(backups)
    os.chdir(pdata.parent)
    t_size = 0
    with tarfile.open(archive_path, "r") as tar:
        for member in tar.getmembers():
            t_size = (t_size+member.size if member.isfile() else t_size)
    print(f"Extracting: \x1b[33;1m{archive_path}\x1b[39;22m")
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
        kbm.do_restore_kamp()
    # Check to see if fluidd-config is installed and restore the symlink
    # to fluidd.cfg
    if tag == "config":
        fluidd_cfg = Path(Path.home().joinpath("fluidd-config", "fluidd.cfg"))
        if fluidd_cfg.is_file() and not Path(pdata_stem).joinpath("config", "fluidd.cfg").exists():
            os.symlink(fluidd_cfg, Path(pdata_stem).joinpath("config", "fluidd.cfg"))

def do_list(tag: str):
    archives = [f for f in conf.backup_dir.glob(f"{tag}*") if f.is_file()]
    if not archives:
        return None
    archives.sort(reverse=True)
    total_size = 0
    num_archives = len(archives)
    count = 1
    for a in archives:
        a_size = friendly_size(a.stat().st_size)
        total_size += a.stat().st_size
        print(f"\x1b[1;97m{count}: \x1b[33;1m{a.name : <}\x1b[97;22m {a_size : >16}\x1b[39m")
        count += 1
    
    print(f"Total \x1b[33;1m{tag}\x1b[39;22m backups: "
    f"\x1b[1;97m{num_archives : <}\x1b[22;39m", "files" if num_archives > 1 else "file",
    f"\x1b[97m{friendly_size(total_size) : >}\x1b[0m")

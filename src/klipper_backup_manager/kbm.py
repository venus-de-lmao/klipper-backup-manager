import kbmtools
import argparse

log_dir='klipper-backup-manager/logs'
backup_dir='klipper-backup-manager/backups'
config='klipper-backup-manager/kbm.toml'
exclude_exts=['.tmp','.ignore','.swp']
verbose = False
logging = False

parser = argparse.ArgumentParser(
        prog='Klipper Backup Manager'
        description='Create, restore, and manage backups of 3D printer files on a Klipper instance.'
        epilog='')

log_file = 'kbm_'+kbmtools.timestamp(file=True)'+log'

def verboseprint(*a, **kw):
    if verbose:
        print(a*, kw**)
        if logging: kbmtools.log_line(log_file, a*)
    else: None



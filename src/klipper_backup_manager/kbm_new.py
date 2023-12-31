import yaml
import os
import sys
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler as fh
from datetime import datetime

bold = '\x1b[1m'
unbold = '\x1b[22m'

def load_settings():
    try:
        with open('kbm.yaml', 'r') as file:
            result = yaml.safe_load(file)
    except FileNotFoundError:
        with open('.kbmdefault.yaml', 'r') as file:
            result = yaml.safe_load(file)
    return result

def get_kbm_profile(profile_name='default'):
    global kbm_settings
    kbm_settings = load_settings()
    settings_profile=kbm_settings['BackupManagers'][profile_name]
    return settings_profile

# This part is really tedious
kbm_profile = get_kbm_profile()
kbmlocal = kbm_profile.setdefault('kbmlocal', '~/.kbmlocal')
homedir = kbm_profile.setdefault('homedir', '~')
backupdir = kbm_profile.setdefault('backupdir', 'backups')
logdir = kbm_profile['logger']['file'].setdefault('logdir', 'logs')
logfile = os.path.join(kbmlocal, logdir, 'kbm.log')
kbmlocal = os.path.expanduser(kbmlocal)
homedir = os.path.expanduser(homedir)
log = logging.getLogger(__name__)
if kbm_profile['logger']['console']['enabled']:
    clog = logging.StreamHandler()
    log.addHandler(clog)
if kbm_profile['logger']['file']['enabled']:
    flog = fh(logfile,
              when='midnight',
              interval=1,
              backupCount=kbm_profile['logger']['file'].setdefault('max', 7),
              delay=True)
    flog.setLevel(kbm_profile
    timefmt = '%Y-%m-%d %H:%M:%S'
    flog.setFormatter(fmt='%(asctime)s - %(levelname)-8s - %(name)-12s %(message)s', datefmt=timefmt)
    log.addHandler(flog)


class BackupManager:
    # I'm pretty sure I only want each instance to have access to its own settings
    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.config = get_kbm_profile(self.profile_name)
        self.homedir = os.path.expanduser(self.homedir)
        self.kbmlocal = os.path.expanduser(self.kbmlocal)

    def __enter__(self):
        print("Enter method called.")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('Exit method called')

    def __repr__(self):
        result = 'BackupManager(\'%s\')' % self.profile_name
        return result

    def __str__(self):
        result = 'BackupManager object with profile %s' % self.profile_name
        return result


class Archiver(BackupManager):
    def __init__(self, profile_name, archive_type):
        super().__init__(profile_name)
        self.archive_type = archive_type
    def __repr__(self):
        result = 'Archiver(\'%s\', \'%s\')' %(self.profile_name, self.archive_type)
        return result
    def __str__(self):
        result = 'BackupManager object of type Archiver with '\
                'profile %s, archive type %s'\
                % (self.profile_name, self.archive_type)
        return result

class Unarchiver(BackupManager):
    def __init__(self, profile_name, archive_type):
        super().__init__(profile_name)
        self.archive_type = archive_type
    def __repr__(self):
        result = 'Unarchiver(\'%s\', \'%s\')'\
                % (self.profile_name, self.archive_type)
        return result
    def __str__(self):
        result = 'BackupManager object of type Unarchiver with '\
                'profile %s, archive type %s'\
                % (self.profile_name, self.archive_type)
        return result


if __name__ == '__main__':
    pass

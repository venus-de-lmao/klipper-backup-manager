import yaml
import os
import sys
import logging
import logging.config
import click
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
kbmlocal = os.path.expanduser(kbmlocal)
homedir = os.path.expanduser(homedir)
logdir = os.path.join(kbmlocal, logdir)
backupdir = os.path.join(kbmlocal, backupdir)
kbm_profile['logger']['file']['logdir'] = logdir
kbm_profile['backupdir'] = backupdir
kbm_profile['homedir'] = homedir
kbm_profile['kbmlocal'] = kbmlocal
kbm_settings['BackupManagers']['default'] = kbm_profile
print(kbmlocal, logdir, backupdir)
print(kbm_profile)
print(kbm_settings)
logfile = os.path.join(logdir, 'kbm.log')
log = logging.getLogger(__name__)
if kbm_profile['logger']['console']['enabled']:
    clog = logging.StreamHandler()
    clog.setLevel(kbm_profile['logger']['console'].setdefault('level', 'WARNING'))
    log.addHandler(clog)
if kbm_profile['logger']['file']['enabled']:
    print(logfile)
    flog = fh(logfile,
              when='midnight',
              interval=1,
              backupCount=kbm_profile['logger']['file'].setdefault('max', 7))
    timestamped = logging.Formatter(fmt='%(asctime)s - %(levelname)-8s - %(name)-12s %(message)s',\
            datefmt='%Y-%m-%d %H:%M:%S')
    flog.setLevel(kbm_profile['logger']['file'].setdefault('level', 'INFO'))
    flog.setFormatter(timestamped)
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
    if not os.path.isdir(backupdir):
        try:
            os.makedirs(backupdir)
        except FileExistsError as e:
            log.critical('Something is in the way.')
            log.critical('e')
            sys.exit()
    if not os.path.isdir(logdir):
        try:
            os.makedirs(logdir)
        except FileExistsError as e:
            log.critical('Something is in the way.')
            log.critical(e)
            sys.exit()

    log.debug('Debug level message.')
    log.info('Info level message.')
    log.warning('Warning level message.')
    log.error('Error level message.')
    log.critical('Critical level message.')

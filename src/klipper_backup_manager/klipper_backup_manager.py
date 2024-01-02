#!/usr/bin/env python3


def main(**kwargs):
    """Klipper Backup Manager"""

    with SettingsParser('default') as s:
        print(s.pull_entry('gcodes'))

if __name__ == "__main__":
    main(prog_name='klipper_backup_manager')
    backup()
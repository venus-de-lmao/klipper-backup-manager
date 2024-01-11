# Klipper Backup Manager

[![PyPI - Version](https://img.shields.io/pypi/v/klipper-backup-manager.svg)](https://pypi.org/project/klipper-backup-manager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/klipper-backup-manager.svg)](https://pypi.org/project/klipper-backup-manager)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation
It's now up on PyPI!

```console
pip install klipper-backup-manager 
```

## License

`klipper-backup-manager` is distributed under the terms of the [GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html) license.

## Use

The interface is simple:
```console
Usage: klipper_backup_manager.py [OPTIONS]

Archive options: [exactly 1 required]
  Specify whether to back up or restore files.
  -b, --backup   Backs up your selected target.
  -r, --restore  Restores your selected target.

Target options: [exactly 1 required]
  Specify which files to back up or restore.
  -c, --config   Backs up Klipper configuration files.
  -g, --gcode    Backs up gcode files.

Other options:
  --help         Show this message and exit.```

Settings are controlled by the **kbm.yaml** file in ~/.kbmlocal which the app will automatically create with default settings the first time you run it. Please let me know via github if you have any issues.

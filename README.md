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

## How to Use

The interface is simple:
`kbm-tool backup TARGET` - valid targets are 'gcodes', 'config', and 'database'.
`kbm-tool restore` gives you a list of saved backups to restore from.
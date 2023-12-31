#!/usr/bin/env python3
import kbm_utils
from kbm_utils import SettingsParser
from kbm_utils import log

bold = "\x1b[1m"
unbold = "\x1b[22m"

if __name__ == "__main__":
    with SettingsParser("klipper") as f:
        print(f)
        kbm_utils.log.warning("WARNING!")
        log.warning("namespace test on logger.")

#!/usr/bin/env python3
import kbm_utils
from kbm_utils import KBMSettings

bold = "\x1b[1m"
unbold = "\x1b[22m"

if __name__ == "__main__":
    with KBMSettings('default') as f:
        print(f)

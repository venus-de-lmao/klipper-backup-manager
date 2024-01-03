import sys
import os
import tarfile
from pathlib import Path
import kbm

log = kbm.log.getChild(__name__)

pdata = os.path.expanduser(kbm.pdata)
phome = Path(pdata).parent.absolute()
print('iunno man i just work here')
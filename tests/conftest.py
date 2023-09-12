import sys
from typing import List

collect_ignore: List[str] = []

if sys.version_info < (3, 11):
    # ExceptionGroup is only available in Python 3.11+
    collect_ignore.append("test_multierror.py")

import sys

collect_ignore = []

if sys.version_info < (3, 11):
    # ExceptionGroup is only available in Python 3.11+
    collect_ignore.append("test_multierror.py")

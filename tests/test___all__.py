from freezeyt import __all__ as all_names
import freezeyt

def test_all_names():
    """Test that all names in freezeyt.__all__ are available"""
    for name in all_names:
        assert hasattr(freezeyt, name)

def test_import_star():
    """Ensure import * is successful"""
    exec('from freezeyt import *')

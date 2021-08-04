import pytest

from freezeyt.util import import_variable_from_module


def test_basic():
    sin = import_variable_from_module("math:sin")
    assert sin.__name__ == 'sin'


def test_default_variable():
    cos = import_variable_from_module("math", default_variable_name='cos')
    assert cos.__name__ == 'cos'


def test_overridden_default_variable():
    sin = import_variable_from_module("math:sin", default_variable_name='cos')
    assert sin.__name__ == 'sin'


def test_dotted_module():
    urlparse = import_variable_from_module("urllib.parse:urlparse")
    assert urlparse.__name__ == 'urlparse'


def test_dotted_variable():
    joinpath = import_variable_from_module("pathlib:Path.joinpath")
    assert joinpath.__name__ == 'joinpath'


def test_missing_variable():
    with pytest.raises(ValueError):
        import_variable_from_module("math:")


def test_missing_module():
    with pytest.raises(ValueError):
        import_variable_from_module(":sin")


def test_missing_variable_with_default_variable():
    """ValueError of empty module.
    Error is raised by import_variable_from_module.
    """
    with pytest.raises(ValueError):
        import_variable_from_module("math:", default_variable_name='cos')


def test_empty():
    with pytest.raises(ValueError):
        import_variable_from_module("")


def test_empty_with_default_variable():
    """ValueError of empty module.
    Error is raised by importlib.import_module.
    """
    with pytest.raises(ValueError):
        import_variable_from_module("", default_variable_name='cos')


def test_empty_with_default_module():
    """ValueError of empty module.
    Error is raised by import_variable_from_module.
    """
    with pytest.raises(ValueError):
        import_variable_from_module("", default_module_name='math')


def test_missing_module_with_default_module():
    """ValueError of empty module.
    Error is raised by import_variable_from_module.
    """
    with pytest.raises(ValueError):
        import_variable_from_module(":cos", default_module_name='math')


def test_overridden_default_module():
    joinpath = import_variable_from_module(
        "pathlib:Path.joinpath", default_module_name='os'
    )
    assert joinpath.__name__ == 'joinpath'


def test_default_module():
    joinpath = import_variable_from_module(
        "Path.joinpath", default_module_name='pathlib'
    )
    assert joinpath.__name__ == 'joinpath'


def test_only_module():
    with pytest.raises(ValueError):
        import_variable_from_module("math")

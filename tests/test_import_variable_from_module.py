from typing import Dict, Tuple, Any

import pytest

from freezeyt.util import import_variable_from_module

INPUT_DATA: Dict[str, Tuple[str, Dict[str, Any], str]] = {
    'basic': ("math:sin", {}, "sin"),
    'dotted_module': ("urllib.parse:urlparse", {}, "urlparse"),
    'dotted_variable': ("pathlib:Path.joinpath", {}, "joinpath"),
    'default_variable': ("math", {"default_variable_name": 'cos'}, "cos"),
    'default_module': (
        "Path.joinpath", {"default_module_name": 'pathlib'}, "joinpath"
    ),
    'overridden_default_variable': (
        "math:sin", {"default_variable_name": 'cos'}, "sin"
    ),
    'overridden_default_module': (
        "pathlib:Path.joinpath", {"default_module_name": 'os'}, "joinpath"
    ),
}

@pytest.mark.parametrize('testname', INPUT_DATA)
def test_valid_data(testname):
    name, kwargs, expected = INPUT_DATA[testname]
    imported = import_variable_from_module(name, **kwargs)
    assert imported.__name__ == expected


INPUT_ERROR_DATA: Dict[str, Tuple[str, Dict[str, Any], str]] = {
    'empty_name': ("", {}, "Missing variable name: ''"),

    'empty_name_with_default_variable':
        ("", {'default_variable_name': 'cos'}, "Missing module name: ''"),

    'empty_name_with_default_module':
        ("", {'default_module_name': 'math'}, "Missing variable name: ''"),

    'empty_name_with_both_default':
        (
            "",
            {
                'default_module_name': 'math',
                'default_variable_name': 'cos'
            },
            "Both default values can not be used simultaneously"
        ),

    'missing_variable': ("math:", {}, "Missing variable name: 'math:'"),

    'missing_module': (":sin", {}, "Missing module name: ':sin'"),

    'only_module': ("math", {}, "Missing variable name: 'math'"),

    'missing_variable_with_default_variable':
        (
            "math:",
            {'default_variable_name': 'cos'},
            "Missing variable name: 'math:'"
        ),

    'missing_module_with_default_module':
        (
            ":cos",
            {'default_module_name': 'math'},
            "Missing module name: ':cos'"
        ),

    'inserted_both_defaults':
        (
            "math",
            {
                'default_module_name': 'math',
                'default_variable_name': 'cos'
            },
            "Both default values can not be used simultaneously"
        ),

    'inserted_both_defaults_with_sep':
        (
            "math:",
            {
                'default_module_name': 'math',
                'default_variable_name': 'cos'
            },
            "Missing variable name: 'math:'"
        ),
}

@pytest.mark.parametrize('testname', INPUT_ERROR_DATA)
def test_errors(testname):
    name, kwargs, error_message = INPUT_ERROR_DATA[testname]
    with pytest.raises(ValueError) as excinfo:
        import_variable_from_module(name, **kwargs)

    assert  excinfo.value.args[0] == error_message

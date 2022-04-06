# This tests that MultiError is usable as an ExceptionGroup
# with the `except*` statement in Python 3.11+.
#
# The tests are skipped on lower versions.

from testutil import context_for_test

from freezeyt import freeze, UnexpectedStatus


def test_except_star():
    with context_for_test('app_various_errors') as module:
        app = module.app
        config = {
            'output': {'type': 'dict'},
        }

        try:
            freeze(app, config)
        except* TypeError as type_errors:
            assert len(type_errors.exceptions) == 2
        except* UnexpectedStatus as status_errors:
            assert len(status_errors.exceptions) == 1
        except* ValueError as value_errors:
            assert len(value_errors.exceptions) == 1


def test_except_star_valueerror_first():
    with context_for_test('app_various_errors') as module:
        app = module.app
        config = {
            'output': {'type': 'dict'},
        }

        try:
            freeze(app, config)
        except* TypeError as type_errors:
            assert len(type_errors.exceptions) == 2
        except* ValueError as value_errors:
            # UnexpectedStatus is a ValueError
            assert len(value_errors.exceptions) == 2

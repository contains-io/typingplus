# -*- coding: utf-8 -*-
"""Tests for annotation type hint casting."""

from __future__ import unicode_literals

from typingplus import get_type_hints


def test_short_form_single():
    """Test type hinting with short-form comments and a single arg."""
    def func(arg1):
        # type: (int) -> None
        pass

    assert get_type_hints(func) == {
        'return': type(None),
        'arg1': int
    }


def test_short_form_multi():
    """Test type hinting with short-form comments and multiple args."""
    from typing import Any, AnyStr

    def func(arg1, arg2):
        # type: (AnyStr, int) -> Any
        pass

    assert get_type_hints(func, globals(), locals()) == {
        'return': Any,
        'arg1': AnyStr,
        'arg2': int
    }


def test_short_form_any_len():
    """Test short-form type hinting withthat doesn't specify arg types."""
    from typing import Any

    def func(arg1, arg2):
        # type: (...) -> Any
        pass

    assert get_type_hints(func, globals(), locals()) == {
        'return': Any
    }


def test_short_form_optional():
    """Test type hinting with short-form comments with an optional arg."""
    from typing import Optional

    def func(arg1=None):
        # type: (int) -> None
        pass

    assert get_type_hints(func, globals()) == {
        'return': type(None),
        'arg1': Optional[int]
    }


def test_long_form():
    """Test type hinting with long-form comments."""
    def func(arg1,
             arg2,  # type: int
             arg3,  # type: str
             arg4
             ):
        # type: (...) -> bool
        pass

    assert get_type_hints(func, globals(), locals()) == {
        'return': bool,
        'arg2': int,
        'arg3': str
    }


def test_no_source():
    """Test that an empty dict is returned without source for the object."""
    assert get_type_hints(int) == {}


def test_method():
    """Test that typed class objects are handled correctly."""
    class TestClass(object):

        def typed(self, arg1):
            # type: (TestClass, int) -> None
            pass

        def untyped(self, arg1):
            # type: (int) -> None
            pass

    assert get_type_hints(TestClass.typed, globals(), locals()) == {
        'return': type(None),
        'self': TestClass,
        'arg1': int
    }
    assert get_type_hints(TestClass.untyped) == {
        'return': type(None),
        'arg1': int
    }

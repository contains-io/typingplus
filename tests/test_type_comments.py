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
    from typing import Optional

    def func(arg1,
             arg2,  # type: int
             arg3,  # type: str
             arg4=None  # type: str
             ):
        # type: (...) -> bool
        pass

    assert get_type_hints(func, globals(), locals()) == {
        'return': bool,
        'arg2': int,
        'arg3': str,
        'arg4': Optional[str]
    }


def test_no_source():
    """Test that an empty dict is returned without source for the object."""
    assert get_type_hints(int) == {}


def test_method():
    """Test that typed class method objects are handled correctly."""
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


def test_class():
    """Test that typed class objects are parsed correctly."""
    class TestClass1(object):
        arg1 = None  # type: int
        arg2 = None  # type: str

    assert get_type_hints(TestClass1) == {
        'arg1': int,
        'arg2': str
    }


def test_nested_class():
    """Test that nested typed class objects are parsed correctly."""
    class TestClass2(object):
        arg1 = None  # type: int
        arg2 = None  # type: str

        class TestClass3(object):
            pass

        def func(self, value):
            # type: (int) -> None

            class TestClass4(object):
                arg4 = None  # type: int

                def func(self, value):
                    # type: (int) -> None

                    class TestClass5(object):
                        arg5 = None  # type: int

                arg6 = None  # type: bool

        arg3 = None  # type: bool

    assert get_type_hints(TestClass2) == {
        'arg1': int,
        'arg2': str,
        'arg3': bool
    }


def test_inherited_class():
    """Test that type hints are inherited by derived classes."""
    class TestClass6(object):
        arg1 = None  # type: int

    class TestClass7(TestClass6):
        pass

    assert get_type_hints(TestClass7) == {
        'arg1': int,
    }


def test_inherited_class_append():
    """Test that type hints are appended to base class type hints."""
    class TestClass8(object):
        arg1 = None  # type: int

    class TestClass9(TestClass8):
        arg2 = None  # type: str

    assert get_type_hints(TestClass9) == {
        'arg1': int,
        'arg2': str
    }


def test_inherited_class_override():
    """Test that type hints shadow base class type hints."""
    class TestClass10(object):
        arg1 = None  # type: int

    class TestClass11(TestClass10):
        arg1 = None  # type: str

    assert get_type_hints(TestClass11) == {
        'arg1': str
    }

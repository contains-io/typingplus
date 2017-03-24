# -*- coding: utf-8 -*-
"""Tests for annotation type hint casting."""

from __future__ import unicode_literals

import os.path
import types
import uuid

import pytest
import six

from typingplus import Any
import typingplus.types as tp


def test_bounded_type():
    """Test the bounded type object."""
    with pytest.raises(TypeError):
        BoundedInt = tp.Bounded[int]
    with pytest.raises(TypeError):
        BoundedInt = tp.Bounded[int, 10:20, lambda x: x, None]
    BoundedInt = tp.Bounded[int, 10:20]
    with pytest.raises(ValueError):
        BoundedInt(5)
    assert BoundedInt(10) == 10
    assert BoundedInt(15) == 15
    assert BoundedInt(20) == 20
    with pytest.raises(ValueError):
        BoundedInt(25)
    BoundedStr = tp.Bounded[str, 1:5, len]
    with pytest.raises(ValueError):
        BoundedStr('')
    assert BoundedStr('abc') == 'abc'
    with pytest.raises(ValueError):
        BoundedStr('abcdef')
    assert str(BoundedInt) == 'typingplus.types.Bounded[int, 10:20]'
    assert tp.Bounded[Any, 10:20](15) == 15
    assert tp.Bounded['int', 20](15) == 15
    assert tp.Bounded['int', 10:](15) == 15


def test_length_type():
    """Test the bounded length type object."""
    with pytest.raises(TypeError):
        LengthBoundedStr = tp.Length[str]
    with pytest.raises(TypeError):
        LengthBoundedStr = tp.Length[str, 10:20, lambda x: x]
    LengthBoundedStr = tp.Length[str, 1:5]
    with pytest.raises(ValueError):
        LengthBoundedStr('')
    assert LengthBoundedStr('a') == 'a'
    assert LengthBoundedStr('abcde') == 'abcde'
    with pytest.raises(ValueError):
        LengthBoundedStr('abcdef')
    LengthBoundedList = tp.Length[list, 1:1]
    with pytest.raises(ValueError):
        LengthBoundedList([])
    assert LengthBoundedList([1]) == [1]
    with pytest.raises(ValueError):
        LengthBoundedList([1, 2])
    assert str(LengthBoundedStr) == 'typingplus.types.Length[str, 1:5]'
    assert tp.Length[Any, 1:5]('abc') == 'abc'
    assert tp.Length['str', 20]('abc') == 'abc'


def test_validation_type():
    """Test that the validation type validates content."""
    ValidFile = tp.Valid[os.path.isfile]
    assert ValidFile(__file__) == __file__
    with pytest.raises(TypeError):
        tp.Valid[int, int, int]


def test_path_types(request):
    """Test that the supplied path validation paths work."""
    assert tp.File(__file__) == __file__
    with pytest.raises(ValueError):
        tp.File(str(uuid.uuid4()))
    assert tp.Dir(os.path.dirname(__file__)) == os.path.dirname(__file__)
    with pytest.raises(ValueError):
        tp.Dir(str(uuid.uuid4()))
    assert tp.ExistingPath(__file__) == __file__
    assert tp.ExistingPath(os.path.dirname(__file__)) == os.path.dirname(
        __file__)
    with pytest.raises(ValueError):
        tp.ExistingPath(str(uuid.uuid4()))
    try:
        home = os.environ['HOME']

        def _reset_home():
            os.environ['HOME'] = home

        request.add_finalizer(_reset_home)
    except KeyError:
        pass
    os.environ['HOME'] = '/home/bob'
    assert tp.Path('~/test') == '/home/bob/test'


def test_none_type():
    """Verify that NoneType is type(None)."""
    assert tp.NoneType is type(None)


def test_singleton():
    """Test that a singleton only allows a single instance of a class."""
    @six.add_metaclass(tp.Singleton)
    class TestClass(object):
        pass

    assert TestClass() is TestClass()


def test_uninstantiable():
    """Test that an uninstantiable class cannot be instantiated."""
    @six.add_metaclass(tp.Uninstantiable)
    class TestClass(object):
        pass

    with pytest.raises(TypeError):
        TestClass()

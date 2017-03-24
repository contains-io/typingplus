# -*- coding: utf-8 -*-
"""Tests for annotation type hint casting."""

from __future__ import unicode_literals

from collections import (
    deque,
    Counter
)
import json

import pytest
import six

from typingplus import *


@pytest.mark.parametrize('type_, expected', [
    (AnyStr, six.string_types + (bytes, bytearray)),
    (str, str),
    (ByteString, (bytes, bytearray)),
    (bytes, bytes),
    (bytearray, bytearray)
])
def test_cast_string(type_, expected):
    """Test that casting string types gives the correct types."""
    assert isinstance(cast(type_, 'abc'), expected)
    assert isinstance(cast(type_, b'abc'), expected)
    assert isinstance(cast(type_, u'abc'), expected)


def test_cast_numeric():
    """Test casting numeric types."""
    assert isinstance(cast(int, '4'), int)
    assert isinstance(cast(float, '4.0'), float)
    assert isinstance(cast(complex, '4+3j'), complex)
    assert isinstance(cast(int, 4.0), int)
    assert isinstance(cast(float, 4), float)
    assert isinstance(cast(complex, 4), complex)
    assert isinstance(cast(complex, 4.0), complex)


@pytest.mark.parametrize('type_, expected_type, expected', [
    (tuple, tuple, ('1', '2', '3', '3', '4')),
    (Tuple, tuple, ('1', '2', '3', '3', '4')),
    (Tuple[int, int, int, int, int], tuple, (1, 2, 3, 3, 4)),
    (list, list, ['1', '2', '3', '3', '4']),
    (List, list, ['1', '2', '3', '3', '4']),
    (List[int], list, [1, 2, 3, 3, 4]),
    (MutableSequence, list, ['1', '2', '3', '3', '4']),
    (MutableSequence[int], list, [1, 2, 3, 3, 4]),
    (set, set, {'1', '2', '3', '4'}),
    (Set, set, {'1', '2', '3', '4'}),
    (Set[int], set, {1, 2, 3, 4}),
    (MutableSet, set, {'1', '2', '3', '4'}),
    (MutableSet[int], set, {1, 2, 3, 4}),
    (frozenset, frozenset, frozenset(['1', '2', '3', '4'])),
    (FrozenSet, frozenset, frozenset(['1', '2', '3', '4'])),
    (FrozenSet[int], frozenset, frozenset([1, 2, 3, 4])),
    (deque, deque, deque(['1', '2', '3', '3', '4'])),
    (Counter, Counter, Counter({'1': 1, '2': 1, '3': 2, '4': 1}))
])
def test_cast_iterables(type_, expected_type, expected):
    """Test casting sequence types."""
    actual = cast(type_, ['1', '2', '3', '3', '4'])
    assert isinstance(actual, expected_type)
    assert actual == expected


@pytest.mark.parametrize('type_, expected_type, expected', [
    (dict, dict, {'1': 1}),
    (Dict, dict, {'1': 1}),
    (Dict[str, int], dict, {'1': 1}),
    (Dict[str, str], dict, {'1': '1'}),
    (Dict[int, float], dict, {1: 1.0}),
    (Dict[complex, ByteString], dict, {complex(1): b'1'})
])
def test_cast_mappings(type_, expected_type, expected):
    """Test casting mapping types."""
    actual = cast(type_, {'1': 1})
    assert isinstance(actual, expected_type)
    assert actual == expected


def test_cast_any():
    """Test casting to Any."""
    assert isinstance(cast(Any, 'abc'), six.string_types)
    assert isinstance(cast(Any, 1), int)
    assert isinstance(cast(Any, 1.0), float)


def test_cast_typevar():
    """Test casting to Any."""
    constrained_types = (int, str)
    T = TypeVar('T', *constrained_types)
    assert isinstance(cast(T, 1), constrained_types)
    assert isinstance(cast(T, b'1'), constrained_types)


def test_bad_cast():
    """Test that a bad cast raises a TypeError."""
    with pytest.raises(TypeError):
        cast(int, 'abc')


def test_bad_tuple_Cast():
    """Test that casting a bad tuple raises a TypeError."""
    with pytest.raises(TypeError):
        cast(Tuple[int], [1, 2, 3])

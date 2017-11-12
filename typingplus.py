# -*- coding: utf-8 -*-
"""A module for handling with typing and type hints.

In addition to the functions below, it also exports everything that the typing
and typing_extensions modules export.

Functions:
    cast: Casts a value to a specific type.
    get_type_hints: Gets all type hints for an object, including comment type
        hints.
    is_instance: An implementation of isinstance that works with the type
        definitions from the typing library.
"""
# pragma pylint: disable=undefined-variable

from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import functools
import inspect
import re
import sys
import tokenize

import pkg_resources
import six

_typing_backport_version = tuple(
    int(v) for v in pkg_resources.get_distribution('typing').version.split('.')
)
if (3, 5) <= sys.version_info < _typing_backport_version:
    # Load the typing backport instead of the built-in typing library.
    #
    # In order to assure that the latest version (backport) is loaded from
    # site-packages sys.path must be reversed.
    import imp
    _path = list(reversed(sys.path))
    _mod_info = imp.find_module('typing', _path)
    typing = imp.load_module('typing', *_mod_info)
else:
    import typing
globals().update(  # Super wildcard import.
    {k: v for k, v in six.iteritems(vars(typing)) if k not in globals()}
)
globals()['__all__'] = tuple(str(v) for v in globals()['__all__'])

import typing_extensions  # pylint: disable=wrong-import-position
globals().update(  # Super wildcard import.
    {k: v for k, v in six.iteritems(vars(typing_extensions))
     if k not in globals()}
)
globals()['__all__'] += tuple(str(v) for v in globals()['__all__'])

globals()['__all__'] += ('is_instance',)

_get_type_hints = typing.get_type_hints

_STRING_TYPES = six.string_types + (ByteString,)

# Deque is not registered in some versions of the typing library.
MutableSequence.register(collections.deque)


def get_type_hints(obj,  # type: Any
                   globalns=None,  # type: Optional[Dict[str, Any]]
                   localns=None  # type: Optional[Dict[str, Any]]
                   ):
    # type: (...) -> Dict[str, Any]
    """Return all type hints for the function.

    This attempts to use typing.get_type_hints first, but if that returns None
    then it will attempt to reuse much of the logic from the Python 3 version
    of typing.get_type_hints; the Python 2 version does nothing. In addition to
    this logic, if no code annotations exist, it will attempt to extract
    comment type hints for Python 2/3 compatibility.

    Args:
        obj: The object to search for type hints.
        globalns: The currently known global namespace.
        localns: The currently known local namespace.

    Returns:
        A mapping of value names to type hints.
    """
    globalns, localns = _get_namespace(obj, globalns, localns)
    hints = _get_type_hints(obj, globalns, localns) or {}
    if not hints and not getattr(obj, '__no_type_check__', None):
        hints.update(getattr(obj, '__annotations__', {}))
        if not hints:
            hints.update(_get_comment_type_hints(obj, globalns, localns))
        defaults = _get_func_defaults(obj)
        for name, value in six.iteritems(hints):
            if value is None:
                value = type(None)
            if isinstance(value, six.string_types):
                value = _ForwardRef(value)
            value = _eval_type(
                value, globalns, localns)
            is_optional = bool(name in defaults and defaults[name] is None)
            if is_optional:
                value = Optional[value]
            hints[name] = value
    return hints


def _get_namespace(obj,  # type: Any
                   globalns,  # type: Optional[Dict[str, Any]]
                   localns  # type: Optional[Dict[str, Any]]
                   ):
    # type: (...) -> Tuple[Dict[str, Any], Dict[str, Any]]
    """Retrieve the global and local namespaces for an object.

    Args:
        obj: An object.
        globalns: The currently known global namespace.
        localns: The currently known local namespace.

    Returns:
        A tuple containing two dictionaries for the global and local namespaces
        to be used by eval.
    """
    if globalns is None:
        globalns = getattr(obj, '__globals__', {})
        if localns is None:
            localns = globalns
    elif localns is None:
        localns = globalns
    return globalns, localns


def _get_comment_type_hints(func,  # type: Callable[..., Any]
                            globalns,  # type: Dict[str, Any]
                            localns  # type: Dict[str, Any]
                            ):
    # type: (...) -> Dict[str, Any]
    """Get a mapping of parameter names to type hints from type hint comments.

    Args:
        func: The function to search for type hint comments.

    Returns:
        A dictionary mapping the function parameters to the type hints found
        for each parameter in the type hint comments.
    """
    try:
        source = inspect.getsource(func)
    except (IOError, TypeError):
        return {}
    hints = {}
    getargspec = getattr(
        inspect, 'get{}argspec'.format('full' if six.PY3 else ''))
    full_signature = getargspec(func)
    signature = list(full_signature[0]) + [s for s in full_signature[1:3] if s]
    for comment in _get_type_comments(source):
        name, value = comment
        name = name.strip()
        value = value.strip()
        if name in signature:
            hints[name] = value
        elif name.startswith('(') and name.endswith(')'):
            hints['return'] = value
            type_values = _parse_short_form(name, globalns, localns)
            if len(type_values) == len(signature) - 1:
                signature = signature[1:]
            if len(type_values) == len(signature):
                hints.update(zip(signature, type_values))
    return hints


def _get_func_defaults(func):
    # type: (Callable[..., Any]) -> Dict[str, Any]
    """Get the default values for the function parameters.

    Args:
        func: The function to inspect.

    Returns:
        A mapping of parameter names to default values.
    """
    _func_like = functools.wraps(func)(lambda: None)
    _func_like.__defaults__ = getattr(func, '__defaults__', None)
    if hasattr(func, '__code__'):
        _func_like.__code__ = func.__code__
    if not hasattr(_func_like, '__kwdefaults__'):
        _func_like.__kwdefaults__ = {}
    return _get_defaults(_func_like)


def _get_type_comments(source):
    # type: (str) -> Generator[Tuple[str, str], None, None]
    """Yield type hint comments from the source code.

    Args:
        source: The source code of the function to search for type hint
            comments.

    Yields:
        All type comments that come before the body of the function as
        (name, type) pairs, where the name is the name of the variable and
        type is the type hint. If a short-form type hint is reached, it is
        yielded as a single string containing the entire type hint.
    """
    reader = six.StringIO(inspect.cleandoc(source)).readline
    name = last_token = None
    tokens = tokenize.generate_tokens(reader)
    for token, value, _, _, _ in tokens:
        if token == tokenize.INDENT:
            return
        if token == tokenize.NAME:
            name = value
        elif token == tokenize.COMMENT:
            match = re.match(r'#\s*type:(.+)', value)
            if match:
                type_sig = match.group(1).strip()
                if '->' in type_sig and last_token == tokenize.NEWLINE:
                    yield type_sig.split('->')
                elif name:
                    yield name, type_sig
                    name = None
        last_token = token


def _parse_short_form(comment, globalns, localns):
    # type: (str, Dict[str, Any], Dict[str, Any]) -> Tuple[type, ...]
    """Return the hints from the comment.

    Parses the left-hand side of a type comment into a list of type objects.
    (e.g. everything to the left of "->").

    Returns:
        A list of types evaluated from the type comment in the given global
        name space.
    """
    if '(...)' in comment:
        return ()
    comment = comment.replace('*', '')
    hints = eval(comment, globalns, localns)  # pylint: disable=eval-used
    if not isinstance(hints, tuple):
        hints = (hints,)
    return hints


def cast(tp, obj):
    # type: (Type[_T], Any) -> _T
    """Cast the value to the given type.

    Args:
        tp: The type the value is expected to be cast.
        obj: The value to cast.

    Returns:
        The cast value if it was possible to determine the type and cast it.
    """
    if is_instance(obj, tp):
        return obj
    obj_repr = repr(obj)
    if isinstance(tp, type):
        if issubclass(tp, _STRING_TYPES):
            obj = _cast_string(tp, obj)
        elif hasattr(tp, '__args__') and tp.__args__:
            obj = _cast_iterables(tp, obj)
    for type_ in _get_cast_types(tp):
        try:
            args = getattr(type_, '__args__', None)
            constraints = getattr(type_, '__constraints__', None)
            if args or constraints:
                return cast(type_, obj)
            return type_(obj)
        except Exception as e:  # pylint: disable=broad-except,unused-variable
            pass
    type_repr = _type_repr(tp)
    six.raise_from(
        TypeError("Cannot convert {} to {}.".format(obj_repr, type_repr)),
        locals().get('e')
    )


def _get_cast_types(type_):
    # type: (Type) -> List[Union[type, Callable[..., Any]]]
    """Return all type callable type constraints for the given type.

    Args:
        type_: The type variable that may be callable or constrainted.

    Returns:
        A list of all callable type constraints for the type.
    """
    cast_types = [type_] if callable(type_) else []
    if (hasattr(type_, '__constraints__') and
            isinstance(type_.__constraints__, Iterable)):
        cast_types.extend(type_.__constraints__)
    if (hasattr(type_, '__args__') and
            isinstance(type_.__args__, Iterable)):
        cast_types.extend(type_.__args__)
    if hasattr(type_, '_abc_registry'):
        cast_types.extend(sorted(  # Give list and tuple precedence.
            type_._abc_registry,
            key=lambda k: k.__name__,
            reverse=True))
    if hasattr(type_, '__extra__') and type_.__extra__:
        if isinstance(type_.__extra__, type):
            cast_types.append(type_.__extra__)
        if hasattr(type_.__extra__, '_abc_registry'):
            cast_types.extend(sorted(  # Give list and tuple precedence.
                type_.__extra__._abc_registry,
                key=lambda k: k.__name__,
                reverse=True))
    return cast_types


def is_instance(obj, type_):
    # type: (Any, Type) -> bool
    """Determine if an object is an instance of a type.

    In addition to the built-in isinstance, this method will compare against
    Any and TypeVars.

    Args:
        obj: Any object.
        type_: The type to check the object instance against.

    Returns:
        True if the object is an instance of the type; otherwise, False.
    """
    if type_ == Any:
        return True
    if isinstance(type_, type):
        if hasattr(type_, '__args__') and type_.__args__:
            generic_type = (type_.__origin__ if hasattr(
                type_, '__origin__') and type_.__origin__ else type_)
            if issubclass(type_, tuple) and Ellipsis not in type_.__args__:
                return (len(obj) == len(type_.__args__) and
                        isinstance(obj, generic_type) and all(
                            is_instance(val, typ) for typ, val in
                            zip(type_.__args__, obj)))
            elif issubclass(type_, Mapping):
                return isinstance(obj, generic_type) and all(
                    is_instance(k, type_.__args__[0]) and
                    is_instance(v, type_.__args__[1]) for
                    k, v in six.iteritems(obj)
                )
            elif issubclass(type_, Iterable):
                return isinstance(obj, generic_type) and all(
                    is_instance(v, type_.__args__[0]) for v in obj)
        elif isinstance(obj, type_):
            return True
    args = getattr(type_, '__args__', getattr(type_, '__constraints__', None))
    return any(is_instance(obj, typ) for typ in args or ())


def _cast_iterables(type_, obj):
    # type: (Type, Any) -> Any
    """Cast items contained in the object if the object is a container.

    Args:
        type_: The type of the container. If the object is not a container, no
            casting is performed.
        obj: The container object. If the object is not a container, no casting
            is performed.

    Returns:
        An object that can be cast to the given type. This may be either the
        original object, or a generator that casts all items within the object
        if the object is a container.
    """
    if issubclass(type_, tuple) and Ellipsis not in type_.__args__:
        if len(obj) == len(type_.__args__):
            return [cast(typ, val) for typ, val in zip(type_.__args__, obj)]
        raise TypeError(
            'The number of elements [{}] does not match the type {}'.format(
                len(obj), _type_repr(type_)))
    if issubclass(type_, Mapping):
        return {
            cast(type_.__args__[0], k): cast(type_.__args__[1], v)
            for k, v in six.iteritems(obj)
        }
    if issubclass(type_, Iterable):
        return [cast(type_.__args__[0], v) for v in obj]
    return obj


def _cast_string(type_, obj):
    # type: (Type, Any) -> Any
    """Cast the object to a string type.

    If the type is a ByteString, but the object does not have a __bytes__
    method, the object will first be converted to a string.

    Note:
        This does not guarantee that it will cast to a string, as some aspects
        are assumed to be handled by the calling function. Unless the object
        needs to be encoded or decoded, the object will be returned unmodified.

    Args:
        type_: The type to cast the object to if possible.
        obj: The object to cast.

    Returns:
        The object cast to a string type if necessary. This is only necessary
        if the requested type is a ByteString and the object does not have a
        __bytes__ method, or the object needs to be encoded or decoded.
    """
    encoding = sys.stdin.encoding or sys.getdefaultencoding()
    if issubclass(type_, ByteString):
        if not hasattr(obj, '__bytes__'):
            obj = str(obj)
        if isinstance(obj, six.string_types):
            return obj.encode(encoding)
    if issubclass(type_, six.string_types) and isinstance(obj, ByteString):
        return obj.decode(encoding)
    return obj

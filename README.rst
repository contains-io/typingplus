typingplus
==========

|PyPI| |Python Versions| |Build Status| |Coverage Status| |Code Quality|

*An enhanced version of the Python typing library that always uses the latest
version of typing available, regardless of which version of Python is in
use.*


Installation
------------

Install it using pip:

::

    pip install typingplus


Features
--------

- Contains all of the typing library, and is guaranteed to use the latest
  installed version of the ``typing`` library, even if the version of Python in
  use has an older version of ``typing``.
- ``typing_extensions`` is integrated to be as compatible with the future of the
  ``typing`` module as possible.
- Support for comment type hints.
- A functional cast method, including to the abstract types defined in the
  ``typing`` module.
- An is_instance method that works with the abstract types defined in the
  ``typing`` module.


Upcoming Features
-----------------

- Comment type hints for classes.


Usage
-----

See `PEP 484`_.


.. _PEP 484: https://www.python.org/dev/peps/pep-0484/

.. |Build Status| image:: https://travis-ci.org/contains-io/typingplus.svg?branch=development
   :target: https://travis-ci.org/contains-io/typingplus
.. |Coverage Status| image:: https://coveralls.io/repos/github/contains-io/typingplus/badge.svg?branch=development
   :target: https://coveralls.io/github/contains-io/typingplus?branch=development
.. |PyPI| image:: https://img.shields.io/pypi/v/typingplus.svg
   :target: https://pypi.python.org/pypi/typingplus/
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/typingplus.svg
   :target: https://pypi.python.org/pypi/typingplus/
.. |Code Quality| image:: https://api.codacy.com/project/badge/Grade/ccf7fb925d32499f80a1cfb8a640436b
   :target: https://www.codacy.com/app/contains-io/typingplus?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=contains-io/typingplus&amp;utm_campaign=Badge_Grade

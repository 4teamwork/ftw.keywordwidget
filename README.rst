.. contents:: Table of Contents


Introduction
============

``ftw.keywordwidget`` Provides three features:

1. A widget, which loads chosen2 for better usability on single and multiselect fields.
2. A ``ChoicePlus``, which allows new terms. This is prevents us from making a specific, complicated source, which allow new items.
3. Render a additional ``New Entry`` textarea for new terms.


Primary Use-Case
----------------

The widget provides the same functionality as the AT Keywordwidget with some benefits.



Demarcation
-----------
There are several other z3c form widgets for plone 4.x, which provides a similar feature set, Like ``collective.z3cform.keywordwidget``, or the ``AutocompleteWidget``.

But this widget is using the default ``zope.schema.Choice`` field, which allows you to provide any source or vocabulary for the widget.

Further you can configure the chosen2 plugin as you wish.



Compatibility
-------------

Plone 4.3.x


Installation
============

- Add the package to your buildout configuration:

::

    [instance]
    eggs +=
        ...
        ftw.keywordwidget


Usage
=====

### USAGE ###

Development
===========

**Python:**

1. Fork this repo
2. Clone your fork
3. Shell: ``ln -s development.cfg buidlout.cfg``
4. Shell: ``python boostrap.py``
5. Shell: ``bin/buildout``

Run ``bin/test`` to test your changes.

Or start an instance by running ``bin/instance fg``.


Links
=====

- Github: https://github.com/4teamwork/ftw.keywordwidget
- Issues: https://github.com/4teamwork/ftw.keywordwidget/issues
- Pypi: http://pypi.python.org/pypi/ftw.keywordwidget
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.keywordwidget


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.keywordwidget`` is licensed under GNU General Public License, version 2.

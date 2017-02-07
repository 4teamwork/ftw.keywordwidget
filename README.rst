.. contents:: Table of Contents


Introduction
============

``ftw.keywordwidget`` provides three features:

1. A widget, which loads select2 for better usability on single and multiselect fields.
2. A ``ChoicePlus`` field, which allows new terms. This is prevents us from making a specific, complicated source, which allow new items.
3. Render a additional ``New Entry`` textarea for new terms.

The widget supports schema.Choice, schema.Tuple and schema.List fields.


Primary Use-Case
----------------

The widget provides the same functionality as the AT Keywordwidget with some benefits.

Features from the AT Widget:

- Protect adding new terms by a permission/role
- Display all possible values
- Add new terms

Benefits:

- Configurable select2 widget
- Sane defaults for the Widget
- z3c.form Widget
- Based on the SelectWidget (No new converter, etc. needed)
- Configurable "add new terms permission" per field/widget possible

Demarcation
-----------
There are several other z3c form widgets for plone 4.x, which provides a similar feature set, Like ``collective.z3cform.keywordwidget``, or the ``AutocompleteWidget``.

- They do not fit the primary Use-Case.

Further you can configure the select2 plugin as you wish.


TODO
----

- Implement async option
- Implement select2 tag option


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


Usage / Integration
===================

This Widget is not automatically applied to all possible select fields.
The idea is that you integrate it where needed by your self.

But for the primary Use-Case mentioned above, there is a behavior:

1. Install the ``default`` profile and the ``select2`` profile if needed.
2. Enable the ``ftw.keywordwidget.behavior.IKeywordCategorization`` behavior on your content type.

For some other Use-Cases you can also enable the ``ftw.keywordwidget.behavior.IKeywordUseCases`` behavior.
This enables a single and multi select field.

Check behaviors.py for examples:


::

    from ftw.keywordwidget.widget import KeywordFieldWidget


    class IKeywordUseCases(model.Schema):

        directives.widget('types', KeywordFieldWidget)
        types = schema.List(
            title=u'Types',
            value_type=schema.Choice(
                title=u"Multiple",
                vocabulary='plone.app.vocabularies.PortalTypes',
                ),
            required=False,
            missing_value=(),
        )

        directives.widget('types2', KeywordFieldWidget)
        types2 = schema.Choice(
            title=u'Single type',
            vocabulary='plone.app.vocabularies.PortalTypes',
            required=False,
            missing_value=(),
        )

    alsoProvides(IKeywordUseCases, IFormFieldProvider)


You can configure select2 as you wish by giving a ``js_config`` to widget factory.

::

    directives.widget('types',
                      KeywordFieldWidget,
                      js_config={'placeholder': 'Select something...'})


The select2 4.0.3 JS Plugin is shipped with this package.
But you it's not installed with the default profile, because you may already have a
select2 JS installed for other purpose.
If you need select2 you can install the ``ftw.keywordwidget Install select2 jquery plugin`` profile.



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

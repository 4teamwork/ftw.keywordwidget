.. contents:: Table of Contents


Introduction
============

``ftw.keywordwidget`` provides three features:

1. A widget, which loads select2 for better usability on single and multiselect fields.
2. A ``ChoicePlus`` field, which allows new terms. This is prevents us from making a specific, complicated source, which allow new items.
3. Render a additional ``New Entry`` textarea for new terms.
4. Uses tags feature of select 2 to add new keywords.
5. A async option to get the selectable options with the select2 ajax options.

The widget supports schema.Choice, schema.Tuple and schema.List fields.


Unicode or utf-8??
------------------

The ICategorization behavior provided by this package depends on the plone
default index "Subject".
In DX "Subject" is a accessor for "subject", which returns utf-8.
"subject" itself has a property getter for "subjects", where the values are actually stored.

The Plone KeywordsVocabulary builds it's terms using the catalog value, which is utf-8 in case of the Subject index. By convention indexed values should be always utf-8 and DX values should always be unicode.

This actually means in the case of the KeywordsVocabulary the value needs to be stored as utf-8, because the vocabulary values are encoded as utf-8.
The SequenceWidget fieldToWidget converter has a sanity check included, which makes sure only field values, which are also in vocabulary are computed. 
And this means if you store new terms as unicode values, the whole thing falls apart. Currently the widget makes sure to work perfectly with the "Subject" index, which relays on utf-8 values, which is not common with DX types. 

Beside of the primary Use-Case, the widget also supports vocabularies, with unicode values, but this needs to be configured separately on the widget.
New terms are than added as unicode instead of utf-8.

::

    directives.widget('unicode_keywords', KeywordFieldWidget, new_terms_as_unicode=True)
    unicode_keywords = schema.Tuple(
        title=u'UnicodeTags',
        value_type=ChoicePlus(
            title=u"Multiple",
            vocabulary='ftw.keywordwidget.UnicodeKeywordVocabulary',
            ),
        required=False,
        missing_value=(),
    )


Async option
------------

The async option can only be used if the source is a IQuerySource from z3c.formwidget.query.interfaces.
This interface extends the ISource specification by a `search` method, which is essential for the async option.

Basically if `async=True` the select2 Widget asks a search endpoint for possible options by a given search term.
Further the search endpoint queries the `IContentSourceBinder` defined on the field.

::

    directives.widget('async', KeywordFieldWidget, async=True)
    async = schema.Tuple(
        title=u'Some async values',
        value_type=ChoicePlus(
            source=MySourceBinder(),
            ),
        required=False,
        missing_value=(),
    )


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

1. Install the ``default`` profile and the ``select2js`` profile if needed.
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

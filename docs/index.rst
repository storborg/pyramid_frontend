Overview
--------

Scott Torborg - `Cart Logic <http://www.cartlogic.com>`_

Provides:

* Theme / template handling.
* Theme configuration.
* Theme stacking (one theme can inherit from another).
* Image filtering / serving.
* Asset handling and compilation.
* Uses Mako, PIL, require.js, and LESS.

Command line tools:

* Compile assets (in addition to a programmatic method for integrating with
  other build steps)


Installation
------------

Install with pip::

    $ pip install pyramid_frontend


Quick Start
------------

Include pyramid_frontend, by calling ``config.include('pyramid_frontend')`` or
adding pyramid_frontend to ``pyramid.includes``.

Configure the following settings:

* ``pyramid_frontend.compiled_asset_dir``
* ``pyramid_frontend.original_image_dir``
* ``pyramid_frontend.processed_image_dir``

* ``pyramid_frontend.image_url_prefix``
* ``pyramid_frontend.asset_url_prefix``

* ``pyramid_frontend.use_compiled``

Register at least one theme, using the ``config.add_theme(theme)`` directive.
You can also pass a dotted string (e.g. ``myapp.themes.foo.FooTheme``) which
will be resolved relative to the calling module.

Other possible mechanisms for theme registration which may be added later are a
setuptools entrypoint or a settings key.

* Themes are subclasses of the ``pyramid_frontend.Theme`` class.
* Class attributes or properties can be set for resource configuration.
* Paths are interpreted as relative to the directory of the module containing
  the class definition.
* An example:

.. code-block:: python

    class MyTheme(Theme):
        template_dir = ...
        static_dir = ...
        image_filters = {
            'detail': ...
            'thumb': ...
        }
        assets = {
            'main-js': ('static/js/main.js', 'requirejs'),
            'main-less': ('static/css/main.less', 'less'),
        }

Configure your application to use a theme, with one of the following methods:

* Specify the ``pyramid_frontend.theme`` setting key.
* Call ``config.set_theme_strategy(func)`` with a function that will return the
  theme to use.
* An example:

.. code-block:: python

    def mobile_theme_strategy(request):
        if request.is_mobile and not request.session.get('use_desktop'):
            return 'my-mobile-theme'
        else:
            return 'my-desktop-theme'

Inside your app, specify a .html or .txt renderer. It will be rendered using
the currently active theme (or call the theme strategy function to determine
which theme to use).

The ``request`` object has a few added methods.

* ``request.asset_tag(key)`` - Generate an asset tag (either a script tag or
  stylesheet tag, or some combination thereof) for a corresponding asset key.
  In production, this will point to a concatenated / minified file.

* ``request.image_url(name, original_ext, filter_key)`` - Generate a URL for an
  image as processed by the specified filter chain.
* ``request.image_tag(name, original_ext, filter_key, **kwargs)`` - Generate an
  img tag for an image as processed by the specified filter chain.
* ``request.image_original_path(name, original_ext)`` - Return the filesystem
  path to the original file for this image.

* ``request.theme`` is a reified property on ``request`` - Return the theme
  instance that will be used to serve this request.

When using in production, call ``pcompile production.ini`` to generate static
assets, or call ``pyramid_frontend.compile(registry.settings)``.


Theme Inheritance
=================

Themes can stack on top of another theme by subclassing them.


Templates
~~~~~~~~~

An inheriting theme's templates will layer on top of the superclass theme's
templates. The renderer will attempt to resolve templates to the child-most
class first, then traverse up the inheritance chain.

Inside a template, you can refer to files with the prefix ``super:`` to make
the filename resolve in the theme that is being inherited from.

Image Filters
~~~~~~~~~~~~~

An inheriting theme's image filters will layer on top of the superclass theme's
image filters. If an image filter of the same name is specified, the child
class will override the superclass.

Assets
~~~~~~

An inheriting theme's asset entry points will layer on top of the super class
theme's entry points. If an entry point of the same name is specified, the
child class will override the superclass.

Static Files
------------

Each theme has exactly one static file directory. It will be served up at an
underscore-prefixed path corresponding to the theme's key.


Asset Compilation
=================

The ``assets`` dict attribute maps entry point names to a tuple of URL paths
and asset type.

In development, simply call ``request.asset_tag(key)`` to generate an asset tag.

In production, assets must be compiled before that call. The asset compilation
step does the following for each entry point in each theme:

- Resolve the entry point path to a filesystem path.
- Collect static dirs from the theme and superclasses for use in resolving
  references during the compilation process.
- Compile the asset by calling a ``Compiler`` instance with the theme and the
  asset entry point.
- Save the result to a file in ``pyramid_frontend.compiled_asset_dir`` with a
  filename based on the sha1 of the contents.  - Collect all filenames for
  compiled files, mapping entry point name to filename.
- Write the filename to a file with a path like
  ``<compiled asset dir>/<theme key>/<entry point>.map``.



Code Standards
--------------

pyramid_frontend has a comprehensive test suite with 100% line and branch
coverage, as reported by the excellent ``coverage`` module. To run the tests,
simply run in the top level of the repo::

    $ nosetests

There are no `PEP8 <http://www.python.org/dev/peps/pep-0008/>`_ or
`Pyflakes <http://pypi.python.org/pypi/pyflakes>`_ warnings in the codebase. To
verify that::

    $ pip install pep8 pyflakes
    $ pep8 .
    $ pyflakes .

Any pull requests must maintain the sanctity of these three pillars.

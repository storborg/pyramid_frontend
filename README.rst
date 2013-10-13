pyramid_frontend - Theme, Images, Assets Handling for Pyramid
=============================================================

Scott Torborg - `Cart Logic <http://www.cartlogic.com>`_

Provides:

* Theme / template handling.
* Theme configuration.
* Theme stacking (one theme can inherit from another).
* Image filtering / serving.
* Asset handling and compilation.
* Uses Mako, PIL, require.js, and LESS.

Command line tools:

* Compile assets (in addition to a programmatic method for integrating with other build steps)


Installation
============

Install with pip::

    $ pip install pyramid_es


Quick Start
===========

Include pyramid_frontend, by calling ``config.include('pyramid_frontend')`` or adding pyramid_frontend to ``pyramid.includes``.

Configure the following settings:

* ``pyramid_frontend.compiled_asset_dir``
* ``pyramid_frontend.original_image_dir``
* ``pyramid_frontend.processed_image_dir``

* ``pyramid_frontend.image_url_prefix``
* ``pyramid_frontend.asset_url_prefix``

* ``pyramid_frontend.use_compiled``

Register at least one theme, using the ``config.add_theme(theme_key, theme)`` directive. (Possibly a setuptools entry point, later.)

* Themes are subclasses of the ``pyramid_frontend.Theme`` class.
* Class attributes or properties can be set for resource configuration.
* Paths are interpreted as relative to the directory of the module containing the class definition.
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
* Call ``config.set_theme_strategy(func)`` with a function that will return the theme to use.
* An example:

.. code-block:: python

    def mobile_theme_strategy(request):
        if request.is_mobile and not request.session.get('use_desktop'):
            return 'my-mobile-theme'
        else:
            return 'my-desktop-theme'

Inside your app, specify a .html or .txt renderer. It will be rendered using the currently active theme (or call the theme strategy function to determine which theme to use).

The ``request`` object has a few added methods.

* ``request.asset_tag(key)``
* ``request.asset_url(path)``

* ``request.image_url(name, filter_key)``
* ``request.image_tag(name, filter_key, **kwargs)``
* ``request.image_original_path(name, original_ext)``

* ``request.theme`` is a reified property on ``request``

When using in production, call ``pcompile production.ini`` to generate static assets, or call ``pyramid_frontend.compile(registry.settings)``.


Templates
=========

Inside a template, you can refer to files with the prefix ``super:`` to make the filename resolve in the theme that is being inherited from.

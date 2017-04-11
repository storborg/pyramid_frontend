from __future__ import absolute_import, print_function, division

import sys

from mako import exceptions
from pyramid.compat import reraise


class MakoRenderingException(Exception):
    """
    When an exception occurs during the rendering of a template, it will be
    re-raised as one of these exceptions.
    """
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return self.s

    __str__ = __repr__


class MakoRenderer(object):
    """
    A class which can be instantiated to make a Pyramid renderer for Mako
    templates.
    """

    def __init__(self, info, plaintext=False):
        self.name = info.name
        self.plaintext = plaintext

    def __call__(self, value, system):
        """Find and render a template.

        This replaces the default Mako renderer to locate templates by theme.

        ``system`` will contain default renderer globals plus those added by
        by :func:`add_renderer_globals`.

        ``value`` will be either the dict returned from a view or the dict
        passed to one of Pyramid's render functions. These values will
        override the ``system`` values.

        :func:`add_renderer_globals` will be called to update ``system``
        before this method is called; it can access ``value`` via
        ``event.rendering_val``.

        """
        # Avoid conflict between Pyramid and Mako ``context``s
        system['_context'] = system.pop('context', None)

        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')

        request = system['request']

        theme = request.theme
        if self.plaintext:
            lookup = theme.lookup_nofilters
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'text/plain'
        else:
            lookup = theme.lookup

        template = lookup.get_template(self.name)

        try:
            result = template.render_unicode(**system)
        except:
            try:
                exc_info = sys.exc_info()
                errtext = exceptions.text_error_template().render(
                    error=exc_info[1],
                    traceback=exc_info[2])
                reraise(MakoRenderingException(errtext), None, exc_info[2])
            finally:
                del exc_info

        return result


def mako_renderer_factory(info):
    """
    A Pyramid renderer factory to render Mako templates with default settings.
    """
    return MakoRenderer(info)


def mako_renderer_factory_txt(info):
    """
    A Pyramid renderer factory to render Mako templates with no default
    HTML-escaping filters. This renderer factory should generally be used for
    plaintext templates rather than HTML.
    """
    return MakoRenderer(info, plaintext=True)

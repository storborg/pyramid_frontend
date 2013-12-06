from __future__ import absolute_import, print_function, division

from webhelpers.html.tags import HTML, literal
from pyramid.settings import asbool

from .requirejs import RequireJSCompiler
from .less import LessCompiler


js_preamble = '''\
<script>
  if (typeof console === 'undefined') {
    console = {
      log: function () {},
      debug: function () {}
    }
  }
</script>
'''


js_paths = '''\
<script>
  require.paths
</script>
'''


compiler_classes = {
    'requirejs': RequireJSCompiler,
    'less': LessCompiler,
}


def render_js_paths(theme):
    """
    Return a script tag for use client-side which sets up require.js paths for
    all theme directories in use by the supplied theme.
    """
    cls = theme.__class__
    keys = []
    while hasattr(cls, 'key'):
        keys.append(cls.key)
        cls = cls.__bases__[0]
    lines = ["require.paths.%s = '/_%s/js';" % (key, key)
             for key in keys]
    return ''.join(['<script>'] + lines + ['</script>'])


def requirejs_tag_development(url, theme):
    """
    Return an HTML fragment to use a require.js entry point in development.
    """
    return ''.join([
        js_preamble,
        HTML.script(src=theme.require_config_path),
        render_js_paths(theme),
        HTML.script(src=theme.require_path),
        HTML.script(src=url),
    ])


def requirejs_tag_production(url, theme):
    """
    Return an HTML fragment to use a require.js entry point in production.
    """
    return ''.join([
        js_preamble,
        HTML.script(src=url),
    ])


def less_tag_development(url, theme):
    """
    Return an HTML fragment to use a less CSS entry point in development.
    """
    return ''.join([
        HTML.link(rel='stylesheet/less', type='text/css', href=url),
        HTML.script(src=theme.less_path),
    ])


def less_tag_production(url, theme):
    """
    Return an HTML fragment to use a less CSS entry point in production.
    """
    return HTML.link(rel='stylesheet', type='text/css', href=url)


tag_map = {
    ('requirejs', True): requirejs_tag_production,
    ('requirejs', False): requirejs_tag_development,
    ('less', True): less_tag_production,
    ('less', False): less_tag_development,
}


def asset_tag(request, key, **kwargs):
    """
    Request method to render an HTML fragment containing tags which reference
    the supplied entry point. This will dispatch to the appropriate tag
    rendering function based on context and entry point type.
    """
    theme = request.theme
    assets = theme.stacked_assets
    url_path, asset_type = assets[key]
    settings = request.registry.settings
    should_compile = asbool(settings.get('pyramid_frontend.compile_%s' %
                                         asset_type))
    tag_func = tag_map[(asset_type, should_compile)]
    if should_compile:
        filename = theme.compiled_asset_path(key)
        url_path = '/compiled/' + theme.key + '/' + filename
    return literal(tag_func(url_path, theme))


def compile_asset(theme, output_dir, key, entry_point, asset_type, minify):
    cls = compiler_classes[asset_type]
    compiler = cls(theme)
    compiler.compile(key=key,
                     entry_point=entry_point,
                     output_dir=output_dir,
                     minify=minify)


def includeme(config):
    config.add_request_method(asset_tag, 'asset_tag')

    compiled_path = \
        config.registry.settings['pyramid_frontend.compiled_asset_dir']
    config.add_static_view(name='compiled', path=compiled_path)

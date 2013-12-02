from __future__ import absolute_import, print_function, division

from webhelpers.html.tags import HTML, literal
from pyramid.settings import asbool


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


def render_js_paths(theme):
    cls = theme.__class__
    keys = []
    while hasattr(cls, 'key'):
        keys.append(cls.key)
        cls = cls.__bases__[0]
    lines = ["require.paths.%s = '/_%s/js';" % (key, key)
             for key in keys]
    return ''.join(['<script>'] + lines + ['</script>'])


def requirejs_tag_development(url, theme):
    return ''.join([
        js_preamble,
        HTML.script(src=theme.require_config_path),
        render_js_paths(theme),
        HTML.script(src=theme.require_path),
        HTML.script(src=url),
    ])


def requirejs_tag_production(url, theme):
    return ''.join([
        js_preamble,
        HTML.script(src=url),
    ])


def less_tag_development(url, theme):
    return ''.join([
        HTML.link(rel='stylesheet/less', type='text/css', href=url),
        HTML.script(src=theme.less_path),
    ])


def less_tag_production(url, theme):
    return HTML.link(rel='stylesheet', type='text/css', href=url)


tag_map = {
    ('requirejs', True): requirejs_tag_production,
    ('requirejs', False): requirejs_tag_development,
    ('less', True): less_tag_production,
    ('less', False): less_tag_development,
}


def asset_tag(request, key, **kwargs):
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


def includeme(config):
    config.add_request_method(asset_tag, 'asset_tag')

    compiled_path = \
        config.registry.settings['pyramid_frontend.compiled_asset_dir']
    config.add_static_view(name='compiled', path=compiled_path)

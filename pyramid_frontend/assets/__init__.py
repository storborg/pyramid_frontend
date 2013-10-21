from __future__ import absolute_import, print_function, division

import pkg_resources

from webhelpers.html.tags import HTML
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


def requirejs_tag_development(url, theme):
    return ''.join([
        js_preamble,
        HTML.script(src=theme.require_config_path),
        HTML.script(src=theme.require_path),
        HTML.script(src=url),
    ])


def requirejs_tag_production(url, theme):
    return HTML.script(src=url)


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
    return tag_func(url_path, theme)


def includeme(config):
    config.add_request_method(asset_tag, 'asset_tag')

    path = pkg_resources.resource_filename('pyramid_frontend', 'static')
    config.add_static_view(name='_pfe', path=path)

    compiled_path = \
        config.registry.settings['pyramid_frontend.compiled_asset_dir']
    compiled_path = '/Users/scott/gallery/compiled/'
    config.add_static_view(name='compiled', path=compiled_path)

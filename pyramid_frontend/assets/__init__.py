import pkg_resources

from webhelpers.html.tags import HTML


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


def requirejs_tag_development(url):
    return ''.join([
        js_premable,
        '<script src="/_pfe/require_config.js"></script>\n',
        '<script src="/_pfe/require.js"></script>\n',
        '<script src="',
        url,
        '"></script>',
    ])


def requirejs_tag_production(url):
    return ''.join(['<script src="', url, '"></script>'])


def less_tag_development(url):
    return ''.join([
        HTML.link(rel='stylesheet/less', type='text/css', href=url),
        '<script src="/_pfe/less.js"></script>',
    ])


def less_tag_production(url):
    return ''.join([
        HTML.link(rel='stylesheet', type='text/css', href=url),
    ])


tag_map = {
    ('requirejs', True): requirejs_tag_production,
    ('requirejs', False): requirejs_tag_development,
    ('less', True): less_tag_production,
    ('less', False): less_tag_development,
}


def asset_tag(request, key, **kwargs):
    assets = request.theme.stacked_assets
    url_path, asset_type = assets[key]
    should_compile = settings.get('pyramid_frontend.compile_%s' % asset_type)
    tag_func = tag_map[(asset_type, should_compile)]
    return tag_func(url_path)


def includeme(config):
    config.add_request_method(asset_tag, 'asset_tag')
    path = pkg_resources.resource_filename('pyramid_frontend', 'static')
    config.add_static_view(name='_pfe', path=path)

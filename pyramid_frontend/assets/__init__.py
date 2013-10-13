def asset_tag(request, key, **kwargs):
    pass
    #settings = request.registry.settings


def asset_url(request, path):
    pass
    #settings = request.registry.settings


def includeme(config):
    config.add_request_method(asset_tag, 'asset_tag')
    config.add_request_method(asset_url, 'asset_url')

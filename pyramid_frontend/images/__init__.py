from webhelpers.html.tags import HTML

from .files import prefix_for_name, get_url_prefix, original_path
from .views import ImageView


def add_image_filter(config, filter_chain):
    settings = config.registry.settings
    filter_registry = settings.setdefault(
        'pyramid_frontend.image_filter_registry', {})
    filter_registry[filter_chain.suffix] = filter_chain


def image_url(request, name, original_ext, filter_key):
    settings = request.registry.settings
    url_prefix = get_url_prefix(settings)
    filter_registry = settings['pyramid_frontend.image_filter_registry']

    # XXX Add this: check if there is a theme active. If so, check that the
    # supplied filter_key is ref'd within the theme: if not, fail with a
    # descriptive exception.

    chain = filter_registry[filter_key]

    return '/'.join([url_prefix,
                     prefix_for_name(name),
                     chain.basename(name, original_ext)])


def image_tag(request, name, original_ext, filter_key, **kwargs):
    settings = request.registry.settings
    filter_registry = settings['pyramid_frontend.image_filter_registry']
    filter_chain = filter_registry[filter_key]

    kwargs.setdefault('width', filter_chain.width)
    kwargs.setdefault('height', filter_chain.height)

    return HTML.img(src=request.image_url(name, original_ext, filter_key),
                    **kwargs)


def image_original_path(request, name, original_ext):
    settings = request.registry.settings
    return original_path(settings, name, original_ext)


def includeme(config):
    config.add_directive('add_image_filter', add_image_filter)

    config.add_request_method(image_url, 'image_url')
    config.add_request_method(image_tag, 'image_tag')
    config.add_request_method(image_original_path, 'image_original_path')

    url_prefix = get_url_prefix(config.registry.settings)
    config.add_route('pyramid_frontend:images',
                     '%s/{prefix}/{name}.{ext}' % url_prefix)
    config.add_view(ImageView, route_name='pyramid_frontend:images')

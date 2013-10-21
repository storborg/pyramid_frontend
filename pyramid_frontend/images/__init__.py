from webhelpers.html.tags import HTML

from .files import prefix_for_name, get_url_prefix, original_path
from .view import ImageView
from .chain import FilterChain, PassThroughFilterChain


def add_image_filter(config, chain, with_theme=None):
    """
    Register an image filter chain.
    """
    def register(with_theme):
        registry = config.registry

        if not hasattr(registry, 'image_filter_registry'):
            registry.image_filter_registry = {}
        filter_registry = registry.image_filter_registry

        if chain.suffix in filter_registry:
            registered_chain, registered_theme_set = filter_registry[chain.suffix]
            if registered_chain != chain:
                raise ValueError(
                    "suffix %r already registered with different instance" %
                    chain.suffix)
            registered_theme_set.add(with_theme)

        filter_registry[chain.suffix] = (chain, set([with_theme]))

    intr = config.introspectable(category_name='image_filters',
                                 discriminator=chain.suffix,
                                 title=chain.suffix,
                                 type_name=None)
    intr['chain'] = chain
    intr['with_theme'] = with_theme

    config.action(('image_filter', chain.suffix, with_theme),
                  register,
                  args=(with_theme,),
                  introspectables=(intr,))


# FIXME Maybe this should be split into request.image_url() and
# request.image_path() for qualified and non-qualified, respectively.
def image_url(request, name, original_ext, filter_key, qualified=False, **kw):
    filter_registry = request.registry.image_filter_registry

    # XXX Add this: check if there is a theme active. If so, check that the
    # supplied filter_key is ref'd within the theme: if not, fail with a
    # descriptive exception.

    chain, with_theme = filter_registry[filter_key]

    prefix = prefix_for_name(name)
    name = chain.basename(name, original_ext)
    if qualified:
        print "req: qualified"
        return request.route_url('pyramid_frontend:images',
                                 prefix=prefix,
                                 name=name,
                                 _scheme=kw.get('_scheme', request.scheme),
                                 _host=kw.get('_host', request.host))
    else:
        return request.route_path('pyramid_frontend:images',
                                  prefix=prefix,
                                  name=name)


def image_tag(request, name, original_ext, filter_key, **kwargs):
    filter_registry = request.registry.image_filter_registry
    chain, with_theme = filter_registry[filter_key]

    kwargs.setdefault('width', chain.width)
    kwargs.setdefault('height', chain.height)

    return HTML.img(src=request.image_url(name, original_ext, filter_key),
                    **kwargs)


def image_original_path(request, name, original_ext):
    settings = request.registry.settings
    return original_path(settings, name, original_ext)


def includeme(config):
    config.add_directive('add_image_filter', add_image_filter)
    config.add_image_filter(PassThroughFilterChain())

    config.add_request_method(image_url, 'image_url')
    config.add_request_method(image_tag, 'image_tag')
    config.add_request_method(image_original_path, 'image_original_path')

    url_prefix = get_url_prefix(config.registry.settings)
    config.add_route('pyramid_frontend:images',
                     '%s/{prefix}/{name:.+\.\w+}' % url_prefix)
    config.add_view(ImageView, route_name='pyramid_frontend:images')

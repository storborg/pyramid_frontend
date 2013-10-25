from __future__ import absolute_import, print_function, division

import os.path
import inspect
import pkg_resources

from pyramid.decorator import reify

from .templating.lookup import SuperTemplateLookup
from .templating.renderer import MakoRenderer

static_dir = pkg_resources.resource_filename('pyramid_frontend', 'static')


class Theme(object):
    template_dir = 'templates'
    static_dir = 'static'
    assets = {}
    image_filters = []
    require_config_path = '/_pfe/require_config.js'
    require_path = '/_pfe/require.js'
    less_path = '/_pfe/less.js'

    def __init__(self, settings):
        self.settings = settings
        self._compiled_asset_cache = {}

    def includeme(self, config):
        pass

    @classmethod
    def qualify_path(cls, path):
        return os.path.join(os.path.dirname(inspect.getfile(cls)), path)

    @classmethod
    def traverse_attributes(cls, name, qualify_paths=False):
        assert len(cls.__bases__) == 1, \
            "multiple inheritance not allowed for themes"
        while cls != Theme:
            el = getattr(cls, name)
            if qualify_paths:
                el = cls.qualify_path(el)
            yield cls.key, el
            cls = cls.__bases__[0]

    @reify
    def template_dirs(self):
        dirs = []
        for key, dir in self.__class__.traverse_attributes(
                'template_dir', qualify_paths=True):
            dirs.append(dir)
        return dirs

    @reify
    def lookup(self):
        return SuperTemplateLookup(directories=self.template_dirs,
                                   input_encoding='utf-8',
                                   output_encoding='utf-8')

    @reify
    def stacked_image_filters(self):
        filters = {}
        collected = self.__class__.traverse_attributes('image_filters')
        for key, class_list in reversed(list(collected)):
            class_dict = {chain.suffix: chain for chain in class_list}
            filters.update(class_dict)
        return filters.values()

    @reify
    def stacked_assets(self):
        assets = {}
        collected = self.__class__.traverse_attributes('assets')
        for key, class_dict in reversed(list(collected)):
            assets.update(class_dict)
        return assets

    @reify
    def keyed_static_dirs(self):
        cls = self.__class__
        stack = list(cls.traverse_attributes('static_dir', qualify_paths=True))
        stack.append(('pfe', static_dir))
        return stack

    def compiled_asset_path(self, key):
        if key in self._compiled_asset_cache:
            return self._compiled_asset_cache[key]
        else:
            map_path = os.path.join(
                self.settings['pyramid_frontend.compiled_asset_dir'],
                self.key,
                '%s.map' % key)
            with open(map_path) as f:
                self._compiled_asset_cache[key] = compiled_path = f.read()
                return compiled_path

    def static_url_to_filesystem_path(self, url):
        """
        Given a URL of the structure /_<theme key>/<path>, locate the static
        dir which corresponds to the theme key and re-qualify the <path> to
        that directory.
        """
        assert url.startswith('/_')
        theme_key, path = url[2:].split('/', 1)
        theme_dirs = dict(self.keyed_static_dirs)
        base_dir = theme_dirs[theme_key]
        return os.path.join(base_dir, path)


def add_theme(config, cls):
    """
    Initialize and register a theme for use.
    """
    resolved_cls = config.maybe_dotted(cls)

    settings = config.registry.settings
    theme = resolved_cls(settings)
    theme.includeme(config)

    # Register static dirs.
    static_dirs = settings.setdefault('pyramid_frontend.static_registry',
                                      set())
    for key, dir in theme.keyed_static_dirs:
        if (key, dir) not in static_dirs:
            static_dirs.add((key, dir))
            config.add_static_view('_%s' % key, path=dir)

    # Update global image filter registry as well, and ensure there are no
    # conflicts.
    for chain in theme.stacked_image_filters:
        config.add_image_filter(chain, with_theme=theme)

    def register(cls):
        themes = settings.setdefault('pyramid_frontend.theme_registry', {})
        themes[theme.key] = theme

    intr = config.introspectable(category_name='themes',
                                 discriminator=cls.key,
                                 title=cls.key,
                                 type_name=None)
    intr['cls'] = cls

    config.action(('theme', cls.key),
                  register,
                  args=(cls,),
                  introspectables=(intr,))


def set_theme_strategy(config, strategy_func):
    settings = config.registry.settings
    settings['pyramid_frontend.theme_strategy'] = strategy_func


def theme(self):
    settings = self.registry.settings
    strategy = settings.get('pyramid_frontend.theme_strategy')
    if strategy:
        key = strategy(self)
    else:
        key = settings['pyramid_frontend.theme']
    themes = settings.setdefault('pyramid_frontend.theme_registry', {})
    return themes[key]


def includeme(config):
    config.add_directive('add_theme', add_theme)
    config.add_directive('set_theme_strategy', set_theme_strategy)
    config.add_request_method(theme, 'theme', reify=True)

    config.add_renderer(name='.html', factory=MakoRenderer)
    config.add_renderer(name='.txt', factory=MakoRenderer)

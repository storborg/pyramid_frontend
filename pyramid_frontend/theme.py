import os.path
import inspect

from pyramid.decorator import reify

from .templating.lookup import SuperTemplateLookup
from .templating.renderer import MakoRenderer


class Theme(object):
    template_dir = 'templates'
    static_dir = 'static'
    assets = {}
    image_filters = {}

    def includeme(self, config):
        pass

    @classmethod
    def qualify_path(cls, path):
        return os.path.join(os.path.dirname(inspect.getfile(cls)), path)

    @classmethod
    def traverse_attributes(cls, name, qualify_paths):
        assert len(cls.__bases__) == 1, \
            "multiple inheritance not allowed for themes"
        while cls != Theme:
            if hasattr(cls, name):
                el = getattr(cls, name)
                if qualify_paths:
                    el = cls.qualify_path(el)
                yield cls.key, el
            cls = cls.__bases__[0]

    @reify
    def template_dirs(self):
        dirs = []
        for key, dir in self.__class__.traverse_attributes('template_dir',
                qualify_paths=True):
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
        for key, class_dict in self.__class__.traverse_attributes('image_filters'):
            filters.update(class_dict)
        return filters

    @reify
    def stacked_assets(self):
        assets = {}
        for key, class_dict in self.__class__.traverse_attributes('assets'):
            assets.update(class_dict)
        return assets

    @reify
    def static_dirs(self):
        return self.__class__.traverse_attributes('static_dir',
                                                  qualify_paths=True)


def add_theme(config, cls):
    """
    Initialize and register a theme for use.
    """
    settings = config.registry.settings
    themes = settings.setdefault('pyramid_frontend.theme_registry', {})
    theme = cls()
    themes[theme.key] = theme
    theme.includeme(config)

    # XXX Register static dirs.

    # XXX Update global image filter registry as well, and ensure there are no
    # conflicts.


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

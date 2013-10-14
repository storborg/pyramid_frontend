import os.path
import inspect

from pyramid.decorator import reify

from .lookup import SuperTemplateLookup


class Theme(object):
    template_dir = 'templates'

    def includeme(self, config):
        pass

    @classmethod
    def qualify_path(cls, path):
        return os.path.join(os.path.dirname(inspect.getfile(cls)), path)

    @classmethod
    def collect_attributes(cls, name, qualify_paths):
        assert len(cls.__bases__) == 1, \
            "multiple inheritance not allowed for themes"
        superclass = cls.__bases__[0]
        if superclass == object:
            els = []
        else:
            els = superclass.collect_attributes(name, qualify_paths)
        if hasattr(cls, name):
            el = getattr(cls, name)
            if qualify_paths:
                el = cls.qualify_path(el)
            els.insert(0, el)
        return els

    @reify
    def lookup(self):
        directories = self.__class__.collect_attributes('template_dir',
                                                        qualify_paths=True)
        return SuperTemplateLookup(directories=directories,
                                   input_encoding='utf-8',
                                   output_encoding='utf-8')


def add_theme(config, key, cls):
    settings = config.registry.settings
    themes = settings.setdefault('pyramid_frontend.theme_registry', {})
    themes[key] = theme = cls()
    theme.includeme(config)
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

#from .lookup import SuperTemplateLookup


class Theme(object):
    pass


def add_theme(config, key, theme):
    settings = config.registry.settings
    themes = settings.setdefault('pyramid_frontend.theme_registry', {})
    themes[key] = theme
    # XXX Update global image filter registry as well, and ensure there are no
    # conflicts.


def set_theme_strategy(config, strategy_func):
    settings = config.registry.settings
    settings['pyramid_frontend.theme_strategy'] = strategy_func


def theme(self):
    settings = self.registry.settings
    strategy = settings.get('pyramid_frontend.theme_strategy')
    if strategy:
        return strategy(self)
    return settings['pyramid_frontend.theme']


def includeme(config):
    config.add_directive('add_theme', add_theme)
    config.add_directive('set_theme_strategy', set_theme_strategy)
    config.add_request_method(theme, 'theme', reify=True)

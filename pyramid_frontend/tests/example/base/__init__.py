from pyramid_frontend.theme import Theme
from pyramid_frontend.images.chain import FilterChain


class BaseTheme(Theme):
    key = 'base'
    image_filters = {
        'full': FilterChain('full', width=400, height=400, crop=True),
    }

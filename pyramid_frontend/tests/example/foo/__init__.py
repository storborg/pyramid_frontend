from ..base import BaseTheme
from pyramid_frontend.images.chain import FilterChain


class FooTheme(BaseTheme):
    key = 'foo'
    image_filters = {
        'tiny': FilterChain('tiny', width=64, height=64, crop=True),
    }

from ..base import BaseTheme
from pyramid_frontend.images.chain import FilterChain


class FooTheme(BaseTheme):
    key = 'foo'
    image_filters = [
        FilterChain('tiny', width=64, height=64, crop=True),
    ]
    assets = {
        'main-less': ('/_foo/css/main.less', 'less'),
    }

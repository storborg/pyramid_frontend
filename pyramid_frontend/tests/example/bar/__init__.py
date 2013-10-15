from ..base import BaseTheme
from pyramid_frontend.images.chain import FilterChain


class BarTheme(BaseTheme):
    key = 'bar'
    image_filters = [
        FilterChain('full', width=400, height=400, crop=True),
    ]


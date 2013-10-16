from unittest import TestCase

from pyramid import testing


class TestConfig(TestCase):
    settings = {
        'pyramid_frontend.compiled_asset_dir': '.'
    }

    def test_directives_get_registered(self):
        with testing.testConfig(settings=self.settings) as config:
            config.include('pyramid_frontend')
            self.assertTrue(hasattr(config, 'add_image_filter'))
            self.assertTrue(hasattr(config, 'add_theme'))

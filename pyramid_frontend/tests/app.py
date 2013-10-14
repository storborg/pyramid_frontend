from pyramid.config import Configurator

from pyramid_frontend.tests.example import base, foo, bar


def noop_view(request):
    return {}


def bad_return_view(request):
    return 'not-a-dict'


def bad_template_view(request):
    return {}


def make_app():
    settings = {
        'pyramid_frontend.theme': 'foo',
    }
    config = Configurator(settings=settings)

    config.include('pyramid_frontend')

    config.add_theme('base', base.BaseTheme)
    config.add_theme('foo', foo.FooTheme)
    config.add_theme('bar', bar.BarTheme)

    config.add_route('index', '/')
    config.add_route('article', '/article')
    config.add_route('bad-return', '/bad-return')
    config.add_route('bad-template', '/bad-template')

    config.add_view(noop_view, route_name='index', renderer='index.html')
    config.add_view(noop_view, route_name='article', renderer='article.html')
    config.add_view(bad_return_view, route_name='bad-return',
                    renderer='index.html')
    config.add_view(bad_template_view, route_name='bad-template',
                    renderer='bad.html')

    return config.make_wsgi_app()


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    app = make_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

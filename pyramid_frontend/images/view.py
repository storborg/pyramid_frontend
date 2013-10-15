import os.path
import mimetypes
import pkg_resources

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.static import FileResponse

from .files import filter_sep, prefix_for_name, processed_path, original_path


def get_image_filter(registry, filter_key):
    settings = registry.settings
    filter_registry = settings.get('pyramid_frontend.image_filter_registry',
                                   {})
    chain, with_theme = filter_registry[filter_key]
    return chain


class MissingOriginal(Exception):

    def __init__(self, path, chain):
        self.path = path
        self.chain = chain
        Exception.__init__(self, 'Missing file %s' % path)


class ImageView(object):

    def __init__(self, request):
        self.request = request

    def placeholder(self, chain):
        orig_path = pkg_resources.resource_filename('pyramid_frontend.images',
                                                    'no-image.jpg')
        image_data = open(orig_path, 'rb')
        f = chain.run_chain(image_data)

        response = Response(f.read())
        response.content_type = \
            mimetypes.guess_type('x.%s' % chain.extension)[0]

        return response

    def __call__(self):
        request = self.request
        settings = request.registry.settings

        url_prefix = self.request.matchdict['prefix']
        name = self.request.matchdict['name']
        ext = self.request.matchdict['ext']

        if filter_sep in name:
            name, original_ext, chain_name = name.split(filter_sep, 2)
        else:
            original_ext = ext
            chain_name = None

        try:
            chain = get_image_filter(request.registry, chain_name)
        except KeyError:
            raise HTTPNotFound()

        if ((chain.extension and chain.extension != ext) or
                prefix_for_name(name) != url_prefix):
            raise HTTPNotFound()

        proc_path = processed_path(settings, name, original_ext, chain)

        if not os.path.exists(proc_path):
            orig_path = original_path(settings, name, original_ext)
            if not os.path.exists(orig_path):
                if settings.get('debug'):
                    return self.placeholder(chain)
                else:
                    raise MissingOriginal(path=orig_path, chain=chain)
            image_data = open(orig_path, 'rb')
            chain.run(proc_path, image_data)

        return FileResponse(proc_path, self.request)

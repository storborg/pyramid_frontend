Configuration
=============

A number of settings keys are available to configure ``pyramid_frontend``.

``pyramid_frontend.compile`` - Set to ``true`` when static assets should be
pre-compiled, rather than being served with no compilation or clientside
compilation.

``pyramid_frontend.image_url_prefix`` - The URL prefix used when serving
images. Generally, your webserver (e.g. nginx) should be configured to attempt
to serve this prefix first out of a static dir, then from the app server. This
will cause cached images to be served much faster and with no load on the app
server.

``pyramid_frontend.compiled_asset_dir`` - Path to store compiled static assets,
like concatenated / minified CSS and javascript.

``pyramid_frontend.error_dir`` - Path to store images which trigger an error
when uploaded. This is useful to debug issues with edge-case formats or user
misunderstandings.

``pyramid_frontend.original_image_dir`` - Path to store original source images
uploaded by users.

``pyramid_frontend.processed_image_dir`` - Path to cache generated variant
images.

``pyramid_frontend.module_directory`` - Path to cache compiled Mako templates
in. Must be writeable by the app server.

``pyramid_frontend.debug`` - If set to ``true``, triggers features which are
more likely to be desirable during development. For now, this just causes
templates to be immediately reloaded when changed. Additional features may use
this settings key in the future.

``pyramid_frontend.template_imports`` - Additional imports to add in every Mako
template.

